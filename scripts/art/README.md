# Art pipeline (build 0.4)

Source: Snasen's photos in the project (cover photo + four halftone ink prints).

1. `extract.py`: flattens the phone-camera lighting (paper estimated with a wide max filter) and lifts each print's
   ink into a mask with the halftone dots kept → `ink/{spikes,islands,bloom,figures}.png`.
2. `make.py`: builds everything in `web/art/`:
   - `cover-plate.webp`: the cover photo turned so "Music for Drone" reads level, duotoned to the game palette.
   - `sleeve-00..15.webp`: one crop of a print per track, lit warm-to-cool like the photos.
   - `paper-*.webp`: the prints' paper areas as alpha, projected on the wall behind play.
   - `halftone.webp`: dot texture used inside bands.
   - `splat-0..5.webp` are re-cut by a follow-up step (see the 0.4 log); regenerate with care.
Crops are seeded, so re-running gives the same sleeves. Higher-resolution scans dropped in `src/` with the same
names give sharper output with no code changes.
