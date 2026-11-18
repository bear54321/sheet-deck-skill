#!/bin/bash
# 雙擊這個檔案：在本機啟動簡報伺服器，並用瀏覽器開啟（Unity WebGL 需要這樣才能執行）
cd "$(dirname "$0")"
PORT=8765
if lsof -iTCP:$PORT -sTCP:LISTEN >/dev/null 2>&1; then
  open "http://localhost:$PORT/index.html"
  exit 0
fi
echo "簡報伺服器啟動中：http://localhost:$PORT/index.html"
echo "要關閉伺服器，直接關掉這個視窗即可。"
( sleep 1; open "http://localhost:$PORT/index.html" ) &
python3 -m http.server $PORT --bind 127.0.0.1
