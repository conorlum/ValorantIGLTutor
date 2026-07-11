# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

A single-script pipeline (`trackerScraper.py`) that scrapes Valorant match pages from tracker.gg (saved locally as complete webpages via browser automation), parses the raw HTML into structured per-round data, and computes a custom per-player, per-round "Impact" score based on kill order, economy state, post-plant timing, and trade windows. There is no package manager manifest, test suite, linter, or build step — this is a personal analysis tool run directly with `python trackerScraper.py`.

## What this hopes to be

A website using the Riot API for valorant matches to pull the same information as the scraping and showing the stats and graphs on the website.  Using the logic behind creating and analyzing the results of the matches show interesting results on the website.  

## Running it

```
python trackerScraper.py
```

The script prompts interactively for a match key in the form `<Map><MMDDYYHHMM>` (e.g. `Haven101725908`). The `__main__` block has most pipeline stages commented out — only `measureOutgoingImpact(filename)` runs by default, which means a corresponding JSON file must already exist under `TrackerHTMLJsons/` before running (see Pipeline stages below for how to regenerate one).

No `requirements.txt` exists. Dependencies inferred from imports: `pyautogui`, `Pillow` (`PIL`), `imagehash`, `networkx`, `matplotlib`, and `pydot` (required by `networkx.drawing.nx_pydot.graphviz_layout`, which also needs Graphviz installed on the system).

### Per-machine config (edit before running on a new machine)

At the top of `trackerScraper.py`:
- `User` — Windows username, used to build absolute `C:\Users\{User}\...` paths throughout the script (paths are not portable/relative).
- `resolutionScaling` — scales `pyautogui` mouse-move offsets in `moveOneRoundOver()`; set to `1.5` for 4K displays.

## Pipeline stages

The script is one file organized into sequential stages, each consuming the previous stage's output. Stage functions are mostly invoked ad hoc from `__main__` (commented in/out) rather than as a single orchestrated run:

1. **Scrape (GUI automation)** — `createMapFolder`, `clickAndSaveRound`, `saveAllRounds`, `moveOneRoundOver`, `cleanUpFiles`. Uses `pyautogui` to drive the browser's "Save As" dialog and save each round of a tracker.gg match as a complete webpage (HTML + `_files/` assets) into `TrackerPages/<filename>_ALL_FILES/<filename>-Round<N>/`. This requires the match page to already be open in a browser window and the mouse positioned correctly — it's a semi-manual, human-supervised loop (`input()` prompts between batches of 20 rounds).

2. **Condense to JSON** — `parseOutRoundCount` (reads total rounds from the saved page's team-A/team-B round-win counters), `saveHTMLToJson` (extracts just the relevant `<body>`-adjacent HTML line per round and writes one combined JSON per match to `TrackerHTMLJsons/<filename>.json`), `loadHTMLSFromJson`.

3. **Extract structured data from HTML** — `parseEconPerRound`, `parseRoundOutcome`, `parseRoundKillList`, `parseTeamPlayers`, `parsePlayerRoundInfo`. These parse tracker.gg's HTML via string-splitting on known CSS class name fragments (not a real HTML parser) — the class names being matched against are documented in `TrackerClasses.txt`. This is brittle to tracker.gg frontend changes; if parsing breaks, check whether these class-name substrings still appear in a freshly saved page.

4. **Icon classification via perceptual hashing** — `agentDisplayIconLookup`, `weaponNewImageLookup`. Saved pages embed agent/weapon icons as numbered local image files (`displayicon<N>.png`, `newimage<N>.png`); these functions identify which agent/weapon an icon represents by comparing `imagehash.average_hash` against the reference sets in `agentDisplayIconPictureReferences/` and `weaponNewImagePictureReferences/` (closest hash wins, distance > 5 is rejected as `"BAD CLASSIFICATION!"`). Adding a new agent/weapon means dropping a new reference PNG into the matching folder.

5. **Impact calculation** — the core analytics, all feeding `measureOutgoingImpact`:
   - `calculateKillOrderBonus` — a `networkx` `DiGraph` of every man-advantage state (`5v5` → ... → `0v0`) with a hand-tuned bonus weight on each edge, used to reward/penalize kills based on how much they swung the round state.
   - `calculateEconSwingRiskFactor` — estimates how "econ-swingy" a round is based on team loadouts/remaining credits and buy thresholds, with special-cased pistol/anti-eco rounds (round 1/13, 2/14, 12/24).
   - `calculateTimeFactor` — weights kills near/after plant or during post-plant defuse windows more heavily.
   - `calculateTradedFactor` — discounts a death's negative impact if the killer was traded back within 10s.
   - `calculateEconDifferential` — categorizes each side's loadout value (save/econ/full-buy) and factors the mismatch into kill value.
   - `calculateDamageAndAssists_KillOrderSum_KillFactorAverage` and `calculateRoundImpact` combine the above into per-round `killImpact`/`deathImpact`/`Impact` for every player.
   - `displayImpact` prints players ranked by average `Impact`; `createAndDisplayKillOrderGraph` renders a `matplotlib` graph of one player's kill/death transitions through the man-advantage state graph.

## Data layout / naming convention

Match keys follow `<MapName><MMDDYYHHMM>` (e.g. `Haven101725908` = Haven, played 10/17, ~08:xx) and are used as the lookup key across all of these directories:

- `TrackerPages/<key>_ALL_FILES/` — raw saved webpages per round (large, browser-snapshot output of stage 1).
- `TrackerHTMLJsons/<key>.json` — condensed per-round HTML produced by stage 2; this is what all downstream parsing (`loadHTMLSFromJson`) actually reads.
- `agentDisplayIconPictureReferences/*.png` — one reference icon per agent, filename is the agent name (`KAYO.png` is looked up but normalized to display as `"KAY/O"`).
- `weaponNewImagePictureReferences/*.png` — one reference icon per weapon, filename is the weapon name.
- `TrackerClasses.txt` — a running notes file of tracker.gg CSS class-name fragments used as string-split anchors throughout stage 3; consult/update this when HTML parsing breaks.
