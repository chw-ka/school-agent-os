#!/usr/bin/env bash
# Regenerate the 10 AI slides that had typos/garbled/placeholder text.
# Run this from the project root on your local Mac after confirming GEMINI_API_KEY is set in .env
#
# Usage:
#   cd /Users/warren_chan/Projects/chw-primary-tasting-steam-course
#   bash scripts/regen-bad-slides.sh

set -e
cd "$(dirname "$0")/.."

echo "=== Regenerating problematic slides ==="
echo "Slide 6  — Hands-on Setup (asterisks in text)"
python scripts/generate_ppt_slides.py --slide 6
sleep 3

echo "Slide 7  — Task 1: Feel the Power (Icon 1/2/3 placeholders + asterisks)"
python scripts/generate_ppt_slides.py --slide 7
sleep 3

echo "Slide 8  — Try Saying… (garbled speech bubble text)"
python scripts/generate_ppt_slides.py --slide 8
sleep 3

echo "Slide 9  — Notice (typo: concernd)"
python scripts/generate_ppt_slides.py --slide 9
sleep 3

echo "Slide 15 — Sound Familiar? (garbled block code labels)"
python scripts/generate_ppt_slides.py --slide 15
sleep 3

echo "Slide 19 — Task 3: Vibe Coding (Classsroom typo, Step IDE buttons)"
python scripts/generate_ppt_slides.py --slide 19
sleep 3

echo "Slide 20 — Pro Tip (Second box right placeholder)"
python scripts/generate_ppt_slides.py --slide 20
sleep 3

echo "Slide 22 — DeepSeek API (typo: undertanding)"
python scripts/generate_ppt_slides.py --slide 22
sleep 3

echo "Slide 23 — Want to Go Deeper? (recommnded, not your everyone)"
python scripts/generate_ppt_slides.py --slide 23
sleep 3

echo "Slide 24 — Takeaways (asterisk, ready-maed, creativvits, garbled footer)"
python scripts/generate_ppt_slides.py --slide 24
sleep 3

echo ""
echo "=== Rebuilding PPTX ==="
python scripts/build_pptx.py

echo ""
echo "=== Adding QR Code feedback slide ==="
python scripts/add_feedback_qr_to_pptx.py

echo ""
echo "✅ Done! Check docs/STEAM-Sharing-M5StickS3.pptx"
