using System.IO;
using System.Linq;
using UnityEditor;
using UnityEditor.Build.Reporting;
using UnityEngine;

/// <summary>
/// 一鍵輸出 WebGL 給網頁簡報使用。
/// 選單：Tools → 簡報 → Build WebGL 給網頁簡報
/// 輸出到 DeckFolder/unity/Build（不壓縮，方便用本機伺服器直接開啟）。
/// 會暫時改用「不壓縮」與「背景執行」，輸出完畢後還原原本的設定。
/// </summary>
public static class SlidesWebGLBuild
{
    // 改成你的網頁簡報資料夾（相對於 Unity 專案根目錄，或填絕對路徑）。WebGL 會輸出到 <簡報資料夾>/unity/Build
    private const string DeckFolder = "../my-deck";

    private static string OutDir =>
        Path.GetFullPath(Path.Combine(Application.dataPath, "..", DeckFolder, "unity/Build"));

    [MenuItem("Tools/簡報/Build WebGL 給網頁簡報")]
    public static void Build()
    {
        var scenes = EditorBuildSettings.scenes.Where(s => s.enabled).Select(s => s.path).ToArray();
        if (scenes.Length == 0)
        {
            EditorUtility.DisplayDialog("Build WebGL", "Build Settings 裡沒有啟用的場景。", "OK");
            return;
        }

        var prevCompression = PlayerSettings.WebGL.compressionFormat;
        var prevBackground = PlayerSettings.runInBackground;
        try
        {
            PlayerSettings.WebGL.compressionFormat = WebGLCompressionFormat.Disabled;
            PlayerSettings.runInBackground = true;

            var options = new BuildPlayerOptions
            {
                scenes = scenes,
                locationPathName = OutDir,
                target = BuildTarget.WebGL,
                options = BuildOptions.None
            };
            BuildReport report = BuildPipeline.BuildPlayer(options);
            var s = report.summary;
            Debug.Log($"[SlidesWebGLBuild] {s.result}，輸出到 {OutDir}（{s.totalSize / 1048576f:F1} MB，{s.totalTime.TotalSeconds:F0} 秒）");
            if (s.result == BuildResult.Succeeded)
            {
                EditorUtility.DisplayDialog("Build WebGL 完成",
                    "已輸出到：\n" + OutDir + "\n\n回到網頁簡報重新整理即可看到最新版本。", "OK");
            }
            else
            {
                EditorUtility.DisplayDialog("Build WebGL 失敗", "請查看 Console 的錯誤訊息。", "OK");
            }
        }
        finally
        {
            PlayerSettings.WebGL.compressionFormat = prevCompression;
            PlayerSettings.runInBackground = prevBackground;
        }
    }
}
