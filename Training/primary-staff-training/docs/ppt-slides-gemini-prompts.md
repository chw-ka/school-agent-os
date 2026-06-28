# PPT Slide Image Prompts — Gemini (16:9)

**Session:** STEAM 分享：M5StickS3  
**Venue:** YL Long Ping Estate Wai Chow School  
**Presenter:** Warren Chan · Carmel Holy Word Secondary School  
**When:** 22 Jun 2026, 14:00–15:30  
**Audience:** Fellow teachers (not primary students)  
**Total slides:** 25

Use with **Gemini image generation** (Imagen). Each slide **1920×1080, 16:9**.  
Batch: `python scripts/generate_ppt_slides.py`

---

## Global style (append to EVERY prompt)

```
STYLE_SUFFIX: Clean modern teacher professional development presentation slide, 16:9 aspect ratio 1920x1080, flat vector illustration, bold readable sans-serif English typography, high contrast, STEAM palette deep blue #1a3a5c teal #2dd4bf orange #f59e0b, minimal clutter, no watermarks, no realistic human faces, crisp edges, workshop deck quality for Hong Kong school teachers.
```

---

## Slide index

| # | Filename | Section |
|---|----------|---------|
| 01 | `slide-01-title.png` | Title |
| 02 | `slide-02-about-me.png` | Self intro |
| 03 | `slide-03-three-tasks.png` | Overview |
| 04 | `slide-04-three-buttons.png` | **Three buttons diagram** |
| 05 | `slide-05-sticks3-features.png` | Hardware features |
| 06 | `slide-06-grouping.png` | 20 units / 3 per group |
| 07 | `slide-07-task1-xiaozhi.png` | Task 1 intro |
| 08 | `slide-08-task1-try-list.png` | Dark mode / music / weather |
| 09 | `slide-09-recording-notice.png` | Recording disclaimer |
| 10 | `slide-10-why-powerful.png` | LLM + platform |
| 11 | `slide-11-xiaozhi-live-demo.png` | Live demo xiaozhi.me (blank) |
| 12 | `slide-12-task2-uiflow-ota.png` | M5Launcher OTA + BtnB |
| 13 | `slide-13-infinite-possibilities.png` | Watch / pencil case robot |
| 14 | `slide-14-cloud-access-code.png` | Cloud + UIFlow web |
| 15 | `slide-15-block-coding-familiar.png` | STEAM teachers know blocks |
| 16 | `slide-16-no-one-codes.png` | Industry uses AI |
| 17 | `slide-17-ai-evolution.png` | Chatbot → Vibe → Agent |
| 18 | `slide-18-vibe-coding-bridge.png` | Vibe as bridge |
| 19 | `slide-19-task3-gemini.png` | Task 3 Gemini |
| 20 | `slide-20-m5-api-trick.png` | M5 API context trick |
| 21 | `slide-21-two-buttons-voice.png` | 2 buttons vs voice |
| 22 | `slide-22-deepseek-next-time.png` | DeepSeek deferred |
| 23 | `slide-23-advanced-courses.png` | Agentic AI / Manus |
| 24 | `slide-24-summary.png` | Summary |
| 25 | `slide-25-qa-thanks.png` | Q&A |

---

## Per-slide prompts

### Slide 01 — Title

**On-slide text (English only):**  
`STEAM Sharing: M5StickS3` / `Xiaozhi · UIFlow 2 · Vibe Coding` / `YL Long Ping Estate Wai Chow School · 22 Jun 2026 · 14:00–15:30` / `Presenter: Warren Chan · Carmel Holy Word Secondary School`

**REFERENCE:** docs/assets/m5sticks3-product-reference.png  
**MODEL:** gemini-2.5-flash-image

