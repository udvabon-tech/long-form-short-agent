#!/usr/bin/env python3
"""
Bangla audio transcription via the Gemini API.
"""

from __future__ import annotations

import argparse
from pathlib import Path

import google.generativeai as genai

from utils import (
    ScriptError,
    ensure_readable_file,
    ensure_writable_parent,
    load_required_env_var,
    echo_error_and_exit,
)

DEFAULT_PROMPT = """Please transcribe this audio file completely and accurately with detailed timestamps. The audio is in Bangla (Bengali) language.

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


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Transcribe Bengali audio with millisecond timestamps using Gemini."
    )
    parser.add_argument(
        "audio",
        type=Path,
        help="Path to the input audio file (mp3, wav, etc.)",
    )
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        help="Optional path for the transcription output file. "
        "Defaults to <audio>_transcription.txt in the same directory.",
    )
    parser.add_argument(
        "--model",
        default="gemini-2.5-pro",
        help="Gemini model identifier to use (default: gemini-2.5-pro).",
    )
    parser.add_argument(
        "--prompt",
        type=Path,
        help="Optional custom prompt file to override the default transcription prompt.",
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Allow overwriting the output file if it already exists.",
    )
    return parser.parse_args()


def read_prompt(prompt_path: Path | None) -> str:
    if not prompt_path:
        return DEFAULT_PROMPT

    prompt_path = ensure_readable_file(prompt_path, "prompt file")
    return prompt_path.read_text(encoding="utf-8")


def transcribe_audio(
    audio_path: Path,
    output_path: Path,
    api_key: str,
    model_name: str,
    prompt_text: str,
) -> None:
    audio_path = ensure_readable_file(audio_path, "audio file")
    output_path = ensure_writable_parent(output_path)

    file_size_mb = audio_path.stat().st_size / (1024 * 1024)
    print(f"🎧 Processing: {audio_path.name} ({file_size_mb:.2f} MB)")

    audio_data = audio_path.read_bytes()

    print("🤖 Connecting to Gemini…")
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel(model_name)

    print("📝 Requesting transcription… this can take a few moments.")
    response = model.generate_content(
        [
            prompt_text,
            {"mime_type": "audio/mpeg", "data": audio_data},
        ]
    )

    if not getattr(response, "text", "").strip():
        raise ScriptError("Gemini response did not include transcription text.")

    output_path.write_text(response.text, encoding="utf-8")
    print(f"✅ Transcription saved to {output_path}")

    # Provide a quick sanity check by printing the first timestamp.
    first_line = response.text.splitlines()[0] if response.text else ""
    if first_line:
        print(f"🔎 First line: {first_line}")


def main() -> None:
    args = parse_args()
    try:
        api_key = load_required_env_var("GEMINI_API_KEY")
        prompt_text = read_prompt(args.prompt)

        if args.output:
            output_path = args.output
        else:
            output_path = args.audio.with_name(f"{args.audio.stem}_transcription.txt")

        output_path = output_path.expanduser().resolve()
        if output_path.exists() and not args.overwrite:
            raise ScriptError(
                f"Output file already exists: {output_path}\n"
                "Re-run with --overwrite to replace it."
            )

        transcribe_audio(
            audio_path=args.audio,
            output_path=output_path,
            api_key=api_key,
            model_name=args.model,
            prompt_text=prompt_text,
        )

    except ScriptError as error:
        echo_error_and_exit(str(error))
    except Exception as error:  # pragma: no cover - unforeseen runtime errors
        echo_error_and_exit(f"Unexpected error: {error}")


if __name__ == "__main__":
    main()
