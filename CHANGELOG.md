# Changelog

All notable changes to gp-outpatient-upload.

---

## [v1.1] — 2026-06-21

### Added
- **免登录功能**：浏览器启动后自动检测已保存的登录状态，无需每次手动登录。首次使用仍需登录一次，之后自动复用。

---

## [v1.0] — 2026-06-20

### Added
- **五类登记模块全覆盖**：门诊病例、手写大病历、门诊病种记录、住院病种记录、临床技术记录
- **Phase 1 数据准备工作流**：图片分类 → 信息提取 → 登记表生成 → 自动补全 → 用户验证
- **Phase 2 浏览器自动化**：Playwright Python 有头 Chromium 自动填表提交
- **自动补全规则**：中医病名 → 西医病名映射、中医四诊现病史/舌脉备注生成
- **多图同病例分组**：连续编号自动分组，支持每病例多页图片合并为一条记录
- **License 验证系统**：按条扣费，服务端配额管理，加密客户端
- **四套登记表模板**：嵌入技能，自包含，不依赖外部文件
- **使用教程**：Markdown + Word 双格式，含配图、提示词模板、完整对话示例

### Routes
| 模块 | Route |
|------|-------|
| 门诊病历 | `/OutpatientCaseRecord/Index` |
| 手写大病历 | `/HospitalizationCaseRecord/Index` |
| 门诊病种记录 | `/OutpatientRecord/Index` |
| 住院病种记录 | `/HospitalizationRecord/Index` |
| 临床技术记录 | `/ClinicalRecord/Index` |

### Infrastructure
- Playwright Python 浏览器自动化（替代 Node REPL）
- 信号文件驱动的交互式登录（`gp_continue.txt` / `gp_done.txt`）
- PyArmor 客户端代码加密
- FastAPI 远程 License 服务（腾讯云 `111.229.30.168:8080`）
- SQLite 数据库（license / usage_logs / admin_config）
- Web 管理后台（`admin.html`）
- 按条扣费模式（dry-run 同样扣费）
