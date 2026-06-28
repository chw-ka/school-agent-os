# CLAUDE.md — primary-steam-tasting-p5

## 專案概覽

小五 STEAM 體驗課（M5StickS3），由 `Training/primary-staff-training/` 教師 PD 分享會改編而來。
目標對象為小學五年級學生（約 10–11 歲），課堂由班主任 / STEAM 老師帶領。

**關鍵差異（vs 教師 PD）：**

| | 教師 PD (`primary-staff-training`) | 小五課堂（本專案） |
|--|-----------------------------------|-------------------|
| 對象 | 3 人一組老師 | 學生（個人或 2 人一組） |
| 開場 | SW 工程師自我介紹 | 簡化：「今日玩 AI 硬件！」 |
| Task 1 | 扮小學生 + 錄音合規說明 | 直接玩小智，老師預先說明 |
| 概念 | MCP、业界唔寫 code | 簡化三層 AI（咪、腦、嘴） |
| Task 3 | Google Classroom + Vibe Coding | 老師派 prompt 卡，跟做 |

---

## 文件結構

| 路徑 | 用途 |
|------|------|
| `docs/lesson-plan-p5-steam-tasting.md` | 完整教案（教師用） |
| `docs/participant-handout.md` | 學生跟做工作紙 |
| `docs/ppt-slides-gemini-prompts.md` | 投影片 prompt 定義（待填） |
| `docs/prompt-card.md` | 學生 Task 3 prompt 卡（可印） |

## 可共用資源

- 硬件燒錄流程：`../primary-staff-training/m5sticks3-clone/`
- PPT 生成腳本：`../primary-staff-training/scripts/`
- 裝置截圖素材：`../primary-staff-training/docs/screen-captures/`
- 設備手冊：`../primary-staff-training/docs/M5StickS3-Device-Manual.pdf`

---

## 環境設定

與 `primary-staff-training` 共用 `.env`（`GEMINI_API_KEY`）及 `config/`。
若獨立運行 PPT 生成，複製 `.env` 及 `config/` 至本目錄。
