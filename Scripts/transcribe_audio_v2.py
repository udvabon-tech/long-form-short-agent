#!/usr/bin/env python3
"""
Bangla Audio Transcription using Gemini API
Alternative approach using direct file upload
"""

import os
import sys
from pathlib import Path
import google.generativeai as genai


def transcribe_audio(audio_file_path, api_key):
    """
    Transcribe Bangla audio using Gemini

    Args:
        audio_file_path: Path to the audio file
        api_key: Gemini API key

    Returns:
        str: Transcribed text
    """
    # Setup API
    genai.configure(api_key=api_key)

    # Verify file exists
    if not os.path.exists(audio_file_path):
        raise FileNotFoundError(f"Audio file not found: {audio_file_path}")

    # Get file info
    file_path = Path(audio_file_path)
    file_size_mb = file_path.stat().st_size / (1024 * 1024)
    print(f"Processing: {file_path.name}")
    print(f"File size: {file_size_mb:.2f} MB")

    # Read audio file
    print("Reading audio file...")
    with open(audio_file_path, 'rb') as f:
        audio_data = f.read()

    # Create model instance - using Gemini 2.5 Pro
    model = genai.GenerativeModel('gemini-2.5-pro')

    # Create prompt for Bangla transcription with detailed timestamps
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

    print("Sending to Gemini API for transcription...")

    # Generate transcription with inline audio data
    response = model.generate_content([
        prompt,
        {
            'mime_type': 'audio/mpeg',
            'data': audio_data
        }
    ])

    return response.text


def main():
    """Main function to handle command line usage"""
    # Get API key from environment or user input
    api_key = os.environ.get('GEMINI_API_KEY')

    if not api_key:
        api_key = input("Enter your Gemini API key: ").strip()
        if not api_key:
            print("Error: API key is required")
            sys.exit(1)

    # Get audio file path
    if len(sys.argv) > 1:
        audio_file = sys.argv[1]
    else:
        audio_file = input("Enter the path to your audio file: ").strip()

    if not audio_file:
        print("Error: Audio file path is required")
        sys.exit(1)

    try:
        # Transcribe
        transcription = transcribe_audio(audio_file, api_key)

        # Display result
        print("\n" + "="*80)
        print("TRANSCRIPTION")
        print("="*80)
        print(transcription)
        print("="*80)

        # Save to file
        output_file = Path(audio_file).stem + "_transcription.txt"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(transcription)
        print(f"\nTranscription saved to: {output_file}")

    except Exception as e:
        print(f"Error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
