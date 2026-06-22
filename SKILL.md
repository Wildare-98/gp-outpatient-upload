---
name: gp-outpatient-upload
description: Control Chrome to submit already-confirmed records into the gp.itcm.cn training management system. Supports 门诊病历, 门诊病种记录, 临床技术记录, 手写大病历, 住院病种记录. License verified per record. Uses Playwright Python (headful browser) with signal-file login and layui form automation.
---

# GP Register Automation

## Scope

> **当前版本：v1.2** — 更新 License 验证服务地址

Use this skill for the Chrome/webpage submission phase after the user has prepared confirmed records.

All scripts run via Playwright Python with a headful Chromium browser. There is no Node REPL requirement.

## License Verification (Required)

This skill requires a valid License Key. **Every record submission deducts one call** — submitting a batch of 50 records deducts 50 calls. If the quota runs out mid-batch, the script stops gracefully.

The verification is automatic and integrated into the script. The user does NOT need to call it separately.

**First-time setup:**

```bash
python scripts/license_check.py setup YOUR-LICENSE-KEY
```

**Query remaining quota** (does not decrement):

```bash
python scripts/license_check.py info
```

**Important rules for the AI assistant:**
1. The script automatically verifies the license before each record submission. The AI does not need to pre-check.
2. If the script exits with `[LICENSE]` error, tell the user the exact error message.
3. Common errors:
   - `"无效的 License Key"` — Key is wrong, ask user to run `license_check.py setup <key>`.
   - `"调用次数已用完，请联系购买"` — Quota exhausted, user must purchase more.
   - `"无法连接服务器"` — Network issue, try again later.

## Safety

Submitting records sends medical and personal data to `https://gp.itcm.cn/`. Proceed only when the user clearly authorizes submitting these records to this system. If the user asks only to inspect, prepare, or dry run, pass `--dry-run` or do not submit.

Do not inspect cookies, local storage, passwords, or browser profile internals.

## Prerequisites

> **必须使用 Python 3.13**（脚本由 PyArmor 加密，其他版本无法解密运行）
>
> 版本不对时，先安装 Python 3.13：
> ```bash
> # Windows
> winget install Python.Python.3.13
>
> # macOS
> brew install python@3.13
> ```
> 安装后用 `python3.13 --version` 确认，然后继续：

```bash
pip install playwright
playwright install chromium
```

## Quick Start

```bash
# 门诊病种 + 临床技术 一次提交
python scripts/playwright/gp_playwright.py \
  --disease disease_records.json \
  --clinical clinical_records.json

# 门诊病历（带图片上传）
python scripts/playwright/gp_playwright.py \
  --outpatient outpatient_records.json

# 手写大病历
python scripts/playwright/gp_playwright.py \
  --handwritten handwritten_records.json

# 住院病种记录
python scripts/playwright/gp_playwright.py \
  --inpatient inpatient_records.json

# dryRun 模式（填写不提交，仍扣 License 次数）
python scripts/playwright/gp_playwright.py \
  --disease test.json --dry-run
```

## CLI Arguments

| 参数 | 说明 |
|------|------|
| `--disease PATH` | 门诊病种记录 JSON |
| `--clinical PATH` | 临床技术记录 JSON |
| `--outpatient PATH` | 门诊病历 JSON（带图片上传） |
| `--handwritten PATH` | 手写大病历 JSON（带图片上传） |
| `--inpatient PATH` | 住院病种记录 JSON |
| `--dry-run` | 仅填表单不提交（仍扣 License） |
| `--outdir PATH` | 输出目录（截图、结果 JSON、信号文件） |

## Login Flow

脚本自动检测登录状态，无需信号文件：

1. 脚本检测到登录页 → 输出 `>>> [需要登录]` → 自动轮询等待用户登录
2. AI 看到该提示 → 弹窗提醒用户 "请在浏览器中登录 gp.itcm.cn"
3. 用户手动登录 → 脚本自动检测并通过
4. 提交完成后，脚本打印结果并退出；Chrome 保持后台运行，下次免登录

---

## 模块一：门诊病历（带图片上传）

Route: `/OutpatientCaseRecord/Index`

Record fields:

```json
{
  "department": "儿科",
  "patient_name": "张三",
  "visit_date": "2026-02-01",
  "image_path": "D:/absolute/path/IMG_0001.jpg",
  "image_paths": [
    "D:/absolute/path/page1.jpg",
    "D:/absolute/path/page2.jpg"
  ]
}
```

Use either `image_path` for a single image or `image_paths` for multiple pages. The page accepts `jpg`, `jpeg`, `bmp`, and `png`.

## 模块二：门诊病种记录（无图片）

Route: `/OutpatientRecord/Index`

