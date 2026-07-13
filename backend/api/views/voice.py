"""
Voice STT/TTS stubs (501).
"""
from __future__ import annotations

from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView


class SpeechToTextView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        return Response(
            {"detail": "Speech-to-text not configured"},
            status=status.HTTP_501_NOT_IMPLEMENTED,
        )


class TextToSpeechView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        return Response(
            {"detail": "Text-to-speech not configured"},
            status=status.HTTP_501_NOT_IMPLEMENTED,
        )
