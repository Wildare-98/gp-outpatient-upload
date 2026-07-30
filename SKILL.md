---
name: gp-outpatient-upload
description: End-to-end workflow for preparing and submitting GP training register records to gp.itcm.cn. Use when Codex must classify medical case images, extract and confirm patient record data, generate registration tables or JSON, or operate the Playwright Chrome automation for 门诊病历, 手写大病历, 门诊病种记录, 住院病种记录, and 临床技术记录.
---

# GP 规培登记手册自动化

当前技能包：v1.6（浏览器自动化基于 v1.6）。此技能分两段使用：

1. **Phase 1：资料准备** - 图片分类、信息提取、登记表和提交 JSON 生成、用户确认。
2. **Phase 2：网站提交** - 使用 Playwright Python 控制有头 Chrome，将已确认记录提交到 `https://gp.itcm.cn/`。

只在用户明确授权后提交真实记录。提交会向网站发送患者个人和医疗信息，并且每条记录会触发 License 校验和扣次。用户只要求检查、整理或演练时，使用 `--dry-run` 或只完成 Phase 1。

## 基本原则

- 不编造姓名、日期、病历号等基础身份信息。临床技术记录的操作内容和备注可按用户要求拟写或编造，但在写入登记表或提交前必须先展示给用户确认。
- 使用用户确认后的数据生成 JSON；不要把未确认的 OCR/视觉识别结果直接提交。
- 图片上传模块只接受 `jpg`、`jpeg`、`png`、`bmp`。发现 `heic`、`webp`、`tiff`、`gif` 等格式时，让用户自行转换。
- 所有本地图片路径写绝对路径，Windows 路径可统一写为 `D:/...` 形式，减少转义问题。
- 不检查浏览器 cookie、localStorage、密码或浏览器配置内部文件。
- 网站结构或模板变化、用户未核对过的新模块，先用 1 条记录 `--dry-run` 验证。

---

# Phase 1：资料准备

## 1. 文件分类

逐一查看用户提供的图片，将每个文件归入以下类别，并先向用户确认分类结果。

| 类别 | 是否上传图片 | 登记字段 |
|---|:---:|---|
| 门诊病例 | 是 | 序号、姓名、就诊日期、手写病历图片位置 |
| 手写大病历 | 是 | 序号、姓名、就诊日期、手写病历图片位置 |
| 门诊病种记录 | 否 | 姓名、就诊日期、病历号、中医病名、西医病名、初诊/复诊/确诊、备注 |
| 住院病种记录 | 否 | 姓名、就诊日期、病历号、中医病名、西医病名、主管/参观、备注 |
| 临床技术记录 | 否 | 姓名、就诊日期、病历号、操作名称、备注 |

如果图片内容不足以判断类别，先询问用户，不要猜。

## 2. 提取和校验字段

从图片中优先提取能直接看到的信息：

- 门诊病例、手写大病历：`patient_name`、`visit_date`、`image_path` 或 `image_paths`。
- 门诊病种记录、住院病种记录：`patient_name`、`visit_date`、`case_code` 或 `hospitalization_code`；住院记录另用 `inpatient_role` 表示主管/参观，省略时默认 `主管`。
- 临床技术记录：`patient_name`、`operation_date` 或 `visit_date`、`case_code`。

校验规则：

- 日期统一为 `YYYY-MM-DD`。
- 姓名和日期是必填项。
- 病历号能读出则填写；读不出时标为「缺失」并让用户确认。
- 同一字段冲突时，以图片中更直接的记录为准，通常手写优先于打印，打印优先于印章。

向用户展示确认预览：

```text
===== [类别名] 登记表预览 =====

[序号] 姓名: XXX | 日期: YYYY-MM-DD | 病历号: XXX | 图片: D:/path/to/image.jpg

以下字段待确认/缺失：
- 字段名: 当前值「???」，请确认

请确认以上信息，或提供补充。
```

## 3. 自动补全

只在基础信息经用户确认后补全诊断、操作和备注。

### 门诊病种记录 / 住院病种记录

先问用户该患者需要登记哪些中医病种。用户给出中医病名后，再补全：

- `western_diagnosis`：对应的主要西医诊断。
- `remarks`：围绕症状、诱因、病情特点写约 50 字，避免编造检查结果或治疗经过。

常用映射可参考：

| 中医病名 | 西医病名 | 备注写法 |
|---|---|---|
| 眩晕 | 高血压 | 以头晕目眩为主要表现，可伴恶心、耳鸣，多与情志、饮食、劳倦相关。 |
| 胸痹 | 冠状动脉粥样硬化性心脏病 | 以胸闷胸痛为主，可痛彻背部，多与寒邪、饮食、情志、劳倦相关。 |
| 心悸 | 心律失常 | 自觉心中悸动不安，可伴胸闷气短、失眠健忘，多与体虚或情志刺激相关。 |
| 心衰 | 心力衰竭 | 以心悸气短、动则喘促、下肢水肿为主，可伴乏力、口唇紫绀。 |
| 血浊 | 高脂血症 | 以血脂升高、血液黏稠为特征，可伴头重、胸闷、肢体困重。 |
| 真心痛 | 急性心肌梗死 | 以胸骨后剧烈疼痛为主，可伴大汗、面色苍白、濒死感，病情危重。 |

