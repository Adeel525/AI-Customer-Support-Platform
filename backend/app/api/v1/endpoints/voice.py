from fastapi import APIRouter, File, UploadFile

from app.services.voice_service import VoiceService

router = APIRouter(prefix="/voice", tags=["Voice Chatbot"])


@router.post("/stt")
async def speech_to_text(audio: UploadFile = File(...)):
    content = await audio.read()
    service = VoiceService()
    return await service.speech_to_text(content)


@router.post("/tts")
async def text_to_speech(text: str):
    service = VoiceService()
    return await service.text_to_speech(text)
