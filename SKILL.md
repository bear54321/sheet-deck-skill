---
name: sheet-deck
description: 製作「網頁動畫簡報＋演示控制台」：單一 HTML，左側頁面縮圖、右側屬性面板（切換動畫、高亮樣式、主色調）、頁面新增／剪下／複製／貼上、文字大小顏色與文字框；可接 Google 試算表即時資料與 ECharts 圖表；可放 three.js 3D 模型（飛行角色、跳舞角色、360° 文物展示）；有「3D 空間」播放模式；可匯出 HTML、純簡報 HTML、PDF、PPTX。只要使用者想做有編輯介面的網頁簡報、要把試算表資料做成會更新的簡報或圖表、要在簡報裡放 3D 模型、或要把實物照片做成 3D 展示，即使沒說「skill」也要使用；使用者只要 PowerPoint 檔時不適用。
---

# 網頁動畫簡報＋演示控制台（sheet-deck）

新簡報一律從 `assets/template.html` 複製開始改，不要從零寫：裡面的編輯器、資料連線、圖表、3D、PDF 摘要、匯出、3D 空間模式都已經在 Chrome 實測過，而且踩過的坑（見文末）都修好了。

使用者偏好繁體中文、白話說明；技術名詞第一次出現時用一句話解釋。

## 工作流程

1. **確認內容與資料**：問清楚主題、頁數、每頁要放什麼；若要接資料，請使用者提供 Google 試算表連結（要「知道連結的人可檢視」），以及要用哪個工作表分頁（網址裡的 `gid=`）。查不到的事實要問，不要編。
   開工前固定用一次提問（有選項的工具就用選項）問這三題，各附推薦答案；使用者已經講過的就不要再問：
   - **用途**：說服（要對方做決定）／傳達資訊（報告進度、數據）／教學（教會一個觀念）。
   - **長度**：簡短 5–7 頁／標準 8–12 頁／詳細 13–18 頁。
   - **版型**：依主題推薦一種，並說一句為什麼（見下表）。
2. **先給計畫，等確認再做**：每頁列出「標題、一句話重點、用什麼呈現（大數字、KPI 卡、圖表、條列、引言）、進場順序」，再加一段視覺方向（版型、主色、哪幾頁是留白的「呼吸頁」）。計畫裡的假設要寫出來讓使用者確認，例如「3,000 是個人單月、11,000 是團隊單月」。使用者說可以才開始做，避免整份重做。
3. **建資料夾**：`<簡報資料夾>/index.html`（複製 template，並把 `<html data-deck="__DECK_ID__">` 改成資料夾名稱，再跑 `python3 scripts/check_deck.py <簡報資料夾>`）、`開啟簡報.command`（複製 `assets/開啟簡報.command`）、需要 3D 時建 `3d/`。
4. **改內容**：見下方「範本結構」。要預設某個版型，在 `<html>` 加 `data-settings='{"v":6,"theme":"版型","layout":"版型","themeSet":1,"accent":"該版型的主色"}'`（`v` 一定要寫，否則舊存檔轉換會把版型改回 street；主色見 `THEMES`）。改完用瀏覽器實際打開檢查（console 不能有錯誤、每頁截圖看一次），修完才回報。
5. **回報**：告訴使用者檔案位置、怎麼開、哪些沒驗證到。

### 版型怎麼推薦

| 版型（`S.layout`） | 適合 |
|---|---|
| `street` 青綠街景 | 預設、親切的內部分享、社區或在地主題 |
| `coral` 珊瑚扁平 | 輕鬆、溫和的報告 |
| `inkgold` 墨金 | 正式演講、策略、要有份量的主題 |
| `cyber` 賽博終端機 | 工程、開發流程、AI 與技術分享 |
| `graph` 深色知識圖譜 | 研究、知識整理、概念之間的關係 |
| `cobalt` 鈷藍格線 | 商業提案、數據論證、規劃書 |
| `zine` 復古小誌 | 故事、社區、人物採訪、活動回顧 |
| `orbit` 8-bit 軌道 | 遊戲、興趣、輕鬆的科普、年輕聽眾 |
| `fintech` 數位金融瑞士風 | 財務、KPI、成長數字為主角 |
| `fieldnotes` 田野筆記 | 調查報告、使用者研究、會議紀要 |
| `win95` 復古 Windows | 懷舊、科技史、輕鬆幽默的分享 |

## 範本結構（template.html）