**PROMPT:**
```
Create a 16:9 professional presentation TITLE slide. Use the attached official M5StickS3 product photo on the RIGHT side — keep the device look exactly like the reference (black stick, STICK S3 screen, blue BtnA, M5Stack branding). LEFT side typography in ENGLISH ONLY — no Chinese characters anywhere.

Text layout:
- Main title: "STEAM Sharing: M5StickS3"
- Subtitle: "Xiaozhi · UIFlow 2 · Vibe Coding"
- Footer: "YL Long Ping Estate Wai Chow School"
- Date line: "22 Jun 2026 · 14:00–15:30"
- Presenter line: "Presenter: Warren Chan · Carmel Holy Word Secondary School"

Deep blue gradient background on text side. Clean workshop deck quality.
```

---

### Slide 02 — About Me

**On-slide text (English only):**  
`About Me` / `Warren Chan` / `Carmel Holy Word Secondary School` / `Software Engineer 10+ years · Secondary teaching 9+ years` / `NGO · Startups · Mentored students at MIT, Stanford, Chicago & more`

**REFERENCE:** docs/assets/m5sticks3-product-reference.png  
**MODEL:** gemini-2.5-flash-image

**PROMPT:**
```
Create a 16:9 presentation slide titled "About Me" in ENGLISH ONLY — no Chinese characters.

Small M5StickS3 product photo accent (bottom-right), matching reference device.

Text:
- Title: "About Me"
- Name: "Warren Chan"
- School: "Carmel Holy Word Secondary School"
- Bullets (clear readable list):
  • Software Engineer — 10+ years
  • Teaching Secondary School — 9+ years
  • Work for NGO and startups
  • Mentored well-known university students — MIT, Stanford, Chicago, and more

Clean professional layout, white background, blue header. No face photo.
```

---

### Slide 03 — Three Tasks

**On-slide text:**  
`Three Tasks` / `1 Experience` / `2 Setup` / `3 Vibe Coding M5StickS3`

**PROMPT:**
```
Slide titled "Three Tasks". Three large numbered cards only: "1 Experience", "2 Setup", "3 Vibe Coding M5StickS3". Simple icons: hand/play for Experience, wrench/download for Setup, sparkle/code for Vibe Coding M5StickS3. Horizontal arrows connecting them. English only, teacher workshop style, 16:9 landscape.
```

---

### Slide 04 — Three Buttons (BLANK — add manually)

**On-slide text:**  
`Know These Three Buttons` / `[ Add device photo & button labels in PowerPoint ]`

**BLANK:** true

**PROMPT:**
```
(Skip AI generation — blank placeholder built in build_pptx.py)
```

---

### Slide 05 — StickS3 Features

**On-slide text:**  
`M5StickS3 — More Than a Toy` / `Screen · WiFi · Mic · Speaker · IMU · IR · Battery`

**REFERENCE:** docs/assets/m5sticks3-product-reference.png  
**MODEL:** gemini-2.5-flash-image

**PROMPT:**
```
Create a 16:9 slide titled "M5StickS3 — More Than a Toy". Place the attached official M5StickS3 product photo prominently in center, exactly like the reference image. Surround with English feature callouts and icons: Color Screen, ESP32-S3 WiFi, Microphone, Speaker, 6-axis IMU, IR transmitter, RTC, USB-C battery. Tagline "Full IoT computer in your palm". English only, teal and orange accents.
```

---

### Slide 06 — Grouping

**On-slide text:**  
`Hands-on Setup` / `20 devices only · M5Stack stock limited` / `Please form groups of 3 teachers`

**PROMPT:**
```
Slide with title text exactly: "Hands-on Setup" (no asterisks, no markdown, plain text). Warning badge with exact text "20 devices only · M5Stack stock limited". Large centered text exactly: "Please form groups of 3 teachers". Icon of three teacher silhouettes sharing one small device. Friendly workshop instruction slide. CRITICAL: render all text exactly as spelled above — no markdown symbols, no asterisks, no bold markers.
```

---

### Slide 07 — Task 1 Xiaozhi

