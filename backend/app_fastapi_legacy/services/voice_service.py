from fastapi import HTTPException, status


class VoiceService:
    """Stub service for voice chatbot (Whisper STT + OpenAI TTS)."""

    async def speech_to_text(self, audio_data: bytes) -> dict:
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail="Voice STT not yet implemented. Configure OpenAI Whisper API.",
        )

    async def text_to_speech(self, text: str) -> dict:
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail="Voice TTS not yet implemented. Configure OpenAI TTS API.",
        )
