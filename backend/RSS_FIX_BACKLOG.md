# RSS & Translation Backlog

## 🛠️ [RSS-001] RSS 翻譯流程與環境相容性修正
**Created:** 2026-02-21
**Current Status:** PARTIALLY RESOLVED

### 📝 Description
RSS 抓取機制目前雖然穩定，但在翻譯與實體提取階段存在環境依賴問題（spaCy 缺失）與 API 成本限制（Anthropic Key）。目前需要將翻譯流程從依賴外部收費 API 轉向更靈活的自動化批次處理。

### ✅ Completed (2026-02-21)
- [x] **Entity Extractor Fallback**: 實作 `F1EntityExtractor` 的 Regex 備援機制，解決 `spaCy` 缺失導致的 `ImportError`。
- [x] **Data Backfill**: 利用 CLI AI 手動補齊今日 (02-21) 全部 117 篇 F1 新聞的繁體中文翻譯 (`zh-TW`)。
- [x] **Model Verification**: 確認 `Translation` 模型與 `Article` 關聯正確，且前端能正常抓取 `PUBLISHED` 狀態的中文內容。

### 🚀 Roadmap & Next Steps
- [ ] **Automated Translation CLI**: 建立一個 management command，能自動抓取「無中文翻譯」的文章並調用 CLI/Local AI 翻譯。
- [ ] **Celery Task Integration**: 將翻譯邏輯整合進 Celery 異步任務，在 `fetch_news` 完成後自動觸發。
- [ ] **Translation Dashboard**: 在後台增加一個簡易界面，顯示翻譯進度與重試失敗的任務。
- [ ] **Term Consistency**: 更新 `ClaudeTranslator` 的術語表至本地數據庫，確保非 Claude 翻譯時也能維持術語一致性（如：MGU-K, DRS）。

---

## 🏎️ Today's Content Summary (2026-02-21)
- Total Articles Fetched: 117
- Translations Backfilled: 117 (zh-TW)
- Key Themes: Ferrari Dominance (Leclerc -0.8s), Aston Martin-Honda PU Crisis, Mercedes Aero Innovations.