Record fields:

```json
{
  "department": "儿科",
  "patient_name": "张三",
  "visit_date": "2026-02-01",
  "tcm_diagnosis": "感冒病",
  "western_diagnosis": "上呼吸道感染",
  "visit_type": "初诊",
  "remarks": "门诊病种记录备注"
}
```

Accepted aliases: `visit_date` ← `outpatient_date`, `date`, `OutpatientDate`; `tcm_diagnosis` ← `diagnosis`, `Diagnosis`, `zhongyi_diagnosis`; `western_diagnosis` ← `diagnosis_western`, `DiagnosisWestern`, `xiyi_diagnosis`; `visit_type` ← `outpatient_type`, `OutpatientType` (values: `初诊`/`复诊`/`确诊` or `0`/`1`/`2`); `remarks` ← `remark`, `note`, `Remarks`.

## 模块三：临床技术记录（无图片）

Route: `/ClinicalRecord/Index`

Record fields:

```json
{
  "department": "儿科",
  "patient_name": "张三",
  "case_code": "2300000000",
  "operation_date": "2026-02-01",
  "operation_item": "耳穴压丸",
  "remarks": "临床技术记录备注"
}
```

Accepted aliases: `case_code` ← `medical_record_no`, `record_no`, `clinic_id`, `CaseCode`; `operation_date` ← `date`, `visit_date`, `OperationDate`; `operation_item` ← `operation_name`, `skill_name`, `item`, `OperationItem`; `remarks` ← `remark`, `note`, `Remarks`.

## 模块四：手写大病历（带图片上传）

Route: `/HospitalizationCaseRecord/Index`

Record fields (same as 门诊病历):

```json
{
  "department": "儿科",
  "patient_name": "张三",
  "visit_date": "2026-02-01",
  "image_path": "D:/absolute/path/IMG_0001.jpg",
  "image_paths": [
    "D:/absolute/path/page1.jpg",
    "D:/absolute/path/page2.jpg"
  ]
}
```

## 模块五：住院病种记录（无图片）

Route: `/HospitalizationRecord/Index`

Record fields:

```json
{
  "department": "儿科",
  "patient_name": "张三",
  "case_code": "2300000000",
  "visit_date": "2026-02-01",
  "tcm_diagnosis": "感冒病",
  "western_diagnosis": "上呼吸道感染",
  "remarks": "住院病种记录备注"
}
```

Use `case_code` or `hospitalization_code` for the hospitalization ID. Date uses a text input (`#CreationTime`), not laydate.

---

## Known Routes

| 模块 | Route | Key Fields |
|------|-------|------------|
| 门诊病历 | `/OutpatientCaseRecord/Index` | `#PatientName`, `#CreationTime` |
| 门诊病种记录 | `/OutpatientRecord/Index` | `#PatientName`, `#OutpatientDate`, `#Diagnosis`, `#DiagnosisWestern`, `input[name="OutpatientType"]`, `#Remarks` |
| 临床技术记录 | `/ClinicalRecord/Index` | `#PatientName`, `#CaseCode`, `#OperationDate`, `#OperationItem`, `#Remarks` |
| 手写大病历 | `/HospitalizationCaseRecord/Index` | `#PatientName`, `#CreationTime` |
| 住院病种记录 | `/HospitalizationRecord/Index` | `#PatientName`, `#HospitalizationCode`, `#CreationTime`, `#Diagnosis`, `#DiagnosisWestern` |

## Operating Rules

1. The script launches a headful Chromium browser and navigates to `https://gp.itcm.cn/`.
2. If the login page appears, the AI must create `gp_continue.txt` after the user logs in.
3. Always click the target sidebar menu before submitting; the site may keep old module iframes in the DOM.
4. Leave `学生` unchanged unless the user says otherwise.
5. Select the record department from the second `请选择` field.
6. Run one record with `--dry-run` if the module has changed or the user has not verified the template.
7. Process in chunks of 4-5 records for live submissions.
8. Stop on validation prompts, duplicate warnings, missing fields, or a form that does not close after submit.
9. The browser stays open after completion for manual review; the AI creates `gp_done.txt` to close it.

## Programmatic Use

```python
from gp_playwright import GpSubmitter

s = GpSubmitter(outdir="./output", dry_run=False)
s.launch_and_login()

# 门诊病种记录
s.run_disease("disease_records.json")

# 临床技术记录
s.run_clinical("clinical_records.json")

# 门诊病历（含图片上传）
s.run_outpatient("outpatient_records.json")

# 手写大病历
s.run_handwritten("handwritten_records.json")

# 住院病种记录
s.run_inpatient_disease("inpatient_records.json")

s.wait_exit()
```
