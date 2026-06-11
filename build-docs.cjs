#!/usr/bin/env node
const fs = require('fs'), path = require('path'), { marked } = require('marked'), hljs = require('highlight.js');
marked.setOptions({ highlight: (c, l) => l && hljs.getLanguage(l) ? hljs.highlight(c, { language: l }).value : hljs.highlightAuto(c).value, breaks: !0, gfm: !0 });

const src = 'architect/docs', out = path.join(src, 'html');
fs.mkdirSync(out, { recursive: !0 });

const docs = {};
for (const f of fs.readdirSync(src).filter(f => f.endsWith('.md') && !f.startsWith('_') && f !== 'index.md').sort())
  docs[f.replace('.md', '')] = fs.readFileSync(path.join(src, f), 'utf-8');

const groups = [
  ['Getting Started', ['quickstart', 'architecture', 'best-practices']],
  ['Core Systems',     ['subsystem', 'ecs', 'event', 'scheduler']],
  ['Advanced',         ['ui', 'plugin', 'bus', 'profiler']],
  ['Reference',        ['math', 'utils', 'fsm']]
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

function anchors(body) {
  return body.replace(/<h2>(.*?)<\/h2>/g, (_, t) =>
    '<h2 id="' + t.toLowerCase().replace(/<[^>]*>/g, '').replace(/[^a-z0-9]+/g, '-').replace(/-+$/, '') + '">' + t + '</h2>');
}

// shadcn/ui dark design tokens — compact inline
const CSS = `<style>
:root{--b:0 0% 3.9%;--f:0 0% 98%;--c:0 0% 6%;--p:267 100% 70%;--s:0 0% 14%;--m:0 0% 63.9%;--r:.5rem}
*,::before,::after{box-sizing:border-box;margin:0;padding:0;border:0 solid hsl(0 0% 14%)}
html{scroll-behavior:smooth;-webkit-font-smoothing:antialiased}
body{font-family:Inter,-apple-system,system-ui,sans-serif;background:hsl(var(--b));color:hsl(var(--f));line-height:1.7;font-size:15px}
nav{position:fixed;top:0;left:0;bottom:0;width:260px;background:hsl(var(--b));border-right:1px solid hsl(0 0% 14%);overflow:hidden;z-index:50;display:flex;flex-direction:column}
nav .logo{padding:.9rem 1.25rem;font-size:1.05rem;font-weight:700;border-bottom:1px solid hsl(0 0% 14%);color:hsl(var(--f));display:flex;align-items:center;gap:.3rem}
nav .logo span{background:linear-gradient(135deg,hsl(var(--p)),hsl(267 100% 80%));-webkit-background-clip:text;-webkit-text-fill-color:transparent;font-weight:800}
nav .pages{flex:1;overflow-y:auto;padding:.5rem 0}
.group{padding:.75rem 1.25rem .2rem;font-size:.62rem;text-transform:uppercase;letter-spacing:.1em;color:hsl(var(--m));font-weight:600;opacity:.6}
nav a{display:block;padding:.35rem 1.25rem;color:hsl(var(--m));text-decoration:none;font-size:.83rem;transition:.12s;border-left:2px solid transparent}
nav a:hover,nav a.active{color:hsl(var(--f));background:hsl(var(--s) / .5);border-left-color:hsl(var(--p))}
nav a.active{font-weight:600}
nav a.sub{padding:.22rem 1.25rem .22rem 2.2rem;font-size:.76rem;opacity:.6}
nav a.sub:hover{opacity:1}
nav::-webkit-scrollbar,.pages::-webkit-scrollbar{width:4px}
nav::-webkit-scrollbar-track,.pages::-webkit-scrollbar-track{background:transparent}
nav::-webkit-scrollbar-thumb,.pages::-webkit-scrollbar-thumb{background:hsl(0 0% 25%);border-radius:4px}
nav::-webkit-scrollbar-thumb:hover,.pages::-webkit-scrollbar-thumb:hover{background:hsl(0 0% 35%)}
nav,.pages{scrollbar-width:thin;scrollbar-color:hsl(0 0% 25%) transparent}
main{margin-left:260px;display:flex;justify-content:center;padding:2rem 2.5rem}
article{background:hsl(var(--c));border:1px solid hsl(0 0% 14%);border-radius:var(--r);padding:2.5rem 3rem;max-width:860px;width:100%}
h1{font-size:2.25rem;font-weight:800;letter-spacing:-.03em;margin-bottom:1.5rem;padding-bottom:.75rem;border-bottom:1px solid hsl(0 0% 14%)}
h2{font-size:1.3rem;font-weight:600;margin-top:2.5rem;margin-bottom:.75rem;padding-bottom:.35rem;border-bottom:1px solid hsl(0 0% 14%)}
h3{font-size:1.1rem;font-weight:600;margin-top:2rem;margin-bottom:.5rem}
h4{font-size:1rem;font-weight:600;margin-top:1.5rem;margin-bottom:.4rem;color:hsl(var(--m))}
p{margin:.8rem 0;line-height:1.75}
a:not(nav a){color:hsl(var(--p));text-decoration:underline}
code{background:hsl(var(--s) / .5);padding:.12em .35em;border-radius:3px;font-size:.87em;font-family:"JetBrains Mono",monospace}
pre{background:hsl(var(--b));border:1px solid hsl(0 0% 14%);border-radius:var(--r);padding:1rem 1.25rem;overflow-x:auto;margin:1.25rem 0}
pre code{background:0 0;padding:0;font-size:.83rem;line-height:1.6}
table{border-collapse:collapse;width:100%;margin:1.5rem 0}
td,th{border:1px solid hsl(0 0% 14%);padding:.55rem .85rem;text-align:left;font-size:.9rem}
th{background:hsl(var(--s) / .5);font-weight:600}
tr:nth-child(even){background:hsl(0 0% 7%)}
blockquote{border-left:3px solid hsl(var(--p));padding:.5rem 1.1rem;margin:1.25rem 0;background:hsl(267 100% 70% / .04);border-radius:0 var(--r) var(--r) 0;font-size:.92rem;color:hsl(var(--m))}
hr{border:0;border-top:1px solid hsl(0 0% 14%);margin:2rem 0}
ol,ul{padding-left:1.5rem;margin:.75rem 0}
li{margin:.35rem 0;line-height:1.75}
strong{color:hsl(var(--f))}
@media(max-width:768px){nav{width:100%;position:relative;max-height:35vh}main{margin-left:0;padding:1rem}article{padding:1.5rem;border-radius:0}}
</style>`;

for (const [name, md] of Object.entries(docs)) {
  const body = anchors(marked.parse(md));
  const html = '<!DOCTYPE html>\n<html lang="zh">\n<head>\n<meta charset="UTF-8">\n<meta name="viewport" content="width=device-width,initial-scale=1.0">\n<title>' + name + ' - RoninNetease v1.1.0</title>\n' + CSS + '\n</head>\n<body>\n<nav>\n<div class="logo">Ronin<span>Netease</span></div>\n<div class="pages">\n' + navHtml(name) + '\n</div>\n</nav>\n<main>\n<article>\n' + body + '\n</article>\n</main>\n</body>\n</html>';
  fs.writeFileSync(path.join(out, name + '.html'), html, 'utf-8');
  console.log('✔ ' + name);
}
console.log('Done — 12 files');