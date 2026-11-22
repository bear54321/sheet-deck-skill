#!/usr/bin/env python3
"""Test for sheet-deck saved-data migrations: old saves must still load correctly.

Rule: every conversion of the saved format (S settings, EDITS text) lives in MIGRATIONS in the template,
and S.v records how far a save has been converted. This test runs the real MIGRATIONS/migrate() code
from the HTML (with Node.js) against sample saves from each older format and checks the result.

Usage:
  python3 test_migrate.py assets/template.html [deck/index.html ...]
Exit code 1 on any problem; each message says where, the rule, and how to fix it.
When you add a migration step, add a sample save for it in CASES below.
"""
import json, re, shutil, subprocess, sys

RULE = '規則：存檔格式的轉換一律寫在 MIGRATIONS（加在最後，不改舊步驟），S.v 只由 migrate() 設定。'

# (說明, 存檔 S, 文字 EDITS, 期望的 S 欄位, 期望的 EDITS)；期望值只列要檢查的欄位
CASES = [
    ('最舊的存檔（沒有版本號）：頁序鍵名、圖表 slide、Unity、舊主色、沒選過的 coral 風格、沒有版型',
     {'theme': 'coral', 'accent': '#B07A4E', 'unity': {'x': 1}, 'charts': [{'id': 'c1', 'slide': 0}]},
     {'0-1': '舊文字', 's2-0': '新文字'},
     {'theme': 'street', 'layout': 'street', 'accent': '#469C9B', 'unity': None, 'charts': [{'id': 'c1', 'sid': 's1'}]},
     {'s1-1': '舊文字', 's2-0': '新文字'}),
    ('自己選過的風格要保留',
     {'theme': 'neon', 'themeSet': 1, 'layout': 'coral', 'accent': '#123456'},
     {},
     {'theme': 'neon', 'layout': 'coral', 'accent': '#123456'},
     {}),
    ('已經轉到最新版的存檔不會再被轉換',
     {'theme': 'coral', 'layout': 'coral', 'accent': '#DC9A8B', 'v': 'LATEST'},
     {'0-1': '這是新格式裡剛好長這樣的鍵'},
     {'theme': 'coral', 'layout': 'coral', 'accent': '#DC9A8B'},
     {'0-1': '這是新格式裡剛好長這樣的鍵'}),
]

JS = r'''
const J=x=>JSON.stringify(x,(k,v)=>v&&typeof v==='object'&&!Array.isArray(v)?Object.fromEntries(Object.entries(v).sort()):v);  // 不管鍵的順序
const out=[];
for(const [name,S0,E0,wantS,wantE] of CASES){
  const S=Object.assign(JSON.parse(JSON.stringify(DEF)),S0), E=JSON.parse(JSON.stringify(E0));
  if(S.v==='LATEST')S.v=MIGRATIONS.length;
  migrate(S,E);
  const S2=JSON.parse(JSON.stringify(S)),E2=JSON.parse(JSON.stringify(E));migrate(S2,E2);  // 再跑一次結果要一樣
  const bad=[];
  for(const [k,v] of Object.entries(wantS)){const got=S[k]===undefined?null:S[k];if(J(got)!==J(v))bad.push(`S.${k} 是 ${JSON.stringify(got)}，應該是 ${JSON.stringify(v)}`)}
  if(J(E)!==J(wantE))bad.push(`EDITS 是 ${JSON.stringify(E)}，應該是 ${JSON.stringify(wantE)}`);
  if(S.v!==MIGRATIONS.length)bad.push(`S.v 是 ${S.v}，應該是 ${MIGRATIONS.length}`);
  if(J(S2)!==J(S)||J(E2)!==J(E))bad.push('轉換完再跑一次 migrate() 結果變了');
  out.push({name,bad});
}
console.log(JSON.stringify(out));
'''


def check(path):
    h = open(path, encoding='utf-8').read()
    if 'function saveS' not in h:
        return []  # 不是 sheet-deck 簡報
    errs = []
    m = re.search(r'/\* MIGRATIONS-BEGIN \*/(.*?)/\* MIGRATIONS-END \*/', h, re.S)
    themes = re.search(r'^const THEMES=.*$', h, re.M)
    defs = re.search(r'^const DEF=.*$', h, re.M)
    if not (m and themes and defs):
        return [f'{path}：找不到 /* MIGRATIONS-BEGIN */…/* MIGRATIONS-END */ 區塊（或 THEMES、DEF）。{RULE} 修法：舊存檔轉換放回這個區塊；這份簡報若是舊版範本產生的，請從最新的 assets/template.html 更新。']
    for mm in re.finditer(r'\bS\.v\s*=(?!=)', h):
        if m.start() < mm.start() < m.end():
            continue
        lineno = h.count('\n', 0, mm.start()) + 1
        errs.append(f'{path}:{lineno}：在 migrate() 以外設定了 S.v（存檔版本號）。{RULE} 修法：刪掉這行；版本號由 migrate() 依 MIGRATIONS 的步數自動設定。')
    node = shutil.which('node')
    if not node:
        print(f'  ! 找不到 Node.js，略過 {path} 的舊存檔實測（只做了靜態檢查）')
        return errs
    src = themes.group(0) + '\n' + defs.group(0) + '\n' + m.group(1) + '\nconst CASES=' + json.dumps(CASES, ensure_ascii=False) + ';\n' + JS
    r = subprocess.run([node, '-e', src], capture_output=True, text=True, timeout=60)
    if r.returncode != 0:
        return errs + [f'{path}：MIGRATIONS 程式執行出錯：{next((l.strip() for l in r.stderr.splitlines() if re.match(r'\s*\w*Error\b', l)), r.stderr.strip()[:200] or "（沒有訊息）")}。{RULE} 修法：修好 MIGRATIONS 區塊裡出錯的步驟。']
    for res in json.loads(r.stdout):
        if res['bad']:
            errs.append(f'{path}：舊存檔「{res["name"]}」轉換結果不對：' + '；'.join(res['bad']) + f'。{RULE} 修法：不要改已經有的步驟，新的格式轉換加在 MIGRATIONS 最後；如果是刻意改變行為，同時更新 scripts/test_migrate.py 的範例。')
        else:
            print(f'  ✓ {res["name"]}')
    return errs


def main(argv):
    if not argv:
        sys.exit(__doc__)
    errs = []
    for f in argv:
        print('檢查', f)
        errs += check(f)
    for e in errs:
        print('  ✗', e)
    print('全部通過' if not errs else f'{len(errs)} 個問題')
    return 1 if errs else 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
