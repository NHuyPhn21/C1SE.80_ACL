#!/usr/bin/env python3
"""Test script: translate 22 text regions in 1 Gemini request."""

import sys
from ai_core.translator import translate_batch_dict

# 22 example text regions
sample_data = {
    str(i): f"ja_text_{i}" for i in range(1, 23)
}
sample_data["1"] = "Ohayou gozaimasu"
sample_data["2"] = "Arigatou gozaimasu"
sample_data["3"] = "Sumimasen"

print("=" * 80)
print("TEST: Translate 22 text regions in 1 Gemini Request")
print("=" * 80)
print(f"Input: {len(sample_data)} regions")

result = translate_batch_dict(sample_data, api_key=None, project_id=None)

print("\n" + "=" * 80)
print(f"Result: {len(result)} regions translated")
print("=" * 80)

if result:
    if len(result) == len(sample_data):
        print("\n[OK] SUCCESS: All 22 sentences translated!")
        sys.exit(0)
    else:
        missing = set(sample_data.keys()) - set(result.keys())
        print(f"\n[WARN] PARTIAL: Missing {len(missing)} sentences: {sorted(missing, key=int)}")
        sys.exit(1)
else:
    print("\n[ERROR] FAILED: No sentences translated")
    sys.exit(1)
