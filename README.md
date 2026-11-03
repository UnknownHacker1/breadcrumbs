# Breadcrumbs

Breadcrumbs checks what your photos give away about where you live and go, and makes clean copies you can share. It was built for SafeSpace Hacks (2026).

Most phones save the exact GPS location, the time and the phone model inside every photo, and many ways of sharing keep it: email attachments, "send as file" in chat apps, cloud share links, and some marketplaces and forums. One photo leaks one place. A few photos show a pattern, such as where you sleep and where you are on weekday mornings. Existing EXIF viewers show raw numbers. Breadcrumbs says what those numbers mean for your safety.

## Try it

Open https://unknownhacker1.github.io/breadcrumbs/, or open `index.html` locally in a modern browser. Click "Try sample photos" or drop in your own. Nothing is uploaded: every check runs in the page, and there is no account, analytics or map service.

## How it works

1. **Read.** A hand-written metadata reader, with no libraries, finds the Exif block in JPEG, PNG, WebP and HEIC, reads the TIFF tag directories in both byte orders, and reads the GPS sub-directory. It also reads GPS written as XMP text and lists other metadata blocks (IPTC, comments, maker data) so nothing is silently ignored.
2. **Group and label.** Photos within 120 m of each other (great-circle distance) are grouped into one place. A place is labelled "may be your home" when at least 2 photos there were taken in the evening or early morning, on at least 2 different days, and they make up at least half of the photos at that place. "May be your school or work" uses the same rule for weekday daytime photos. The reason is shown next to the label.
3. **Map.** The places are drawn as SVG to scale with a scale bar, using a local flat projection in meters. No map tiles are requested.
4. **Clean and verify.** Each photo is redrawn through `createImageBitmap` (which respects orientation) and a canvas into a new JPEG with no hidden data. Breadcrumbs reads every new file back, block by block, and passes it only if nothing is left except the image data, the JFIF header and a color profile. Your originals are never changed. If any file could not be read, the verdict says so instead of turning green.

The sample set is 7 synthetic photos: 4 "home" photos, 2 "school" photos on weekday mornings and 1 screenshot with no location. Before cleaning, 6 of 7 reveal a location. After, 0 of 7.

## Rebuild

Python 3, standard library only. From the repo root:

```
python build.py
```

This reads `src/src.html` and `src/samples/samples.json` and rewrites `index.html`.

To regenerate the sample photos (requires Pillow):

```
python src/make_samples.py src/samples
```

The script writes the EXIF bytes by hand, so every tag is under control, and it overwrites the JPEGs and `samples.json` in `src/samples`. The samples use public locations in New York (Central Park and a public library), not anyone's real home.

## Credits

All code and the sample images were written for this project. There are no third-party libraries, datasets or assets in the page. The sample generator uses Pillow.

## Limitations

- It cannot see clues in the picture itself: house numbers, street signs, school logos, the view from a window.
- HEIC hidden data is read, but most browsers cannot redraw HEIC, so no clean copy is made for it. RAW files are not read. Export both as JPEG first.
- On iPhone, the browser's photo picker may strip location before Breadcrumbs sees it, while the same photo sent as an email attachment keeps it. Check the files you will actually send.
- The home and work labels are guesses based on time patterns. A night-shift worker would be labelled wrongly.
- Cleaning re-encodes the photo (JPEG quality 0.92) in sRGB, so wide-color photos may look slightly less vivid. Privacy browsers that block canvas may produce blank copies.

## AI assistance

Claude (Anthropic), via Claude Code, helped write and test the code and draft the write-up. The author chose the idea and reviewed everything.

## License

MIT. See `LICENSE`.
