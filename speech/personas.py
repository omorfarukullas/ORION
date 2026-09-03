"""
speech/personas.py
==================
Persona engine for ORION.

Provides selectable voice personas with distinct vocal styles, speech rates,
inflections, and synthesis hooks (e.g. Professional ORION, Friendly Mode,
and Coqui TTS / Custom Voice Clone).
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Callable, Dict, List, Optional
import re
from utils.logger import get_logger

logger = get_logger(__name__)


@dataclass
class Persona:
    """Represents a voice persona profile with styling and synthesis parameters."""
    id: str
    name: str
    description: str
    rate: int
    volume: float
    voice_index: int
    prefix_style: Optional[str] = None
    suffix_style: Optional[str] = None
    use_neural: bool = False
    custom_model_path: Optional[str] = None

    def transform_text(self, text: str) -> str:
        """Apply persona phrasing adjustments to the spoken response."""
        cleaned = text.strip()
        if not cleaned:
            return cleaned

        if self.id == "friendly":
            # Warm and conversational enhancements
            if cleaned.startswith("Result:") or cleaned.startswith("Calculated:"):
                cleaned = "Sure thing! " + cleaned
            elif cleaned.startswith("Opening") or cleaned.startswith("Launching"):
                cleaned = f"Right away! {cleaned}"
            elif cleaned.startswith("Current weather"):
                cleaned = f"Here is what it looks like outside: {cleaned}"
        elif self.id == "professional":
            # Concise and direct formal adjustments
            pass

        return cleaned


class PersonaManager:
    """Manages active voice personas and synthesis parameters."""

    DEFAULT_PERSONAS: Dict[str, Persona] = {
        "professional": Persona(
            id="professional",
            name="Professional ORION",
            description="Crisp, efficient, and direct. Ideal for deep work and rapid automation.",
            rate=175,
            volume=0.90,
            voice_index=0,
            use_neural=False,
        ),
        "friendly": Persona(
            id="friendly",
            name="Friendly Mode",
            description="Warm, upbeat, and conversational with supportive conversational cues.",
            rate=190,
            volume=0.95,
            voice_index=1,
            use_neural=False,
        ),
        "coqui_clone": Persona(
            id="coqui_clone",
            name="Coqui TTS / Custom Voice",
            description="Extensible offline neural voice synthesis and voice cloning pipeline.",
            rate=170,
            volume=1.0,
            voice_index=0,
            use_neural=True,
        ),
    }

    def __init__(self, default_persona: str = "professional") -> None:
        self._personas: Dict[str, Persona] = dict(self.DEFAULT_PERSONAS)
        self._active_id: str = default_persona if default_persona in self._personas else "professional"

    @property
    def active_persona(self) -> Persona:
        return self._personas.get(self._active_id, self._personas["professional"])

    def set_persona(self, persona_id_or_name: str) -> bool:
        """Switch active persona by id or display name."""
        key = persona_id_or_name.lower().strip()
        # Check by id
        if key in self._personas:
            self._active_id = key
            logger.info(f"Switched voice persona to: {self.active_persona.name}")
            return True
        # Check by name
        for pid, p in self._personas.items():
            if p.name.lower() == key or key in p.name.lower():
                self._active_id = pid
                logger.info(f"Switched voice persona to: {p.name}")
                return True

        logger.warning(f"Persona '{persona_id_or_name}' not found. Keeping '{self.active_persona.name}'")
        return False

    def list_personas(self) -> List[Dict[str, str]]:
        """Return list of available personas for GUI and Web selection."""
        return [
            {
                "id": p.id,
                "name": p.name,
                "description": p.description,
                "rate": str(p.rate),
                "is_active": str(p.id == self._active_id),
                "use_neural": str(p.use_neural),
            }
            for p in self._personas.values()
        ]

    def register_custom_clone(self, name: str, model_path: str, rate: int = 170) -> None:
        """Register a custom cloned voice model path for offline neural synthesis."""
        pid = f"clone_{len(self._personas)}"
        self._personas[pid] = Persona(
            id=pid,
            name=name,
            description=f"Local neural cloned voice from {model_path}",
            rate=rate,
            volume=1.0,
            voice_index=0,
            use_neural=True,
            custom_model_path=model_path,
        )
        logger.info(f"Registered custom voice clone: {name} (path: {model_path})")


# Global singleton instance
persona_manager = PersonaManager()
