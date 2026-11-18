#!/usr/bin/env python3
"""把 .glb 包成 3d/<name>.glb.js（base64），讓簡報直接雙擊開啟（file://）也能載入 3D 模型。

用法：python3 glb2js.py 模型.glb [名稱]
  名稱預設用檔名（不含副檔名），會寫出 <同資料夾>/<名稱>.glb.js
  簡報裡用 MODELS 的 key 對應這個名稱，例如 MODELS.globe → 3d/globe.glb.js
"""
import base64, os, sys

def main():
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    src = sys.argv[1]
    name = sys.argv[2] if len(sys.argv) > 2 else os.path.splitext(os.path.basename(src))[0]
    data = open(src, 'rb').read()
    if data[:4] != b'glTF':
        sys.exit('這不是 GLB 檔（開頭不是 glTF）：' + src)
    out = os.path.join(os.path.dirname(os.path.abspath(src)), name + '.glb.js')
    with open(out, 'w') as f:
        f.write('(window.__GLB=window.__GLB||{})[%r]="%s";\n' % (name, base64.b64encode(data).decode()))
    print('已寫出 %s（%.1f MB）' % (out, os.path.getsize(out) / 1048576))

if __name__ == '__main__':
    main()
