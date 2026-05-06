# AutoJustice AI NEXUS — Synthetic Dataset Schema

**Version:** 1.0  
**Total Records:** 52 demo cases  
**Purpose:** Hackathon demonstration of cybercrime complaint AI triage pipeline  
**Compliance:** BNS 2023 · IT Act 2000 · DPDP Act 2023 · Section 65B IEA  

---

## Dataset Overview

| Attribute | Value |
|---|---|
| Total Cases | 52 |
| High Risk | 19 |
| Medium Risk | 16 |
| Low Risk | 10 |
| Fake / Rejected | 7 |
| With Complaint Reports | 24 |
| Indian States Covered | 18 |
| Crime Categories | 9 |
| Date Range | March – April 2024 |

---

## Schema Fields

### Core Identifiers

| Field | Type | Description | Example |
|---|---|---|---|
| `id` | UUID string | Unique report identifier (auto-generated) | `"a3f9c2d1-..."` |
| `case_number` | string | Police case number `CY-YYYY-XXXXXXXX` | `"CY-2024-10000000"` |
| `created_at` | datetime (UTC) | Timestamp of report submission | `"2024-04-14T14:30:00"` |
| `updated_at` | datetime (UTC) | Last modification timestamp | `"2024-04-14T15:00:00"` |

---

### Complainant PII (DPDP Act 2023 Protected)

| Field | Type | Required | Description |
|---|---|---|---|
| `complainant_name` | string (max 255) | Yes | Full legal name of complainant |
| `complainant_phone` | string (max 20) | No | 10-digit Indian mobile number |
| `complainant_email` | string (max 255) | No | Email address |
| `complainant_address` | text | No | City, State, PIN |

> ⚠️ All PII is stored encrypted at rest in production and subject to DPDP Act 2023 data minimization principles.

---

### Incident Details

| Field | Type | Required | Description | Example |
|---|---|---|---|---|
| `incident_description` | text | Yes | Full narrative (20–5000 chars) | "On 14th April 2024..." |
| `incident_date` | string (50) | No | Free-form date/time of incident | "14 April 2024, 2:30 PM" |
| `incident_location` | string (500) | No | City or "Online" | "Bandra West, Mumbai" |

---

### AI Triage Results

| Field | Type | Range/Enum | Description |
|---|---|---|---|
| `risk_level` | enum string | `HIGH` / `MEDIUM` / `LOW` / `PENDING` | AI-assigned risk classification |
| `risk_score` | float | 0.0 – 1.0 | Numerical risk confidence score |
| `crime_category` | string | See categories below | Primary crime classification |
| `crime_subcategory` | string | Free text | Specific subcategory |
| `ai_summary` | text | — | 1–2 sentence AI-generated briefing |
| `entities` | JSON object | See entity schema | Extracted named entities |
| `bns_sections` | JSON array of strings | BNS/IT Act sections | Auto-mapped applicable legal sections |

#### Crime Categories (enum)
```
Financial Crime          — UPI fraud, bank phishing, investment scam, e-commerce
Identity Theft           — KYC misuse, fake profiles, Aadhaar fraud
Online Harassment        — Cyberstalking, defamation, deepfake threats
Extortion                — Sextortion, ransomware, blackmail
Child Safety             — POCSO, minor sextortion, CSAM
Data Breach              — Corporate hack, ransomware, insider threat
Hacking                  — Unauthorized access, account takeover
Disinformation           — Fake news, voter manipulation
Other Cybercrime         — Miscellaneous, suspected false reports
```

#### Entity Schema (JSON Object)
```json
{
  "victim":           "string | null   — Victim name/identifier",
  "suspect":          "string | null   — Suspect name/handle/number",
  "financial_amount": "string | null   — e.g. 'Rs. 45,000'",
  "financial_vector": "string | null   — e.g. 'Google Pay UPI - handle@bank'",
  "platform":         "string | null   — e.g. 'WhatsApp', 'Instagram'",
  "location":         "string | null   — Physical or online location",
  "contact_numbers":  "array<string>   — Phone numbers of suspect",
  "urls_links":       "array<string>   — URLs, handles, wallet addresses"
}
```

---

### Fake Report Detection

| Field | Type | Range/Enum | Description |
|---|---|---|---|
| `authenticity_score` | float | 0.0 – 1.0 | Composite AI authenticity score |
| `is_flagged_fake` | boolean | true/false | Whether AI flagged as likely fake |
| `fake_flags` | JSON array of strings | — | Specific anomalies detected |
| `fake_recommendation` | enum string | `GENUINE` / `REVIEW` / `REJECT` | AI verdict |

