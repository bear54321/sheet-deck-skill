---
name: sheet-deck
description: 製作「網頁動畫簡報＋演示控制台」：單一 HTML，左側頁面縮圖、右側屬性面板（切換動畫、高亮樣式、主色調）、頁面新增／剪下／複製／貼上、文字大小顏色與文字框；可接 Google 試算表即時資料與 ECharts 圖表；可放 three.js 3D 模型（飛行角色、跳舞角色、360° 文物展示）、嵌入 Unity WebGL；有「3D 空間」播放模式；可匯出 HTML、純簡報 HTML、PDF、PPTX。只要使用者想做有編輯介面的網頁簡報、要把試算表資料做成會更新的簡報或圖表、要在簡報裡放 3D 模型或 Unity 遊戲、或要把實物照片做成 3D 展示，即使沒說「skill」也要使用；使用者只要 PowerPoint 檔時不適用。
---

# 網頁動畫簡報＋演示控制台（sheet-deck）

新簡報一律從 `assets/template.html` 複製開始改，不要從零寫：裡面的編輯器、資料連線、圖表、3D、Unity、匯出、3D 空間模式都已經在 Chrome 實測過，而且踩過的坑（見文末）都修好了。

使用者偏好繁體中文、白話說明；技術名詞第一次出現時用一句話解釋。

## 工作流程

1. **確認內容與資料**：問清楚主題、頁數、每頁要放什麼；若要接資料，請使用者提供 Google 試算表連結（要「知道連結的人可檢視」），以及要用哪個工作表分頁（網址裡的 `gid=`）。查不到的事實要問，不要編。
2. **建資料夾**：`<簡報資料夾>/index.html`（複製 template）、`開啟簡報.command`（複製 `assets/開啟簡報.command`）、需要 3D 時建 `3d/`、需要 Unity 時建 `unity/`。
3. **改內容**：見下方「範本結構」。改完用瀏覽器實際打開檢查（console 不能有錯誤、每頁截圖看一次），修完才回報。
4. **回報**：告訴使用者檔案位置、怎麼開、哪些沒驗證到。

## 範本結構（template.html）

- 舞台 1920×1080，等比縮放。每頁是 `<section class="slide" data-sid="s1">`，進場動畫用 `.a` 加 `style="--d:.3s"` 控制延遲。
- 可編輯文字加 `data-ed`；使用者在畫面上改的字存在 `localStorage`（key 以網址路徑區分），匯出 HTML 時會烘進檔案。
- 設定預設值在 `const DEF={...}`：
  - `src1`、`src2`、`src3`：Google 試算表網址（範本是空的，要填）。也可以在右側面板「資料來源管理」新增。
  - `charts:[...]`：預設圖表（類型、資料來源、X 欄、Y 欄、位置大小）。
  - `flyers:[...]`：預設 3D 角色（範本是空的）。
  - `accent`：主色。
- **資料頁**：`<section class="slide live" data-src="1">` 會讀 `src1`，自動取**第一個文字欄當名稱、最後一個數字欄當數值**，產生 KPI 卡、排行長條、圓環圖。標題文字照試算表內容改。
- **圖表**：使用者可用「📊 插入圖表」自己加（長條、折線、面積、圓餅、圓環、散佈、雷達、漏斗、橫條），可拖曳、改欄位。時間格式（如 `5:32`）與金額會自動轉數字，「總計」列會被排除。
- 風格是扁平珊瑚色系（白底、#DC9A8B、#E9A576、#CDA4A4、#4F6B6B、對話框、時鐘裝飾），裝飾由 `makeDeco` 依 `data-deco` 產生。換風格時改 CSS 變數與 `makeDeco`。

## 3D 模型

細節見 `references/3d-models.md`。重點：

- 模型放 `3d/<名稱>.glb`，再用 `python3 scripts/glb2js.py 3d/<名稱>.glb` 包成 `3d/<名稱>.glb.js`。這樣直接雙擊 HTML（`file://`）也能載入。
- 檔案太大（>5 MB）先壓：`Blender -b --python scripts/optimize_model.py -- 輸入 輸出.glb 最多面數 貼圖邊長`。
- 範本內建四種：`parrot`（飛行）、`girl`（跳舞，需有動畫 clip）、`porcelain`、`globe`（360° 展示）。新模型要在 `const MODELS={...}` 加一筆（`kind`: `fly` / `dance` / `showcase`），並在 `#flyAddBox` 加按鈕。
- 實物照片轉 3D：`references/photo-to-3d.md`（iPhone 拍 60–100 張 → Mac 內建 Object Capture → Blender）。
- 模型來源與授權要查清楚並寫在頁面上（例如 Sketchfab 的 CC0／CC-BY）。

## Unity WebGL

細節見 `references/unity.md`。把 `assets/unity/` 三個檔案放進 Unity 專案，用選單 Tools → 簡報 → Build WebGL 輸出到 `<簡報資料夾>/unity/Build`，簡報用「🎮 插入 Unity」。Unity 需要用 `開啟簡報.command`（本機伺服器）開，`file://` 不行。

## 3D 空間模式

工具列「🌌 3D 空間」：頁面漂浮在空間中，鏡頭飛行換頁；O 鍵全貌（所有頁面排成弧形牆）、點頁面直接前往、Esc 離開。不需要額外設定。

## 匯出

匯出選單有四種：HTML（保留編輯結果）、純簡報 HTML（無控制台）、PDF（列印）、PPTX（文字可編輯、圖表為原生 PowerPoint 圖表）。注意：匯出的 HTML 若放到別的資料夾，`3d/`、`unity/` 要一起帶走。

## 檢查

- 用本機伺服器開（`python3 -m http.server` 或 `開啟簡報.command`），逐頁看、開 console 看錯誤。
- 有資料的頁面要確認數字跟試算表一致。
- 有 3D 的頁面要確認模型有出現、大小位置合理；360° 展示要試拖曳。
- 3D 空間模式要試：全貌、點頁面、改視窗大小。

## 踩過的坑（範本已處理，改程式時不要改壞）

- Google 試算表用 JSONP（`gviz/tq?tqx=out:json;responseHandler:...`）讀，才能在 `file://` 運作；`fetch` 會被擋。
- ECharts 用 cdnjs 5.5.0（5.5.1 不存在）。
- 3D 空間模式**不要**用 CSS 3D（`preserve-3d` 或傾斜的 `matrix3d`）畫頁面：Chrome 在部分 Mac 上會把傾斜的網頁元素切成碎條或只畫一部分（縮放、改視窗大小時最明顯）。範本做法是：飛行與全貌用 WebGL 畫頁面截圖（html2canvas），停下來時才顯示正對螢幕、不傾斜的真實頁面。
- 跳舞角色的大小要用動畫姿勢下的蒙皮外框計算（`Box3.setFromObject(model,true)`），否則會過大被裁切。
- 360° 展示的 canvas 尺寸要用 `style.setProperty(...,'important')` 設，否則被 CSS 蓋掉。
