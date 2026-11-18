# 3D 模型

## 載入方式

- 簡報用 three.js 0.160.0（importmap 從 jsdelivr 載入），GLTFLoader 解析模型。
- 模型以 base64 包在 `3d/<名稱>.glb.js`，內容是 `(window.__GLB=window.__GLB||{})['名稱']="..."`。簡報需要時才用 `<script>` 載入，所以 `file://` 也能用。
- 產生方式：`python3 scripts/glb2js.py 3d/<名稱>.glb`。

## 三種類型（`MODELS` 的 `kind`）

| kind | 效果 | 注意 |
|---|---|---|
| `fly` | 沿 8 字形路徑在整頁上飛，會轉彎傾斜 | 模型正面要朝 +Z；有往前傾的角度（body.rotation.x≈.55），換模型時可能要調 |
| `dance` | 站在頁面中間播放動畫 | GLB 要有動畫 clip；在 `MODELS.girl.clips` 列出要給使用者選的 clip 名稱 |
| `showcase` | 頁面上一個圓角展示框，可拖曳旋轉、滾輪縮放、雙擊復原，閒置自動轉 | 用 RoomEnvironment 做反光；`maxZoom` 可調放大上限（看小字時調高，如 4.5） |

新增模型：

```js
const MODELS={...,vase:{name:'青花瓷瓶 360° 展示',icon:'🏺',kind:'showcase'}};
```

再在右側面板 `#flyAddBox` 加 `<button class="btn" data-m="vase">🏺 青花瓷瓶</button>`。

每個 3D 角色存在 `S.flyers`：`{id,sid,model,size,speed,yaw,on,clip?,box?}`；`box` 是 360° 展示框的位置大小（舞台座標）。

## 壓縮

`/Applications/Blender.app/Contents/MacOS/Blender -b --python scripts/optimize_model.py -- 輸入檔 輸出.glb [最多面數] [貼圖最大邊長]`

- 支援 .glb / .gltf / .fbx / .obj；輸出 JPEG 貼圖的 GLB。
- 參考值：飛行角色 40k 面、1024 貼圖；360° 文物 0（不減面）、2048 貼圖；要看清楚文字的物件（如地球儀）用 8192 貼圖。
- 實例：Meshy 鸚鵡 FBX → 1.2 MB；Sketchfab 瓷瓶 16 MB → 2.7 MB。

## 找模型

- Sketchfab 搜尋時勾「Downloadable」，看授權（CC0 最自由；CC-BY 要標示作者）。下載選 **GLB**。
- 博物館常有 CC0 文物掃描（例如 Virtual Museums of Małopolska）。
- AI 生成（Meshy）：適合角色、公仔；**不適合有文字、地圖的物件**，AI 會把文字畫成亂碼。
