# Art pipeline (build 0.8)

Source: Snasen's photos in the project (cover photo + five halftone ink prints).

1. `extract.py` — flattens the lamp light and lifts each print's ink into a mask, halftone dots kept
   → `ink/{spikes,islands,bloom,figures,branches}.png`.
2. `make.py` — title plate, sleeves 01–15 (one print in ink, a second overprinted as a ghost),
   `paper-*.webp` backdrops, halftone texture. Does not touch the splats.
3. `sprites.py` — finds free-floating ink fragments and paper shapes enclosed by ink in all prints
   (thin threads cut by a small opening, edges restored from the original ink), lays each flat along its long axis,
   writes a numbered contact sheet to choose from.
4. `atlas.py` — packs the chosen numbers into `web/art/sprites.webp` + `sprites.json` by role:
   hit (falling targets), head (player), spark (spatter), drift (background).
Crops are seeded: re-running gives the same results. Paths point at the build workspace; adjust before CI use.