**On-slide text:**  
`Task 1: Feel the Power` / `Press Power (left) → Wait → Talk` / `Xiaozhi = English tutor`

**PROMPT:**
```
Slide with title text exactly: "Task 1: Feel the Power" (no asterisks, plain text). Three numbered step icons in a row: Step 1 finger pressing power button labeled "Press Power", Step 2 clock icon labeled "Wait", Step 3 speech bubble labeled "Talk". Below the steps: text exactly "Xiaozhi = English tutor". Orange accent badge with text "5 min explore". CRITICAL: do not use placeholder words like "Icon 1" "Icon 2" "Icon 3" — draw actual icons. Render all text exactly as spelled — no markdown, no asterisks.
```

---

### Slide 08 — Things to Try

**On-slide text:**  
`Try Saying…` / `Turn on dark mode · Play a song · What's the weather? · Teach me English`

**PROMPT:**
```
Slide with title exactly "Try Saying…". Four distinct speech bubble cards arranged in a 2x2 grid. Each card has a microphone icon and ONE exact phrase — card 1: "Turn on dark mode", card 2: "Play a song", card 3: "What's the weather?", card 4: "Teach me English". CRITICAL: each speech bubble must contain only the exact English phrase listed above — no other text, no garbled words, no placeholder text. Playful but professional teacher training slide.
```

---

### Slide 09 — Recording Notice

**On-slide text:**  
`Notice` / `Conversations may be recorded for teaching quality` / `Use brief test phrases if concerned`

**PROMPT:**
```
Slide with title exactly "Notice" and a subtle recorder icon. Two lines of body text — line 1 exactly: "Conversations may be recorded for teaching quality" — line 2 exactly: "Use brief test phrases if concerned" (spell "concerned" c-o-n-c-e-r-n-e-d). Calm yellow amber advisory banner style, not alarming, professional compliance tone. CRITICAL: spell every word exactly as written above. No typos. No placeholder text.
```

---

### Slide 10 — Why So Powerful (keep — includes architecture)

**On-slide text:**  
`Why So Powerful?` / `Sensors → Xiaozhi Platform → LLM` / `Knowledge Base · MCP` / `Voice → WiFi → Cloud → Speaker`

**PROMPT:**
```
Single combined slide titled "Why So Powerful?" — do NOT duplicate a second architecture slide. Include one clear left-to-right flow: Voice → Microphone → WiFi → Xiaozhi Platform + LLM → Speaker. Also show layers: on-device sensors, Xiaozhi cloud platform, LLM brain, optional Knowledge Base and MCP tools. Technical teacher PD style, English only, white background, 16:9 landscape.
```

---

### Slide 11 — Live Demo xiaozhi.me (replaces duplicate architecture)

**On-slide text:**  
`Live Demo` / `xiaozhi.me` / `[ Browser demo — add platform screenshot manually if needed ]`

**BLANK:** true

**PROMPT:**
```
(Skip AI generation — blank placeholder for live xiaozhi.me demo in build_pptx.py)
```

---

### Slide 12 — Task 2 UIFlow OTA (BLANK — add screenshots manually)

**On-slide text:**  
`Task 2: Install UIFlow 2` / `M5Launcher → BtnB → OTA → Select UIFlow → Wait` / `[ Add screenshots manually ]`

**BLANK:** true

**PROMPT:**
```
(Skip AI generation — blank placeholder built in build_pptx.py)
```

---

### Slide 13 — Infinite Possibilities

**On-slide text:**  
`Imagine…` / `Wear it → AI watch · Pencil case → Desk robot · Endless STEAM projects`

**PROMPT:**
```
Inspirational slide titled "Imagine…". Three vignettes: StickS3 on wrist as AI watch, StickS3 in pencil case as desk robot, StickS3 with custom 3D case. Tagline "Endless STEAM projects". Creative colorful but clean vector art.
```

---

