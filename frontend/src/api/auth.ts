import { request } from "./client";
import type { LoginResponse } from "./types";

export const login = (email: string, password: string, rememberMe: boolean) => request<LoginResponse>("/api/auth/login", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ email, password, remember_me: rememberMe }) });
export const register = (fullName: string, email: string, password: string) => request<LoginResponse>("/api/auth/register", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ full_name: fullName, email, password }) });
export const requestPasswordReset = (email: string) => request<{ message: string }>("/api/auth/forgot-password", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ email }) });
