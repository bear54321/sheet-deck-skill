# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 這個 repo 是什麼

Claude Code skill「sheet-deck」的原始碼：製作有演示控制台的網頁動畫簡報。公開在 GitHub `bear54321/sheet-deck-skill`。
- `SKILL.md` 是給**使用這個 skill** 的 Claude 看的說明（範本結構、功能、踩過的坑）；改範本前先讀它，這份 CLAUDE.md 不重複那些內容。
- 這份檔案是給**維護這個 repo** 的人看的。

使用者偏好繁體中文、白話說明；技術名詞第一次出現時用一句話解釋。

## Claude 載入的 skill 就是這個 repo

`~/.claude/skills/sheet-deck` 是指向這個 repo 的捷徑（symlink），在這裡改的內容 Claude 下次載入 skill 就會用到，不需要複製；所以改壞了也會立刻影響使用。不要再放一份手動複製的副本：`scripts/pre-commit` 發現那裡是另一份副本時會擋下 commit。

## 常用指令

沒有建置、套件管理或單元測試；範本是單一 HTML，直接用瀏覽器開。

- commit 前由 `scripts/pre-commit` 自動對要 commit 的 HTML 跑下面兩個檢查，沒過就擋下（每台電腦裝一次：`ln -sf ../../scripts/pre-commit .git/hooks/pre-commit`）。
- AI 請求檢查（改過 PDF 摘要／AI 相關程式後必跑）：
  - 靜態檢查（快）：`python3 scripts/check_ai_calls.py assets/template.html`
  - 實測（headless Chrome 假造兩次 503，確認會重試）：`python3 scripts/check_ai_calls.py --run assets/template.html`
- 存檔鍵名一律來自 `<html data-deck>`（每份簡報唯一，範本保持 `__DECK_ID__`），不能用網址路徑：`python3 scripts/check_deck.py <簡報.html 或資料夾…>` 把關，多個檔案一起給時也檢查 id 重複。
- 預覽：`python3 -m http.server 8799 --bind 127.0.0.1 --directory assets` 後開 `http://localhost:8799/template.html`（`~/Desktop/anime/.claude/launch.json` 有名為 `template` 的同一個設定）。Google 文件來源只有從 `http://localhost` 開才讀得到，`file://` 不行。
- 3D 模型：`python3 scripts/glb2js.py 3d/<名稱>.glb`；壓縮用 Blender 背景執行 `scripts/optimize_model.py`（參數見檔頭說明）。

## template.html 的整體架構

一個約 2200 行的檔案，依序是：`<style>`（介面外殼 → 投影片 → 裝飾動畫 → 版型／風格）、一張封面 `<section class="slide" data-deco="cover">`、控制台 HTML、一個大 `<script>`。

`<script>` 裡的主要流程：
1. **裝飾產生器**：`makeDeco(type,sid)` 產生每頁的 SVG，只畫目前版型（`S.layout`）的那一套插圖：珊瑚 `.g-coral`、街景 `streetDeco()`、墨金 `inkDeco()`、賽博終端機 `cyDeco()`、深色知識圖譜 `grDeco()`、鈷藍格線 `cbDeco()`、復古小誌 `znDeco()`、8-bit 軌道 `obDeco()`、數位金融瑞士風 `ftDeco()`、田野筆記報告風 `fdDeco()`、復古 Windows `wnDeco()`；`<svg data-lay>` 記著畫的是哪個版型，`apply()` 換版型時重畫。`type` 是 `cover` 或 `content`；`sid` 當亂數種子，同一頁每次畫出來一樣。插圖全部用 SVG 程式畫，**不嵌外部圖片**。
2. **狀態**：`DEF` 是預設值，`S` 是目前設定（存 `localStorage[KEY+':set']`），`EDITS` 是使用者改過的文字（存 `KEY+':ed'`），`KEY='sheet-deck:'+location.pathname`。AI 金鑰另存 `sheet-deck:key:<provider>`，不放進 `S`，所以不會被匯出。
3. **頁面管理**：`TPL` 存原始頁面；新增頁記在 `S.added[sid]={from}`，由 `makeSlide()` 重建（`from` 可為 `blank`、`live:srcN`、`doc:srcN`、`pdf:id` 或既有頁的 sid）；`prepSlide()` 填裝飾並套用 `EDITS`；`applyOrder()` 依 `S.order` 排序。
4. **`apply()`**：把 `S` 套到畫面（版型、風格、主色、動畫開關 `body[data-anim]`、小圖案開關 `body[data-leaf]`）。
5. 其後是資料來源（試算表 JSONP、Google 文件）、ECharts 圖表、three.js 3D、PDF 摘要（`httpJSON()` 包 `httpJSONOnce()`）、3D 空間模式、匯出。

改程式時要留意：
- **存檔格式**：`S`、`EDITS` 的格式改了，就在 `MIGRATIONS` 最後加一步（不改舊步驟、不在別處寫轉換），並在 `scripts/test_migrate.py` 加一個舊存檔範例；由 `test_migrate.py`（commit 前自動跑）把關。
- **動畫**：只在 `.slide.active` 時播放；新增的動畫要加進 `.static`／`.slide.leaving`／`body[data-anim=off]` 的停用規則。裝飾要加 `.leaf` class，「隱藏小圖案」才關得掉。
- **顏色**：用 `--th-*` 變數或既有的顏色 class（見 SKILL.md「版型與風格分開」），不要寫死，否則換風格時不會變色。

## 授權

- 工具列 15 種風格取材自 Lemo-Opuscar（CC BY-NC 4.0，不可商用），細節在 `NOTICE.md`；新增外部素材或套件時要更新 `NOTICE.md`。
- 這個 repo 是公開的：不要把來源不明的圖片、PPT 範本插畫或 3D 模型放進來。`.gitignore` 已排除 `*.glb`、`*.glb.js`。
