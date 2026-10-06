# Cooper Technology Group website

Static, framework-free build. Jinja2 templates compile to plain HTML.

## Build
    pip install jinja2
    python3 build.py            # -> dist/  (deploy this folder; it is not included in the zip, build it first)

## Deploy on Vercel
vercel.json tells Vercel to install Jinja2, run build.py and serve the dist/ folder.
Push this folder as the project root (build.py, vercel.json and src/ at the top level).

## Structure
    src/templates/   base layout, shared macros, one template per page
    src/data.py      all page copy and structured content
    src/posts.py     journal articles
    src/assets/      main.css (design tokens at the top), main.js (all motion and interaction)
    assets/img/      responsive WebP images (800 / 1600 / 2400 widths) and Open Graph JPGs
    dist/            production output, including sitemap.xml and robots.txt

## Before launch
- Contact form: set data-endpoint on #project-form in src/templates/contact.html
  (Formspree, Netlify Forms, or your own handler). Until then it asks visitors to call.
- Swap the typographic logo mark in src/templates/_macros.html (mark) for the real Cooper logo.
- Add real client testimonials if available (none existed on the current site).
- Journal dates are set to 2026; adjust to the real publish dates.
- Photography is from Unsplash (free licence). Replace with Cooper project photography over time.