- 範本只有**一張空白封面頁**（`data-deco="cover"`，標題、副標題預留位置），沒有範例資料或圖表；直接用瀏覽器打開就是一份空白簡報。資料頁、文件頁、PDF 摘要頁由 `livePgHTML()`／`docPgHTML()`／`pdfPgHTML()` 產生，要預先放資料頁時照下方「資料頁」的寫法加 `<section>`。
- 舞台 1920×1080，等比縮放。每頁是 `<section class="slide" data-sid="s1">`，進場動畫用 `.a` 加 `style="--d:.3s"` 控制延遲。
- 可編輯文字加 `data-ed`；使用者在畫面上改的字存在 `localStorage`（鍵名來自 `<html data-deck>`，每份簡報要不一樣；匯出的 HTML 會自動換一個新 id），匯出 HTML 時會烘進檔案。
- 設定預設值在 `const DEF={...}`：
  - `src1`、`src2`、`src3`：Google 試算表網址（範本是空的，要填）。也可以在右側面板「資料來源管理」新增。
  - `charts:[...]`：預設圖表（類型、資料來源、X 欄、Y 欄、位置大小）。範本是空的。
  - `flyers:[...]`：預設 3D 角色（範本是空的）。
  - `accent`：主色。
- **資料頁**：`<section class="slide live" data-src="1">` 會讀 `src1`，自動取**第一個文字欄當名稱、最後一個數字欄當數值**（使用者可在「格式」分頁的「本頁資料來源」改選名稱欄／數值欄，存在 `S.pageCols[sid]`），產生 KPI 卡、排行長條、圓環圖。標題文字照試算表內容改。使用者也能在「文件」分頁按試算表來源那一列的「＋」新增資料頁（`S.added[sid]={from:'live:srcN',t:標題}`）。
- **文件頁（Google 文件）**：在「資料來源管理」貼 Google 文件連結（`/document/d/…`）會問要不要新增一頁 `<section class="slide docpg" data-doc="srcN">`（之後也能按來源那一列的「＋」再新增）：第一行當標題、其餘段落排進卡片（字太多會自動縮小、分兩欄），每 30 秒跟著文件更新。右側「本頁資料來源」有**摘要／全文**切換（預設摘要）：摘要不靠 AI，是取每段第一句、最多 5 點（`docSummary()`），頁尾會註明「自動擷取」。**只有用 `開啟簡報.command`（http://localhost）開才讀得到**，雙擊開檔會顯示提示。圖表、資料頁只用試算表來源（`sheetKeys()`）。
- **介面（仿 Keynote）**：上方工具列分三區：左＝目錄開關、頁數；中＝播放｜新增頁、文字、圖表、PDF 摘要、3D 角色（下拉選單 `#flyAddBox`）｜3D 空間；右＝更新資料、匯出、檢查器分頁。右側面板分三個分頁 `.ptab`：**格式**（選到物件時只顯示該物件設定，沒選時顯示「幻燈片外觀」`#slideFmt`）、**動畫**、**文件**（資料來源、AI 金鑰、重置）。再按一次目前分頁會收起面板。新增功能時把按鈕放進工具列中區、設定放進對應分頁，不要再加一排按鈕。
- **PDF 摘要頁**：工具列「PDF 摘要」→ 選 PDF → 用使用者自己的金鑰請 AI 讀 PDF，回傳 JSON `title／subtitle／points／takeaway`，新增 `<section class="slide docpg pdfpg" data-pdf="id">`，內容存在 `S.pdfs[id]`（會跟著匯出）。支援三家，在「文件」分頁選（貼金鑰時依開頭自動判斷：`sk-ant-`＝Claude、`AIza`／`AQ.`＝Gemini、其他 `sk-`＝OpenAI）：
  - **Claude**：Anthropic JS SDK（jsDelivr `@anthropic-ai/sdk@1.6.0/+esm`，`dangerouslyAllowBrowser: true`），PDF 用 base64 `document`，`output_config.format` JSON schema；預設 `claude-opus-5-5`（effort medium，加 `fallbacks:'default'`；Haiku 不加）。
  - **Gemini**：REST `v1beta/models/{model}:generateContent`，`inline_data` PDF＋`responseSchema`（大寫型別）。上限約 19 MB。
  - **OpenAI**：REST `/v1/chat/completions`，`type:'file'` 的 PDF＋`response_format: json_schema`。
  - Gemini／OpenAI 的模型清單用金鑰即時讀取（`/models`），存在 localStorage，不寫死型號。
  - 金鑰存 `localStorage['sheet-deck:key:<claude|gemini|openai>']`，**不放進 `S`**，所以不會被匯出。三家 API 都允許瀏覽器直接呼叫，`file://` 也能用。
