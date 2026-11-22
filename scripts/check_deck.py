#!/usr/bin/env python3
"""Guard for sheet-deck HTML: every deck saves to its own storage keys, only through saveS()/saveEdits().

Rule: storage keys come from <html data-deck="..."> (unique per deck), never from the URL path.
Why: 開啟簡報.command serves each deck folder as the site root, so every deck is at /index.html;
path-based keys made one deck's edits and settings show up in another.

Usage:
  python3 check_deck.py deck/index.html [more.html ...]   # several files: also checks the ids are unique
  python3 check_deck.py path/to/folder                     # checks folder/index.html
Exit code 1 on any problem; each message says where, the rule, and how to fix it.
"""
import os, re, sys

PLACEHOLDER = '__DECK_ID__'
RULE = '規則：每份簡報的存檔鍵名來自 <html data-deck="…">，每份都要不一樣；不能用網址路徑（開啟簡報.command 讓每份簡報都是 /index.html，會互相覆蓋）。'


def is_template(path):
    return os.path.abspath(path).replace(os.sep, '/').endswith('/assets/template.html')


def check(path, h):
    errs, deck = [], None
    tag = re.search(r'<html\b[^>]*>', h)
    m = re.search(r'\bdata-deck="([^"]*)"', tag.group(0)) if tag else None
    if not m:
        errs.append(f'{path}:1：<html> 沒有 data-deck。{RULE} 修法：在 <html> 加 data-deck="<這份簡報的資料夾名稱>"，例如 data-deck="museum-renewal"。')
    else:
        deck = m.group(1)
        if not re.fullmatch(r'[A-Za-z0-9_-]+', deck):
            errs.append(f'{path}:1：data-deck="{deck}" 含有不允許的字元。{RULE} 修法：只用英文字母、數字、- 和 _，例如 data-deck="museum-renewal"。')
        elif is_template(path):
            if deck != PLACEHOLDER:
                errs.append(f'{path}:1：範本的 data-deck 要保持 "{PLACEHOLDER}"，複製出去的簡報才會被這個檢查抓到沒改。修法：改回 data-deck="{PLACEHOLDER}"。')
        elif deck == PLACEHOLDER:
            errs.append(f'{path}:1：data-deck 還是範本的 "{PLACEHOLDER}"。{RULE} 修法：改成這份簡報的資料夾名稱，例如 data-deck="museum-renewal"。')
    for mm in re.finditer(r'location\.(pathname|href)', h):
        line_start = h.rfind('\n', 0, mm.start()) + 1
        line = h[line_start:h.find('\n', mm.start())]
        if 'const OLD=' in line:  # 舊鍵名的一次性搬移，只讀舊資料、讀完就刪
            continue
        lineno = h.count('\n', 0, mm.start()) + 1
        errs.append(f'{path}:{lineno}：用了 location.{mm.group(1)}（網址）。{RULE} 修法：存檔或快取的鍵名改用 KEY（由 data-deck 而來）；這份簡報若是舊版範本產生的，請從最新的 assets/template.html 更新。')
    # 存檔一律經過 saveS()／saveEdits()：它們會跳過純簡報模式（PLAYER），直接寫 localStorage 會漏掉這個保護
    for mm in re.finditer(r'localStorage\.setItem\(\s*KEY\b', h):
        line_start = h.rfind('\n', 0, mm.start()) + 1
        line = h[line_start:h.find('\n', mm.start())]
        if re.match(r'\s*function (saveS|saveEdits)\(\)', line) or 'const OLD=' in line:
            continue
        lineno = h.count('\n', 0, mm.start()) + 1
        errs.append(f'{path}:{lineno}：直接用 localStorage.setItem(KEY…) 存檔。規則：存檔一律經過 saveS()（設定 S）或 saveEdits()（文字 EDITS），它們會跳過純簡報模式。修法：改成呼叫 saveS() 或 saveEdits()。')
    # HTML 跳脫只有一個 escH()；各自再寫一份容易漏掉某個符號。escH 要是 function（會提前可用），寫成 const 在初始化時會出錯
    for mm in re.finditer(r'\.replace\(\s*/\[[^\]]*&[^\]]*<[^\]]*\]/g', h):
        line_start = h.rfind('\n', 0, mm.start()) + 1
        line = h[line_start:h.find('\n', mm.start())]
        if re.match(r'\s*(function escH\(|(const|let|var)\s+escH\s*=)', line):  # escH 本身（寫成 const 由下一條規則報）
            continue
        lineno = h.count('\n', 0, mm.start()) + 1
        errs.append(f'{path}:{lineno}：自己寫了一份 HTML 跳脫（把 & < > 換成 &amp; 等）。規則：HTML 跳脫一律用 escH()。修法：刪掉這份，改成呼叫 escH(文字)。')
    if re.search(r'\b(const|let|var)\s+escH\s*=', h):
        errs.append(f'{path}：escH 寫成了 const／let。規則：escH 要用 function escH(s){{…}} 宣告，頁面初始化時（makeSlide）就會用到，const 那時還不能用。修法：改回 function 宣告。')
    return errs, deck


def main(argv):
    files = [os.path.join(a, 'index.html') if os.path.isdir(a) else a for a in argv]
    if not files:
        sys.exit(__doc__)
    errs, seen = [], {}
    for f in files:
        print('檢查', f)
        e, deck = check(f, open(f, encoding='utf-8').read())
        errs += e
        if deck and deck != PLACEHOLDER and not e:
            seen.setdefault(deck, []).append(f)
    for deck, fs in seen.items():
        if len(fs) > 1:
            errs.append(f'{"、".join(fs)}：data-deck 都是 "{deck}"。{RULE} 修法：把其中一份改成自己的資料夾名稱。')
    for e in errs:
        print('  ✗', e)
    print('全部通過' if not errs else f'{len(errs)} 個問題')
    return 1 if errs else 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
