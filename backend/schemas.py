"""Pydantic request schemas for the FastAPI application."""

from pydantic import BaseModel, Field


class TranslationRequest(BaseModel):
    page_id: int
    regions: dict[int, str] = Field(default_factory=dict)


class ApiKeyRequest(BaseModel):
    project_id: int
    provider: str = "gemini"
    api_key: str


class BubbleUpdateRequest(BaseModel):
    translated_text: str | None = None
    bbox: list[int] | None = Field(default=None, min_length=4, max_length=4)
    font_size: float | None = Field(default=None, gt=0)


class BubbleCreateRequest(BaseModel):
    bbox: list[int] = Field(min_length=4, max_length=4)
    original_text: str = ""


class BubbleRestoreRequest(BubbleCreateRequest):
    region_id: int
    page_id: int
    translated_text: str = ""
    font_size: float | None = Field(default=None, gt=0)


class TypesettingUpdateRequest(BaseModel):
    region_id: int
    translated_text: str
    font_size: float | None = Field(default=None, gt=0)


class GlossaryCreateRequest(BaseModel):
    project_id: int
    source_term: str
    target_term: str


class LoginRequest(BaseModel):
    email: str
    password: str
    remember_me: bool = False


class RegisterRequest(BaseModel):
    full_name: str
    email: str
    password: str


class ForgotPasswordRequest(BaseModel):
    email: str


class ProjectCreateRequest(BaseModel):
    title: str
    description: str = ""


class TeamInviteRequest(BaseModel):
    email: str
    role: str


class ChapterCreateRequest(BaseModel):
    chapter_name: str


class QueueStartRequest(BaseModel):
    chapter_id: int
