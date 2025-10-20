#!/usr/bin/env python3
"""
Agent responsible for transcribing audio using Gemini API.
"""

from __future__ import annotations

import time
from pathlib import Path
import google.generativeai as genai

from .base_agent import BaseAgent, AgentResult
from ..utils.errors import TranscriptionError, retry_on_failure
from ..config.validators import validate_audio_file


class TranscriptionAgent(BaseAgent):
    """Transcribes Bengali audio to text with timestamps using Gemini."""

    @property
    def stage_name(self) -> str:
        return "transcription"

    def validate_preconditions(self) -> None:
        """Validate audio file exists."""
        audio_file = self.project_config.project_root / "Transcripts" / "audio_30min.mp3"

        self._check_file_exists(audio_file, "audio file")

        # Validate audio file
        try:
            audio_info = validate_audio_file(audio_file)
            self.logger.info(f"Audio: {audio_info['duration']:.1f}s, "
                           f"{audio_info['codec']}, "
                           f"{audio_info['size_bytes']:,} bytes")
        except Exception as e:
            raise TranscriptionError(f"Invalid audio file: {str(e)}")

    @retry_on_failure(
        max_retries=3,
        delay=2.0,
        exponential_backoff=True,
        exceptions=(Exception,)
    )
    def _call_gemini_api(self, audio_data: bytes, prompt: str) -> str:
        """Call Gemini API with retry logic."""
        genai.configure(api_key=self.settings.api.gemini_api_key)
        model = genai.GenerativeModel(self.settings.api.gemini_model)

        self.logger.info(f"Calling Gemini API ({self.settings.api.gemini_model})...")

        start_time = time.time()

        response = model.generate_content([
            prompt,
            {'mime_type': 'audio/mpeg', 'data': audio_data}
        ])

        duration = time.time() - start_time

        # Record API call metrics
        self.metrics.record_api_call(
            endpoint=self.settings.api.gemini_model,
            duration=duration,
            success=True
        )

        if not getattr(response, 'text', '').strip():
            raise TranscriptionError("Gemini response did not include transcription text")

        return response.text

    def execute(self) -> AgentResult:
        """Transcribe audio file."""
        audio_file = self.project_config.project_root / "Transcripts" / "audio_30min.mp3"
        transcript_output = audio_file.with_name(f"{audio_file.stem}_transcription.txt")

        try:
            self.logger.info(f"Loading audio file...")
            audio_data = audio_file.read_bytes()

            # Build prompt
            prompt = """Please transcribe this audio file completely and accurately with detailed timestamps. The audio is in Bangla (Bengali) language.

Requirements:
- Provide complete transcription of all spoken content in Bangla script (বাংলা)
- Include very detailed timestamps for each speaker segment in the format [HH:MM:SS.mmm] at the beginning of each line or phrase
- Use millisecond precision (e.g., [00:00:15.500])
- Add timestamps frequently throughout the conversation, ideally every few seconds or when the speaker changes
- Maintain proper punctuation and formatting
- If there are multiple speakers, indicate speaker changes with labels (Speaker 1, Speaker 2, etc.)
- Preserve the original meaning and context

Format example:
[00:00:00.000] Speaker 1: [Bangla text here]
[00:00:15.500] Speaker 2: [Bangla text here]
[00:00:23.750] Speaker 1: [Bangla text continues]

Transcription:"""

            # Call Gemini API
            transcript_text = self._call_gemini_api(audio_data, prompt)

            # Save transcript
            transcript_output.write_text(transcript_text, encoding='utf-8')

            self.logger.info(f"✓ Transcription saved to: {transcript_output}")

            # Update project config
            self.project_config.transcript_path = transcript_output
            self.project_config.save()

            return AgentResult(
                success=True,
                message="Transcription completed",
                artifacts={"transcript_file": transcript_output},
                metadata={"lines": len(transcript_text.splitlines())}
            )

        except Exception as e:
            error_msg = f"Transcription failed: {str(e)}"
            self.logger.error(error_msg)
            return AgentResult(
                success=False,
                message=error_msg,
                error=TranscriptionError(error_msg)
            )

    def validate_postconditions(self, result: AgentResult) -> None:
        """Validate transcript file."""
        if not result.success:
            return

        transcript_file = result.artifacts.get('transcript_file')
        if not transcript_file:
            raise TranscriptionError("Transcript file not found in result artifacts")

        self._check_file_exists(transcript_file, "transcript")
        self._check_file_not_empty(transcript_file, min_size_bytes=100)

        # Check for timestamps
        content = transcript_file.read_text(encoding='utf-8')
        import re
        timestamps = re.findall(r'\[[\d:.]+\]', content)

        if len(timestamps) < 5:
            raise TranscriptionError(
                f"Transcript has too few timestamps ({len(timestamps)}). "
                "Expected detailed timestamps throughout."
            )

        self.logger.info(f"✓ Transcript validated: {len(timestamps)} timestamps found")
