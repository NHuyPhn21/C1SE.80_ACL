
export class ApiRequestError extends Error {
  constructor(
    message: string,
    public readonly status?: number,
    public readonly retryAfter?: string,
  ) {
    super(message);
    this.name = "ApiRequestError";
  }
}

function getErrorMessage(body: unknown, status: number): string {
  if (body && typeof body === "object") {
    const data = body as Record<string, unknown>;
    const detail = data.detail;

    if (typeof detail === "string") {
      return detail;
    }

    if (Array.isArray(detail)) {
      const messages = detail
        .filter(
          (item): item is { msg: string } =>
            item !== null &&
            typeof item === "object" &&
            typeof item.msg === "string",
        )
        .map((item) => item.msg);

      if (messages.length > 0) {
        return messages.join("; ");
      }
    }

    if (typeof data.message === "string") {
      return data.message;
    }
  }

  if (status === 429) {
    return "API quota exceeded. Please try again later.";
  }
  if (status === 401) {
    return "Your session has expired. Please sign in again.";
  }
  if (status === 403) {
    return "You do not have permission to perform this action.";
  }
  if (status === 422 || status === 400) {
    return "Please check the submitted information.";
  }
  if (status >= 500) {
    return "The server is temporarily unavailable.";
  }

  return `Request failed (${status}).`;
}

export const request = async <T>(
  url: string,
  init?: RequestInit,
): Promise<T> => {
  let response: Response;

  try {
    response = await fetch(url, init);
  } catch (error) {
    if (error instanceof Error && error.name === "AbortError") {
      throw new ApiRequestError("The request was cancelled or timed out.");
    }

    throw new ApiRequestError(
      "Unable to connect to the server. Please check your network.",
    );
  }

  if (!response.ok) {
    const body: unknown = await response.json().catch(() => null);
    const message = getErrorMessage(body, response.status);

    throw new ApiRequestError(
      message,
      response.status,
      response.headers.get("Retry-After") ?? undefined,
    );
  }

  if (response.status === 204) {
    return undefined as T;
  }

  return response.json() as Promise<T>;
};
