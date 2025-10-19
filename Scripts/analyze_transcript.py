#!/usr/bin/env python3
"""
Analyze transcript and identify viral-worthy reel segments
"""

import os
import google.generativeai as genai

# Configure API
api_key = os.environ.get('GEMINI_API_KEY')
genai.configure(api_key=api_key)

# Read the transcript
with open('podcast_audio_30min_transcription.txt', 'r', encoding='utf-8') as f:
    transcript = f.read()

# Create model
model = genai.GenerativeModel('gemini-2.5-pro')

# Analyze for viral moments
prompt = f"""আপনাকে একটি বাংলা পডকাস্ট ট্রান্সক্রিপ্ট দেওয়া হচ্ছে। এই ট্রান্সক্রিপ্ট থেকে ৩টি সবচেয়ে ভাইরাল-যোগ্য রিল (Reel) সেগমেন্ট চিহ্নিত করুন।

প্রতিটি রিলের জন্য:
1. ভাইরাল হুক টাইটেল (৫-১০ শব্দ)
2. হুক টাইপ (Mind-Blowing Stat, Fear/Shock, Problem-Solution, etc.)
3. স্টার্ট টাইমস্ট্যাম্প [HH:MM:SS.mmm]
4. এন্ড টাইমস্ট্যাম্প [HH:MM:SS.mmm]
5. সময়কাল (৩০-৯০ সেকেন্ড ideally)
6. কী কোট/মূল বক্তব্য
7. ভাইরাল পটেনশিয়াল (⭐⭐⭐⭐⭐)

মনে রাখবেন:
- প্রতিটি রিল ৩০-৯০ সেকেন্ডের মধ্যে হওয়া উচিত
- শক্তিশালী হুক দিয়ে শুরু হতে হবে
- সম্পূর্ণ বক্তব্য থাকতে হবে (মাঝখানে কাটা যাবে না)
- মোবাইল ভিউয়ারদের জন্য engaging হতে হবে

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

---

## REEL #2: "[বাংলা হুক টাইটেল]"
[একই ফরম্যাট]

---

## REEL #3: "[বাংলা হুক টাইটেল]"
[একই ফরম্যাট]
"""

print("Analyzing transcript for viral moments...")
response = model.generate_content(prompt)

print("\n" + "="*80)
print("REEL CUT DIRECTIONS")
print("="*80)
print(response.text)
print("="*80)

# Save to file
with open('REEL_CUT_DIRECTIONS.md', 'w', encoding='utf-8') as f:
    f.write(response.text)

print("\n✅ Analysis saved to: REEL_CUT_DIRECTIONS.md")
