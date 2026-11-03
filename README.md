# BeatBomBasement

A rhythm game played to *Music for Drone* by Snasen. Steer a signal line under falling hits and pulse in time with the music, through all 15 tracks of the album.

**Play it:** https://bbb.widr.one

Free to play in the browser on Windows, Mac and phones. No accounts, no cookies, no tracking.

## How to play

**Signal mode** (default). An oscilloscope trace of the track runs along the bottom of the screen, and you steer its head left and right. Hits fall where their sound sits: bass on the left, highs on the right. Be under a hit and pulse as it lands. When a drone sustains, keep the head inside the band until it ends.

**Lanes mode.** A classic four-lane highway, for players who prefer it.

| | Keyboard | Controller | Touch |
|---|---|---|---|
| Steer (Signal) | A / D or ← / → | Left stick or D-pad | Drag |
| Pulse (Signal) | Space, J, K or ↑ | A, B, X, Y, RB or RT | Tap |
| Lanes | D F J K or arrows | D-pad, or X A Y B | Tap the columns |
| Pause | Esc | Start | Pause button |
| Switch mode (menu) | — | LB / RB | Mode buttons |
| Calibrate offset (menu) | — | Y | Bottom of the track list |

Each track has Easy, Normal and Hard charts. Timing windows are ±45 ms (Perfect), ±90 ms (Great) and ±135 ms (Good).

### Before you play

- **Calibrate your audio offset.** Use "Calibrate audio offset" at the bottom of the track list: tap along to 20 clicks, and the game suggests an offset for your speakers or headphones. Bluetooth headphones usually need +150 ms or more.
- **Controller players:** browsers only allow sound after one click or key press on the page. Do that once, and the controller works for everything after it.
- Controllers need the `https://` address. Chrome and Edge are tested; Safari and Firefox should work but haven't been checked yet.

## Credits

- **Music:** Snasen, *Music for Drone* (Sellout! Music, 2015). The score for Tonje Hessen Schei's documentary *Drone* (2014).
- **Artwork:** Snasen. The cover and five halftone ink prints, photographed and cut into the game's sleeves, backdrops and sprites.
- **Game:** design, code and charts built with Claude (Anthropic).

## Licence

The code in this repository is licensed under the GPL-3.0 (see `LICENSE`).

**The music and artwork are not covered by that licence.** The audio in `web/audio/` and the images in `web/art/` are © Snasen / Sellout! Music. They are included with permission so the game can be played, and may not be reused, redistributed or remixed outside this game without the rights holders' permission.

## Repository layout

```
web/                 the site, published as-is to bbb.widr.one
  index.html         the whole game (HTML, CSS and JavaScript in one file)
  tracks.json        setlist: title, audio file, chart, length, tempo, loudness gain per track
  audio/             the album, AAC .m4a, one file per track (NN-title-vN.m4a)
  charts/            one chart file per track (NN.json): Signal + Lanes × Easy/Normal/Hard
  art/               sleeves, backdrops, cover plate and the sprite sheet (sprites.webp + sprites.json)
scripts/
  charts/            chart pipeline: analyse audio, detect the beat grid, bake and check charts
  art/               art pipeline: lift ink from the photos, make sleeves and backdrops, cut and pack sprites
.github/workflows/   deploy.yml: publishes web/ to GitHub Pages on every push to main
```

## Updating the site

Every push to `main` deploys automatically: open the **Actions** tab to watch it. The deploy step refuses lossless audio (WAV/AIFF/FLAC) in `web/` and any file over 50 MB.

To publish a new build: unzip it and drag its `web/` (and `scripts/` if included) folder into the repo root on GitHub. GitHub merges the files and overwrites any that changed.

When an audio file changes, give it a new version in its name (`-v2.m4a`) and update `tracks.json`, so returning players don't get a cached old copy.

## Running it locally

The game loads its tracks, charts and art with `fetch`, so it needs a local web server rather than opening `index.html` directly:

```sh
cd web
python3 -m http.server 8000
```

Then open http://localhost:8000. Controllers work on `localhost` as well as on https.

## How the charts are made

Charts are generated from the audio, then meant to be hand-tuned:

1. Each track is analysed for onsets (where sounds start), their pitch, and its loudness.
2. Tracks with a steady tempo get a beat grid (03, 05, 07, 08 lock to exact studio tempos), and their hits snap to it. Free-time tracks follow the audio directly.
3. Each difficulty keeps only hits above a strength threshold, so quiet sustained passages become bands instead of filling up with weak hits.
4. Every chart is checked by a bot that steers at full speed: every hit must be reachable, and hits must keep a minimum gap.
5. Each chart stores a short fingerprint of its audio. On load the game checks the browser decoded the file with the same timing and corrects it if not.

Loudness is evened out in the game: each track plays at about −15 LUFS, with true peaks kept under −1 dBTP.