- **圖表**：使用者可用「📊 插入圖表」自己加（長條、折線、面積、圓餅、圓環、散佈、雷達、漏斗、橫條），可拖曳、改欄位。時間格式（如 `5:32`）與金額會自動轉數字，「總計」列會被排除。
- 珊瑚扁平風格是（白底、#DC9A8B、#E9A576、#CDA4A4、#4F6B6B、對話框、時鐘裝飾），裝飾由 `makeDeco` 依 `data-deco` 產生。
- **版型與風格分開**（工具列「🎨 風格」選單分兩區）：
  - **版型**（`S.layout`，`<html data-layout>`）決定構圖：`street`＝青綠街景版型（預設：外框＋內頁，封面有樹枝、草叢、人行道、房子，內頁（含新增頁）是縮小版的同一個場景，樹枝會長出來並隨風輕擺、草叢會長高，由 `streetDeco()` 用 SVG 畫，沒有外部圖片）；`coral`＝珊瑚扁平版型（`makeDeco()` 的色塊、對話框、時鐘）；`inkgold`＝墨金版型（近黑底、單一強調色、大字標題靠左、等寬字型標籤、卡片上緣一條強調色；插圖由 `inkDeco()` 畫：角落裁切記號；封面有格線、斜向掃光、右上「星盤」（同心圓、輻射線、黃金螺線、反轉的刻度環、慢轉的虛線外環、繞行小點、上下掃描的線）、漂浮的金色微粒、閃爍點陣；內頁有右上小星盤、點陣、微粒、左側跑光直線、右下角圓弧、底部刻度尺與移動光點，標題下有一條長出來的強調色短線。線條進場用 `.draw`；循環動畫（`.igr/.igr2/.igo/.igp/.igdust/.igtw/.igtr/.igsw/.igsc`）只在 `.slide.active` 播，縮圖、離場、關閉動畫時停住。強調色跟著主色調 `var(--accent)`）。另外五種：`cyber`＝賽博終端機（終端機視窗標題列、逐行打出的程式碼欄、閃爍游標、往下掃的光帶、掃描線）；`graph`＝深色知識圖譜（柔光、知識圖譜節點與連線、擴散光圈、沿線跑的訊號）；`cobalt`＝鈷藍格線（米紙格線、粗細雙規線、四邊刻度、轉動的對位十字、一格一格跳的方框、閃爍的填色方塊、封面大圓盤）；`zine`＝復古小誌（撕邊紙、會晃的紙膠帶、蓋章、轉動的波浪貼紙、網點、手繪線與循環重畫的星星、彈出的剪報拼字塊、飄落紙屑、剪刀沿虛線前進、膠片條）；`orbit`＝8-bit 軌道（兩層視差星空、像素行星與光環、小行星帶、兩顆反向繞行的衛星、雷達波、往上射雷射的飛船、橫越的飛碟、翻轉的寶石、流星、愛心與能量格 HUD）。再三種：`fintech`＝數位金融瑞士風（米白底 12 欄細格線、右側黑色面板的長條圖與走勢線、螢光綠標記、底部跑馬燈）；`fieldnotes`＝田野筆記報告風（筆記本橫線與粉紅邊線、浮動的圓角粉彩卡、循環重畫的留存曲線與手繪圈、圓環圖、輪流打勾的清單、擺動的便利貼、右緣索引標籤、咖啡杯印、邊走邊畫線的鉛筆、副標題螢光筆）；`win95`＝復古 Windows（藍綠桌面、依序打開的三層視窗、輪流選取的桌面圖示、紙張飛過的複製對話框與翻轉沙漏、進度條、工作列按鈕、定時跳出的提示泡泡、移動的滑鼠游標；內頁有選單列反白、上下捲動的捲軸）。插圖分別由 `cyDeco()`／`grDeco()`／`cbDeco()`／`znDeco()`／`obDeco()`／`ftDeco()`／`fdDeco()`／`wnDeco()` 畫。**每頁的 SVG 只畫目前版型的插圖**（`<svg data-lay=版型>`），換版型時 `apply()` 發現 `data-lay` 不同就重畫；新增版型要在 `makeDeco()` 的 `DF` 加上它的函式。版型清單在 `LAYOUTS`，讀版型一律用 `layoutOf(S.layout)`，不要再寫 `S.layout==='coral'?…` 這種二選一。這六種都是重寫的原創程式碼，沒有複製 OpenDesign 或其他範本的 CSS／HTML（參考來源見 `NOTICE.md`）；新增版型也要自己寫。版型專屬的標題樣式寫成 `:root[data-layout=street] …`。
  - **風格**（`S.theme`，`<html data-theme>`）只換顏色、字體、質感，套在目前的版型上：15 種取材自 Lemo-Opuscar 風格庫（CC BY-NC 4.0，商用要另外確認）。選版型會把風格重設成該版型原本的配色（`street`／`coral` 本身也是 `THEMES` 項目）。
  - 做法是換 `--th-*` 變數：通用規則寫成 `:root:not([data-theme=coral]) …`；街景插圖顏色用 class（`.stf` 外框、`.lc0-4` 葉草、`.bk` 樹枝、`.stw/.stt` 人行道、`.bd1-7` 房子），風格沒指定時由 `--th-h`、`--th-d1…d5` 推出；珊瑚圖形用 `.dk1`～`.dk5`、`.dkf`。圖表文字與格線用 `CI()`、色盤用 `chartPal()`。新增元件時若寫死顏色，記得改成 `--th-*`。
  - 瀏覽器記住的舊設定若沒有自己選過（`S.themeSet`），開啟時會改用目前的預設。

