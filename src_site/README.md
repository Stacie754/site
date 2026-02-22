# src_site

Static website source for 喵喵大业 / Stacie Cat Care.

## Structure
- `index.html`, `services.html`, `environment.html`, `reviews.html`, `faq.html`, `contact.html`
- `en/` mirrored English pages
- `assets/css/styles.css` global styles
- `assets/js/site.js` nav + active link + footer year
- `assets/data/*.json` content datasets
- `sitemap.xml`, `robots.txt`, `llms.txt`, `llms-full.txt`

## Before production launch
1. (Optional) Add private channels like email/WeChat in `contact.html` and `en/contact.html`.
2. (Optional) If you want a form backend, replace the message-template block with your real Formspree endpoint.
3. Replace placeholder SVGs in `assets/images/` with real photos (WebP recommended).
4. If your final domain is not `https://qihang.github.io/staice-site/`, update:
   - all canonical/hreflang tags
   - Open Graph URLs
   - `sitemap.xml`
   - `robots.txt`
   - `llms.txt` / `llms-full.txt`
