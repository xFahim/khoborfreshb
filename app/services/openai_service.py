"""
Deprecated: This file has been replaced by app/services/mistral_service.py
Keeping for backward-compatibility of imports if any remain. New code should
import MistralService from app.services.mistral_service instead.
"""

from app.services.mistral_service import (
    MistralService as OpenAIService,
)  # alias for compatibility
