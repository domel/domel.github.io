# Dominik Tomaszuk Academic Website

This repository contains a Quarto-based academic website.

## Repository layout

- `site/`: Quarto project sources, page content, styles, scripts, and assets
- `references.bib`: bibliography source used to generate the publications page
- `.github/workflows/deploy.yml`: GitHub Pages build and deployment workflow

## Local workflow

```bash
cd site
quarto preview
```

To render the full site locally:

```bash
cd site
quarto render
```

The rendered output is written to `site/_site/` and is not intended to be committed.