#### Score Interpretation
| Score Range | Label | Meaning |
|---|---|---|
| 0.80 – 1.00 | Genuine | High confidence — genuine complaint |
| 0.65 – 0.79 | Likely Genuine | Probably genuine — minor gaps |
| 0.45 – 0.64 | Review | Ambiguous — officer must verify manually |
| 0.25 – 0.44 | Suspicious | Multiple authenticity concerns |
| 0.00 – 0.24 | Reject | Likely fabricated — do not act without investigation |

---

### Image Forensics

| Field | Type | Description |
|---|---|---|
| `forensics_tamper_score` | float (0–1) | Highest tamper score across all uploaded images |
| `forensics_flags` | JSON array | Specific forensic anomalies (ELA, EXIF, AI-gen) |
| `forensics_summary` | text | Human-readable forensics summary |

#### Per-Evidence-File Fields (in `evidence_files[]`)
| Field | Type | Description |
|---|---|---|
| `sha256_hash` | string (64) | SHA-256 hash for Section 65B chain of custody |
| `ocr_text` | text | Extracted text via Tesseract OCR |
| `ocr_confidence` | float (0–1) | OCR extraction confidence |
| `tamper_score` | float (0–1) | Per-file tamper score |
| `tamper_flags` | JSON array | Per-file anomaly flags |
| `ela_analysis` | JSON | ELA heatmap statistics (mean_diff, max_diff, std_diff) |
| `exif_data` | JSON | Extracted EXIF metadata |
| `is_tampered` | boolean | Whether file is flagged as tampered |
| `gps_lat` / `gps_lon` | float | GPS coordinates if present in EXIF |

---

### Reporter Trust

| Field | Type | Description |
|---|---|---|
| `reporter_trust_score` | float (0–1) | Computed trust score for this reporter |
| `reporter_profile_id` | UUID | Link to `reporter_profiles` table |

#### Trust Score Bands
| Score | Label | Action |
|---|---|---|
| ≥ 0.80 | High Trust | Expedited processing |
| 0.40 – 0.79 | Neutral | Standard processing |
| 0.20 – 0.39 | Low Trust | Requires manual review |
| < 0.20 | Blocked | Submission rejected |

---

### Case Status & Workflow

| Field | Type | Enum Values | Description |
|---|---|---|---|
| `status` | enum string | `PENDING` `PROCESSING` `TRIAGED` `COMPLAINT_REGISTERED` `CLOSED` `REJECTED` | Current case state |
| `fir_path` | string | filename | PDF path on disk if CR generated |
| `fir_generated_at` | datetime | — | Timestamp of CR generation |
| `fir_hash` | string (64) | SHA-256 | PDF integrity hash |
| `assigned_officer` | string | — | Officer name/badge assigned |

#### Status Flow
```
PENDING → PROCESSING → TRIAGED → COMPLAINT_REGISTERED → CLOSED
                              ↘ REJECTED (fake/false)
```

---

### Chain of Custody (Section 65B IEA)

| Field | Type | Description |
|---|---|---|
| `content_hash` | string (64) | SHA-256 of complainant_name + description + OCR text |
| `fir_hash` | string (64) | SHA-256 of generated PDF file |
| `submission_ip` | string (45) | Client IP address at submission |

---

## Dataset Distribution (52 cases)

### By Risk Level
| Risk Level | Count | % |
|---|---|---|
| HIGH | 19 | 36.5% |
| MEDIUM | 16 | 30.8% |
| LOW | 10 | 19.2% |
| FAKE/REJECTED | 7 | 13.5% |

### By Crime Category
| Category | Count |
|---|---|
| Financial Crime | 24 |
| Identity Theft | 5 |
| Online Harassment | 7 |
| Extortion | 4 |
| Child Safety | 2 |
| Data Breach | 3 |
| Hacking | 3 |
| Other/False Report | 4 |

### By Status
| Status | Count |
|---|---|
| COMPLAINT_REGISTERED | 22 |
| TRIAGED | 18 |
| CLOSED (fake/false) | 7 |
| PENDING | 5 |

### By Geographic Region
| State | Count |
|---|---|
| Maharashtra (Mumbai, Pune, Nagpur) | 7 |
| Delhi NCR | 6 |
| Karnataka (Bengaluru) | 5 |
| Telangana (Hyderabad) | 5 |
| Uttar Pradesh | 5 |
| Kerala | 4 |
| Tamil Nadu | 4 |
| Gujarat | 3 |
| West Bengal | 2 |
| Rajasthan | 2 |
| Others (13 states) | 9 |

---

## Legal Compliance Notes

- **Section 65B IEA**: SHA-256 hashes stored for every document and report for digital evidence admissibility
- **DPDP Act 2023**: PII fields tagged for encryption at rest; no third-party data sharing  
- **BNS 2023**: All crime categories mapped to applicable BNS and IT Act sections  
- **POCSO Act**: Child safety cases flagged for mandatory POCSO application  
- **CERT-In**: Data breach cases flagged for mandatory 6-hour reporting  

---

