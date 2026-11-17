# Video Studio

Ramesh's free toolkit for making videos with code. Separate from GymBhai (`~/gymbahi`). Reuse what is here instead of rebuilding it: that is the point of this folder, and it saves tokens.

## Rules

- **Free tools only.** No paid APIs, connectors or plans (Magnific, ElevenLabs, Veo credits, YouTube "Promote"). Say so before suggesting anything that costs money.
- **Finished files go to `~/Downloads/`**, never only to a temp folder. Lumi Land: one folder per episode, `~/Downloads/Lumi Land/Episode NN - <Title>/`, holding the MP4, `…-thumbnail-a.jpg` / `-b.jpg` and `youtube-details.txt`. Channel art: `~/Downloads/Lumi Land/Channel Art/`. Check before overwriting.
- **Every finished video comes with its upload details**, given in the chat and saved as `youtube-details.txt` in the video's Downloads folder, without being asked:
  - **Title:** 3 options, recommended first, under 100 characters, search words first (e.g. "Learn Shapes for Toddlers ⭐ …").
  - **Description:** a hook line, who it's for, what the child learns, the characters, chapters (first at 0:00, each ≥10 s, times from `out/timeline.json`), a safety line (no scary scenes or flashing), a link to the earlier episode, subscribe, and 3 hashtags.
  - **Tags:** under 500 characters; include US and UK spellings (colors/colours).
  - **Education "Problems":** each question asked in the video, with its time.
  - **Thumbnail choice** (A main, B for "Test & compare"), the playlist, and the upload settings below.
- **Rendered frames** (`out/frames/`, 1–2 GB per episode) are deleted after Ramesh confirms that video is fine, never before: ask him, and delete them only on his yes. They are only for re-rendering one scene of that same video; future episodes never reuse them. Finished videos in `~/Downloads/` and the code and voices are never deleted with them.
- **Claude cannot watch or hear the result.** Check still frames (`--still`) before a full render, and ask Ramesh to watch once with sound before uploading.
- Running downloaded binaries (e.g. Rhubarb Lip Sync) is blocked by the permission settings; the lip sync here is our own (`visemes.py`).

## What is here

| Folder | What it makes | Status |
|---|---|---|
| `cartoon-3d/` | 3D toddler cartoons (Three.js, rendered frame by frame on the Mac GPU) | Used for Lumi Land ep 1–10 |
| `cartoon-2d/` | Flat 2D cartoon (SVG), first test of Rainbow Rescue Bus scenes 1–3 | Superseded by 3D |
| `channel-art/` | YouTube profile picture, banner, watermark (Lumi Land style) | Done |
| `reels/` | Short vertical comedy stories for Reels/Shorts (9:16, 1080×1920). Not Lumi Land: own characters, not for the kids' channel. Files go to `~/Downloads/Reels/<Title>/` | `fart-tax/`: built with the toy 3D characters (1:48). Ramesh also wants a more realistic look later: AI clips he makes in Google Flow from `prompts.html` (https://claude.ai/artifact/6sDsDEifQC5GBWg4v2QYrd), 3 of 27 done in `~/Downloads/Reels/Fart Tax/Clips/` |
| `app-demo/` | Product demo videos from a real web app + phone app (Playwright + iOS simulator + Maestro), captions, voice-over | Built for GymBhai; app-specific bits point into `~/gymbahi` |

Tools: `node_modules/` (Playwright 1.63, `npm install`), `.venv/` (edge-tts, numpy: `python3 -m venv .venv && .venv/bin/pip install -r requirements.txt`), Homebrew `ffmpeg`. Fonts: Fredoka (cartoons), Inter, Noto Sans Devanagari (Google Fonts).

## Lumi Land (the kids' channel)

