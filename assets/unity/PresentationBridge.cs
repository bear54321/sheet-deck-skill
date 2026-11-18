using System;
using System.Runtime.InteropServices;
using UnityEngine;
using UnityEngine.SceneManagement;

/// <summary>
/// 網頁簡報 ↔ Unity 的溝通橋樑。
/// 不需要放進任何場景：遊戲啟動時會自動建立一個名為 "PresentationBridge" 的物件。
///
/// 網頁 → Unity（在簡報裡呼叫 unityInstance.SendMessage("PresentationBridge", 方法, 參數)）：
///   Pause()            暫停遊戲時間與聲音（切到別頁時）
///   Resume()           繼續（切回這頁時）
///   LoadScene(name)    切換到指定場景，例如 "Courtyard"
///   SetMute("1"/"0")   靜音 / 取消靜音
///   SetData(json)      接收簡報傳來的試算表資料（遊戲程式可訂閱 OnData 使用）
///
/// Unity → 網頁（簡報會收到 window 事件 "unity-bridge"）：
///   ready / scene / paused / resumed / goto ...
///   遊戲程式可呼叫 PresentationBridge.GotoSlide(3) 讓簡報跳到第 3 頁，
///   或 PresentationBridge.Notify("自訂事件", "內容")。
/// </summary>
public class PresentationBridge : MonoBehaviour
{
    public static PresentationBridge Instance { get; private set; }

    /// <summary>簡報送來資料時觸發（參數是 JSON 字串）。</summary>
    public static event Action<string> OnData;

    /// <summary>最近一次收到的資料（JSON）。</summary>
    public static string LastData { get; private set; } = "";

#if UNITY_WEBGL && !UNITY_EDITOR
    [DllImport("__Internal")] private static extern void PB_Notify(string type, string payload);
#else
    private static void PB_Notify(string type, string payload) => Debug.Log($"[PresentationBridge] → 網頁 {type}: {payload}");
#endif

    private float _savedTimeScale = 1f;
    private bool _paused;

    [RuntimeInitializeOnLoadMethod(RuntimeInitializeLoadType.AfterSceneLoad)]
    private static void Boot()
    {
        if (Instance != null) return;
        var go = new GameObject("PresentationBridge");
        DontDestroyOnLoad(go);
        Instance = go.AddComponent<PresentationBridge>();
    }

    private void Awake()
    {
        if (Instance != null && Instance != this) { Destroy(gameObject); return; }
        Instance = this;
        SceneManager.sceneLoaded += HandleSceneLoaded;
    }

    private void OnDestroy()
    {
        SceneManager.sceneLoaded -= HandleSceneLoaded;
    }

    private void Start()
    {
        Notify("ready", SceneManager.GetActiveScene().name);
    }

    private void HandleSceneLoaded(Scene scene, LoadSceneMode mode)
    {
        Notify("scene", scene.name);
        if (_paused) ApplyPause();
    }

    // ---------- 網頁呼叫 ----------

    public void Pause()
    {
        if (_paused) return;
        if (Time.timeScale > 0f) _savedTimeScale = Time.timeScale;
        _paused = true;
        ApplyPause();
        Notify("paused", "");
    }

    public void Resume()
    {
        if (!_paused) return;
        _paused = false;
        Time.timeScale = _savedTimeScale > 0f ? _savedTimeScale : 1f;
        AudioListener.pause = false;
        Notify("resumed", "");
    }

    public void LoadScene(string sceneName)
    {
        if (string.IsNullOrEmpty(sceneName)) return;
        if (!Application.CanStreamedLevelBeLoaded(sceneName))
        {
            Notify("error", "找不到場景：" + sceneName);
            return;
        }
        SceneManager.LoadScene(sceneName);
    }

    public void SetMute(string on)
    {
        AudioListener.volume = on == "1" ? 0f : 1f;
    }

    public void SetData(string json)
    {
        LastData = json ?? "";
        OnData?.Invoke(LastData);
        Notify("data-received", LastData.Length.ToString());
    }

    // ---------- 遊戲程式呼叫 ----------

    /// <summary>讓網頁簡報跳到指定頁（從 1 開始）。</summary>
    public static void GotoSlide(int page) => Notify("goto", page.ToString());

    /// <summary>送任意事件給網頁簡報。</summary>
    public static void Notify(string type, string payload)
    {
        try { PB_Notify(type ?? "", payload ?? ""); }
        catch (Exception e) { Debug.LogWarning("[PresentationBridge] " + e.Message); }
    }

    private static void ApplyPause()
    {
        Time.timeScale = 0f;
        AudioListener.pause = true;
    }
}
