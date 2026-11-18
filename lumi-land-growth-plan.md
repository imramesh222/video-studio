# Lumi Land growth plan (from 17 Nov 2026)

Goal: real toddler viewers and subscribers, using only free tools. No bought views, no "sub for sub" (both can get a kids' channel penalized).

## Where we are

- 4 videos public. Ep 1 got ~350 views on day one, ep 2–4 almost none.
- Likely reason: ep 1's views came from the old "TRENDING NEPAL" subscribers (football fans, not parents). They left quickly, so YouTube stopped showing the next videos to them.
- Made for Kids videos get no subscriber notifications, no comments, no end screens or cards. They are found through search, suggested videos, Shorts and the YouTube Kids app, which takes weeks, not days.
- Honest expectation: kids' channels usually take 2–6 months of steady uploads before views grow. Monetization (YouTube Partner Program) needs 1,000 subscribers plus 4,000 watch hours in a year, or 10 million Shorts views in 90 days.

## The plan

### 1. Shorts every day (the fastest way to be found)
- One 30–45 second vertical Short per episode: a question and its answer ("Find the red!"), the title at the top, "Full episode on Lumi Land" at the bottom.
- Post one a day, same time each day. Title: "Find the RED! 🔴 Learn Colors for Toddlers #shorts".
- Made by `shorts/make_shorts.py` from the finished episodes, into `~/Downloads/Lumi Land/Shorts/`.

### 2. Long episodes on a fixed schedule (two a week)
Don't upload everything at once; a steady rhythm teaches YouTube when to expect us.

| Day | Upload |
|---|---|
| Thu 19 Nov | Ep 5 The Fruit Picnic |
| Mon 23 Nov | Ep 6 The Weather Day |
| Thu 26 Nov | Ep 7 Touch Your Nose |
| Mon 30 Nov | Ep 8 Things That Go |
| Thu 3 Dec | Ep 9 How Do You Feel? |
| Mon 7 Dec | Ep 10 ABC with Pip (A to H) |
| Thu 10 Dec | 40-minute compilation of ep 1–10 |
| then | Rescue missions (pilot Ep 11, digger) |

Use YouTube's "Schedule" option so they go up even if you are busy.

### 3. Compilation (watch time)
- All ten episodes back to back (~40 min), with chapters. Parents leave long videos playing; that builds the watch hours the channel needs.
- Made into `~/Downloads/Lumi Land/Compilation - Episodes 1 to 10/`.

### 4. Subtitles on every video
- An English subtitle file (.srt) for each episode, made from the exact script and timings. Upload under Subtitles → Upload file → With timing. Helps search, and parents who watch with sound off.

### 5. Channel set-up (one time, in YouTube Studio)
- **Playlist** "Learn with Pip & Friends" with every episode in order (autoplay keeps toddlers watching).
- **Channel home**: a section with that playlist at the top; the newest episode as the featured video.
- **Channel description**: who it's for and what they learn, with the main search words (toddler learning, colors, shapes, numbers, ABC).
- Old football subscribers: nothing to do; new viewers will outweigh them.

### 6. Real viewers outside YouTube (free)
- Share each new episode in family and friends' groups and Nepali parents' WhatsApp and Facebook groups, asking them to watch with their child and subscribe.
- Toddlers watching for minutes is exactly the signal YouTube needs to show the channel to more parents.

### 7. Keep improving from the numbers (every Monday)
In YouTube Studio → Analytics, check for each video:
- **Impressions** (is YouTube showing it?) and **click-through rate** (do people click?). Low click-through → try thumbnail B ("Test & compare").
- **Average view duration** (do they stay?). The video that keeps viewers longest shows what to make more of.
- **Traffic source** (search, Shorts, suggested, external).
Send Claude screenshots; we adjust titles, thumbnails and the next topics.

### 8. New content after ep 10
- Rescue missions series (see `cartoon-3d/episodes/rescue-missions-plan.md`), pilot first, judged on the numbers above.
- Later: Nepali versions of the best episodes; ABC parts 2 and 3.
