#!/usr/bin/env python3
"""Guard for sheet-deck HTML: catches the slide-drawing mistakes that already happened once.

Rules (each one broke a layout before):
  1. The page script must parse (needs Node.js; skipped with a note if Node is missing).
  2. No id-referenced SVG paint (fill/stroke="url(#…)") — thumbnails copy the same id, and in
     play mode the browser picks the hidden thumbnail's copy, so the gradient disappears.
  3. No stroke-width="…" attribute on an SVG element whose CSS class already sets stroke-width —
     the class wins and the line is drawn thinner than intended.
  4. No CSS animation directly on `.hd h2` / `.hd p` — they already fade in with `.a`, and
     replacing that animation leaves the title or subtitle invisible.
  5. <html data-settings> that sets a layout must include "v" — without it the old-save
     migration resets the layout to street.

Usage:
  python3 check_deco.py assets/template.html [deck/index.html ...]
Exit code 1 on any problem; each message says where, the rule, and how to fix it.
"""
import json, re, shutil, subprocess, sys

SVG_TAG = re.compile(r'<(?:path|rect|circle|ellipse|line|polyline|polygon)\b[^>]*>')


def line_of(h, i):
    return h.count('\n', 0, i) + 1


def css_text(h):
    css = '\n'.join(re.findall(r'<style[^>]*>([\s\S]*?)</style>', h))
    # 註解換成等長的空白：選擇器不會沾到註解文字，行號也不變
    return re.sub(r'/\*[\s\S]*?\*/', lambda m: re.sub(r'[^\n]', ' ', m.group(0)), css)


def check_script(path, h):
    node = shutil.which('node')
    if not node:
        print('  （略過第 1 項：找不到 Node.js，無法檢查程式語法）')
        return []
    errs = []
    for m in re.finditer(r'<script>([\s\S]*?)</script>', h):
        r = subprocess.run([node, '-e', 'try{new Function(require("fs").readFileSync(0,"utf8"))}catch(e){console.log(e.message);process.exit(1)}'],
                           input=m.group(1), capture_output=True, text=True)
        if r.returncode:
            errs.append(f'{path}:{line_of(h, m.start())}：<script> 有語法錯誤：{r.stdout.strip()}。'
                        '規則：頁面程式要能執行，否則整份簡報打不開。修法：照錯誤訊息修好那一段（常見是字串裡的反引號、括號沒配對）。')
    return errs


def check_url_ref(path, h):
    errs = []
    for m in re.finditer(r'(?:fill|stroke|filter|mask|clip-path)\s*[=:]\s*["\']?url\(#', h):
        errs.append(f'{path}:{line_of(h, m.start())}：插圖用了 id 參照（url(#…)）。'
                    '規則：左側縮圖會複製出同一個 id，播放時縮圖被隱藏，瀏覽器抓到的是縮圖那一份，漸層／濾鏡就消失。'
                    '修法：改成疊幾層半透明圖形（例如 grDeco() 的 glow），不要用 <linearGradient>／<radialGradient>／<filter> 加 id。')
    return errs


def check_stroke_width(path, h):
    css = css_text(h)
    classes = set()
    for m in re.finditer(r'([^{}]+)\{([^{}]*)\}', css):
        if re.search(r'(^|;)\s*stroke-width\s*:', m.group(2)):
            sel = m.group(1)
            if '.slide' in sel or ':root' in sel:  # 只看單純的插圖 class 規則
                continue
            classes.update(re.findall(r'\.([A-Za-z][\w-]*)', sel))
    errs = []
    for m in SVG_TAG.finditer(h):
        tag = m.group(0)
        if not re.search(r'\sstroke-width="', tag):
            continue
        cm = re.search(r'class="([^"]*)"', tag)
        if not cm:
            continue
        hit = [c for c in re.split(r'\s+', cm.group(1)) if c in classes]
        if hit:
            errs.append(f'{path}:{line_of(h, m.start())}：class「{hit[0]}」在 CSS 裡已經設了 stroke-width，元素上的 stroke-width="…" 屬性會被蓋掉。'
                        '規則：CSS class 的線寬優先於屬性，線會畫得比預期細。修法：改寫成 style="stroke-width:…"（已經有 style 就加在裡面）。')
    return errs


def check_heading_animation(path, h):
    errs, css = [], css_text(h)
    sm = re.search(r'<style[^>]*>', h)
    start = sm.end() if sm else 0
    for m in re.finditer(r'([^{}]+)\{([^{}]*)\}', css):
        if not re.search(r'(^|;)\s*animation\s*:', m.group(2)):
            continue
        for sel in m.group(1).split(','):
            sel = sel.strip()
            if re.search(r'\.hd\s+(h2|p)$', sel):
                errs.append(f'{path}:{line_of(h, start + m.start() + len(m.group(1)) - len(m.group(1).lstrip()))}：「{sel}」直接設了 animation。'
                            '規則：.hd 的標題和副標題本身有 .a 淡入動畫，被蓋掉後會一直是透明的。'
                            '修法：把效果畫在 ::before 或 ::after（參考 fieldnotes 副標題的螢光筆）。')
    return errs


def check_settings(path, h):
    tag = re.search(r'<html\b[^>]*>', h)
    m = tag and re.search(r"\bdata-settings='([^']*)'", tag.group(0))
    if not m:
        return []
    try:
        s = json.loads(m.group(1))
    except ValueError:
        return [f'{path}:1：<html data-settings> 不是正確的 JSON。修法：用單引號包住、裡面用雙引號，例如 data-settings=\'{{"v":6,"layout":"cyber"}}\'。']
    if ('layout' in s or 'theme' in s) and 'v' not in s:
        return [f'{path}:1：<html data-settings> 指定了版型但沒有 "v"。'
                '規則：沒有 v 會被當成最舊的存檔，舊存檔轉換會把版型改回 street。'
                '修法：加上 "v":6（範本 MIGRATIONS 目前的步數），例如 data-settings=\'{"v":6,"theme":"cyber","layout":"cyber","themeSet":1}\'。']
    return []


def main(argv):
    if not argv:
        sys.exit(__doc__)
    errs = []
    for f in argv:
        print('檢查', f)
        h = open(f, encoding='utf-8').read()
        for fn in (check_script, check_url_ref, check_stroke_width, check_heading_animation, check_settings):
            errs += fn(f, h)
    for e in errs:
        print('  ✗', e)
    print('全部通過' if not errs else f'{len(errs)} 個問題')
    return 1 if errs else 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
