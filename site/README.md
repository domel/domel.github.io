# Academic Website with Quarto

This repository contains a static academic website built with Quarto. The site includes Markdown-authored pages, a publications page generated from the bibliography source, and a Bio page that links to a PDF while showing only the About section on the web.

The Quarto project root is this `site/` directory.

## Pages

- `index.qmd`: homepage
- `about.qmd`: profile and academic background
- `research.qmd`: research themes and projects
- `publications.qmd`: BibTeX-driven publications list
- `conferences.qmd`: conference talks and presentations
- `service.qmd`: reviewing activity and program committees
- `bio.qmd`: Bio landing page plus PDF output
- `contact.qmd`: contact details and institutional address

Shared content lives in `_partials/` so the website and Bio PDF reuse the same source material.
The publications list is generated during Quarto pre-render by `scripts/render_publications.py`.
The generated publications partial is kept in the repository so a clean checkout can render without a prior local build.

## Requirements

- Quarto 1.8+
- A LaTeX distribution for PDF builds such as TinyTeX or TeX Live

## Local workflow

Preview the site locally:

```bash
cd site
quarto preview
```

Render the full site, including the PDF version of Bio:

```bash
cd site
quarto render
```

Render only the PDF biography:

```bash
cd site
quarto render bio.qmd --to pdf
```

## Updating content

- Edit `_quarto.yml` to change the site title or navigation.
- Edit the files in `_partials/` to update page content without duplicating text.
- Edit the bibliography source file in the repository root to add or change publications.
- Keep `scripts/render_publications.py` if you want publications to stay sorted newest-first from BibTeX.
- Edit `styles.css` to adjust the visual design.

## Deployment

GitHub Actions builds the site on pull requests and deploys it to GitHub Pages on pushes to `main`. The workflow file lives at `../.github/workflows/deploy.yml`.
