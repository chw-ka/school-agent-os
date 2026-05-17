# School-Agent-OS

基於 **Agentic Infrastructure** 的校園自動化系統。核心理念：**基礎設施大於 Prompt**，將行政與教學功能拆解為可重用的「微服務工具 (Shared Tools)」。

## Repo Structure
- `.cursorrules`: 根目錄憲法（工作原則、格式規範、隱私）
- `shared-tools/`: 可重用 Python 工具（Skills）
- `Subjects/`: 教學區（依科目/級別分資料與流程）
- `Administrative/`: 行政區（依功能分資料與流程）
- `templates/`: 學校標準 Word/PDF 範本

## Quick Start (Formatter Tool)
1. 建立並啟用 venv（建議）：
   - macOS/Linux:
     - `python3 -m venv .venv`
     - `source .venv/bin/activate`
2. 安裝依賴：
   - `pip install -r requirements.txt`
3. 準備 Word 範本：
   - 參考 `templates/README.md` 放入 `templates/exam_template.docx`
4. 產生試卷：
   - `python shared-tools/paper-formatter/exam_generator.py --help`

