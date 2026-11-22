#!/usr/bin/env python3
"""Guard for sheet-deck HTML: AI requests must survive temporary server errors (5xx, e.g. Gemini 503 "high demand").

Rule: every Gemini/OpenAI request goes through httpJSON() (which retries 5xx); never call fetch() on an AI host directly.
Claude goes through the Anthropic SDK, which retries on its own - so maxRetries must not be turned off.

Usage:
  python3 check_ai_calls.py deck/index.html [more.html ...]          # static check (fast)
  python3 check_ai_calls.py --run deck/index.html [...]              # also runs the page in headless Chrome with a faked 503
Exit code 1 on any problem; each message says where, the rule, and how to fix it.
"""
import functools, http.server, json, os, re, shutil, subprocess, sys, tempfile, threading

AI_HOSTS = ('generativelanguage.googleapis.com', 'api.openai.com')
RULE = '規則：Gemini／OpenAI 的請求一律經過 httpJSON()（它會在 5xx 伺服器忙碌時自動重試）；Claude 走 SDK，不能關掉重試。'


def line_of(text, pos):
    return text.count('\n', 0, pos) + 1


def static_check(path):
    h = open(path, encoding='utf-8').read()
    errs = []
    if 'function httpJSON' not in h:
        return errs  # deck without the AI feature: nothing to check
    for host in AI_HOSTS:
        for m in re.finditer(re.escape(host), h):
            before = h[max(0, m.start() - 120):m.start()]
            call = before[before.rfind(';') + 1:] if ';' in before else before
            if 'httpJSON(' not in call:
                errs.append(f'{path}:{line_of(h, m.start())}：直接呼叫了 {host}，沒有經過 httpJSON()。{RULE} 修法：改成 httpJSON(p, url, opt, note)。')
    for m in re.finditer(r'\bfetch\(\s*[`\'"]https://(' + '|'.join(map(re.escape, AI_HOSTS)) + ')', h):
        errs.append(f'{path}:{line_of(h, m.start())}：用 fetch() 直接打 AI 服務，遇到 503 不會重試。{RULE} 修法：改用 httpJSON()。')
    body = re.search(r'async function httpJSON\(p,url,opt,note\)\{(.*?)\n(?=\S)', h, re.S)
    if not body or 'httpJSONOnce' not in body.group(1) or 'e.status>=500' not in body.group(1) or 'AI_RETRY_MS' not in body.group(1):
        errs.append(f'{path}：httpJSON() 不再對 5xx 自動重試（找不到 httpJSONOnce／e.status>=500／AI_RETRY_MS 的重試迴圈）。{RULE} 修法：讓 httpJSON 包住 httpJSONOnce，遇到 status>=500 時依 AI_RETRY_MS 等待後重試。')
    if re.search(r'maxRetries\s*:\s*0', h):
        errs.append(f'{path}：Claude SDK 設了 maxRetries:0，503／529 不會重試。{RULE} 修法：拿掉 maxRetries:0。')
    return errs


