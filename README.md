# alexgiboi.com

Personal website of Ion-Alexandru Giboi. Plain static HTML and CSS: no build step, no server, no database.

Everything public lives in `public/`:

- `index.html` – homepage
- `factfocus/` – FactFocus Labs project page
- `library/` – the Library (explainers, maps, tools)
- `assets/` – shared stylesheet and the contact-form script
- `404.html`, `robots.txt`, `sitemap.xml`, `favicon.svg`

Hosted on Cloudflare Workers (static assets, see `wrangler.jsonc`): every change to `main` is published automatically.
Build command: none. Deploy command: `npx wrangler deploy`.

## Analytics

Cloudflare Web Analytics (cookieless). Every HTML page includes this snippet just before `</body>`; add it to any new page:

```html
<!-- Cloudflare Web Analytics --><script type='module' src='https://static.cloudflareinsights.com/beacon.min.js' data-cf-beacon='{"token": "7d9db5e07c304e999664d641552d4d91"}'></script><!-- End Cloudflare Web Analytics -->
```
