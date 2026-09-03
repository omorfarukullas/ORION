"""
api/schemas.py
==============
Pydantic schemas for ORION REST API and WebSocket events.
"""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class CommandRequest(BaseModel):
    command: str = Field(..., description="Raw text command to execute in ORION", json_schema_extra={"example": "open chrome"})


class CommandResponse(BaseModel):
    raw_text: str
    intent: str
    confidence: float
    entities: dict[str, Any] = {}
    outcome: str
    success: bool = True


class StatusResponse(BaseModel):
    name: str = "ORION"
    version: str = "2.0.0"
    status: str = "IDLE"
    persona: str = "Professional ORION"
    cpu_percent: float = 0.0
    ram_percent: float = 0.0
    battery_percent: int | None = None
    battery_charging: bool | None = None


class PersonaItem(BaseModel):
    id: str
    name: str
    description: str
    rate: str
    is_active: str
    use_neural: str


class PersonaChangeRequest(BaseModel):
    persona_id: str = Field(..., description="Target persona ID or name", json_schema_extra={"example": "friendly"})


class PluginActionRequest(BaseModel):
    plugin_id: str = Field(..., description="Target plugin identifier", json_schema_extra={"example": "spotify_controller"})