用户给出的病名不在表中时，可以基于中医知识推理，但补全结果必须再次给用户确认。

门诊病种记录若用户未提供初诊/复诊/确诊字段，则默认`初诊`。
住院病种记录若用户未提供主管/参观字段，则默认`主管`。

### 临床技术记录

先问用户需要登记多少条，以及每条操作名称。

- `中医四诊`：可按用户要求拟写现病史 + 舌脉描述，约 50 字；可以基于用户指定病情生成，也可以按用户要求补充合理表述。
- `其他`：如心电图、耳穴压丸、针灸等，操作名称和备注可由用户提供，也可按用户要求拟写。
- 拟写或编造任何临床技术记录内容前，先说明将要生成的操作名称、备注方向和是否属于编造内容；用户确认后再写入登记表或 JSON。

示例：

```text
姓名 | 就诊日期 | 病历号 | 操作名称 | 备注
沈x瑶 | 2026-04-21 | 141xxx713 | 中医四诊 | 患者高血压病史，规律服药后血压控制平稳，纳眠尚可，小便调，大便偏溏。舌质红，苔白，脉弦细。
沈x瑶 | 2026-04-21 | 141xxx713 | 心电图 | 窦性心律，左室高电压，ST-T未见明显异常
```

## 4. 输出登记表和 JSON

Phase 1 完成后，为每个类别输出纯文本登记表和提交用 JSON。登记表可放在当前目录或用户指定目录，常用文件名：

- `门诊病例登记表.txt`
- `手写大病历登记表.txt`
- `门诊病种记录表.txt`
- `住院病种记录表.txt`
- `临床技术记录表.txt`

JSON 可为单条对象或对象数组。字段优先使用以下规范名称；Phase 2 也支持常见别名。

### 门诊病例 / 手写大病历

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

### 门诊病种记录

```json
{
  "department": "心血管内科",
  "patient_name": "张三",
  "visit_date": "2026-02-01",
  "tcm_diagnosis": "眩晕",
  "western_diagnosis": "高血压",
  "visit_type": "初诊",
  "remarks": "以头晕目眩为主要表现..."
}
```

### 住院病种记录

```json
{
  "department": "心血管内科",
  "patient_name": "张三",
  "case_code": "2300000000",
  "visit_date": "2026-02-01",
  "tcm_diagnosis": "眩晕",
  "western_diagnosis": "高血压",
  "inpatient_role": "主管",
  "remarks": "以头晕目眩为主要表现..."
}
```

### 临床技术记录

```json
{
  "department": "心血管内科",
  "patient_name": "张三",
  "case_code": "2300000000",
  "operation_date": "2026-02-01",
  "operation_item": "中医四诊",
  "remarks": "患者高血压病史..."
}
```

---

# Phase 2：网站提交

## 资源布局

根技能包内应包含这些 v1.6 资源：

```text
scripts/
  gp_config.py
  license_check.py
  playwright/
    gp_login.py
    gp_playwright.py
    gp_core.py
    pyarmor_runtime_000000/
agents/
  openai.yaml
```

`gp_login.py`、`gp_playwright.py`、`license_check.py` 和 `gp_config.py` 是可读入口。`gp_core.py` 是受保护实现，包含提交逻辑、License 扣次逻辑和服务器端点；
`gp_login.py`若出现错误可自行修复。

## 环境准备

v1.6 要求使用 Python 3.13。Windows 优先使用 `py -3.13`，如果系统只有 `python` 命令且它指向 3.13，也可以用 `python`。

```bash
py -3.13 -m pip install playwright
py -3.13 -m playwright install chromium
```

验证：

```bash
py -3.13 -c "from playwright.sync_api import sync_playwright; print('Playwright OK')"
```

## License Key

License Key 存在本地明文配置文件：

```text
scripts/.license_key
```

常用命令：

```bash
py -3.13 scripts/license_check.py setup <YOUR_LICENSE_KEY>
py -3.13 scripts/license_check.py path
py -3.13 scripts/license_check.py path --absolute
py -3.13 scripts/license_check.py show
py -3.13 scripts/license_check.py info
py -3.13 scripts/license_check.py clear
```

规则：

- `info` 只查询剩余次数，不扣次。
- `gp_playwright.py` 每提交一条记录前会自动校验并扣次；批量 50 条扣 50 次。
- 出现 `[LICENSE]` 错误时，原样告诉用户错误内容。
- 常见错误：`无效的 License Key`、`调用次数已用完，请联系购买`、`无法连接服务器`。

## 登录流程

登录已从提交脚本中拆出。先运行登录检查，不要直接跑提交：

```bash
py -3.13 scripts/playwright/gp_login.py
```

如果输出 `[LOGIN_REQUIRED]`：

