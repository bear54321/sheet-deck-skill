# Unity WebGL 嵌入

## 放進 Unity 專案

| 檔案 | 放到 |
|---|---|
| `assets/unity/PresentationBridge.cs` | `Assets/` 下任一 Scripts 資料夾 |
| `assets/unity/PresentationBridge.jslib` | `Assets/Plugins/WebGL/` |
| `assets/unity/SlidesWebGLBuild.cs` | 任一 `Editor/` 資料夾 |

- `PresentationBridge` 會在遊戲啟動時自動建立，不用放進場景。
- 打開 `SlidesWebGLBuild.cs`，把 `DeckFolder` 改成簡報資料夾（相對 Unity 專案根目錄或絕對路徑）。
- 選單 **Tools → 簡報 → Build WebGL 給網頁簡報**：會暫時關閉壓縮、開啟背景執行，輸出到 `<簡報資料夾>/unity/Build`，再還原設定。
- 若用 Unity MCP 自動化：新增腳本後先 `refresh_unity`，選單才會出現，再 `execute_menu_item`。Build 時 MCP 連線斷掉是正常的，看輸出資料夾與 Console 確認結果。

## 簡報端

- 「🎮 插入 Unity」加一個 Unity 畫面框（可拖曳、縮放）；右側面板可設建置資料夾、標題、切換場景、靜音、全螢幕。
- 範本裡 `const UNITY_SCENES=[]` 填入可切換的場景名稱。
- 只會有一個 Unity 實體，換頁時暫停（`Pause`），回到該頁時繼續（`Resume`）。
- 玩遊戲時鍵盤不會翻頁（`window.__gameFocus`），按 Esc 交還給簡報。
- **必須用本機伺服器開**（`開啟簡報.command`），`file://` 無法載入 WebGL。

## 溝通介面

網頁 → Unity：`unityInstance.SendMessage('PresentationBridge', 方法, 參數)`

| 方法 | 參數 | 作用 |
|---|---|---|
| `Pause` / `Resume` | — | 暫停／繼續時間與聲音 |
| `LoadScene` | 場景名稱 | 切換場景（找不到會回報 error） |
| `SetMute` | `"1"`/`"0"` | 靜音 |
| `SetData` | JSON 字串 | 把試算表資料傳進遊戲；遊戲訂閱 `PresentationBridge.OnData` |

Unity → 網頁：window 事件 `unity-bridge`，`detail={type,payload}`；type 有 `ready`、`scene`、`paused`、`resumed`、`goto`（讓簡報跳頁）、`data-received`、`error`。遊戲裡呼叫 `PresentationBridge.GotoSlide(3)` 或 `PresentationBridge.Notify("事件","內容")`。
