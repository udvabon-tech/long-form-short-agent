#!/usr/bin/env python3
"""
Agent responsible for analyzing transcript and identifying viral reel segments.
"""

from __future__ import annotations

import time
import google.generativeai as genai

from .base_agent import BaseAgent, AgentResult
from ..utils.errors import AnalysisError, TranscriptionError, retry_on_failure
from ..config.schemas import ReelConfig


class AnalysisAgent(BaseAgent):
    """Analyzes transcript to identify viral-worthy reel segments."""

    @property
    def stage_name(self) -> str:
        return "analysis"

    def validate_preconditions(self) -> None:
        """Validate transcript exists."""
        if not self.project_config.transcript_path:
            raise AnalysisError("Transcript path not set in project config")

        self._check_file_exists(self.project_config.transcript_path, "transcript")
        self._check_file_not_empty(self.project_config.transcript_path, min_size_bytes=100)

    @retry_on_failure(max_retries=2, delay=2.0, exponential_backoff=True)
    def _call_gemini_for_analysis(self, transcript_text: str) -> str:
        """Call Gemini API for transcript analysis."""
        genai.configure(api_key=self.settings.api.gemini_api_key)
        model = genai.GenerativeModel(self.settings.api.gemini_model)

        prompt = f"""আপনাকে একটি বাংলা পডকাস্ট ট্রান্সক্রিপ্ট দেওয়া হচ্ছে। এই ট্রান্সক্রিপ্ট থেকে {self.settings.analysis.max_reels}টি সবচেয়ে ভাইরাল-যোগ্য রিল (Reel) সেগমেন্ট চিহ্নিত করুন।

প্রতিটি রিলের জন্য:
1. ভাইরাল হুক টাইটেল (৩-৭ শব্দের মধ্যে, শক্তিশালী প্রশ্ন/উক্তি)
2. হুক টাইপ (Mind-Blowing Stat, Fear/Shock, Problem-Solution, Contrarian, Emotional)
3. স্টার্ট টাইমস্ট্যাম্প [HH:MM:SS.mmm]
4. এন্ড টাইমস্ট্যাম্প [HH:MM:SS.mmm]
5. সময়কাল ({self.settings.analysis.min_duration_seconds}-{self.settings.analysis.max_duration_seconds} সেকেন্ড ideally)
6. কী কোট/মূল বক্তব্য (১টি শক্তিশালী লাইন)
7. ভাইরাল পটেনশিয়াল (১-৫ ⭐)
8. CTA বা পরবর্তী ভাবনার পরামর্শ (ঐচ্ছিক)

অতিরিক্ত নির্দেশনা:
- প্রতিটি রিলের শুরুতে শক্তিশালী হুক থাকতে হবে
- বক্তব্যের ধারাবাহিকতা বজায় রাখতে হবে, মাঝপথে কাটা যাবে না
- মনোযোগ ধরে রাখতে প্রাকৃতিক ব্রেক বা সুর পরিবর্তনের সময় রিল শেষ করুন
- শুধুমাত্র রিয়েল ভ্যালু ড্রাইভ করে এমন অংশ বাছাই করুন (ফিলার বাদ দিন)

ট্রান্সক্রিপ্ট:
{transcript_text}

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

        start_time = time.time()
        response = model.generate_content(prompt)
        duration = time.time() - start_time

        self.metrics.record_api_call(
            endpoint=f"{self.settings.api.gemini_model}/analysis",
            duration=duration,
            success=True
        )

        return response.text

    def _parse_analysis_results(self, analysis_text: str) -> list[ReelConfig]:
        """Parse Gemini analysis results into ReelConfig objects."""
        import re

        reels = []
        reel_blocks = re.split(r'##\s+REEL\s+#\d+:', analysis_text)

        for idx, block in enumerate(reel_blocks[1:], 1):  # Skip first empty split
            try:
                # Extract title
                title_match = re.search(r'"([^"]+)"', block)
                title = title_match.group(1) if title_match else f"Reel {idx}"

                # Extract timestamps
                start_match = re.search(r'\*\*Start:\*\*\s*\[?([0-9:.]+)\]?', block)
                end_match = re.search(r'\*\*End:\*\*\s*\[?([0-9:.]+)\]?', block)

                if not start_match or not end_match:
                    self.logger.warning(f"Could not parse timestamps for reel {idx}")
                    continue

                start = start_match.group(1)
                end = end_match.group(1)

                # Extract hook type
                hook_match = re.search(r'\*\*Hook Type:\*\*\s*([^\n]+)', block)
                hook_type = hook_match.group(1).strip() if hook_match else ""

                # Extract viral potential (count stars)
                viral_stars = block.count('⭐')

                reel = ReelConfig(
                    id=f"reel{idx}",
                    start=start,
                    end=end,
                    title=title,
                    hook_type=hook_type,
                    viral_potential=viral_stars
                )

                reels.append(reel)

            except Exception as e:
                self.logger.warning(f"Failed to parse reel {idx}: {str(e)}")

        return reels

    def execute(self) -> AgentResult:
        """Analyze transcript and identify reels."""
        try:
            transcript_path = self.project_config.transcript_path
            transcript_text = transcript_path.read_text(encoding='utf-8')

            self.logger.info(f"Analyzing transcript ({len(transcript_text):,} characters)...")

            # Call Gemini for analysis
            analysis_text = self._call_gemini_for_analysis(transcript_text)

            # Save analysis
            analysis_dir = self.project_config.project_root / "Analysis"
            self._ensure_directory(analysis_dir)

            analysis_file = analysis_dir / "REEL_CUT_DIRECTIONS.md"
            analysis_file.write_text(analysis_text, encoding='utf-8')

            self.logger.info(f"✓ Analysis saved to: {analysis_file}")

            # Parse results into reel configurations
            reels = self._parse_analysis_results(analysis_text)

            # Add reels to project config
            for reel in reels:
                self.project_config.add_reel(reel)

            self.project_config.save()

            self.logger.info(f"✓ Identified {len(reels)} viral reel candidates")

            return AgentResult(
                success=True,
                message=f"Analysis completed: {len(reels)} reels identified",
                artifacts={"analysis_file": analysis_file},
                metadata={"reels_found": len(reels)}
            )

        except Exception as e:
            error_msg = f"Analysis failed: {str(e)}"
            self.logger.error(error_msg)
            return AgentResult(
                success=False,
                message=error_msg,
                error=AnalysisError(error_msg)
            )

    def validate_postconditions(self, result: AgentResult) -> None:
        """Validate analysis results."""
        if not result.success:
            return

        reels_found = result.metadata.get('reels_found', 0)

        if reels_found == 0:
            raise AnalysisError("No viral reels were identified in the transcript")

        if reels_found < self.settings.analysis.min_viral_potential:
            self.logger.warning(f"Only {reels_found} reels found (expected >= {self.settings.analysis.max_reels})")

        self.logger.info(f"✓ Analysis validated: {reels_found} reels identified")
