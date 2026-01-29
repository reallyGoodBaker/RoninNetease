import os
import io
import markdown

ROOT = os.path.dirname(os.path.dirname(__file__))
DOCS = os.path.join(ROOT, 'docs')
OUT = os.path.join(DOCS, '_site')

TEMPLATE = u'''<!doctype html>
<html>
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>{title}</title>
  <style>
    body{{font-family:Segoe UI, Roboto, Arial, sans-serif; padding:24px; max-width:900px; margin:0 auto}}
    pre {{ background:#f6f8fa; padding:12px; overflow:auto }}
    code {{ background:#f6f8fa; padding:2px 4px }}
  </style>
</head>
<body>
{content}
</body>
</html>'''


def ensure_dir(path):
    if not os.path.exists(path):
        os.makedirs(path)


def convert_file(src, dst):
    with io.open(src, 'r', encoding='utf-8') as f:
        md = f.read()
    html = markdown.markdown(md, extensions=['fenced_code', 'tables', 'toc'])
    title = os.path.splitext(os.path.basename(src))[0]
    page = TEMPLATE.format(title=title, content=html)
    with io.open(dst, 'w', encoding='utf-8') as f:
        f.write(page)


def main():
    ensure_dir(OUT)
    for root, dirs, files in os.walk(DOCS):
        # skip output dir
        if os.path.abspath(root).startswith(os.path.abspath(OUT)):
            continue
        rel = os.path.relpath(root, DOCS)
        out_dir = os.path.join(OUT, rel) if rel != '.' else OUT
        ensure_dir(out_dir)
        for fn in files:
            if fn.endswith('.md'):
                src = os.path.join(root, fn)
                dst = os.path.join(out_dir, fn[:-3] + '.html')
                print('Converting', src, '->', dst)
                convert_file(src, dst)

if __name__ == '__main__':
    main()