## 講者備忘稿與講者模式

- **備忘稿**：右側「格式」分頁（沒選物件時）最上面的「講者備忘稿」，每頁一段純文字，存在 `S.notes[頁 id]`，跟著設定一起存檔、匯出 HTML；匯出 PPTX 時會放進每頁的 PowerPoint 備忘稿。做簡報時，若計畫裡有每頁要講的話，就預先寫進 `data-settings` 的 `notes`（鍵是頁 id，例如 `s1`）。
- **講者模式**：工具列「講者」或按 **P**，另開一個視窗：目前頁與下一頁的縮圖、可直接編輯的備忘稿、計時器（暫停／歸零）和現在時間。兩個視窗都能換頁（按鈕、方向鍵、空白鍵），會互相同步；「在主視窗播放」切換主視窗成播放模式。純簡報 HTML 也能按 P 開，備忘稿唯讀。
- 用法：把主視窗拖到投影機那個螢幕播放，講者視窗留在自己的筆電。瀏覽器若擋住彈出視窗，要先允許這個網頁開新視窗。
- 講者視窗的頁面是靜態複本；圖表會換成當下畫面的圖片，3D 角色不會顯示。

## 3D 模型

細節見 `references/3d-models.md`。重點：

- 模型放 `3d/<名稱>.glb`，再用 `python3 scripts/glb2js.py 3d/<名稱>.glb` 包成 `3d/<名稱>.glb.js`。這樣直接雙擊 HTML（`file://`）也能載入。
- 檔案太大（>5 MB）先壓：`Blender -b --python scripts/optimize_model.py -- 輸入 輸出.glb 最多面數 貼圖邊長`。
- 「3D 角色」選單只放「📦 匯入 3D 模型」與使用者匯入過的模型；內建的 `parrot`、`girl`、`porcelain`、`globe` 已從選單移除（`MODELS` 裡的定義保留，舊簡報已放上的角色照常顯示）。要預先放模型給使用者，就在 `S.flyers` 指定 `model`，或請使用者用匯入功能。
- **使用者自己的 3D 模型（GLB 或 FBX，建議 GLB）**：工具列「3D 角色」→「📦 匯入 3D 模型」。`parseModel()` 依檔頭判斷：GLB 用 `GLTFLoader`、FBX 用 `FBXLoader`；有動畫的當跳舞角色（可選動畫），沒動畫的做 360° 展示。檔案存在 IndexedDB `sheet-deck-models`，`S.models3d[id]` 記名稱與種類，模型鍵是 `fbx:<id>`；匯出 HTML 時內嵌在 `data-fbx`，換電腦也能開。匯入時會把太亮的 Phong 材質調暗（`fbxSoften`，避免臉部反光）。角色動作可選「🎲 隨機」（每 5 秒以上換一個），也能用「＋ 從其他 FBX 加入動作」合併同骨架的動作檔（存成 `S.models3d[id].extra`）。編輯時可直接拖曳跳舞角色改位置（`f.x`／`f.y`）；360° 展示按物件是旋轉、按周圍背景是移動整個展示框（`f.box`）。貼圖若是 FBX 外部檔案會讀不到（只會顯示顏色），請在 Blender 用「嵌入貼圖」匯出，或改用 GLB。
- 實物照片轉 3D：`references/photo-to-3d.md`（iPhone 拍 60–100 張 → Mac 內建 Object Capture → Blender）。
- 模型來源與授權要查清楚並寫在頁面上（例如 Sketchfab 的 CC0／CC-BY）。

## 3D 空間模式

工具列「🌌 3D 空間」：頁面漂浮在空間中，鏡頭飛行換頁；O 鍵全貌（所有頁面排成弧形牆）、點頁面直接前往、Esc 離開。不需要額外設定。

