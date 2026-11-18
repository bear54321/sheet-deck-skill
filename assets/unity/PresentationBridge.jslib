mergeInto(LibraryManager.library, {
  // Unity → 網頁簡報：送出 window 事件 "unity-bridge"；若在 iframe 裡，也用 postMessage 通知外層頁面。
  PB_Notify: function (type, payload) {
    var t = UTF8ToString(type);
    var p = UTF8ToString(payload);
    try {
      window.dispatchEvent(new CustomEvent("unity-bridge", { detail: { type: t, payload: p } }));
    } catch (e) {}
    try {
      if (window.parent && window.parent !== window) {
        window.parent.postMessage({ source: "unity-bridge", type: t, payload: p }, "*");
      }
    } catch (e) {}
  }
});
