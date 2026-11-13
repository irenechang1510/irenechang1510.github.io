#!/usr/bin/env python3
"""Convert LaTeX notes with Pandoc; assemble a static site without publishing sources."""
import argparse
import html
import json
from pathlib import Path
import re
import shutil
import subprocess

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / '_site'

def run(args, **kwargs):
    return subprocess.run(['pandoc', *args], check=True, capture_output=True, text=True, **kwargs).stdout

def resolve_equation_references(ast):
    """Give labeled equations HTML anchors and resolve Pandoc's eqref links."""
    labels = {}
    def equations(node):
        if isinstance(node, list):
            return [equations(item) for item in node]
        if not isinstance(node, dict):
            return node
        if node.get('t') == 'Math' and node['c'][0]['t'] == 'DisplayMath':
            tex = node['c'][1]
            found = re.search(r'\\label\{([^}]+)\}', tex)
            if found:
                label = found.group(1)
                number = str(len(labels) + 1)
                labels[label] = number
                tex = re.sub(r'\\label\{[^}]+\}', '', tex)
                tex = tex.replace(r'\begin{equation}', '').replace(r'\end{equation}', '')
                node['c'][1] = tex + r'\tag{' + number + '}'
                return {'t': 'Span', 'c': [[label, [], []], [node]]}
        return {key: equations(value) for key, value in node.items()}
    ast = equations(ast)
    def links(node):
        if isinstance(node, list):
            for item in node:
                links(item)
        elif isinstance(node, dict):
            if node.get('t') == 'Link':
                target = node['c'][2][0].removeprefix('#')
                if target in labels:
                    node['c'][1] = [{'t': 'Str', 'c': '(' + labels[target] + ')'}]
            for value in node.values():
                links(value)
    links(ast)
    return ast

def page(title, body, nested=False, math=False):
    prefix = '../' if nested else ''
    math_script = '<script defer src="https://cdn.jsdelivr.net/npm/mathjax@3.2.2/es5/tex-mml-chtml.js"></script>' if math else ''
    return f'''<!DOCTYPE html>
<html lang="en"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(title)} | Irene Chang</title><link rel="stylesheet" href="{prefix}assets/css/style.css">{math_script}</head>
<body><header class="site-header"><a class="wordmark" href="{prefix}index.html">Irene Chang</a>
<nav aria-label="Main navigation"><a href="{prefix}index.html">Home</a><a href="{prefix}notes.html" aria-current="page">Research Notes</a></nav></header>
<main id="main-content">{body}</main><footer>© Irene Chang</footer></body></html>'''

def build(drafts=False):
    if not shutil.which('pandoc'):
        raise SystemExit('Pandoc is required. On macOS: brew install pandoc')
    # Build fully in memory before replacing output, so errors preserve the last preview.
    pages, entries = {}, []
    for source in sorted((ROOT / 'notes-src').glob('*.tex')):
        text = source.read_text()
        meta = dict(re.findall(r'^%\s*(date|summary|draft):\s*(.*?)\s*$', text, re.M))
        if meta.get('draft', 'true').lower() not in ('true', 'false'):
            raise ValueError(f'{source.name}: draft must be true or false')
        draft = meta.get('draft', 'true').lower() == 'true'
        if draft and not drafts:
            continue
        date = meta.get('date', '')
        from datetime import date as Date
        Date.fromisoformat(date)
        ast = json.loads(run(['--from=latex', '--to=json', source.name], cwd=source.parent))
        title_meta = ast['meta'].get('title')
        if not title_meta:
            raise ValueError(f'{source.name}: add \\title{{Your title}}')
        title_doc = {'pandoc-api-version': ast['pandoc-api-version'], 'meta': {},
                     'blocks': [{'t': 'Plain', 'c': title_meta['c']}]}
        title = run(['--from=json', '--to=plain', '--wrap=none'], input=json.dumps(title_doc)).strip()
        ast = resolve_equation_references(ast)
        body = run(['--from=json', '--to=html5', '--mathjax', '--number-sections', '--wrap=none'], input=json.dumps(ast))
        summary = html.escape(meta.get('summary', ''))
        badge = ' · Draft preview' if draft else ''
        heading = f'<div class="notes-header"><p class="eyebrow">Research notes{badge}</p><h1>{html.escape(title)}</h1></div>'
        pages[f'{source.stem}.html'] = page(title, heading + '<article class="note-body">' + body + '</article>', True, True)
        entries.append((date, source.stem, title, summary, badge))
    intro = '<div class="notes-header"><p class="eyebrow">Notebook</p><h1>Research notes</h1><p>Notes on statistics, machine learning, and ideas from my research.</p></div>'
    if entries:
        listing = '<section class="section" aria-label="Notes">' + ''.join(
            f'<article class="research-item"><h2><a href="notes/{slug}.html">{html.escape(title)}</a></h2><p>{summary}</p></article>'
            for date, slug, title, summary, badge in sorted(entries, reverse=True)) + '</section>'
    else:
        listing = '<section class="empty-state"><h2>Notes coming soon</h2><p>I’ll share research notes here as they’re ready.</p></section>'
    OUT.mkdir(exist_ok=True)
    shutil.copy2(ROOT / 'index.html', OUT / 'index.html')
    shutil.copytree(ROOT / 'assets', OUT / 'assets', dirs_exist_ok=True)
    notes = OUT / 'notes'
    if notes.exists():
        shutil.rmtree(notes)
    notes.mkdir()
    for filename, content in pages.items():
        (notes / filename).write_text(content)
    if (ROOT / 'notes-src' / 'images').exists():
        shutil.copytree(ROOT / 'notes-src' / 'images', notes / 'images')
    archive = '<section class="section" aria-labelledby="archive-title"><h2 id="archive-title">Earlier work</h2><p>A collection of projects and writing from my undergraduate years.</p><a href="https://medium.com/@irenechang1510">Browse the archive on Medium ↗</a></section>'
    (OUT / 'notes.html').write_text(page('Research Notes', intro + listing + archive))
    (OUT / '.nojekyll').touch()
    print(f'Built {len(pages)} notes in _site/' + (' (including drafts)' if drafts else ''))

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--drafts', action='store_true', help='Include draft notes for local preview only')
    build(parser.parse_args().drafts)
