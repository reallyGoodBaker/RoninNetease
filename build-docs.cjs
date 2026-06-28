#!/usr/bin/env node
const fs = require('fs'), path = require('path'), { marked } = require('marked'), hljs = require('highlight.js');

const hljsCSS = fs.readFileSync(
  path.join(__dirname, 'node_modules', 'highlight.js', 'styles', 'atom-one-dark.min.css'),
  'utf-8'
).trim().replace(/background:#282c34/g, 'background:#0a0a0a');

function decodeHTMLEntities(str) {
  var A = String.fromCharCode(38);
  str = str.split(A + 'amp;').join('\x00A\x00');
  str = str.split(A + 'lt;').join('<');
  str = str.split(A + 'gt;').join('>');
  str = str.split(A + 'quot;').join('"');
  str = str.split(A + '#x27;').join("'");
  str = str.split(A + '#39;').join("'");
  str = str.split(A).join('&');
  str = str.split('\x00A\x00').join('&');
  return str;
}

function highlightCodeBlocks(html) {
  return html.replace(/<pre><code class="language-(\w+)">([\s\S]*?)<\/code><\/pre>/g, function(m, lang, code) {
    var txt = decodeHTMLEntities(code);
    var highlighted;
    try {
      highlighted = hljs.getLanguage(lang)
        ? hljs.highlight(txt, { language: lang, ignoreIllegals: true }).value
        : hljs.highlightAuto(txt).value;
    } catch(e) {
      highlighted = txt;
    }
    return '<pre><code class="hljs language-' + lang + '">' + highlighted + '</code></pre>';
  });
}

const src = 'architect/docs', out = path.join(src, 'html');
fs.mkdirSync(out, { recursive: !0 });

const docs = {};
for (const f of fs.readdirSync(src).filter(f => f.endsWith('.md') && !f.startsWith('_') && f !== 'index.md').sort())
  docs[f.replace('.md', '')] = fs.readFileSync(path.join(src, f), 'utf-8');

const groups = [
  ['\u5165\u95e8',     ['quickstart', 'architecture', 'best-practices']],
  ['\u6838\u5fc3\u7cfb\u7edf', ['subsystem', 'ecs', 'event', 'scheduler']],
  ['\u8fdb\u9636',     ['ui', 'plugin', 'plugins', 'bus', 'profiler']],
  ['\u53c2\u8003',     ['math', 'molang', 'persona', 'fsm', 'utils']]
];

function navHtml(cur) {
  let h = '';
  for (const [label, keys] of groups) {
    h += '<div class="group">' + label + '</div>';
    for (const k of keys) {
      if (!docs[k]) continue;
      const t = docs[k].split('\n')[0].replace(/^#\s*/, '').trim() || k;
      h += '<a href="' + k + '.html"' + (k === cur ? ' class="active"' : '') + '>' + t + '</a>';
      const h2s = docs[k].match(/^## (.+)$/gm);
      if (h2s) for (let i = 0; i < Math.min(h2s.length, 6); i++) {
        const s = h2s[i].replace(/^##\s*/, '').replace(/[`*]/g, '').slice(0, 42);
        h += '<a href="' + k + '.html#' + s.toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/-+$/, '') + '" class="sub">' + s + '</a>';
      }
    }
  }
  return h;
}

function fixMdLinks(html) {
  return html.replace(/href="(\w+)\.md"/g, 'href="$1.html"');
}

function anchors(body) {
  return body.replace(/<h2>(.*?)<\/h2>/g, (_, t) =>
    '<h2 id="' + t.toLowerCase().replace(/<[^>]*>/g, '').replace(/[^a-z0-9]+/g, '-').replace(/-+$/, '') + '">' + t + '</h2>');
}

// Build search index
const searchIndex = [];
for (const [name, md] of Object.entries(docs)) {
  const title = md.split('\n')[0].replace(/^#\s*/, '').trim() || name;
  searchIndex.push({ id: name + '.html', title: title, type: 'page' });
  const h2s = md.match(/^## (.+)$/gm);
  if (h2s) for (const h of h2s) {
    const t = h.replace(/^##\s*/, '').trim();
    const anchor = t.toLowerCase().replace(/<[^>]*>/g, '').replace(/[^a-z0-9]+/g, '-').replace(/-+$/, '');
    searchIndex.push({ id: name + '.html#' + anchor, title: t, type: 'section', parent: title });
  }
}
fs.writeFileSync(path.join(out, 'search-index.json'), JSON.stringify(searchIndex), 'utf-8');
fs.writeFileSync(path.join('docs', 'search-index.json'), JSON.stringify(searchIndex), 'utf-8');

const SEARCH_HTML = [
'<div id="search-overlay" style="display:none;position:fixed;inset:0;z-index:999;background:rgba(0,0,0,.6);align-items:flex-start;justify-content:center;padding-top:12vh">',
'<div style="background:hsl(0 0% 6%);border:1px solid hsl(0 0% 14%);border-radius:.5rem;width:580px;max-width:90vw;max-height:70vh;display:flex;flex-direction:column;overflow:hidden">',
'<div style="display:flex;align-items:center;padding:.75rem 1rem;border-bottom:1px solid hsl(0 0% 14%)">',
'<svg style="width:1.2rem;height:1.2rem;margin-right:.6rem;opacity:.4;flex-shrink:0" viewBox="0 0 24 24" fill="none" stroke="hsl(0 0% 63.9%)" stroke-width="2"><circle cx="11" cy="11" r="8"/><path d="m21 21-4.35-4.35"/></svg>',
'<input id="search-input" type="text" placeholder="\u641c\u7d22\u6587\u6863..." autofocus style="flex:1;background:0 0;border:0;outline:0;color:hsl(0 0% 98%);font-size:.95rem;font-family:inherit">',
'<kbd style="font-size:.72rem;padding:.15em .5em;border-radius:3px;background:hsl(0 0% 12%);color:hsl(0 0% 63.9%);border:1px solid hsl(0 0% 20%);margin-left:.5rem;flex-shrink:0">Esc</kbd>',
'</div>',
'<div id="search-results" style="flex:1;overflow-y:auto;padding:.4rem 0"></div>',
'<div id="search-empty" style="padding:1.5rem;text-align:center;color:hsl(0 0% 40%);font-size:.85rem;display:none">\u6ca1\u6709\u627e\u5230\u7ed3\u679c</div>',
'</div>',
'</div>'
].join('');

const SEARCH_JS = '<script>' +
'(function(){' +
'var idx=[];' +
'var r=document.getElementById("search-results");' +
'var e=document.getElementById("search-empty");' +
'var o=document.getElementById("search-overlay");' +
'var inp=document.getElementById("search-input");' +
'function openSearch(){o.style.display="flex";inp.value="";inp.focus();render([])}' +
'function closeSearch(){o.style.display="none"}' +
'function render(list){' +
'  e.style.display=list.length?"none":"block";' +
'  r.innerHTML=list.slice(0,20).map(function(x){' +
'    var t=x.type==="page"?"\u9875\u9762":"\u7ae0\u8282";' +
'    return \'<a href="\'+x.id+\'" class="sr">\'+' +
'      \'<span class="sr-t">\'+t+\'</span>\'+\'<span>\'+x.title+\'</span>\'+\'</a>\'' +
'  }).join("")' +
'}' +
'o.addEventListener("click",function(ev){if(ev.target===o)closeSearch()});' +
'function doSearch(q){' +
'  var t=q.toLowerCase();' +
'  if(!t)return render([]);' +
'  var f=idx.filter(function(x){' +
'    return x.title.toLowerCase().indexOf(t)>-1||(x.parent||"").toLowerCase().indexOf(t)>-1' +
'  });render(f)' +
'}' +
'inp.addEventListener("input",function(){doSearch(inp.value)});' +
'document.addEventListener("keydown",function(ev){' +
'  if((ev.ctrlKey||ev.metaKey)&&ev.key==="k"){ev.preventDefault();openSearch()}' +
'  if(ev.key==="Escape"&&o.style.display==="flex"){closeSearch();ev.stopPropagation()}' +
'});' +
'o.addEventListener("keydown",function(ev){' +
'  if(ev.key==="ArrowDown"){var a=r.querySelector("a");if(a){a.focus();ev.preventDefault()}}' +
'});' +
'fetch("search-index.json").then(function(rr){return rr.json()}).then(function(d){idx=d});' +
'})()' +
'</script>';

const LOGO_HTML = '<div class="logo">\nRonin<span>Netease</span>\n<button title="\u641c\u7d22 (Ctrl+K)" onclick="document.dispatchEvent(new KeyboardEvent(\'keydown\',{ctrlKey:!0,key:\'k\'}))" class="sr-btn"><svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="11" cy="11" r="8"/><path d="m21 21-4.35-4.35"/></svg></button>\n</div>';

const CSS = '<style>' +
':root{--b:0 0% 3.9%;--f:0 0% 98%;--c:0 0% 6%;--p:267 100% 70%;--s:0 0% 14%;--m:0 0% 63.9%;--r:.5rem}' +
'*,::before,::after{box-sizing:border-box;margin:0;padding:0;border:0 solid hsl(0 0% 14%)}' +
'html{scroll-behavior:smooth;-webkit-font-smoothing:antialiased}' +
'body{font-family:"Noto Sans","Noto Sans SC","Noto Sans JP","Noto Sans KR",Inter,-apple-system,system-ui,sans-serif;background:hsl(var(--b));color:hsl(var(--f));line-height:1.7;font-size:15px;zoom:1.25}' +
'nav{position:fixed;top:0;left:0;bottom:0;width:17rem;background:hsl(var(--b));border-right:1px solid hsl(0 0% 14%);overflow:hidden;z-index:50;display:flex;flex-direction:column}' +
'nav .logo{padding:.9rem 1.25rem;font-size:1.05rem;font-weight:700;border-bottom:1px solid hsl(0 0% 14%);color:hsl(var(--f));display:flex;align-items:center;gap:.3rem}' +
'nav .logo span{background:linear-gradient(135deg,hsl(var(--p)),hsl(267 100% 80%));-webkit-background-clip:text;-webkit-text-fill-color:transparent;font-weight:800}' +
'.sr-btn{margin-left:auto;background:0 0;border:0;cursor:pointer;color:hsl(0 0% 63.9%);padding:.2rem;border-radius:4px;display:flex;align-items:center;justify-content:center;transition:.12s;flex-shrink:0}' +
'.sr-btn:hover{background:hsl(0 0% 14%);color:hsl(0 0% 98%)}' +
'nav .pages{flex:1;overflow-y:auto;padding:.5rem 0}' +
'.group{padding:.75rem 1.25rem .2rem;font-size:.62rem;text-transform:uppercase;letter-spacing:.1em;color:hsl(var(--m));font-weight:600;opacity:.6}' +
'nav a{display:block;padding:.35rem 1.25rem;color:hsl(var(--m));text-decoration:none;font-size:.83rem;transition:.12s;border-left:2px solid transparent}' +
'nav a:hover,nav a.active{color:hsl(var(--f));background:hsl(var(--s) / .5);border-left-color:hsl(var(--p))}' +
'nav a.active{font-weight:600}' +
'nav a.sub{padding:.22rem 1.25rem .22rem 2.2rem;font-size:.76rem;opacity:.6}' +
'nav a.sub:hover{opacity:1}' +
'nav::-webkit-scrollbar,.pages::-webkit-scrollbar{width:4px}' +
'nav::-webkit-scrollbar-track,.pages::-webkit-scrollbar-track{background:transparent}' +
'nav::-webkit-scrollbar-thumb,.pages::-webkit-scrollbar-thumb{background:hsl(0 0% 25%);border-radius:4px}' +
'nav::-webkit-scrollbar-thumb:hover,.pages::-webkit-scrollbar-thumb:hover{background:hsl(0 0% 35%)}' +
'nav,.pages{scrollbar-width:thin;scrollbar-color:hsl(0 0% 25%) transparent}' +
'main{margin-left:17rem;display:flex;justify-content:center;padding:2rem 2.5rem}' +
'article{background:hsl(var(--c));border:1px solid hsl(0 0% 14%);border-radius:var(--r);padding:2.5rem 3rem;max-width:860px;width:100%}' +
'h1{font-size:2.25rem;font-weight:800;letter-spacing:-.03em;margin-bottom:1.5rem;padding-bottom:.75rem;border-bottom:1px solid hsl(0 0% 14%)}' +
'h2{font-size:1.3rem;font-weight:600;margin-top:2.5rem;margin-bottom:.75rem;padding-bottom:.35rem;border-bottom:1px solid hsl(0 0% 14%)}' +
'h3{font-size:1.1rem;font-weight:600;margin-top:2rem;margin-bottom:.5rem}' +
'h4{font-size:1rem;font-weight:600;margin-top:1.5rem;margin-bottom:.4rem;color:hsl(var(--m))}' +
'p{margin:.8rem 0;line-height:1.75}' +
'a:not(nav a){color:hsl(var(--p));text-decoration:underline}' +
'code{background:hsl(var(--s) / .5);padding:.12em .35em;border-radius:3px;font-size:.87em;font-family:"Noto Sans Mono","JetBrains Mono","Fira Code",Consolas,monospace}' +
'pre{background:hsl(var(--b));border:1px solid hsl(0 0% 14%);border-radius:var(--r);padding:1rem 1.25rem;overflow-x:auto;margin:1.25rem 0}' +
'pre code{background:0 0;padding:0;font-size:.83rem;line-height:1.6}' +
'table{border-collapse:collapse;width:100%;margin:1.5rem 0}' +
'td,th{border:1px solid hsl(0 0% 14%);padding:.55rem .85rem;text-align:left;font-size:.9rem}' +
'th{background:hsl(var(--s) / .5);font-weight:600}' +
'tr:nth-child(even){background:hsl(0 0% 7%)}' +
'blockquote{border-left:3px solid hsl(var(--p));padding:.5rem 1.1rem;margin:1.25rem 0;background:hsl(267 100% 70% / .04);border-radius:0 var(--r) var(--r) 0;font-size:.92rem;color:hsl(var(--m))}' +
'hr{border:0;border-top:1px solid hsl(0 0% 14%);margin:2rem 0}' +
'ol,ul{padding-left:1.5rem;margin:.75rem 0}' +
'li{margin:.35rem 0;line-height:1.75}' +
'strong{color:hsl(var(--f))}' +
'.sr{display:flex;align-items:center;padding:.5rem 1rem;text-decoration:none;color:hsl(0 0% 63.9%);font-size:.87rem;transition:.08s}' +
'.sr:hover,.sr:focus{background:hsl(0 0% 12%);color:hsl(0 0% 98%);outline:0}' +
'.sr-t{flex-shrink:0;width:1.8rem;font-size:.66rem;opacity:.5;text-transform:uppercase}' +
'@media(max-width:768px){nav{width:100%;position:relative;max-height:35vh}main{margin-left:0;padding:1rem}article{padding:1.5rem;border-radius:0}}' +
hljsCSS +
'</style>';

for (const [name, md] of Object.entries(docs)) {
  const body = fixMdLinks(anchors(highlightCodeBlocks(marked.parse(md, { breaks: !0, gfm: !0 }))));
  const html = '<!DOCTYPE html>\n<html lang="zh">\n<head>\n<meta charset="UTF-8">\n<meta name="viewport" content="width=device-width,initial-scale=1.0">\n<title>' + name + ' - RoninNetease v1.1.0</title>\n' + CSS + '\n</head>\n<body>\n<nav>\n' + LOGO_HTML + '\n<div class="pages">\n' + navHtml(name) + '\n</div>\n</nav>\n<main>\n<article>\n' + body + '\n</article>\n</main>\n'
    + SEARCH_HTML
    + '\n<script>(function(){var p=document.querySelector(".pages");var k="rns";var y=sessionStorage.getItem(k);if(y){p.scrollTop=parseInt(y,10)||0};p.addEventListener("scroll",function(){sessionStorage.setItem(k,p.scrollTop)});var as=document.querySelectorAll("nav a");for(var i=0;i<as.length;i++){as[i].addEventListener("click",function(){sessionStorage.setItem(k,p.scrollTop)})}})()</script>\n'
    + SEARCH_JS
    + '\n</body>\n</html>';
  fs.writeFileSync(path.join(out, name + '.html'), html, 'utf-8');
  fs.writeFileSync(path.join('docs', name + '.html'), html, 'utf-8');
  console.log('\u2714 ' + name);
}

// Build index page
{
  const indexBody = [
    '<h1>RoninNetease v1.1.0 \u6587\u6863</h1>',
    '<p>RoninNetease \u662f\u4e00\u4e2a\u4e13\u4e3a\u7f51\u6613\u7248\u300a\u6211\u7684\u4e16\u754c\u300b\u8bbe\u8ba1\u7684 ECS\u6a21\u7ec4\u6846\u67b6\u3002\u6b64\u6587\u6863\u6db5\u76d6\u4ece\u5165\u95e8\u5230\u8fdb\u9636\u7684\u6240\u6709\u5185\u5bb9\u3002</p>'
  ];
  for (const [label, keys] of groups) {
    indexBody.push('<h2>' + label + '</h2>');
    indexBody.push('<ul>');
    for (const k of keys) {
      if (!docs[k]) continue;
      const t = docs[k].split('\n')[0].replace(/^#\s*/, '').trim() || k;
      indexBody.push('<li><a href="' + k + '.html">' + t + '</a></li>');
    }
    indexBody.push('</ul>');
  }
  const idxHtml = '<!DOCTYPE html>\n<html lang="zh">\n<head>\n<meta charset="UTF-8">\n<meta name="viewport" content="width=device-width,initial-scale=1.0">\n<title>RoninNetease v1.1.0 \u6587\u6863</title>\n' + CSS + '\n</head>\n<body>\n<nav>\n' + LOGO_HTML + '\n<div class="pages">\n' + navHtml('') + '\n</div>\n</nav>\n<main>\n<article>\n' + indexBody.join('\n') + '\n</article>\n</main>\n'
    + SEARCH_HTML
    + '\n<script>(function(){var p=document.querySelector(".pages");var k="rns";var y=sessionStorage.getItem(k);if(y){p.scrollTop=parseInt(y,10)||0};p.addEventListener("scroll",function(){sessionStorage.setItem(k,p.scrollTop)});var as=document.querySelectorAll("nav a");for(var i=0;i<as.length;i++){as[i].addEventListener("click",function(){sessionStorage.setItem(k,p.scrollTop)})}})()</script>\n'
    + SEARCH_JS
    + '\n</body>\n</html>';
  fs.writeFileSync(path.join(out, 'index.html'), idxHtml, 'utf-8');
  fs.writeFileSync(path.join('docs', 'index.html'), idxHtml, 'utf-8');
  console.log('\u2714 index');
}

console.log('Done \u2014 ' + Object.keys(docs).length + ' files + index');