HARNESS = r'''<!doctype html><meta charset="utf-8"><body>running<script>
const KEY='sheet-deck:';localStorage.setItem(KEY+'ai-models:gemini',JSON.stringify([['gemini-9.9-flash','x']]));
localStorage.setItem(KEY+'ai-models:openai',JSON.stringify([['gpt-9','x']]));
const R=(o,s)=>new Response(JSON.stringify(o),{status:s||200,headers:{'content-type':'application/json'}});
const SUM=JSON.stringify({title:'OK',subtitle:'s',points:['a','b','c'],takeaway:'t'});
async function run(prov,key,model){
  Object.keys(localStorage).filter(k=>k.startsWith(KEY+'/')).forEach(k=>localStorage.removeItem(k));  // fresh deck state per run
  localStorage.setItem(KEY+'ai-provider',prov);localStorage.setItem(KEY+'key:'+prov,key);localStorage.setItem(KEY+'ai-model:'+prov,model);
  const f=document.createElement('iframe');f.style.cssText='width:1600px;height:900px';f.src='deck.html?'+prov;document.body.appendChild(f);
  await new Promise(r=>f.onload=r);await new Promise(r=>setTimeout(r,1500));
  const w=f.contentWindow,d=w.document;let n=0;const of=w.fetch;
  w.fetch=async(u,o)=>{u=String(u);if(u.includes(':generateContent')||u.includes('/chat/completions')){n++;
      if(n<=2)return R({error:{code:503,message:'This model is currently experiencing high demand.',status:'UNAVAILABLE'}},503);
      return prov==='gemini'?R({candidates:[{content:{parts:[{text:SUM}]},finishReason:'STOP'}]}):R({model,choices:[{finish_reason:'stop',message:{content:SUM,refusal:null}}]})}
    if(u.includes('/models'))return R({models:[],data:[]});return of(u,o)};
  const P=w.HTMLInputElement.prototype,oc=P.click;P.click=function(){if(this.type==='file'){const dt=new w.DataTransfer();dt.items.add(new w.File(['%PDF-1.4'],'t.pdf',{type:'application/pdf'}));this.files=dt.files;this.dispatchEvent(new w.Event('change'));P.click=oc}else oc.call(this)};
  const before=d.querySelectorAll('.slide[data-pdf]').length,btn=d.getElementById('bPdf');btn.click();
  for(let i=0;i<200&&(btn.classList.contains('busy')||i<3);i++)await new Promise(r=>setTimeout(r,250));
  const ok=d.querySelectorAll('.slide[data-pdf]').length>before&&n>=3;const toast=d.getElementById('toast').textContent;f.remove();
  return {prov,calls:n,ok,toast}}
(async()=>{const out=[];try{out.push(await run('gemini','AIzaTEST','gemini-9.9-flash'));out.push(await run('openai','sk-TEST','gpt-9'))}catch(e){out.push({error:String(e)})}
  document.body.innerHTML='<pre id="result">'+JSON.stringify(out)+'</pre>'})();
</script>'''


def find_chrome():
    for c in ('/Applications/Google Chrome.app/Contents/MacOS/Google Chrome', shutil.which('google-chrome') or '', shutil.which('chromium') or ''):
        if c and os.path.exists(c):
            return c
    return None


def run_check(path):
    chrome = find_chrome()
    if not chrome:
        return [f'{path}：找不到 Chrome，無法執行實測（--run）。請安裝 Google Chrome 或只跑靜態檢查。']
    tmp = tempfile.mkdtemp()
    shutil.copy(path, os.path.join(tmp, 'deck.html'))
    open(os.path.join(tmp, 'harness.html'), 'w', encoding='utf-8').write(HARNESS)
    class Quiet(http.server.SimpleHTTPRequestHandler):
        def log_message(self, *a): pass
    handler = functools.partial(Quiet, directory=tmp)
    srv = http.server.ThreadingHTTPServer(('127.0.0.1', 0), handler)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    try:
        out = subprocess.run([chrome, '--headless=new', '--disable-gpu', f'--user-data-dir={tmp}/profile', '--virtual-time-budget=120000',
                              '--dump-dom', f'http://127.0.0.1:{srv.server_address[1]}/harness.html'], capture_output=True, text=True, timeout=180).stdout
    finally:
        srv.shutdown(); shutil.rmtree(tmp, ignore_errors=True)
    m = re.search(r'<pre id="result">(.*?)</pre>', out, re.S)
    if not m:
        return [f'{path}：實測沒有跑完（headless Chrome 沒產生結果）。']
    errs = []
    for r in json.loads(m.group(1).replace('&quot;', '"').replace('&amp;', '&')):
        if r.get('error') or not r.get('ok'):
            errs.append(f'{path}：實測失敗——{r.get("prov")} 回傳兩次 503 後就放棄了（呼叫 {r.get("calls")} 次，畫面訊息：「{r.get("toast")}」）。{RULE} 修法：確認這個供應商的請求有經過 httpJSON() 並把 note 傳下去。')
        else:
            print(f'  ✓ {r["prov"]}：兩次 503 後自動重試成功（共呼叫 {r["calls"]} 次）')
    return errs


def main(argv):
    run = '--run' in argv
    files = [a for a in argv if a != '--run']
    if not files:
        print(__doc__); return 2
    errs = []
    for f in files:
        print(f'檢查 {f}')
        e = static_check(f)
        if run and not e and 'function httpJSON' in open(f, encoding='utf-8').read():
            e += run_check(f)
        errs += e
    for e in errs:
        print('✗ ' + e)
    print('全部通過' if not errs else f'{len(errs)} 個問題')
    return 1 if errs else 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
