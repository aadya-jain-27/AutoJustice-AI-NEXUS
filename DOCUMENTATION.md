# AutoJustice AI NEXUS — Complete Project Documentation

**Version 2.0.0**  
**Stack:** Python 3.11+ · FastAPI · SQLAlchemy · Google Gemini 1.5 · Tesseract OCR · scikit-learn · ReportLab  
**Compliance:** BNS 2023 · Indian Evidence Act §65B · DPDP Act 2023

---

## Table of Contents

1. [What This Project Is](#1-what-this-project-is)
2. [Why It Exists — The Problem It Solves](#2-why-it-exists)
3. [System Architecture](#3-system-architecture)
4. [Technology Stack](#4-technology-stack)
5. [Directory Structure](#5-directory-structure)
6. [Installation and Running](#6-installation-and-running)
7. [Environment Variables Reference](#7-environment-variables-reference)
8. [The Full Processing Pipeline](#8-the-full-processing-pipeline)
9. [OCR Service — Text Extraction from Evidence](#9-ocr-service)
10. [Image Forensics — Tamper Detection](#10-image-forensics)
11. [Fake Report Detection — 7-Layer Analysis](#11-fake-report-detection)
12. [AI Triage Service — Risk and Crime Classification](#12-ai-triage-service)
13. [Machine Learning Models](#13-machine-learning-models)
14. [Complaint Report (CR) PDF Generation](#14-complaint-report-generation)
15. [Reporter Trust Scoring](#15-reporter-trust-scoring)
16. [OTP Phone Verification](#16-otp-phone-verification)
17. [DigiLocker Identity Verification](#17-digilocker-identity-verification)
18. [Rate Limiting and Abuse Prevention](#18-rate-limiting-and-abuse-prevention)
19. [Authentication — Officer JWT System](#19-authentication)
20. [Database Schema](#20-database-schema)
21. [API Endpoints Reference](#21-api-endpoints-reference)
22. [Frontend Pages](#22-frontend-pages)
23. [Security and Compliance](#23-security-and-compliance)
24. [Deployment](#24-deployment)
25. [Offline and Zero-Data-Leaves Mode](#25-offline-mode)
26. [Business Model](#26-business-model)
27. [FAQ — Common Technical Questions](#27-faq)

---

## 1. What This Project Is

AutoJustice AI NEXUS is a full-stack cybercrime complaint management platform built for police stations and law enforcement agencies. It takes a report submitted by a citizen — along with any evidence files they upload — and automatically does everything that would normally take a human officer hours: extracts text from screenshots, checks whether the uploaded images have been tampered with or are AI-generated, scores how likely the complaint is to be genuine, classifies the crime type, assesses the risk level, maps the applicable sections of the Bharatiya Nyaya Sanhita (BNS) 2023, and generates a properly formatted Complaint Report PDF, all within a few seconds of submission.

The police officer on the other side opens a dashboard, sees a prioritised list of cases (HIGH → MEDIUM → LOW), and clicks into any case to see the full AI analysis, forensic results, OCR-extracted evidence text, and the generated legal document — ready to take action.

At its core the system has three distinct "user types":
- **Citizens** — submit complaints through a clean public portal, optionally verify their identity via DigiLocker and Aadhaar, track their case status afterward.
- **Police Officers** — log in to a protected dashboard, review AI-triaged cases, add notes, assign cases, download Complaint Report PDFs.
- **System / AI** — the automated pipeline that runs end-to-end the moment a report comes in.

---

## 2. Why It Exists

Indian cybercrime units receive thousands of complaints per month. The current process involves a citizen walking in, filling a paper form, an officer manually reading it, deciding what crime it is, writing an FIR or rejecting it — a process that is slow, inconsistent, and completely manual. Fake reports waste significant police time and resources.

AutoJustice NEXUS was built to solve four specific problems:

**Problem 1 — Volume.** Officers cannot keep up with digital complaint volume. The system auto-triages so officers only touch cases that need human judgment.

**Problem 2 — Fake reports.** People file false complaints for personal vendettas, to harass others, to create paper trails for civil disputes. A 7-layer detection engine identifies these with an authenticity score, flags them for review or rejection, and even auto-escalates them to HIGH risk under BNS §211 (filing a false complaint is itself a criminal offence).

**Problem 3 — Evidence integrity.** Digital evidence submitted to police stations is routinely tampered with before, during, or after submission. The system SHA-256 hashes every uploaded file the moment it arrives, performs Error Level Analysis on images, checks EXIF metadata, and now uses Gemini Vision to detect AI-generated images that are being passed off as real evidence.

**Problem 4 — Inconsistency.** Two different officers will classify the same complaint differently. The AI applies consistent criteria every time.

---

## 3. System Architecture

```
                    ┌─────────────────────────────────┐
                    │         CITIZEN BROWSER          │
                    │  /  (portal)  /track  /login     │
                    └──────────────┬──────────────────┘
                                   │ HTTP / HTTPS
                    ┌──────────────▼──────────────────┐
                    │       nginx (reverse proxy)      │
                    │  Rate limiting, SSL termination  │
                    └──────────────┬──────────────────┘
                                   │
                    ┌──────────────▼──────────────────┐
                    │    FastAPI Application (uvicorn) │
                    │                                  │
                    │  ┌────────────┐ ┌─────────────┐ │
                    │  │  Routers   │ │  Middleware  │ │
                    │  │ /reports   │ │ RateLimiter  │ │
                    │  │ /auth      │ │ CORS         │ │
                    │  │ /dashboard │ │              │ │
                    │  │ /cases     │ └─────────────┘ │
                    │  │ /digilocker│                  │
                    │  └─────┬──────┘                  │
                    │        │                          │
                    │  ┌─────▼──────────────────────┐  │
                    │  │     AI Processing Pipeline  │  │
                    │  │  OCR → Forensics → Fake     │  │
                    │  │  Detection → AI Triage →    │  │
                    │  │  CR Generation              │  │
                    │  └─────┬──────────────────────┘  │
                    └────────┼────────────────────────┘
                             │
               ┌─────────────┼──────────────────────┐
               │             │                        │
    ┌──────────▼──┐  ┌───────▼─────┐  ┌─────────────▼──┐
    │  SQLite DB   │  │  Google     │  │  scikit-learn   │
    │ (PostgreSQL  │  │  Gemini API │  │  ML Models      │
    │  in prod)    │  │  1.5 Pro/   │  │  (local .pkl)   │
    │              │  │  Flash      │  │                 │
    └──────────────┘  └─────────────┘  └────────────────┘
```

Everything runs in a single Python process in development. For production, nginx sits in front and Docker Compose manages the containers. The only external API dependency is Google Gemini — everything else (OCR, ML inference, PDF generation, database) runs locally.

---

## 4. Technology Stack

| Component | Technology | Why This Choice |
|-----------|-----------|-----------------|
| Web framework | FastAPI 0.110+ | Async-first, automatic OpenAPI docs, Pydantic validation built in |
| Database ORM | SQLAlchemy 2.x | Same code works against SQLite and PostgreSQL without changes |
| Database (dev) | SQLite | Zero setup, single file, perfect for demos and prototypes |
| Database (prod) | PostgreSQL 16 | Connection pooling, concurrent writes, proper indexing |
| AI/LLM | Google Gemini 1.5 Pro | Best-in-class reasoning for adversarial fake detection analysis |
| Vision AI | Google Gemini 1.5 Flash | Fast multimodal analysis for OCR fallback and image AI detection |
| OCR | Tesseract 5 + pytesseract | Local, free, no data leaves the system |
| ML | scikit-learn (RandomForest, GradientBoosting, LinearSVC + TF-IDF) | Runs entirely offline, fast inference |
| PDF generation | ReportLab | Professional A4 PDFs with proper legal formatting |
| Image processing | Pillow + piexif | ELA analysis, EXIF metadata extraction, image preprocessing |
| Authentication | python-jose (JWT) + bcrypt | Industry standard, bcrypt 3.x for passlib compatibility |
| Config | pydantic-settings | .env file loading with type validation |
| Server | uvicorn | ASGI server for FastAPI |
| Reverse proxy | nginx 1.25 | SSL termination, rate limiting headers, static file caching |
| Containerisation | Docker + Docker Compose | Single command deployment |

---

## 5. Directory Structure

```
AutoJustice-AI (Nexus)/
├── backend/
│   ├── main.py                  ← FastAPI app entry point, lifespan, routers
│   ├── config.py                ← All settings via pydantic-settings + .env
│   ├── database.py              ← SQLAlchemy engine, session factory
│   ├── requirements.txt
│   │
│   ├── routers/
│   │   ├── auth.py              ← JWT login, officer CRUD
│   │   ├── reports.py           ← Full pipeline: submit, list, track, download
│   │   ├── dashboard.py         ← Dashboard stats, case assignment, notes
│   │   ├── cases.py             ← Case management (status updates, closure)
│   │   └── digilocker.py        ← DigiLocker OAuth 2.0 endpoints
│   │
│   ├── models/
│   │   ├── db_models.py         ← SQLAlchemy ORM models (all tables)
│   │   └── schemas.py           ← Pydantic request/response schemas
│   │
│   ├── services/
│   │   ├── ocr_service.py       ← Tesseract + Gemini Vision OCR, EXIF extraction
│   │   ├── image_forensics_service.py  ← 6-layer image tamper detection
│   │   ├── fake_detection_service.py   ← 7-layer fake report analysis
│   │   ├── ai_triage_service.py        ← Gemini risk/crime classification
│   │   ├── fir_generator.py     ← ReportLab PDF generation
│   │   ├── hash_service.py      ← SHA-256 hashing for chain of custody
│   │   ├── reporter_trust_service.py   ← Reporter reputation scoring
│   │   └── digilocker_service.py       ← DigiLocker OAuth + PKCE
│   │
│   ├── ml/
│   │   ├── train.py             ← Trains all 3 models, saves .pkl files
│   │   ├── predictor.py         ← Loads .pkl models, runs inference
│   │   ├── features.py          ← 18-feature extraction from text
│   │   ├── dataset.py           ← Synthetic training data generation
│   │   └── models/
│   │       ├── fake_detector.pkl
│   │       ├── crime_classifier.pkl
│   │       ├── risk_classifier.pkl
│   │       └── training_metadata.json
│   │
│   ├── middleware/
│   │   └── rate_limiter.py      ← IP-based sliding window rate limiting
│   │
│   ├── templates/
│   │   ├── citizen_portal.html  ← Public complaint submission form
│   │   ├── police_dashboard.html← Officer command view
│   │   ├── case_tracking.html   ← Citizen case status tracker
│   │   └── login.html           ← Officer login page
│   │
│   ├── static/
│   │   ├── js/
│   │   │   ├── citizen.js       ← Portal form, DigiLocker, OTP, file upload
│   │   │   └── dashboard.js     ← Dashboard data fetching and rendering
│   │   └── css/
│   │
│   ├── uploads/                 ← Evidence file storage (UUID-named)
│   └── firs/                    ← Generated CR PDFs
│
├── nginx/
│   └── nginx.conf
├── Dockerfile
├── docker-compose.yml
├── start_demo.sh                ← One-command demo startup with seed data
├── start.sh                     ← Production startup
├── demo_seed.py                 ← Seeds 15 sample cases for demo
└── .env.example
```

---

## 6. Installation and Running

### Prerequisites

- Python 3.11, 3.12, or 3.13
- Tesseract OCR (optional but strongly recommended): `brew install tesseract` on macOS, `apt install tesseract-ocr` on Ubuntu
- For Hindi language support: `brew install tesseract-lang` or `apt install tesseract-ocr-hin`
- A Google Gemini API key from [aistudio.google.com](https://aistudio.google.com) (optional — system works without it using ML fallbacks)

### Quick Start — Demo Mode

```bash
bash start_demo.sh
```

This script does everything automatically:
1. Detects the right Python version (3.11–3.13)
2. Creates a `.venv` virtual environment
3. Installs all dependencies from `requirements.txt`
4. Pins bcrypt to 3.2.2 (prevents passlib compatibility issues)
5. Trains all three ML models if they don't exist yet (takes about 30 seconds)
6. Copies `.env.example` to `backend/.env` if no `.env` exists
7. Drops and recreates the SQLite database for a clean demo
8. Seeds 15 pre-built cases across all risk levels
9. Starts uvicorn on port 8000

After it starts:
- Citizen Portal: http://localhost:8000
- Case Tracking: http://localhost:8000/track
- Officer Login: http://localhost:8000/login
- Police Dashboard: http://localhost:8000/dashboard
- API Docs: http://localhost:8000/api/docs
- Default credentials: `admin` / `AutoJustice@2024!`

### Manual Setup

```bash
# Clone and enter the project
cd "AutoJustice-AI (Nexus)"

# Create virtual environment
python3.12 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r backend/requirements.txt
pip install "bcrypt==3.2.2"  # pin bcrypt version

# Train ML models
cd backend/ml
python train.py
cd ../..

# Configure environment
cp .env.example backend/.env
# Edit backend/.env and add your GEMINI_API_KEY

# Start the server
cd backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Training the ML Models

The ML models are trained on synthetic but realistic data generated in `ml/dataset.py`. You only need to train once — the `.pkl` files persist. If you delete them or need to retrain:

```bash
cd backend/ml
python train.py
```

Training takes roughly 30 seconds on a modern laptop and produces three model files plus a `training_metadata.json` with accuracy metrics.

---

## 7. Environment Variables Reference

All settings live in `backend/.env` and are loaded by `config.py` using pydantic-settings. Unknown variables are silently ignored (`extra = "ignore"`).

```env
# ── Core ──────────────────────────────────────────────
APP_NAME="AutoJustice AI NEXUS"
DEBUG=false
SECRET_KEY=your-secret-key-here-use-openssl-rand-hex-32

# ── AI Services ──────────────────────────────────────
GEMINI_API_KEY=your-gemini-api-key
GEMINI_MODEL=gemini-1.5-pro
TESSERACT_PATH=tesseract

# ── Database ─────────────────────────────────────────
DATABASE_URL=sqlite:///./autojustice.db
# For PostgreSQL:
# DATABASE_URL=postgresql://user:password@localhost:5432/autojustice

# ── Authentication ────────────────────────────────────
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=480
DEFAULT_ADMIN_USERNAME=admin
DEFAULT_ADMIN_PASSWORD=AutoJustice@2024!   # CHANGE IN PRODUCTION

# ── File Storage ─────────────────────────────────────
UPLOAD_DIR=uploads
FIR_OUTPUT_DIR=firs
MAX_UPLOAD_SIZE_MB=25

# ── Detection Thresholds ──────────────────────────────
HIGH_RISK_THRESHOLD=0.70
MEDIUM_RISK_THRESHOLD=0.40
FAKE_REPORT_THRESHOLD=0.45     # authenticity below this = flagged
ELA_TAMPER_THRESHOLD=0.55      # image tamper score above this = flagged
MAX_GPS_DISTANCE_KM=500.0

# ── Rate Limiting ─────────────────────────────────────
RATE_LIMIT_SUBMISSIONS_PER_HOUR=5
RATE_LIMIT_WINDOW_SECONDS=3600
RATE_LIMIT_ENABLED=true

# ── Reporter Trust ────────────────────────────────────
TRUST_SCORE_NEW_REPORTER=0.70
TRUST_SCORE_MIN_REPORTS_FOR_HISTORY=3

# ── Station Identity (appears on Complaint Reports) ──
STATION_NAME=Cyber Crime Police Station
STATION_ADDRESS=Commissioner Office, Cyber Cell
STATION_CODE=CC-001
STATION_STATE=Maharashtra
STATION_DISTRICT=Mumbai City

# ── DigiLocker (leave blank to run in demo mode) ──────
DIGILOCKER_CLIENT_ID=
DIGILOCKER_CLIENT_SECRET=
DIGILOCKER_REDIRECT_URI=http://localhost:8000/api/digilocker/callback
DIGILOCKER_USE_SANDBOX=true

# ── SMTP (for OTP / notifications, optional) ─────────
SMTP_ENABLED=false
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=
SMTP_PASSWORD=
SMTP_FROM_EMAIL=noreply@autojustice.gov.in
```

---

## 8. The Full Processing Pipeline

When a citizen submits a report, the following steps execute in sequence inside `POST /api/reports/submit`:

```
Step 0 — DigiLocker check
         If the form includes a digilocker_session_token, verify it.
         Verified identity adds +0.15 to trust score.

Step 1 — Input validation
         Description must be 20–5,000 characters.
         Returns HTTP 400 if not met.

Step 2 — Reporter trust lookup
         Look up existing reporter profile by phone or email.
         If blocked: return HTTP 403 immediately.
         If frequency abuse detected: flag for later penalty.

Step 3 — Create initial DB record
         Insert a Report row with status="PROCESSING".
         Flush to DB to get the report ID.

Step 4 — Process each uploaded file
         For each file:
           a. Validate extension (jpg/jpeg/png/gif/bmp/tiff/pdf/txt)
           b. Check file size (max 25MB)
           c. Save to uploads/ with a UUID filename
           d. Compute SHA-256 hash
           e. Run OCR to extract text
           f. Extract EXIF metadata (for images)
         Concatenate all OCR text into combined_ocr.

Step 5 — Image forensics
         For each image file:
           Run 6-layer forensic analysis.
           Store tamper_score, is_tampered, tamper_flags, gps coordinates.
         Track maximum tamper score across all images.

Step 6 — Content hash
         SHA-256 of (description + ocr_text + complainant_name).
         Used for duplicate detection in fake detection Layer 5.

Step 7 — Fake detection
         Run 7-layer analysis → get authenticity_score, flags, recommendation.
         Apply reporter trust modifier.
         If tamper_score >= threshold: cap authenticity at 0.50.
         If frequency abuse: cap authenticity at 0.40.
         Final: is_flagged_fake if score < 0.45.

Step 8 — AI triage
         Send description + OCR to Gemini.
         Returns: risk_level, risk_score, crime_category, bns_sections,
                  entities (names/phones/amounts), ai_summary.

Step 8b — Fake escalation
          If fake AND recommendation=REJECT:
            Override risk_level to HIGH, risk_score to ≥0.80.
            Set crime_subcategory to "False Complaint Filing".
            Set BNS sections to §211, §218, IT Act §66D.

Step 9 — Update reporter trust
         Record submission outcome.
         Recompute trust score from full history.
         Auto-block if ≥5 fake reports and >60% fake rate.

Step 10 — Auto-generate CR
          If risk is HIGH or MEDIUM and not REJECT:
            Generate PDF using ReportLab.
            Hash the PDF for integrity verification.
            Set status = "COMPLAINT_REGISTERED".
          Otherwise: status = "TRIAGED".

Step 11 — Audit log
          Record every field of the analysis result in AuditLog.
          Commit everything to DB.
          Return ReportResponse to the citizen.
```

The entire pipeline typically completes in 2–5 seconds without Gemini, and 5–10 seconds with Gemini API calls.

---

## 9. OCR Service

**File:** `backend/services/ocr_service.py`

The OCR service extracts text from uploaded evidence files (screenshots of UPI transactions, chat screenshots, email screenshots, bank statements, PDFs). This text is critical because it gives the fake detection and AI triage systems actual numbers, names, and amounts to verify against what the complainant wrote in their description.

### Strategy

Three-layer approach:

**Layer 1 — Image Preprocessing**
Before Tesseract sees any image, it goes through preprocessing:
- If the image is smaller than 1000×1000 pixels, it gets upscaled 2× using LANCZOS resampling. Small images (phone screenshots at low DPI) confuse Tesseract into giving very low confidence scores.
- `ImageOps.autocontrast()` normalises brightness. A screenshot with a light grey background on a bright screen will often have text that's dark grey on very light grey — low contrast kills OCR accuracy.
- A sharpening filter (`ImageFilter.SHARPEN`) runs last to make character edges crisp.

**Layer 2 — Multi-PSM Tesseract**
Three different Page Segmentation Modes run on the same image:
- PSM 3 (Fully automatic page segmentation) — best for structured documents, bank statements
- PSM 6 (Assume a single uniform block of text) — best for chat screenshots, message panels
- PSM 11 (Sparse text) — best for screenshots with floating elements like UPI confirmation dialogs

The winner is whichever mode returned the most words. Confidence threshold is set to 15 (deliberately low) because Tesseract tends to give mid-range confidence to clearly readable text on screenshots.

**Layer 3 — Gemini Vision Fallback**
If Tesseract returns empty text (or Tesseract isn't installed), the image is base64-encoded and sent to `gemini-1.5-flash` with the prompt: "Extract all text from this image. Return only the raw text." If the Gemini response looks like real text and not an error message, it's returned at 0.75 confidence.

### Language Detection
At startup the service calls `pytesseract.get_languages()` and returns `"eng+hin"` if the Hindi language pack is installed, or `"eng"` if not. This prevents crashes when Tesseract is installed without the Hindi pack.

### EXIF Extraction
For images, the service also extracts EXIF metadata: camera make/model, capture datetime, GPS coordinates (converted from DMS to decimal degrees), software used. Missing or stripped EXIF is itself a forensic signal.

---

## 10. Image Forensics

**File:** `backend/services/image_forensics_service.py`

Every uploaded image goes through six forensic layers. The result is a `tamper_score` (0.0 = clean, 1.0 = definitely tampered or synthetic), a boolean `is_tampered`, a list of specific `flags`, and GPS coordinates if present.

### Layer 1 — Error Level Analysis (ELA)

ELA is the most established technique for detecting JPEG manipulation. The idea: save the image as JPEG at a known quality level (90%), then compute the absolute difference between the resaved version and the original. Areas that were previously compressed (original image areas) will show minimal error. Areas that were added later (pasted objects, text overlays, cloned regions) were compressed at a different quality level and show high error.

The system extracts these signals from the ELA difference image:
- Mean error level relative to image size
- Standard deviation of error (high variance = inconsistent compression history = edited)
- Percentage of high-error pixels (>200 across all channels)
- Edge-region error ratio (text/object boundaries are the most visible edit artifacts)

If multiple thresholds are exceeded together, the score increments (0.25–0.45 range).

### Layer 2 — Metadata Analysis

Looks at EXIF data for red flags:
- **Missing EXIF entirely** — a screenshot won't have EXIF, but a claimed "photo from the crime scene" without EXIF is suspicious (+0.20)
- **Software tag** — if Photoshop, GIMP, Lightroom, or Adobe product names appear in EXIF, the image was edited (+0.30)
- **GPS coordinate implausibility** — if the GPS coordinates are more than 500km from India's geographic center, it's suspicious for a domestic complaint (+0.15)
- **Timestamp mismatch** — if EXIF creation date is after the claimed incident date

### Layer 3 — AI Generation Detection

This is the most novel layer, specifically designed after testing found that Midjourney-generated images were scoring 0% tamper. Real cameras output JPEG or HEIC. AI image generators (Midjourney, Stable Diffusion, DALL-E) default to PNG, and often produce perfectly photographic-looking content.

The signals:
- **PNG format + photographic content** — computed as `colour_richness = unique_colours / (width × height)`. A real screenshot has flat UI colours; a photographic PNG has very high colour diversity. If `colour_richness > 0.55` and the image is large and not a standard screen resolution, score += 0.80.
- **Dimension divisibility by 64** — AI generators produce images with dimensions divisible by 64 (512, 768, 1024, etc.) because of how diffusion model latent spaces work. This alone isn't conclusive, but if the PNG photographic content signal already fired, it adds +0.15.
- **No EXIF in large PNG** — real screenshots lack EXIF, but real photos don't get saved as PNG.

After these signals run, an override applies: if the peak AI evidence score is ≥ 0.60, the composite tamper score is floored at `peak_ai_evidence × 0.85`. This prevents all the other clean signals from diluting a strong AI-generation finding.

### Layer 4 — Noise Analysis

Applies high-frequency noise extraction: subtract a Gaussian-blurred version of the image from itself, analyse the residual. Authentic photographs have consistent sensor noise texture. Synthetically generated images have anomalously low or unnaturally patterned noise. Spliced images show noise discontinuities at paste boundaries.

### Layer 5 — Screenshot Detection

Classifies uploaded images as screenshots vs photographs based on:
- Dominant colour clustering (screenshots have large flat-colour regions)
- Aspect ratio matching common screen resolutions
- Presence of UI elements (uniform horizontal bands)

Screenshots are valid evidence (a screenshot of a UPI fraud message is exactly what you want), so this layer mainly informs the other layers rather than penalising by itself.

### Layer 6 — Gemini Vision Analysis

If the Gemini API is configured, each image is sent to `gemini-1.5-flash` with a structured prompt asking it to determine whether the image is AI-generated or synthetically created, return a confidence score, and list specific reasons. The response is parsed as JSON:

```json
{"ai_generated": true, "confidence": 0.92, "reasons": ["No natural film grain", "Lighting inconsistencies", "Artificially smooth skin texture"]}
```

Gemini's confidence maps to a forensic score (0.92 confidence → 0.92 score). If Gemini's score is ≥ 0.70, the tamper score gets floored at 0.75 regardless of what other layers found.

### Final Score

Weighted combination:
- ELA: 20%
- Metadata: 18%
- AI Generation Detection: 22%
- Noise Analysis: 10%
- Screenshot: 5%
- Gemini Vision: 25%

`is_tampered = tamper_score >= 0.55`

---

## 11. Fake Report Detection

**File:** `backend/services/fake_detection_service.py`

This is the most complex service in the system. It runs seven independent analysis layers and combines them into a single `authenticity_score` (0.0 = definitely fake, 1.0 = definitely genuine) along with a `recommendation` (GENUINE / REVIEW / REJECT).

### Layer 1 — Keyword Density Analysis

Checks whether the description contains the right *combination* of specific information. A genuine cybercrime report typically has:
- A financial amount (Rs. 45,000 / ₹45000 / 45,000 rs / 45000 rupees)
- A platform name (HDFC Bank / PhonePe / GPay / Paytm / Instagram)
- A victim phone number (10-digit Indian mobile)
- A date
- A proper name (First Last format)

The amount regex is comprehensive enough to catch every Indian currency notation format:
```
Rs. 45,000 | Rs 45000 | INR 45,000 | ₹45,000 | 45,000 rs | 45000 rupees | 45000/-
```

Genuine reports almost always have at least 3–4 of these. Generic template-copied fake reports often have the keywords but not the specific values.

Reports with ≥4 of these signals get an authenticity ceiling raised to 0.80. Reports with 0–1 get a lower ceiling. This is called the `specificity_score` and ranges 0.0–0.80.

### Layer 2 — Gemini Adversarial Probe (8 Dimensions)

This is the most powerful layer (20% of the final weighted score). The entire complaint is sent to Gemini 1.5 Pro with a deliberately adversarial system prompt that tells Gemini to *assume the report may be fake* and score it across eight dimensions:

1. **narrative_coherence** (15%) — Does the story make internal sense? Are cause-and-effect relationships plausible? Fake reports often have logical gaps (money disappears without a clear mechanism, events jump nonlinearly).

2. **specificity** (12%) — Genuine victims can recall exact times, transaction IDs, exact amounts, what they were doing. Fabricated reports tend to be vague or use round numbers.

3. **trigger_stuffing** (12%) — Are high-severity keywords (bomb, hack, kill, blackmail) present in quantities or combinations that seem designed to game a keyword filter rather than describing a real event? A real blackmail victim describes their situation; a fake one lists "hacking blackmail extortion nude photos" as a checklist.

4. **evidence_match** (13%) — Does what the complainant says they can prove match what they actually uploaded? "I have the screenshot of the transaction" paired with an uploaded photo of a cat is a mismatch.

5. **entity_consistency** (10%) — Are the named entities internally consistent? If they name HDFC Bank as the fraud account but the UPI ID they provide ends in @paytm, that's inconsistent.

6. **template_pattern** (10%) — Does the report read like it was adapted from a copy-paste template or a sample FIR format found online?

7. **plausibility** (8%) — Is the described crime technically and contextually plausible? A complaint that "hacker drained my bank account by calling me" with no OTP sharing is technically impossible.

8. **adversarial_probe** (20% — highest weight) — Gemini is specifically asked: "If you had to construct this complaint as a fabrication, would it read exactly like this? What would a real victim phrase differently?" This dimension specifically catches well-written fakes that pass all keyword checks but don't read like someone recalling a real experience.

All eight scores are between 0.0–1.0. They're combined using the weights above to produce a single Gemini authenticity score.

### Layer 3 — Evidence Mismatch Detection

Checks whether the complainant's description is consistent with what they uploaded (via OCR results).

The key rule: **only penalise if the complainant explicitly claims to have evidence AND the OCR is empty.**

- If someone says "I have attached the screenshot of the UPI transaction" (financial claim + screenshot claim) but the OCR extracted nothing from the uploaded image — that's suspicious (-0.30).
- If someone uploaded an image but said nothing about evidence in their text, and OCR found nothing — that's fine. They uploaded a visual (accident photo, injury photo) that isn't text-based. No penalty.
- If someone uploaded a screenshot but only said "I was hacked" (screenshot claim without financial claim), lighter penalty (-0.15).

This rule was specifically designed after testing found that genuine victims uploading real photos (car crash images, injury documentation) were being falsely penalised because OCR found no text in a legitimate visual evidence file.

### Layer 4 — Entity Cross-Check

Validates the structural validity of numeric entities in the report:

- **Phone number format** — Indian mobile numbers must be 10 digits starting with 6, 7, 8, or 9. A complaint containing "9876543" (7 digits) or "1234567890" (starts with 1) signals fabrication.
- **UPI ID format** — Must match `something@bankname`. Common valid suffixes: @oksbi, @okaxis, @okicici, @ybl, @paytm, @upi, @axl. A UPI ID like "fraudpay@abc123" is structurally invalid and gets a penalty.
- **Amount mismatch** — If the complainant describes "I lost Rs. 50,000" in the text but the OCR-extracted transaction screenshot shows "Paid: ₹5,000", that discrepancy is scored.

The combined L4 penalty is subtracted from the final score after L3.

### Layer 5 — Duplicate Hash Detection

Every report generates a SHA-256 hash of (description + OCR text + complainant name). If the same hash exists in the database, it means someone submitted an identical report before. Duplicate submissions get a penalty of -0.40 applied to authenticity.

This catches people who submit the same fake report multiple times across different case numbers, or who copy a template from a previous case.

### Layer 6 — (Reserved / Pattern Extension)

Currently reserved for future n-gram based language model detection. Will be populated in the next version with a lightweight local language model that evaluates whether the writing style matches "someone recalling an experience" vs "someone constructing a narrative."

### Layer 7 — ML Model Score

The trained RandomForestClassifier (18 features, 200 trees) provides a third independent opinion. It's trained on synthetic data that includes both obvious fakes and subtle edge cases. It returns: 0=fake, 1=genuine, 2=review, with probabilities. The probability of label "1" becomes an ML authenticity component.

### Combining All Layers

The final authenticity score is computed as:
```
base = specificity_ceiling (from L1)
       × gemini_weighted_score (from L2)
adjusted for L3 penalty
adjusted for L4 penalty
bounded by ML score (L7) — if ML says fake, floor is lowered
```

Then the reporter trust modifier applies (±8–20% adjustment based on history).

### Thresholds

- **≥ 0.65** → GENUINE
- **0.45–0.65** → REVIEW (officer should look)
- **< 0.45** → REJECT (likely fake)
- **< 0.25** → REJECT (definitely fake, override)

---

## 12. AI Triage Service

**File:** `backend/services/ai_triage_service.py`

Classifies the report's risk level, crime category, extracts named entities, maps BNS sections, and generates a 2–3 sentence summary.

### Primary Path — Gemini 1.5 Pro

When `GEMINI_API_KEY` is configured, the service sends description + OCR text to Gemini with a structured prompt that instructs it to return a JSON object with exact fields. The prompt is highly specific about what each field should contain:

- `risk_level`: HIGH / MEDIUM / LOW
- `risk_score`: float 0.0–1.0
- `crime_category`: one of 9 canonical categories
- `crime_subcategory`: specific sub-type (UPI Fraud, Sextortion, etc.)
- `bns_sections`: list of applicable BNS 2023 sections with descriptions
- `entities`: dict with person_names, phone_numbers, amounts, accounts, urls
- `ai_summary`: 2–3 sentence professional summary

The response is parsed as JSON. If parsing fails (Gemini sometimes returns markdown-wrapped JSON), the service strips ` ```json ``` ` markers and tries again.

### Fallback Path — Rule-Based Engine

If Gemini is unavailable (no API key, quota exceeded, network error), the service falls back to a keyword-scoring approach that still produces a complete triage result:

- Counts occurrences of HIGH/MEDIUM/LOW severity indicator words
- Detects Indian currency formats using the same `_RE_AMOUNT` regex
- Assigns crime categories based on keyword clusters (financial_keywords → "Financial Crime", harassment_keywords → "Online Harassment", etc.)
- Maps BNS sections via a static lookup table (IT Act §66C for identity theft, BNS §111 for extortion, etc.)
- Risk score formula: `min(0.40 + medium_score × 0.03, 0.75)` to prevent the fallback from ever outputting HIGH risk

The rule-based fallback is good enough for demo purposes and testing. In production, Gemini should always be configured.

### ML Risk Scorer

The `GradientBoostingClassifier` (`risk_classifier.pkl`) runs independently alongside the Gemini/fallback triage. It processes the 18-feature vector from `features.py` and returns HIGH/MEDIUM/LOW with probabilities. Its output is used as a cross-check: if the Gemini triage says LOW but the ML model says HIGH with high confidence, the risk score gets a small upward adjustment. This prevents Gemini from being gamed by a well-written but high-risk complaint.

---

## 13. Machine Learning Models

All three models live in `backend/ml/models/`. They're trained by `train.py` using data generated by `dataset.py`. The training data is synthetic — it was designed to represent the statistical patterns of real cybercrime complaints, not to train on any real personal data.

### Model 1 — Fake Detector (fake_detector.pkl)

**Algorithm:** RandomForestClassifier (200 trees, max_depth=12, balanced class weights)  
**Input:** 18-feature vector  
**Output:** Class probabilities for [Fake, Genuine, Review]  
**Training data:** ~2,000 synthetic samples across three classes

**The 18 features:**

| Feature | What it Measures |
|---------|-----------------|
| word_count | Log-normalised total word count |
| unique_word_ratio | Vocabulary diversity (repetitive text is suspicious) |
| trigger_word_count | Density of high-severity keywords |
| has_financial_amount | Whether a specific rupee amount is present |
| has_phone_number | Whether a 10-digit phone number is present |
| has_date | Whether a date appears |
| has_proper_name | Whether "FirstName LastName" pattern appears |
| template_match_count | Matches against known fake template phrases |
| avg_word_length | Word complexity |
| sentence_count | Structural completeness |
| specificity_score | Combined score of 4 concrete-detail indicators |
| capital_letter_ratio | Unusual capitalisation patterns |
| numeric_ratio | Density of numbers in text |
| has_url | Presence of a web address |
| has_email | Presence of an email address |
| exclamation_count | Emotional amplification markers |
| question_mark_count | Rhetorical question patterns |
| financial_claim_without_amount | Claims money loss but gives no specific amount |

The last feature (`financial_claim_without_amount`) is particularly important: genuine fraud victims always know exactly how much they lost. A report that talks about "my money was taken" without a specific amount is a strong fake indicator.

### Model 2 — Crime Classifier (crime_classifier.pkl)

**Algorithm:** TF-IDF Vectorizer (3,000 features, 1-2 word n-grams, sublinear TF scaling) + LinearSVC (C=1.0)  
**Input:** Raw complaint text  
**Output:** One of 9 crime categories  
**Training data:** ~3,600 labelled complaint descriptions

**Crime Categories:**
- Financial Crime
- Online Harassment
- Identity Theft
- Extortion
- Child Safety
- Data Breach
- Cyber Fraud
- Impersonation
- Other Cybercrime

The TF-IDF vectoriser uses bigrams (1–2 word combinations) because phrases like "UPI fraud" or "unauthorized login" are more discriminative than individual words. `sublinear_tf=True` applies log normalisation so terms that appear 100 times aren't 100× more important than terms that appear once.

### Model 3 — Risk Classifier (risk_classifier.pkl)

**Algorithm:** GradientBoostingClassifier (150 trees, max_depth=5, learning_rate=0.1)  
**Input:** Same 18-feature vector as the fake detector  
**Output:** HIGH / MEDIUM / LOW with probabilities  
**Training data:** ~3,000 synthetic reports labelled by risk level

GradientBoosting was chosen over RandomForest for this task because risk scoring is a ranking problem (relative importance matters more than binary classification) and GBM handles it better with its sequential residual-correction approach.

**Note on the distinction between AI Triage and GradientBoosting Risk Scorer:**  
They're not doing the same thing. The GradientBoosting model classifies risk from *structural text features* (presence of specific numeric entities, word patterns). The AI Triage service classifies risk from *semantic meaning* (it understands what the victim is describing). For the same complaint, they can disagree — and that disagreement is itself informative. The ML model catches formally well-written high-risk complaints that Gemini might rank lower, and Gemini catches low-information high-impact cases that the ML model might miss.

---

## 14. Complaint Report Generation

**File:** `backend/services/fir_generator.py`

When a report is assessed as HIGH or MEDIUM risk and not flagged as REJECT, the system automatically generates a Complaint Report (CR) PDF. This is different from a traditional FIR (First Information Report) — the CR is the system's formatted output that documents the AI analysis, the evidence inventory, and the applicable legal sections. An officer reviews it and decides whether to formally register an FIR.

The PDF is generated using ReportLab and follows government document formatting conventions:
- A4 paper size
- Indian tricolour header (navy/saffron/green)
- Risk level prominently displayed with colour coding (RED for HIGH, ORANGE for MEDIUM)
- Complainant details section
- AI analysis summary box
- Evidence inventory table (filename, file type, SHA-256 hash, OCR confidence, tamper score)
- BNS sections table with full section text
- Forensics summary
- Section 65B certificate (certifying the digital evidence was received and hashed at a specific timestamp)
- Chain of custody block (SHA-256 of the report content, SHA-256 of the PDF itself)

The PDF itself is SHA-256 hashed and the hash stored in `report.fir_hash`. This means any later modification to the PDF file is immediately detectable.

Files are saved as `CR_{case_number}.pdf` in the `firs/` directory.

---

## 15. Reporter Trust Scoring

**File:** `backend/services/reporter_trust_service.py`

Every citizen who submits a report is tracked by phone number (primary) or email (fallback). The system builds a `ReporterProfile` that accumulates their submission history over time.

### Trust Score Calculation

The trust score is a weighted combination of four components:

| Component | Weight | What it Measures |
|-----------|--------|-----------------|
| Accuracy ratio (genuine/total) | 50% | What fraction of their submissions were genuine |
| FIR quality ratio (firs/genuine) | 25% | Of genuine reports, how many were serious enough for a CR |
| Serious cases ratio (high_risk/total) | 15% | How often they report genuinely serious incidents |
| Longevity bonus | 10% | Reward for established track record (≥5 genuine = 0.75 bonus, ≥10 = 1.0) |

A new reporter starts at 0.70 (neutral). Three or more fake reports trigger a progressive penalty (-0.10 per fake above 2, max -0.40). The trust score is always clamped to [0.0, 1.0].

### Trust Modifier on Authenticity

Before the final `is_flagged_fake` decision, the raw authenticity score is multiplied by a trust modifier:

- Trust ≥ 0.85 → ×1.08 (trusted reporter, slight boost)
- Trust 0.65–0.85 → ×1.00 (neutral)
- Trust 0.40–0.65 → ×0.90 (slightly suspicious history, 10% penalty)
- Trust < 0.40 → ×0.80 (very suspicious history, 20% penalty)
- Trust = 0 (blocked) → capped at 0.10

### Auto-Block Threshold

A reporter is automatically permanently blocked when they accumulate ≥5 fake-flagged reports AND their fake rate exceeds 60%. The block reason is recorded.

### DigiLocker Boost

If the citizen verified their identity via DigiLocker before submitting, their effective trust score gets +0.15 added. Aadhaar-verified identity makes fake reporting significantly riskier for the person doing it.

---

## 16. OTP Phone Verification

OTP-based phone verification was added as an additional layer of citizen identity assurance before report submission. The implementation exists in `citizen.js` and the backend routing.

### How It Works

When a citizen fills in their phone number on the submission form, they can request an OTP be sent to that number before they submit. The flow:

1. Citizen enters their mobile number in the form
2. Clicks "Send OTP" 
3. Backend generates a 6-digit OTP, stores it (with TTL of 10 minutes) mapped to the phone number
4. OTP is sent via SMS (Twilio / MSG91 / or SMTP fallback)
5. Citizen enters the OTP in the form
6. Backend verifies OTP — if valid, marks the phone as OTP-verified for this session
7. OTP verification status travels along with the report submission

### Effect on Trust Score

A phone number that was OTP-verified before submission gets treated similarly to DigiLocker verification: it adds confidence that the phone number belongs to the actual person submitting and not a throwaway number. This is factored into the reporter trust score.

### Configuration

OTP delivery requires SMTP or an SMS gateway to be configured:

```env
SMTP_ENABLED=true
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your@gmail.com
SMTP_PASSWORD=your-app-password
```

For SMS-based OTP (MSG91 / Twilio), configure the respective API keys in `.env`. The OTP service automatically falls back to email delivery if SMS is not configured.

### Security Notes

- OTPs are single-use and expire after 10 minutes
- The same OTP cannot be used twice even within the valid window
- Failed OTP attempts are rate-limited per phone number (max 5 attempts before 1-hour cooldown)
- OTPs are stored as hashed values in memory/DB — never in plaintext

---

## 17. DigiLocker Identity Verification

**Files:** `backend/services/digilocker_service.py`, `backend/routers/digilocker.py`

DigiLocker is India's official digital document storage service, backed by Aadhaar. It allows citizens to verify their identity using government-issued documents without sharing them directly.

### Two Modes

**Demo Mode** (no credentials in `.env`): The service operates in sandbox mode where clicking "Verify Identity" shows a popup asking for your name, and returns a simulated verified profile. This is specifically for hackathon demos and development where actual DigiLocker credentials aren't available.

**Production Mode** (DIGILOCKER_CLIENT_ID and DIGILOCKER_CLIENT_SECRET set in `.env`): Full OAuth 2.0 + PKCE flow against DigiLocker's actual API.

### The OAuth Flow

1. Frontend calls `GET /api/digilocker/auth-url` — returns a URL with state parameter and PKCE code challenge
2. Citizen is redirected (popup) to DigiLocker's login page
3. Citizen authenticates with their Aadhaar-linked credentials
4. DigiLocker redirects to `GET /api/digilocker/callback?code=...&state=...`
5. Backend exchanges code for access token (verifying state parameter and PKCE verifier)
6. Backend fetches user profile from DigiLocker's `/profile` endpoint
7. Backend issues a session token (SHA-256 of access token + timestamp)
8. The popup page sends `postMessage({type: 'DIGILOCKER_VERIFIED', profile: {...}})` to the parent window
9. The citizen portal receives the profile, stores the session token, and shows verified name in the form

### Session Tokens

DigiLocker session tokens are in-memory, expire after 30 minutes, and are only checked when a report is submitted. The verification status (`digilocker_verified=True`, `digilocker_name=verified_name`) is permanently stored on the report record.

---

## 18. Rate Limiting and Abuse Prevention

**File:** `backend/middleware/rate_limiter.py`

The `RateLimiterMiddleware` uses a **sliding window** algorithm — not a fixed window. The difference matters: a fixed window allows 2× the rate at window boundaries (submit 5 at 11:59pm, submit 5 at 12:00am = 10 in 2 minutes). A sliding window counts requests in a true rolling period.

### Protected Endpoints

| Endpoint | Limit | Window |
|----------|-------|--------|
| POST /api/reports/submit | 5 requests | Per hour, per IP |
| POST /api/auth/login | 10 attempts | Per 15 minutes, per IP |

### Response on Rate Limit

```json
HTTP 429
{
  "error": "Too many requests. Please wait before submitting again.",
  "retry_after_seconds": 1847,
  "limit": 5,
  "window_seconds": 3600
}
```

Headers include `Retry-After`, `X-RateLimit-Limit`, `X-RateLimit-Remaining`, `X-RateLimit-Reset`.

### Frequency Abuse Detection (Reporter-Level)

The rate limiter works at the IP level. The reporter trust service adds a second layer at the account level: if a reporter submits more than 10 reports in 24 hours OR more than 4 reports in 1 hour (regardless of IP), a frequency abuse flag is set, which caps the authenticity score at 0.40 and adds a flag to the report.

This catches people who use multiple IPs, VPNs, or proxies to bypass the IP-level rate limiter.

### Production Note

The in-memory rate limiter does not persist across restarts and does not share state between multiple processes. For multi-worker production deployments, replace the `_windows` dict with Redis (`aioredis` + sorted sets for sliding window). The interface is identical — just swap the storage backend.

---

## 19. Authentication

**File:** `backend/routers/auth.py`

Police officer authentication uses JWT Bearer tokens.

### JWT Configuration

- Algorithm: HS256
- Default expiry: 480 minutes (8 hours, suitable for a full police shift)
- Secret key: Set via `SECRET_KEY` in `.env` — must be at least 32 random bytes in production. Generate with: `openssl rand -hex 32`

### Password Hashing

bcrypt with 12 rounds is used directly (bypassing passlib) because passlib 1.7.4 has incompatibilities with bcrypt 4.x. The system pins bcrypt to 3.2.2 in startup scripts to prevent this issue.

Passwords are truncated to 72 bytes before hashing — this is a bcrypt protocol limitation, not a security concern for typical passwords.

### Role System

Three roles exist:
- **admin** — full access: create/deactivate officers, view all cases, all actions
- **officer** — full case access, cannot manage other officers
- **read_only** — view-only, cannot assign or close cases

The default admin account is created at startup if the `officer_users` table is empty:
- Username: `admin`
- Password: `AutoJustice@2024!`
- **This password must be changed immediately in production.**

### FastAPI Dependencies

```python
get_current_officer()  # Returns OfficerUser or None
require_officer()      # Returns OfficerUser or raises HTTP 401
require_admin()        # Returns OfficerUser (admin only) or raises HTTP 403
```

These are used as FastAPI `Depends()` parameters on any route that requires authentication.

---

## 20. Database Schema

The database uses SQLAlchemy ORM. All tables work identically on SQLite (development) and PostgreSQL (production) — the only change needed is `DATABASE_URL` in `.env`.

### Table: reports

The core table. Every field of the AI analysis pipeline is stored here.

| Column | Type | Description |
|--------|------|-------------|
| id | UUID | Primary key |
| case_number | String | Unique case number (CY-YYYY-XXXXXXXX format) |
| created_at | DateTime | UTC timestamp |
| complainant_name | String | Full name |
| complainant_phone | String | Normalized phone |
| complainant_email | String | Email address |
| incident_description | Text | Full complaint text |
| extracted_text | Text | Combined OCR text from all evidence |
| risk_level | String | HIGH / MEDIUM / LOW |
| risk_score | Float | 0.0–1.0 |
| crime_category | String | One of 9 canonical categories |
| crime_subcategory | String | Specific sub-type |
| entities | JSON | Extracted names, phones, amounts, accounts |
| bns_sections | JSON | List of applicable BNS/IT Act sections |
| ai_summary | Text | 2–3 sentence AI-generated summary |
| authenticity_score | Float | 0.0–1.0 fake detection score |
| is_flagged_fake | Boolean | True if below threshold |
| fake_flags | JSON | List of specific fake detection triggers |
| fake_recommendation | String | GENUINE / REVIEW / REJECT |
| forensics_tamper_score | Float | Max tamper score across all images |
| forensics_flags | JSON | List of forensic anomaly descriptions |
| forensics_summary | Text | Human-readable forensics summary |
| digilocker_verified | Boolean | Whether identity was verified |
| digilocker_name | String | Aadhaar-verified name |
| reporter_trust_score | Float | Trust score at time of submission |
| status | String | PROCESSING / TRIAGED / COMPLAINT_REGISTERED / CLOSED |
| fir_path | String | Filename of generated CR PDF |
| fir_hash | String | SHA-256 of the CR PDF |
| content_hash | String | SHA-256 of report content (for duplicate detection) |
| submission_ip | String | Submitter IP address |

### Table: evidence_files

One row per uploaded file per report.

| Column | Type | Description |
|--------|------|-------------|
| id | UUID | Primary key |
| report_id | UUID | Foreign key → reports |
| original_filename | String | Original upload filename |
| stored_filename | String | UUID-based safe storage name |
| file_type | String | image / pdf / text |
| sha256_hash | String | SHA-256 of file bytes |
| ocr_text | Text | Extracted text |
| ocr_confidence | Float | Tesseract confidence score |
| exif_data | JSON | Full EXIF metadata |
| is_tampered | Boolean | Forensics result |
| tamper_score | Float | 0.0–1.0 |
| tamper_flags | JSON | Specific forensic findings |
| gps_lat / gps_lon | Float | GPS coordinates if present |

### Table: officer_users

| Column | Type | Description |
|--------|------|-------------|
| id | UUID | Primary key |
| username | String | Unique login name |
| full_name | String | Display name |
| badge_number | String | Police badge number |
| hashed_password | String | bcrypt hash |
| role | String | admin / officer / read_only |
| is_active | Boolean | Soft delete flag |
| last_login | DateTime | Last successful login |

### Table: reporter_profiles

| Column | Type | Description |
|--------|------|-------------|
| id | UUID | Primary key |
| phone | String | Normalized phone (index) |
| email | String | Normalized email (index) |
| total_submissions | Integer | Count of all submissions |
| genuine_count | Integer | Submissions assessed as genuine |
| fake_flagged_count | Integer | Submissions flagged as fake |
| trust_score | Float | Current computed trust score |
| is_blocked | Boolean | Permanently blocked flag |
| block_reason | Text | Reason for block |

### Table: audit_logs

Immutable. Records every system action. Never updated or deleted.

| Column | Type | Description |
|--------|------|-------------|
| id | UUID | Primary key |
| report_id | UUID | Associated report (nullable) |
| timestamp | DateTime | UTC timestamp |
| action | String | REPORT_SUBMITTED / OFFICER_LOGIN / etc. |
| actor | String | Username or "SYSTEM" |
| details | JSON | All relevant context fields |
| ip_address | String | Request IP |

### Table: case_notes

Officer notes attached to cases.

| Column | Type | Description |
|--------|------|-------------|
| id | UUID | Primary key |
| report_id | UUID | Foreign key → reports |
| officer_id | UUID | Foreign key → officer_users |
| note_text | Text | The note content |
| is_internal | Boolean | If true, not visible to citizen |

### Indexes

- `reports.case_number` — unique index for case lookup
- `reports.created_at + risk_level` — composite index for dashboard queries
- `evidence_files.report_id` — for evidence-by-report queries
- `reporter_profiles.phone`, `reporter_profiles.email` — for reporter lookup
- `audit_logs.report_id`, `audit_logs.action` — for audit trail queries

---

## 21. API Endpoints Reference

All endpoints are accessible at `http://localhost:8000`. Interactive documentation: `http://localhost:8000/api/docs`

### Reports

| Method | Path | Description |
|--------|------|-------------|
| POST | /api/reports/submit | Submit complaint + evidence files |
| GET | /api/reports/ | List reports (officers) |
| GET | /api/reports/track/{case_number} | Track case by number (public) |
| GET | /api/reports/{id} | Get full report detail |
| GET | /api/reports/{id}/fir/download | Download CR PDF |
| POST | /api/reports/{id}/generate-fir | Force-generate CR (officer) |
| GET | /api/reports/{id}/verify-integrity | Verify SHA-256 hashes of all evidence |

### Authentication

| Method | Path | Description |
|--------|------|-------------|
| POST | /api/auth/login | Officer login → JWT |
| GET | /api/auth/me | Get current officer profile |
| POST | /api/auth/officers | Create officer (admin only) |
| GET | /api/auth/officers | List all officers |
| PUT | /api/auth/officers/{id}/deactivate | Deactivate officer (admin only) |

### Dashboard

| Method | Path | Description |
|--------|------|-------------|
| GET | /api/dashboard/stats | Aggregate stats (total, by risk, by category) |
| GET | /api/dashboard/recent | Recent cases feed |
| POST | /api/dashboard/cases/{id}/assign | Assign case to officer |
| POST | /api/dashboard/cases/{id}/close | Close a case |

### Cases

| Method | Path | Description |
|--------|------|-------------|
| GET | /api/cases/ | Paginated case list with filters |
| GET | /api/cases/{id}/notes | Get case notes |
| POST | /api/cases/{id}/notes | Add case note |
| PUT | /api/cases/{id}/status | Update case status |

### DigiLocker

| Method | Path | Description |
|--------|------|-------------|
| GET | /api/digilocker/status | DigiLocker configuration status |
| GET | /api/digilocker/auth-url | Get OAuth authorization URL |
| GET | /api/digilocker/callback | OAuth callback (production) |
| GET | /api/digilocker/demo-callback | Demo mode callback |
| GET | /api/digilocker/demo-verify | JSON demo verification |
| POST | /api/digilocker/verify-session | Validate session token |

### System

| Method | Path | Description |
|--------|------|-------------|
| GET | /api/health | System health check |

---

## 22. Frontend Pages

### / — Citizen Portal (citizen_portal.html)

The public-facing complaint submission form. No authentication required. Features:
- Multi-step form (personal details → incident details → evidence upload)
- DigiLocker identity verification button (opens popup)
- OTP phone verification flow
- File drag-and-drop with preview and size validation
- Real-time submission progress with AI processing steps animated
- Case number display and tracking link after successful submission

### /track/{case_number} — Case Tracking (case_tracking.html)

Citizens enter their case number to see status. Shows a 3-step progress indicator:
1. **Submitted** — report received
2. **Under Review** — AI triage complete
3. **CR Generated** — Complaint Report has been created and can be downloaded

If the case is REJECTED (fake detection), a clear message explains the outcome without revealing the AI's internal scoring.

### /login — Officer Login (login.html)

Simple login form. On success, stores JWT in localStorage and redirects to dashboard.

### /dashboard — Police Dashboard (police_dashboard.html)

The command view for officers. Shows:
- Summary stats (total cases, HIGH risk count, pending cases)
- Case list with risk colour coding, authenticity score, crime category
- Click-through to full case detail with all AI analysis fields
- Assignment and closure controls
- Case notes panel

---

## 23. Security and Compliance

### BNS 2023 (Bharatiya Nyaya Sanhita)

The system automatically maps applicable sections to every complaint:

- **BNS §111** — Organised crime (extortion, ransom)
- **BNS §211** — Giving false information to public servant (fake reports escalated to HIGH risk under this section)
- **BNS §218** — Public servant framing incorrect record
- **BNS §308** — Extortion
- **BNS §318** — Cheating
- **BNS §351** — Criminal intimidation (online harassment)

### IT Act 2000 Sections

- **§43** — Unauthorised access to computer
- **§66** — Computer related offences
- **§66C** — Identity theft using digital means
- **§66D** — Cheating by personation using computer resource
- **§67** — Publishing obscene material electronically
- **§67A/B** — Sexually explicit material, child pornography

### Section 65B — Indian Evidence Act

Every evidence file receives a SHA-256 hash at the moment of upload. The CR PDF includes a Section 65B certificate certifying:
- File name, MIME type, size
- SHA-256 hash
- Exact UTC timestamp of receipt
- That no processing was performed on the file content before hashing

The `GET /api/reports/{id}/verify-integrity` endpoint re-hashes every evidence file and compares against stored hashes — detectable post-upload tampering.

### DPDP Act 2023

- PII (Aadhaar-linked name from DigiLocker, phone numbers, addresses) is stored in columns marked for encryption in production
- Reporter profiles use normalized phone/email as identifiers — no unnecessary PII stored
- Audit logs provide the data processing trail required by DPDP
- The `submission_ip` column enables the right-to-erasure workflow

### General Security

- Passwords stored as bcrypt hashes (never plaintext)
- JWT tokens signed with HS256 using a secret key from environment
- File uploads stored with UUID names (no original filename in the path) to prevent path traversal
- File extensions validated against a strict allowlist before storage
- File size capped at 25MB per file
- SQL injection: impossible — SQLAlchemy ORM is used exclusively, no raw SQL
- CORS is configured open (`allow_origins=["*"]`) for development — restrict to specific domains in production

---

## 24. Deployment

### Development

```bash
bash start_demo.sh
```

### Docker Production

```bash
# Build and start
docker-compose up -d

# View logs
docker-compose logs -f app

# Stop
docker-compose down
```

The `docker-compose.yml` runs two containers:
- `autojustice_app` — FastAPI via uvicorn on port 8000 (internal)
- `autojustice_nginx` — nginx on port 80 (public), reverse proxying to app

Evidence files and FIR PDFs are stored in named Docker volumes (`uploads_data`, `firs_data`) that persist across container restarts.

### nginx Configuration

The nginx config at `nginx/nginx.conf` handles:
- Reverse proxy to `app:8000`
- Client max body size: 30MB (for evidence uploads)
- Proxy timeouts: 120s (for AI pipeline processing)
- Gzip compression for API responses
- Cache headers for static files

### Migrating from SQLite to PostgreSQL

Only one change is needed:

1. Set `DATABASE_URL=postgresql://user:password@host:5432/autojustice` in `.env`
2. Install: `pip install psycopg2-binary`
3. Run: `python -c "from database import engine, Base; Base.metadata.create_all(bind=engine)"` (or use Alembic)

No changes to any Python code are needed — SQLAlchemy ORM is database-agnostic. The `database.py` file already auto-detects whether it's connecting to SQLite or PostgreSQL and adjusts connection arguments accordingly.

For schema migrations going forward, the recommended approach is Alembic:
```bash
pip install alembic
alembic init alembic
# Configure alembic.ini with DATABASE_URL
alembic revision --autogenerate -m "initial"
alembic upgrade head
```

### SSL / HTTPS

Uncomment the 443 port mapping and SSL volume in `docker-compose.yml`, add your certificate files to `nginx/ssl/`, and uncomment the SSL server block in `nginx.conf`.

For Let's Encrypt:
```bash
certbot certonly --standalone -d yourdomain.com
# Copy fullchain.pem and privkey.pem to nginx/ssl/
```

---

## 25. Offline Mode

The system is designed to work fully offline with zero data leaving the host machine. Here's what works with and without internet:

### Full Functionality (no internet needed)

- Complete report submission and storage
- Tesseract OCR (runs locally)
- All 3 ML models — fake detector, crime classifier, risk scorer (run locally from .pkl files)
- Image forensics layers 1–5 (ELA, metadata, AI generation signal, noise, screenshot)
- PDF generation (ReportLab runs locally)
- SHA-256 hashing and chain of custody
- Reporter trust scoring
- Rate limiting
- JWT authentication
- DigiLocker demo mode

### Requires Internet

- Gemini 1.5 Pro — AI triage (semantic analysis, BNS section mapping, entity extraction)
- Gemini Vision fallback for OCR (Layer 3 of OCR service)
- Gemini Vision for image forensics Layer 6

### Degraded Mode Behaviour

When Gemini is unavailable, the system falls back gracefully:
- AI triage uses the rule-based engine (keyword scoring + ML model) instead of Gemini
- OCR falls back to multi-PSM Tesseract only (no Gemini Vision fallback)
- Image forensics uses layers 1–5 only (no Gemini Vision layer 6)
- All other functionality continues normally

The fallback is transparent to both the citizen and the officer — the response has the same structure, just lower-confidence scores from the rule-based triage.

---

## 26. Business Model

AutoJustice NEXUS has three realistic deployment paths:

### 1. Government SaaS (B2G)

The most direct path. Police departments, state cybercrime units, and CERTs license the platform on a per-station basis. Pricing structured as:
- **Base station license** — per-year fee covering 1 active station, unlimited reports
- **Volume tier** — discounted pricing for state-level rollouts across multiple stations
- **Training and onboarding** — paid implementation support for initial setup, officer training, system customisation
- **Compliance consulting** — help with DPDP Act data residency requirements, Section 65B certification workflows

Government procurement timelines are long, so the short-term path is winning hackathons and pilot programs, then converting those pilots to contracts.

### 2. Managed Service for Private Sector

Banks, fintech companies, and telecom operators face massive fraud volumes and could use the fake detection and forensics pipeline as an API. The value proposition is different here — not about generating FIRs but about:
- Screening fraud reports before escalating to internal investigation teams
- Validating evidence submitted in insurance claims
- Scoring authenticity of social engineering complaint reports

Pricing: per-API-call for the fake detection and forensics endpoints.

### 3. Legal Tech / Citizen Services

Consumer legal platforms (VakilSearch, LegalWiz, etc.) could integrate the evidence submission and case tracking components to help individuals who want to file cybercrime complaints but don't know how to navigate the police system. Revenue model: transaction fee per successfully submitted complaint.

---

*This documentation covers AutoJustice AI NEXUS v2.0. For architecture diagrams, API schemas, and integration guides, see the interactive Swagger documentation at `/api/docs` when the server is running.*
