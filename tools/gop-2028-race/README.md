# GOP 2028 race – build scripts

Not published (only `public/` is served). They generate `public/library/gop-2028-race/`:

- `poster.py` – the fight-card illustration: `hero-{en,it,ro}.webp` (1600×800), `hero-m-{en,it,ro}.webp` (1000×1250, phones) and `share-card.jpg` (1200×630). Needs Playwright with Chrome at `/usr/bin/google-chrome` and the Inter / Inter Display fonts.
- `page.py` – the article page in EN/IT/RO (text, the two inline SVG charts, sources), using the midterms post's styles.

Weekly update: edit the figures and text in both scripts (all three languages), run `python3 poster.py` then `python3 page.py`, check the images and the page, then commit and push to `main`.