### Slide 14 — Cloud & Access Code (BLANK — add screenshots manually)

**On-slide text:**  
`Pair with UIFlow 2` / `Cloud icon → Access code → uiflow2.m5stack.com → Run Once` / `[ Add screenshots manually ]`

**BLANK:** true

**PROMPT:**
```
(Skip AI generation — blank placeholder built in build_pptx.py)
```

---

### Slide 15 — Block Coding Familiar

**On-slide text:**  
`Sound Familiar?` / `Block-based web IDE — many STEAM teachers already know this`

**PROMPT:**
```
Slide with title exactly "Sound Familiar?". Mockup of a block coding workspace in Scratch/micro:bit style — show colorful coding blocks snapping together visually. Any text labels on the blocks should be simple readable English words like "when button pressed", "set LED", "show text", "play tone" — clear real words only, no garbled or nonsense text. Subtitle below: exactly "Block-based web IDE — many STEAM teachers already know this". CRITICAL: all visible text must be real English words — absolutely no garbled, nonsense, or placeholder text anywhere on the slide.
```

---

### Slide 16 — No One Codes Anymore

**On-slide text:**  
`Honest Truth from a Software Engineer` / `Industry rarely hand-writes code anymore` / `We review AI output — don't break the codebase`

**PROMPT:**
```
Slide titled "Honest Truth from a Software Engineer". Bold quote style text "Industry rarely hand-writes code anymore" and "We review AI output — don't break the codebase". Icons of human plus AI robot pair programming. Dark blue background white text authoritative but friendly.
```

---

### Slide 17 — AI Evolution

**On-slide text:**  
`Chatbot → Vibe Coding → Agentic AI` / `Use · Create · Automate`

**PROMPT:**
```
Evolution diagram slide with three nodes arrow linked: Chatbot "Use" example Xiaozhi, Vibe Coding "Create" example Gemini game, Agentic AI "Automate" example Manus multi-step agent. Horizontal infographic strong central visual.
```

---

### Slide 18 — Vibe Coding Bridge

**On-slide text:**  
`Vibe Coding = The Bridge` / `From chatbot AI (Gemini) toward agentic AI` / `Experience before you can teach AI what to do`

**PROMPT:**
```
Slide titled "Vibe Coding = The Bridge". Bridge metaphor connecting island Chatbot to island Agentic AI with middle pillar labeled Vibe Coding. Subtitle "Experience before you can teach AI what to do". Elegant metaphor illustration.
```

---

### Slide 19 — Task 3 Gemini

**On-slide text:**  
`Task 3: Vibe Coding` / `Use Gemini in UIFlow 2 · Sample prompt on Google Classroom` / `Copy · Paste · Generate`

**PROMPT:**
```
Slide with title exactly "Task 3: Vibe Coding". Show Gemini sparkle logo and a UIFlow IDE mockup. Show Google Classroom icon with text exactly "Sample prompt posted". Three step action chips with exact labels: chip 1 "Copy", chip 2 "Paste", chip 3 "Generate". CRITICAL: spell "Google Classroom" exactly — one 'o' in Google, one 's' in Classroom (C-l-a-s-s-r-o-o-m). The three chips must say exactly "Copy", "Paste", "Generate" — not "Step IDE" or any other text. Teacher workshop hands-on slide.
```

---

### Slide 20 — M5 API Trick

**On-slide text:**  
`Pro Tip` / `Tell Gemini the M5 StickS3 API first` / `Buttons · Widgets · UIFlow 2 libraries — then ask for the game`

**PROMPT:**
```
Slide with title exactly "Pro Tip" and a lightbulb icon. Two clearly labeled boxes side by side: left box header exactly "Step 1: Give M5StickS3 API context" with example code labels "BtnA", "BtnB", "Widgets", "Label"; right box header exactly "Step 2: Then ask for your game" with a sparkle/AI icon. A crossed-out warning below: "Wrong order = bad code". Monospace code hint aesthetic. CRITICAL: both boxes must have the exact headers as written — no placeholder text like "Second box right". All text spelled correctly.
```