## 匯出

匯出選單有四種：HTML（保留編輯結果）、純簡報 HTML（無控制台）、PDF（列印）、PPTX（文字可編輯、圖表為原生 PowerPoint 圖表）。注意：匯出的 HTML 若放到別的資料夾，`3d/` 要一起帶走。

## 檢查

- 用本機伺服器開（`python3 -m http.server` 或 `開啟簡報.command`），逐頁看、開 console 看錯誤。
- 有資料的頁面要確認數字跟試算表一致。
- 有 3D 的頁面要確認模型有出現、大小位置合理；360° 展示要試拖曳。
- 3D 空間模式要試：全貌、點頁面、改視窗大小。

## 踩過的坑（範本已處理，改程式時不要改壞）

改版型、插圖或 `data-settings` 後跑 `python3 scripts/check_deco.py <簡報.html>`：下面插圖相關的幾條（`url(#id)`、線寬屬性、標題動畫、`v`）和程式語法都由它自動檢查。

- AI 請求（PDF 摘要）一律經過 `httpJSON()`，它會在 5xx（例如 Gemini 503「high demand」）時自動重試；Claude 走 SDK，不能設 `maxRetries:0`。由 `python3 scripts/check_ai_calls.py --run <簡報>.html` 把關（靜態檢查＋用 headless Chrome 假造兩次 503 實測），改過 AI 相關程式後要跑。

- Google 試算表用 JSONP（`gviz/tq?tqx=out:json;responseHandler:...`）讀，才能在 `file://` 運作；`fetch` 會被擋。
- Google 文件沒有 gviz/JSONP，只能 `fetch('…/document/d/ID/export?format=txt')`：從 `http://localhost` 可以（Google 回 `Access-Control-Allow-Origin: *`），從 `file://` 一定失敗。文件連結也符合 `sheetId()` 的格式，判斷來源類型要先用 `isDocUrl()`。
- ECharts 用 cdnjs 5.5.0（5.5.1 不存在）。
- 3D 空間模式的頁面截圖（一律用 `snapEl()`，每頁約 0.2 秒；直接呼叫 html2canvas 會複製整份文件，一頁 2 秒以上。截圖會短暫卡住畫面）一律在起飛前做完（顯示「準備頁面中」），存進 IndexedDB `sheet-deck-snaps`，快取鑰匙排除頁尾「更新於」時間；WebGL 解析度上限 1.25 倍，只在鏡頭或頁面移動時重畫；背景裝飾畫在 WebGL 裡，不要用網頁元素每格更新。
- 3D 空間模式**不要**用 CSS 3D（`preserve-3d` 或傾斜的 `matrix3d`）畫頁面：Chrome 在部分 Mac 上會把傾斜的網頁元素切成碎條或只畫一部分（縮放、改視窗大小時最明顯）。範本做法是：飛行與全貌用 WebGL 畫頁面截圖（html2canvas），停下來時才顯示正對螢幕、不傾斜的真實頁面。
- 插圖**不要用 `id` 參照的 SVG 漸層、濾鏡或 `<use>`**（`fill="url(#…)"`）：左側縮圖會複製出一模一樣的 id，瀏覽器會抓到縮圖裡那一份；播放時縮圖被隱藏，漸層就跟著消失。要柔光或漸層就疊幾層半透明的圖形（例如 `grDeco()` 的 `glow`）。也不要用 CSS `filter: blur()`，縮圖與 3D 空間的截圖（html2canvas）畫不出來。
- 要繞著某點轉的 SVG 群組（例如 8-bit 行星的衛星），**位置、傾斜、旋轉要寫在同一個 CSS `transform`**（`.oborbit`：`translate(var(--cx),var(--cy)) … rotate()`）。外層用 `transform` 屬性定位、內層再用 CSS 旋轉的話，`transform-box:view-box` 的轉軸會跑到畫面左上角，東西會劃過整個畫面。
- 不要直接改 `.hd h2`／`.hd p` 的 `animation`：它們有 `.a` 進場淡入，蓋掉就永遠是透明的。要加效果就畫在 `::before`／`::after`。
- 插圖元素有 CSS class 時，**線寬寫在 `style="stroke-width:…"`，不要寫成 `stroke-width="…"` 屬性**：class 規則裡的 `stroke-width` 會蓋過屬性，畫出來會變細。
- 跳舞角色的大小要用動畫姿勢下的蒙皮外框計算（`Box3.setFromObject(model,true)`），否則會過大被裁切。
- 360° 展示的 canvas 尺寸要用 `style.setProperty(...,'important')` 設，否則被 CSS 蓋掉。
