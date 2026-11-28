# 第三方授權聲明（NOTICE）

## Lemo-Opuscar 風格庫

範本工具列「🎨 風格」裡的 15 種風格（木刻版畫、中國水墨、浮世繪、紅色窗花剪紙、孔版印刷、普普藝術、瑞士動態排版、包浩斯幾何、裝飾藝術、工程藍圖、黑板粉筆、霓虹燈管、CRT 字元終端、1920s 默片、水彩筆刷），視覺規則參考自 Lemo-Opuscar 風格庫的風格說明（`styles/*/STYLE.md`）。

- **作品**：Lemo-Opuscar 風格說明
- **作者**：Lemomo（LemoLab）
- **出處**：https://github.com/lemomo-ai/lemo-opuscar
- **授權**：CC BY-NC 4.0（姓名標示—非商業性）https://creativecommons.org/licenses/by-nc/4.0/
- **改了什麼**：依各風格說明的配色、材質與排版規則，改寫成簡報用的 CSS 變數與樣式（`assets/template.html` 裡的 `THEMES` 與 `:root[data-theme=…]` 規則）。沒有使用 Lemo-Opuscar 的程式、圖片、字型、影片或示範短片。

因此，**這 15 種風格不可用於商業用途**（例如販售、付費接案）。若要商用，請先取得 Lemomo 的同意，或在範本中移除這 15 種風格，只保留預設的「珊瑚扁平」。

## 版型的外觀參考

以下版型的**外觀**（配色、字型氣質、版面構圖）參考自 OpenDesign 內附的簡報範本；程式碼（`assets/template.html` 裡的 CSS、`cyDeco()`／`grDeco()`／`cbDeco()`／`znDeco()`／`obDeco()`）全部重新寫，沒有複製原範本的 CSS、HTML、圖片或文字。

- **鈷藍格線、復古小誌、8-bit 軌道**：參考 Zara Zhang 的 beautiful-html-templates（`cobalt-grid`、`retro-zine`、`8-bit-orbit`），https://github.com/zarazhangrui/beautiful-html-templates ，MIT 授權，Copyright (c) 2026 Zara Zhang。
- **賽博終端機、深色知識圖譜**：參考 lewislulu/html-ppt-skill 的 `hermes-cyber-terminal`、`graphify-dark-graph`，https://github.com/lewislulu/html-ppt-skill 。本機的 OpenDesign 副本沒有附授權檔，所以只參考外觀、不使用任何原始碼。

- **數位金融瑞士風、田野筆記報告風**：參考 OpenDesign 內附的 `digits-fintech-swiss-template`、`field-notes-editorial-template`。這兩份範本沒有註明出處或授權，所以只參考外觀、不使用任何原始碼。
- **復古 Windows**：參考 Zara Zhang 的 beautiful-html-templates（`retro-windows`），MIT 授權，出處同上。視窗、圖示、游標都是重新畫的簡單幾何圖形，沒有使用微軟的圖示或字型。

「墨金」版型是原創，沒有參考特定範本。

## 執行時載入的外部資源（不包含在本資料夾）

簡報打開時會從網路載入以下資源，各自依其授權使用：

- ECharts（Apache-2.0）
- three.js（MIT）
- html2canvas（MIT）
- PptxGenJS（MIT）
- Anthropic TypeScript SDK（MIT，只在使用 Claude 做 PDF 摘要時載入）
- Google Fonts：Noto Sans TC、Noto Serif TC、LXGW WenKai TC（SIL Open Font License 1.1）
