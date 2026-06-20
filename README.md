<p align="center">
  <h1 align="center">GP Outpatient Upload</h1>
  <p align="center">AI-powered browser automation for submitting medical training records to <code>gp.itcm.cn</code></p>
</p>

---

## What It Does

This is a **WorkBuddy skill** that automates the entire workflow of submitting standardized medical case records to the Chinese General Practitioner training management system (`gp.itcm.cn`).

It handles **data preparation** (image classification, OCR extraction, auto-completion of TCM diagnoses) and **browser automation** (headful Chromium form-filling via Playwright) across all 5 record modules.

| Module | Description | Image Upload |
|--------|-------------|:---:|
| 门诊病例 (Outpatient Case) | General outpatient visit records | ✓ |
| 手写大病历 (Handwritten Grand Case) | Full handwritten case records | ✓ |
| 门诊病种记录 (Outpatient Disease Record) | Disease-specific outpatient tracking | ✗ |
| 住院病种记录 (Inpatient Disease Record) | Inpatient disease tracking | ✗ |
| 临床技术记录 (Clinical Technical Record) | Clinical procedure records (TCM Four Examinations, etc.) | ✗ |

---

## How It Works

### Phase 1 — Data Preparation
1. **Classify** uploaded images into the 5 record categories
2. **Extract** patient name, visit date, and medical record number from images
3. **Auto-complete** TCM-to-Western diagnosis mappings and clinical notes (~50 chars)
4. **Verify** with user — fuzzy or missing data is flagged, never fabricated
5. **Output** registration tables (`.txt`) and structured JSON files ready for submission

### Phase 2 — Browser Automation
1. Launch headful Chromium via Playwright
2. Prompt user to log in to `gp.itcm.cn` via a signal-file pattern
3. Fill and submit forms record-by-record with automatic license verification
4. Keep browser open for manual review after submission

---

## Installation

### Prerequisites

- [WorkBuddy](https://www.workbuddy.cn) desktop client
- Python 3.8+
- Playwright and Chromium

### Quick Start

1. Download the `gp-outpatient-upload.zip` release.
2. Open WorkBuddy, create a new conversation, and select **DeepSeek V4 Pro**.
3. Drag the ZIP file into the chat and say:

   > 帮我安装这个技能压缩包，并安装好 Playwright

4. Set up your License Key:

   > 帮我设置 License Key：XXXX-XXXX-XXXX

---

## Usage

Once the skill is loaded, just **send your case images and describe what you want**:

```
帮我提交这些门诊病例图片到 gp.itcm.cn，科室是心血管内科。每份病例有 3 张图片。
```

The AI will guide you through classification, extraction, auto-completion, and submission — no commands to memorize.

For detailed instructions, see the included `使用教程.md` or `使用教程.docx`.

---

## Project Structure

```
gp-outpatient-upload/
├── SKILL.md              # Skill definition and workflow rules
├── 使用教程.md/docx       # User tutorial (Chinese)
├── scripts/
│   ├── gp_outpatient_upload.mjs      # Outpatient case image upload
│   ├── gp_no_photo_records.mjs       # Disease & clinical records (no photo)
│   ├── license_check.py              # License client (encrypted)
│   └── playwright/
│       └── gp_playwright.py          # Headful browser automation (encrypted)
├── license-server/       # FastAPI license management service
├── test_data/            # Test fixtures
├── test_encrypted.py     # Integration tests
└── README.md
```

---

## ⚠️ Disclaimer

This program runs **entirely on your local machine**. It does **not** collect, store, or transmit any personal information. All case data is sent directly from your browser to `gp.itcm.cn` — no third-party servers are involved.

---

## License

This project uses a proprietary call-based license. Each record submission consumes one license call. Contact the skill provider for license keys and quota management.
