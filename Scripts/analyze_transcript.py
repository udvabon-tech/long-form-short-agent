#!/usr/bin/env python3
"""
Analyze a Bengali transcript and identify viral-worthy reel segments.
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

DEFAULT_PROMPT = """আপনাকে একটি বাংলা পডকাস্ট ট্রান্সক্রিপ্ট দেওয়া হচ্ছে। এই ট্রান্সক্রিপ্ট থেকে ৩টি সবচেয়ে ভাইরাল-যোগ্য রিল (Reel) সেগমেন্ট চিহ্নিত করুন।

প্রতিটি রিলের জন্য:
1. ভাইরাল হুক টাইটেল (৩-৭ শব্দের মধ্যে, শক্তিশালী প্রশ্ন/উক্তি)
2. হুক টাইপ (Mind-Blowing Stat, Fear/Shock, Problem-Solution, Contrarian, Emotional)
3. স্টার্ট টাইমস্ট্যাম্প [HH:MM:SS.mmm]
4. এন্ড টাইমস্ট্যাম্প [HH:MM:SS.mmm]
5. সময়কাল (৩০-৯০ সেকেন্ড ideally)
6. কী কোট/মূল বক্তব্য (১টি শক্তিশালী লাইন)
7. ভাইরাল পটেনশিয়াল (১-৫ ⭐)
8. CTA বা পরবর্তী ভাবনার পরামর্শ (ঐচ্ছিক)

অতিরিক্ত নির্দেশনা:
- প্রতিটি রিলের শুরুতে শক্তিশালী হুক থাকতে হবে
- বক্তব্যের ধারাবাহিকতা বজায় রাখতে হবে, মাঝপথে কাটা যাবে না
- মনোযোগ ধরে রাখতে প্রাকৃতিক ব্রেক বা সুর পরিবর্তনের সময় রিল শেষ করুন
- শুধুমাত্র রিয়েল ভ্যালু ড্রাইভ করে এমন অংশ বাছাই করুন (ফিলার বাদ দিন)

ট্রান্সক্রিপ্ট:
{transcript}

নিচের ফরম্যাটে উত্তর দিন:

## REEL #1: "[বাংলা হুক টাইটেল]"
**Hook Type:** [হুক টাইপ]
**Start:** [HH:MM:SS.mmm]
**End:** [HH:MM:SS.mmm]
**Duration:** [XX সেকেন্ড]
**Viral Potential:** ⭐⭐⭐⭐⭐

**Key Quote:** "[মূল উক্তি]"

**Content Summary:**
- [পয়েন্ট ১]
- [পয়েন্ট ২]
- [পয়েন্ট ৩]

**CTA Idea:** [ঐচ্ছিক]

---

## REEL #2: "[বাংলা হুক টাইটেল]"
[একই ফরম্যাট অনুসরণ করুন]

---

## REEL #3: "[বাংলা হুক টাইটেল]"
[একই ফরম্যাট অনুসরণ করুন]
"""


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Identify viral reel candidates inside a Bengali transcript."
    )
    parser.add_argument(
        "transcript",
        type=Path,
        help="Path to the Gemini-generated transcript file.",
    )
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        default=Path("REEL_CUT_DIRECTIONS.md"),
        help="Markdown file to write the reel directions to (default: REEL_CUT_DIRECTIONS.md).",
    )
    parser.add_argument(
        "--model",
        default="gemini-2.5-pro",
        help="Gemini model identifier to use (default: gemini-2.5-pro).",
    )
    parser.add_argument(
        "--prompt",
        type=Path,
        help="Optional prompt override file (UTF-8 text).",
    )
    parser.add_argument(
        "--max-reels",
        type=int,
        default=3,
        help="Maximum number of reel segments to request from the model (default: 3).",
    )
    return parser.parse_args()


def build_prompt(transcript_text: str, max_reels: int, prompt_override: Path | None) -> str:
    template = DEFAULT_PROMPT
    if prompt_override:
        template = ensure_readable_file(prompt_override, "prompt file").read_text(encoding="utf-8")
    return template.replace("৩টি", f"{max_reels}টি").replace("{transcript}", transcript_text)


def analyze_transcript(
    transcript_path: Path,
    transcript_text: str,
    output_path: Path,
    api_key: str,
    model_name: str,
    prompt_text: str,
) -> None:
    transcript_path = ensure_readable_file(transcript_path, "transcript")
    output_path = ensure_writable_parent(output_path)

    if not transcript_text.strip():
        raise ScriptError(f"Transcript {transcript_path} is empty.")

    genai.configure(api_key=api_key)
    model = genai.GenerativeModel(model_name)

    print(f"🧠 Analyzing transcript: {transcript_path}")
    response = model.generate_content(prompt_text)

    if not getattr(response, "text", "").strip():
        raise ScriptError("Gemini response did not include analysis text.")

    output_path.write_text(response.text, encoding="utf-8")
    print(f"✅ Reel directions saved to {output_path}")


def main() -> None:
    args = parse_args()
    try:
        api_key = load_required_env_var("GEMINI_API_KEY")
        transcript_text = ensure_readable_file(args.transcript, "transcript").read_text(encoding="utf-8")
        prompt_text = build_prompt(
            transcript_text=transcript_text,
            max_reels=args.max_reels,
            prompt_override=args.prompt,
        )

        analyze_transcript(
            transcript_path=args.transcript,
            transcript_text=transcript_text,
            output_path=args.output,
            api_key=api_key,
            model_name=args.model,
            prompt_text=prompt_text,
        )

    except ScriptError as error:
        echo_error_and_exit(str(error))
    except Exception as error:  # pragma: no cover
        echo_error_and_exit(f"Unexpected error: {error}")


if __name__ == "__main__":
    main()