---

### Slide 21 — Two Buttons vs Voice

**On-slide text:**  
`Design Constraint` / `Only BtnA + BtnB for games` / `Add voice input → completely different possibilities`

**PROMPT:**
```
Slide titled "Design Constraint". Left side two buttons limited game pad icon "Only BtnA + BtnB". Right side microphone plus game "Add voice → new possibilities". Versus layout educational product design slide.
```

---

### Slide 22 — DeepSeek Next Time

**On-slide text:**  
`DeepSeek API — Next Session` / `DIY backend · Slower than Xiaozhi · Great for understanding APIs`

**PROMPT:**
```
Slide with title exactly "DeepSeek API — Next Session". Postponed calendar icon with badge "Later". Three bullet points with exact text — bullet 1: "DIY backend", bullet 2: "Slower than Xiaozhi", bullet 3: "Great for understanding APIs". Muted gray-blue color scheme. CRITICAL: spell "understanding" correctly: u-n-d-e-r-s-t-a-n-d-i-n-g. All text spelled exactly as written above. No placeholder text.
```

---

### Slide 23 — Advanced Courses

**On-slide text:**  
`Want to Go Deeper?` / `My strength: teaching Agentic AI` / `Small-group classes recommended · Learn only if you are interested`

**PROMPT:**
```
Slide with title exactly "Want to Go Deeper?". Subtitle exactly "My strength: teaching Agentic AI". Four bullet points with exact text — bullet 1: "Contact me for advanced workshops", bullet 2: "Small-group teaching recommended" (spell "recommended" r-e-c-o-m-m-e-n-d-e-d), bullet 3: "High interest required — not for everyone" (spell "everyone" correctly, NOT "not your everyone"), bullet 4: "Professional Vibe Coding & Agentic AI". Friendly invitation tone, NO Manus logo. English only, clean professional 16:9 slide. CRITICAL: spell every word exactly as written above with no typos.
```

---

### Slide 24 — Summary

**On-slide text:**  
`Takeaways` / `① Xiaozhi = ready-made AI` / `② UIFlow 2 = student creativity` / `③ Vibe Coding = how we build now`

**PROMPT:**
```
Summary slide with title exactly "Takeaways" (plain text, no asterisk, no markdown). Three numbered points with icons — point 1 exactly: "① Xiaozhi = ready-made AI" (spell "ready-made" r-e-a-d-y hyphen m-a-d-e); point 2 exactly: "② UIFlow 2 = student creativity" (spell "creativity" c-r-e-a-t-i-v-i-t-y); point 3 exactly: "③ Vibe Coding = how we build now". Clean celebratory professional closing design. CRITICAL: title is just "Takeaways" with no asterisks. Spell "ready-made" and "creativity" exactly as shown. No garbled footer text. No placeholder text anywhere.
```

---

### Slide 25 — Q&A Thanks

**On-slide text:**  
`Questions?` / `Thank you!` / `YL Long Ping Estate Wai Chow School · Warren Chan`

**PROMPT:**
```
Closing slide large "Questions?" and "Thank you!". Subtitle "STEAM Sharing: M5StickS3". Footer "YL Long Ping Estate Wai Chow School · Warren Chan · Carmel Holy Word Secondary School". Small device icon. Dark blue background white text minimal elegant end slide. English only.
```

---

## Batch generation

```bash
cp .env.example .env
# Edit .env → set GEMINI_API_KEY=your-key

pip install -r requirements.txt
python scripts/generate_ppt_slides.py
# Output: docs/ppt-output/slide-01-title.png … slide-25-qa-thanks.png
```

`.env` is gitignored — do not commit your key.

**Critical:** Regenerate **Slide 04** until three buttons are clearly labeled — it is the key hardware diagram.
