# Irene Chang — personal website

Static academic website with LaTeX research notes, converted to HTML by Pandoc and rendered with MathJax.

## Write and preview notes

Pandoc is already installed on this computer. On a new Mac, install it with `brew install pandoc`. Python 3 is also required; no Python packages or LaTeX installation are needed to build the website.

1. Edit `notes-src/first-note.tex` in your preferred LaTeX editor, or copy it to a new `.tex` file in `notes-src/`. The filename becomes the URL: `notes-src/my-topic.tex` → `/notes/my-topic.html`.
2. Set `\title{...}` and the three comments at the top:
   ```tex
   % date: 2026-11-12
   % summary: A short description for the notes index.
   % draft: true
   ```
   Dates must use `YYYY-MM-DD`. Notes default to drafts if the draft comment is omitted.
3. Run `python3 scripts/preview.py` from the repository directory.
4. Open http://localhost:8001/notes.html. Save your `.tex` file and refresh the browser; the preview rebuilds automatically. Drafts are included and labeled in this local preview.
5. When ready, change `% draft: true` to `% draft: false`. Commit and push to `main` to trigger the deployment workflow once GitHub Pages is configured below.

The starter is a draft, not a published research note. There is no need to edit generated HTML or manually add note links: the notes index is generated automatically, newest first.

## LaTeX support

Use ordinary `article` documents with `\begin{document}` / `\end{document}`, headings, paragraphs, lists, links, inline/display equations, aligned equations, matrices, and simple math macros. The starter demonstrates this format. `\maketitle` is handled by the website template.

For figures, put browser-compatible PNG/JPEG/SVG files in `notes-src/images/`, then use `\includegraphics{images/your-figure.png}`. That folder is copied into the website. Avoid spaces in image filenames.

Pandoc converts document structure rather than reproducing PDF page layout. Custom LaTeX packages, TikZ, complex tables, theorem environments, and cross-references may need additional conversion support. Ask for help incorporating those rather than assuming they will render identically. MathJax needs an internet connection for browser math rendering. A TeX engine is only needed if you also want to compile PDFs yourself.

## Build and deploy

`python3 scripts/build_notes.py` produces `_site/` with published notes only.
`python3 scripts/build_notes.py --drafts` includes drafts for preview.
The generated directory is ignored by Git. Edit source files instead.

For a one-time GitHub setup, go to repository **Settings → Pages → Build and deployment → Source → GitHub Actions**. The workflow in `.github/workflows/pages.yml` builds on pull requests and deploys pushes to `main`. No deployment has been activated by these local changes.

Only `_site/` is uploaded to Pages; `.tex` sources and draft pages are excluded from that artifact. Source files, including drafts, are still visible to anyone with access to the repository itself.

The original port-8000 preview serves source files directly. Use port 8001 for the generated site and automatic LaTeX builds.

## Edit the rest of the site

- `index.html`: biography, research, education, and experience.
- `assets/css/style.css`: shared styling.
- `notes.html`: fallback page for source-only previews; the build replaces it in `_site/`.
- `scripts/build_notes.py`: HTML templates and note conversion.

Original site template by [codewithsadee](https://github.com/codewithsadee/vcard-personal-portfolio).
