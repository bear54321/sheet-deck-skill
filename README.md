# sheet-deck skill

Claude Code skill：製作有「演示控制台」的網頁動畫簡報。單一 HTML，可接 Google 試算表即時資料、ECharts 圖表、three.js 3D 模型、AI 摘要 PDF，有 3D 空間播放模式，能匯出 HTML／PDF／PPTX。

## 安裝

```bash
git clone https://github.com/bear54321/sheet-deck-skill.git ~/.claude/skills/sheet-deck
```

之後在 Claude Code 說「幫我做一份網頁簡報，接這個試算表……」就會用到。

## 內容

| 路徑 | 說明 |
|---|---|
| `SKILL.md` | 給 Claude 的使用說明 |
| `assets/template.html` | 簡報範本（編輯器、資料、圖表、3D、PDF 摘要、匯出、3D 空間） |
| `assets/開啟簡報.command` | Mac 雙擊啟動本機伺服器並開啟簡報 |
| `scripts/glb2js.py` | 把 GLB 包成 `.glb.js`，雙擊開 HTML 也能載入 |
| `scripts/optimize_model.py` | Blender 背景壓縮模型（減面、縮貼圖） |
| `scripts/object_capture.swift` | Mac Object Capture：照片轉 3D 模型 |
| `references/` | 3D 模型、照片轉 3D 的詳細說明 |
| `NOTICE.md` | 第三方授權聲明（Lemo-Opuscar 風格、外部套件） |

3D 模型檔不在這個 repo 裡，請依 `references/3d-models.md` 自行準備。

## 授權與致謝

- 範本的介面與程式由本 repo 作者製作。
- 工具列「🎨 風格」裡的 15 種風格，參考自 [Lemo-Opuscar](https://github.com/lemomo-ai/lemo-opuscar) 風格庫（作者 Lemomo），採 [CC BY-NC 4.0](https://creativecommons.org/licenses/by-nc/4.0/) 授權：**可以分享與修改，但要註明出處，且不可用於商業用途。** 預設的「珊瑚扁平」風格不在此限。
- 詳細內容與用到的外部套件，請見 [NOTICE.md](NOTICE.md)。