YouTube: **Lumi Land**, handle `@lumiland321` (was "TRENDING NEPAL", renamed; old custom URL `/c/footballTalks-222` can't be deleted). Ages 2–5, English, US spelling ("colors"). Set every video **Made for kids**.

Channel keywords (Studio → Settings → Channel → Basic info; channel-wide, not per episode):
`kids learning videos, toddler learning videos, learning videos for toddlers, preschool learning, kids educational videos, baby learning videos, learn colors, learn shapes, learn numbers, counting for kids, early learning, kindergarten learning, kids cartoon, 3d cartoon for kids, animal cartoon for kids, kids cartoon english, toddler videos, nursery learning, Lumi Land, Rainbow Rescue Bus, Pip and friends`

Published: Ep 1 "Learn Colors" (https://youtu.be/QEoUifHEM8A, 15 Nov 2026; 332 views on day one), Ep 2 "The Shape Hunt" (15 Nov 2026). Ready to upload: Ep 3 "Counting 1 to 10", Ep 4 "Opposites", Ep 5 "The Fruit Picnic", Ep 6 "The Weather Day", Ep 7 "Touch Your Nose", Ep 8 "Things That Go", Ep 9 "How Do You Feel?", Ep 10 "ABC with Pip (A to H)". The channel holds only Lumi Land videos (old Trending Nepal videos are gone) and is set Made for Kids.

**Cast and voices** (edge-tts, Microsoft's free neural voices; `VOICES` in `episode.py`):

| Character | Look | Voice |
|---|---|---|
| Pip | baby panda, red T-shirt, blue shorts, brown eyes — the guide | `en-US-AnaNeural` -6% |
| Sunny | rounded yellow bus, two big blue eyes on the windshield, orange stripe, rainbow emblem, real window openings | `en-US-RogerNeural` +12Hz |
| Kitty | white kitten, blue eyes, pink bow | `en-GB-MaisieNeural` +25Hz |
| Ducky | yellow duckling, orange beak/feet | `en-NZ-MollyNeural` +45Hz |
| Froggy | green frog, big eyes, yellow backpack | `en-NZ-MitchellNeural` +35Hz |
| Birdie | sky-blue bird, orange beak | `en-CA-ClaraNeural` +70Hz |
| Lumi | glowing yellow star with a face — channel mascot (from ep 2) | `en-GB-LibbyNeural` +22Hz |

**Style rules:** bright toy-like 3D, no tone mapping (`NoToneMapping` keeps colours saturated), soft shadows, slow camera moves, no flashing (thunder is allowed as a soft rumble sound, without lightning). Colours: red `#e53935`, yellow `#f2b705`/`#ffd43b`, green `#43a047`, blue `#1e88e5`. Shapes always keep one colour: circle red, square blue, triangle green, star yellow. Every question to the viewer gets a 2-second answer pause with three dots on screen. Big rounded word pop-ups (Fredoka 700, white outline). Episodes run 4–5 min (toddler pace beats the "8 seconds per scene" of AI-video scripts).

**Worlds already built** (`buildWorlds()` in `episode.html`): Rainbow Valley (road, trees, flowers), red garden, rainbow road (scrolls past a still bus), yellow pond, green forest (stream, Froggy's leaf), blue-sky meadow (Birdie's tree, friendship tree), recap studio, sky rainbow. Skies: day, dusk, night (stars, moon) via `setSky()` (ep 2). Props: shape toys `shapeToy()`, outlines that light up side by side `outline()`/`lightSides()`, balloons, toy car, ball, apple, leaf, star, cookies, blocks, present, shape house. Ep 3 (`buildEpisode3()`): number balloons `numBalloon()`, number cards `numCard()`, `fish()`, `cookie()`, 7-band `rainbow7()`, Lumi's star friends `starFriend()` in sky `SLOT`s, cartoon hands overlay for finger counting. Numbers keep one colour each (`NUMC`). Ep 4 (`buildEpisode4()`): `giftBox()` with a lid (`setLid(box, 0..1)`) and cookies inside, a big and a small pink star, sound `rings()`, speed streaks on the road, Birdie's tear. Ep 5 (`buildEpisode5()`): fruits `banana()`, `peelBanana()` + `setPeel()`, `orange()`, `strawberry()`, `grapes()`, `watermelon()` + `setMelon(m, 0..1)` (opens to show red inside), `basket()` + `fill(b, n)`, a picnic blanket, `picnic()` (everyone around the blanket), `arc()` (pass a thing along an arc). `word()` and `game()` also take a fruit name (`FRUIT`). Ep 6 (`buildEpisode6()`): `weather(u, t, {grey, cover, rain, wind, puddles, cx})` (sky blue→grey→storm via `mixSky()`, grey clouds sliding over the sun, instanced rain, blowing leaves and wind streaks, puddle ripples), `setSky('storm')`, `greyCloud()`, `wxCard(kind)` weather cards, Kitty's `sunHat()`, `umbrella()` + `holdUmbrella()`, `kite()`, wipers on Sunny, `droplets()` (a puddle splash). Weather words are in `WX` (merged into `FRUIT` for `word()`). Ep 7 (`buildEpisode7()`): `ring(who, part, at, t, until)` (a glowing ring on a body part, drawn over the picture; `partPts()` knows where each part is on every character), Pip's poses `TOUCH.eyes/ears/nose/mouth/hands/tummy` and `FLAP`, `blinkAt()`, `stompLegs()`, body words in `PART`. Ep 8 (`buildEpisode8()`): `train()` + `setTrain()` (three cars, wheels turn, smoke puffs) on a `track()` in the forest, `boat()` (sailboat Ducky sits in), `plane()` (spinning propeller), `trafficLight()` + `setLight(tl, 'red'|'green')`, `placeCard('road'|'water'|'sky')`, `miniBus()` (a small copy of Sunny), Sunny's hubs light up; vehicle words in `VEH`. Engine/chug sounds in `sound.py`: `engine()`, `chug()`, `toot()`, `vroom()`. Ep 9 (`buildEpisode9()`): `feel(c, kind, t, k)` shows a feeling on any character (eyebrows built for everyone in `R.brows`, eye height, an expression mouth from `exprTextures()` while quiet, beak, shake/droop) for `happy sad angry scared surprised sleepy calm` (`FACE`, words in `FEEL`), `tear(c, t)`, the `HUG` pose, `breathe(c, k)`; sounds `breath()`, `rustle()`. Ep 10 (`buildEpisode10()`): letters keep the first eight number colours (`LETC`); `letterTex()`, `letterSprite()`, `letterBalloon()`, `letterCard()`, `bigLetter(L, x, y, z, at, u, t)` (a big floating letter; keep it out of the top band where words pop up), `abc(L, word, a, b, t)` ("A  APPLE" pop-up), `nestEgg()`; the ep 2 shape house is assembled in `buildEpisode10()`; `word()`/`game()` take a letter.

## Making a new episode (the shortcut)

1. **Script first.** Same format as ep 1/2 scripts: 24 scenes, ≤3 short lines each, `(Hold 2 seconds)` after questions. Reuse the cast; one new character at most.
2. `./new-episode.sh ep03-<slug> "Episode 03 - <Title>"` — copies the latest episode and makes the Downloads folder.
3. In `episode.py`, replace `SCENES`: beats are `('say', who, text)`, `('all', [whos], text)` (chorus), `('wait', s)`, `('cue', name)`, `('word', name, word)` (time of a word in the last line; from ep 4 a 4th item picks the k-th time it is said, and a 4th item on `'say'` sets that line's loudness, e.g. 1.35 loud, 0.4 whisper). Cue names the soundtrack already knows: `pop horn shape/color answer sparkle found jump n1..n10 c1..c4 d1..d4 w1..w4 h1..h4 r1..r10 clap wobble roll land done rainbow thanks subscribe`.
   **Sync rules** (Ramesh checks these when watching):
   - Choruses (`'all'`) are one or two words only. Each voice speaks at its own speed, so a longer chorus drifts apart by seconds. To count together, use `chant(whos, k)`: one line per number, all voices start together.
   - Every action on a number (hop, pop, badge, jump) goes on that number's cue (`n1..nk`), never on a separate cue placed after the line. A celebration jump lands on the last number: `chant(..., last=[('cue', 'jump')])`.
   - When a long line is split into short ones, line numbers change: use `ln(s, -1)` for a scene's last line, not a fixed number.
4. Run, from the episode folder (`../../.venv/bin/python`):
   `episode.py` (voices + `out/timeline.json`; voices are cached by text) → `visemes.py` (mouth shapes) → `sound.py` (music + effects + mix, edit `BIRDS/WATER/NIGHT` scene lists).
5. Write each scene's `draw(s, u, t)` in `episode.html` (`SCENES` object). Helpers: `place`, `seat` (bus windows), `animate` (talk, blink, hop, flap, walk, dance), `WAVE/POINT/POINT_R/CLAP/ARMS_UP`, `camPath(u, [[time, camX,Y,Z, lookX,Y,Z], ...])`, `ln(s, n)` (n-th line), `cu(s, cue)`, `NS(s, k)` (times of n1..nk), `game()` (find-the-thing scenes), `word()` (a shape or a number), `dots()`, `number()`, `tag(n, obj, at, t)` (number badge pinned over a counted thing; call after the camera moves), `sparkleAt()`, `lumiAt()`. Ep 4 added `pair(key, ta, tb, end, t)` (two opposite words side by side, blue then red; `PAIRS`), `stretch(c, k)` (squash and stretch), `duel()` (Lumi's two-thing guessing game), `travelled(u, speed)` (road scroll at a changing speed).
6. Check stills: `node render.cjs --still 12.5,40,80` → `out/still-*.png`. Fix framing (characters too close, objects hidden, things visible in the wrong scene).
7. Full render in two halves (about 1 min of render per minute of video):
   `node render.cjs --from 0 --to N/2 & node render.cjs --from N/2 --to N & wait` (N = total × 30).
8. Encode straight into the episode's Downloads folder:
   `ffmpeg -framerate 30 -i out/frames/%05d.jpg -i out/mix.wav -vf "fade=in:st=0:d=0.6,fade=out:st=<total-1.2>:d=1.2,format=yuv420p" -af "loudnorm=I=-16:TP=-1.5:LRA=11,aresample=48000" -c:v libx264 -crf 18 -preset slow -c:a aac -b:a 192k -ac 2 -shortest -movflags +faststart "<folder>/lumi-land-rainbow-rescue-bus-epNN.mp4"`
9. Thumbnails: edit `thumb.cjs` (two versions for YouTube "Test & compare"), save as 1280×720 JPG.
10. `youtube-details.txt`: title, description with chapters (each ≥10 s, first at 0:00), tags (<500 chars), Education "Problems" (time + question per line), settings below.

**Upload settings:** Made for kids · Category Education → type "Concept overview" · Remixing: Don't allow · Altered/synthetic content: No (cartoon) · Likes count hidden for now · Comments off (automatic) · Playlist with earlier episodes · no Premiere · never "Promote" (paid).

## Reels (new stories, new casts)

- **Characters first.** For a new cast, render character sheets and get Ramesh's OK before building any of the video.
- People come from one pattern, `makePerson()` in `reels/fart-tax/cast.js` (skin, hair, clothes, glasses, hats, phone); pose them with `act()`. Shiny gold/silver/brass uses `metal()`, which needs the reflection map made in `setup()` (`engine.js`).
- **Reel files** (`reels/fart-tax/`, run from that folder): `reel.py` (voice + `out/timeline.json`; shots are beats like `episode.py`, cue `f1..` = a toot that costs $10) → `sound.py` (music, toots, mix) → `reel.html` (overlays and one `SHOTS.sNN(s, u, t)` per shot; scenery in `sets.js`) → `node render.cjs --still 2.1,34.5` then the full render in two halves → ffmpeg as for episodes. Check stills as a sheet of vertical frames.
- Reel look: captions 2–3 words at a time with the spoken word in yellow (built from the voice's word timings), `pop()` for "−$10" labels pinned to a 3D point, a bank-balance pill at the top, text kept out of the top 10% and bottom 20%.
- Google Flow (flow.google.com): no API, so Ramesh generates there. Pictures are free (Nano Banana); video is Omni 1.2 Flash at 3 credits/second at 720p, 50 free credits a day. Flow defaults to 10 s (30 credits), so every clip prompt ends with its length. Save characters under Characters and attach them to keep faces the same. No watermark seen on the free plan.
- A nose built from a long rounded shaft and two balls looks rude. Use a bridge that widens downward, nostrils facing out, and eyes above it.

## Lessons learned

- edge-tts sometimes joins two words into one word timing ("Now close" in ep 7), so a `('word', …)` cue on the second word fails: put the cue on another word of the line.
- edge-tts adds silence at both ends of each line: `trim()` in `episode.py` cuts it (saved ~1 min per episode).
- Word timings: `boundary='WordBoundary'` gives each word's start, used for pop-ups exactly as a word is said.
- Choruses drift apart when long (ep 3: Birdie finished "…ten" at 4 s, Froggy at 8 s). Fixed with `chant()`; see the sync rules in step 3.
- Lip sync: letters → 9 Rhubarb-style mouth shapes (`A`–`H`, `X`), closed when quiet. Good enough; real Rhubarb needs permission to run.
- Headless Chrome uses the Mac's GPU only with `--use-angle=metal --enable-gpu --ignore-gpu-blocklist`.
- Things that face the camera (rings, sprites) must turn **after** the camera moves in that frame.
- Objects from one scene leak into others unless `render()` hides them every frame.
- Keep characters ≥ ~6 units from the camera or they fill the frame; butterflies are hidden when close.
- Free music and sound effects are synthesised in `sound.py`: nothing to license, no Content ID claims.
- Letter sounds (phonics) do not work with the free voices: spellings like "buh", "b-b-bus" and "bih" were tested for A–H in Pip's voice and Ramesh found them not nice. ABC episodes use letter names: "A is for apple, B is for ball".
- **Voices must always be clear over everything else** (Ramesh, ep 6: the wind at 1:02 drowned the characters). In `sound.py` (from ep 6, copied into each new episode): background sounds (birds, water, wind, rain, crickets, thunder) go into `amb`, never `fx`, and drop to a fifth while anyone speaks; music drops to a quarter. `sound.py` prints a check per scene and every scene must pass before rendering: background at least 15 dB and music at least 10 dB under the voices while someone talks. A big sound tied to a word (thunder on "Boom!", a whoosh on "Whoosh!") starts just after the word, not on it.
- **Water sounds must sound like water.** In ep 3 the fish's `splash()` (filtered noise plus a few blips) did not sound like a water splash to Ramesh. Ep 3 stays as it is. From ep 4 on (Ducky jumping in the pond, puddles in ep 6): build a splash from a low "plop" that drops in pitch, then a burst of hissing spray that fades, then a few bubbles; and always list every new kind of sound, with its time, for Ramesh to listen to, because Claude cannot hear them.
- Canvas textures drawn with Fredoka (number sprites) need the font loaded before `init()`: `render.cjs`/`thumb.cjs` call `document.fonts.load` first.
- Small characters need their own measurements: Birdie's eyes are only 0.77 above the ground, so a prop pinned to her face (her tear) must use her size, and a light-blue tear on a light-blue bird is invisible (use dark blue).
- Characters at a picnic or in a circle still face the camera (turned slightly toward the middle, `rotY: -x * 0.12`); facing the basket showed their backs.
- `game()` resets each toy's scale to 1, so a toy that needs its own size (a small model of the bus, a train) goes inside a wrapper group and is scaled inside it.
- Two things that look alike confuse the picture: Lumi's "which star is small?" game uses pink stars, because yellow stars with faces looked like Lumi.
- Check stills as a contact sheet (ffmpeg `xstack`, no `drawtext` in Homebrew's ffmpeg) to review a dozen frames in one image.
- YouTube: custom URLs can't be changed any more (handles replaced them); thumbnails need a phone-verified account.

## Ideas for later

- **Planned episodes**: none left (ep 4–10 built). Next ideas below; write the script first and wait for Ramesh's OK.
- **Rescue missions** (Ramesh's pick for what's next, from a look at what toddlers watch now): a story series where Sunny and a new helper vehicle rescue a friend. Plan in `cartoon-3d/episodes/rescue-missions-plan.md` (why, the repeated series elements, helpers, 8 episode ideas, the 20-scene shape, pilot first). Gentle only: stuck or lost, never hurt; no flashing siren lights. Each script's header lists its colours and the new things to build. To build one: `./new-episode.sh epNN-<slug> "Episode NN - <Title>"` (it keeps the script already in the folder and copies the newest started episode).
- More episode ideas: ABC parts 2 and 3 (I–P, Q–Z) · Bath and bedtime routines · Animal sounds (needs new animals; computer voices saying "moo" sound like people) · Days of the week (abstract for ages 2–5).
- Nepali versions (voices `ne-NP-SagarNeural` / `ne-NP-HemkalaNeural`; Devanagari captions need Noto Sans Devanagari).
- Shorts (vertical 1080×1920, 20–35 s) cut from each episode's best scene.
- Characters sing a short original song per episode (melody already in `sound.py`).
- Blender (free) via Python scripts for a softer, more polished look; Remotion for animated explainers.
