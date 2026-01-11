"""Pydantic models for request/response validation."""

from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, HttpUrl, field_validator
import re


class MusicMetadata(BaseModel):
    """Metadata for music generation request."""
    project: Optional[str] = None
    tags: Optional[List[str]] = None
    callback_url: Optional[HttpUrl] = None


class MusicGenerationRequest(BaseModel):
    """Music generation request model."""
    
    request_id: str = Field(
        ...,
        description="Unique identifier for the request",
        pattern=r"^req_[a-zA-Z0-9_-]+$"
    )
    prompt: str = Field(
        ...,
        description="Text description of the music to generate",
        min_length=10,
        max_length=500
    )
    duration: int = Field(
        default=60,
        description="Duration in seconds (5s - 5min)",
        ge=5,
        le=300
    )
    model: str = Field(
        default="musicgen-medium",
        description="Model to use for generation"
    )
    output_format: str = Field(
        default="wav",
        description="Output audio format"
    )
    melody_file: Optional[HttpUrl] = Field(
        default=None,
        description="Optional URL to melody file for conditioning"
    )
    temperature: float = Field(
        default=1.0,
        description="Sampling temperature (creativity)",
        ge=0.1,
        le=2.0
    )
    top_k: int = Field(
        default=250,
        description="Top-k sampling parameter",
        ge=0,
        le=500
    )
    top_p: float = Field(
        default=0.0,
        description="Top-p (nucleus) sampling parameter",
        ge=0.0,
        le=1.0
    )
    metadata: Optional[MusicMetadata] = None
    
    @field_validator('model')
    @classmethod
    def validate_model(cls, v: str) -> str:
        """Validate model name."""
        allowed_models = ["musicgen-small", "musicgen-medium", "musicgen-large"]
        if v not in allowed_models:
            raise ValueError(f"Model must be one of {allowed_models}")
        return v
    
    @field_validator('output_format')
    @classmethod
    def validate_format(cls, v: str) -> str:
        """Validate output format."""
        allowed_formats = ["wav", "mp3", "flac"]
        if v not in allowed_formats:
            raise ValueError(f"Format must be one of {allowed_formats}")
        return v


class MusicGenerationResponse(BaseModel):
    """Music generation response model."""
    
    request_id: str
    status: str  # "success", "failed", "processing"
    audio_url: Optional[str] = None
    duration: Optional[float] = None
    generation_time: Optional[float] = None
    model_used: Optional[str] = None
    error: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
