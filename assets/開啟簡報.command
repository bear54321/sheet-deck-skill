#!/bin/bash
# 雙擊這個檔案：在本機啟動簡報伺服器，並用瀏覽器開啟（Google 文件需要這樣才能讀取）
cd "$(dirname "$0")"
MINE=$(md5 -q index.html)
PORT=8765
while lsof -iTCP:$PORT -sTCP:LISTEN >/dev/null 2>&1; do
  # 這個連接埠已有伺服器：如果就是這份簡報，直接打開；否則（別的專案）換下一個連接埠
  if [ "$(curl -s "http://localhost:$PORT/index.html" | md5 -q)" = "$MINE" ]; then
    open "http://localhost:$PORT/index.html"
    exit 0
  fi
  PORT=$((PORT+1))
done
echo "簡報伺服器啟動中：http://localhost:$PORT/index.html"
echo "要關閉伺服器，直接關掉這個視窗即可。"
( sleep 1; open "http://localhost:$PORT/index.html" ) &
python3 -m http.server $PORT --bind 127.0.0.1