1. 停止继续运行命令。
2. 告诉用户在打开的 Chrome 窗口中手动登录 `gp.itcm.cn`。
3. 用户确认登录完成后，再运行一次 `gp_login.py`。
4. 只有输出 `[LOGIN_READY]` 后，才能运行 `gp_playwright.py`。

`gp_login.py` 会启动或连接带 CDP 的 Chrome，登录状态保存在输出目录下的 `.gp_browser_profile`。提交脚本只连接这个已登录 Chrome；如果会话过期，重新跑登录流程。

可选旧行为：`gp_login.py --wait` 会等待手动登录，并可用 `{outdir}/gp_continue.txt` 触发重检。默认不等待。

## 提交命令

```bash
# 门诊病种 + 临床技术
py -3.13 scripts/playwright/gp_playwright.py \
  --disease disease_records.json \
  --clinical clinical_records.json

# 门诊病例（图片上传）
py -3.13 scripts/playwright/gp_playwright.py \
  --outpatient outpatient_records.json

# 手写大病历（图片上传）
py -3.13 scripts/playwright/gp_playwright.py \
  --handwritten handwritten_records.json

# 住院病种记录
py -3.13 scripts/playwright/gp_playwright.py \
  --inpatient inpatient_records.json

# 只填表不最终提交；仍会扣 License 次数
py -3.13 scripts/playwright/gp_playwright.py \
  --disease test.json --dry-run
```

CLI 参数：

| 参数 | 说明 |
|---|---|
| `--disease PATH` | 门诊病种记录 JSON |
| `--clinical PATH` | 临床技术记录 JSON |
| `--outpatient PATH` | 门诊病例 JSON，带图片上传 |
| `--handwritten PATH` | 手写大病历 JSON，带图片上传 |
| `--inpatient PATH` | 住院病种记录 JSON |
| `--dry-run` | 仅填表单不最终提交，仍扣 License |
| `--outdir PATH` | 输出目录，放截图、结果 JSON、信号文件 |
| `--wait` | 提交完成后等待 `{outdir}/gp_done.txt` 再退出 |
| `--no-wait` | 兼容旧参数；v1.6 默认提交完成即退出 |

## 模块和字段

| 模块 | 路由 | 必填/关键字段 |
|---|---|---|
| 门诊病例 | `/OutpatientCaseRecord/Index` | `department`, `patient_name`, `visit_date`, `image_path` 或 `image_paths` |
| 门诊病种记录 | `/OutpatientRecord/Index` | `department`, `patient_name`, `visit_date`, `tcm_diagnosis`, `western_diagnosis`, `visit_type`, `remarks` |
| 临床技术记录 | `/ClinicalRecord/Index` | `department`, `patient_name`, `case_code`, `operation_date`, `operation_item`, `remarks` |
| 手写大病历 | `/HospitalizationCaseRecord/Index` | 同门诊病例 |
| 住院病种记录 | `/HospitalizationRecord/Index` | `department`, `patient_name`, `case_code` 或 `hospitalization_code`, `visit_date`, `tcm_diagnosis`, `western_diagnosis`, `inpatient_role`（默认 `主管`）, `remarks` |

常见别名：

- `visit_date`：`outpatient_date`, `date`, `OutpatientDate`
- `tcm_diagnosis`：`diagnosis`, `Diagnosis`, `zhongyi_diagnosis`
- `western_diagnosis`：`diagnosis_western`, `DiagnosisWestern`, `xiyi_diagnosis`
- `visit_type`：`outpatient_type`, `OutpatientType`；值可为 `初诊`、`复诊`、`确诊` 或 `0`、`1`、`2`
- `inpatient_role`：`Visit`, `management_type`, `HospitalizationType`；对应网站原始组件 `input[name="Visit"]`，值可为 `未知`、`主管`、`参观` 或 `0`、`1`、`2`，省略时默认 `主管`
- `case_code`：`hospitalization_code`, `medical_record_no`, `record_no`, `clinic_id`, `CaseCode`
- `operation_date`：`date`, `visit_date`, `OperationDate`
- `operation_item`：`operation_name`, `skill_name`, `item`, `OperationItem`
- `remarks`：`remark`, `note`, `Remarks`

## 运行规则

1. 先运行 `license_check.py setup` 保存 License Key，再运行 `gp_login.py`。
2. 只有 `[LOGIN_READY]` 出现后，才运行 `gp_playwright.py`。
3. 提交前再次确认用户已授权提交这些记录。
4. 每次进入模块都要点击目标侧边栏菜单；网站可能保留旧 iframe。
5. 除非用户另说，保持 `学生` 选择不变。
6. 科室通常选择第二个 `请选择` 字段。
7. 活体提交建议每批 4-5 条，便于发现重复或校验问题后及时停止。
8. 遇到校验弹窗、重复提示、缺失字段、表单提交后不关闭等异常，停止并让用户看浏览器。
9. v1.6 默认提交完成后脚本退出、Chrome 保持打开供人工复核；只有显式使用 `--wait` 时才等待 `gp_done.txt`。
