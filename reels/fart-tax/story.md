# The Fart Tax

A short comedy story for Reels / Shorts. Not Lumi Land: its own characters, its own look, and not for the kids' channel.

- **Format:** vertical 1080×1920, 30 fps, one narrator, fast cuts (a new picture every 2–4 seconds).
- **Hook:** the first line and the first "−$10" land inside the first 2 seconds.
- **Finished video goes to:** `~/Downloads/Reels/Fart Tax/`.

## Narration

In this town, farting costs $10.

Sensors are everywhere. One tiny toot, and $10 disappears from your bank account.

My name is Toby, and last night I ate beans. Big mistake.

I got out of bed. Minus $10. I tied my shoe. Another $10. By breakfast, I was almost broke.

People here got creative. Some ate only plain rice. One guy lived inside a soundproof box. And the rich? They farted all day, because $10 meant nothing to them.

So I spent all night building the Silent Pants. No sound. No smell. No bill.

Soon the whole town was wearing them, and the government was losing millions.

The next morning, drones filled the sky. "New rule! Pants without a license cost $1,000!"

Everyone panicked. One man ran home in his underwear. My neighbor held it in so long, he floated away like a balloon.

Then I noticed something strange. The mayor farted on live TV, and he wasn't charged a single dollar.

That night, I followed his car to a secret room under City Hall. Inside, a giant machine was sniffing the whole town. And in the middle, a big red button: Disable fart tax.

No guards. No cameras. I pressed it.

Every screen in town turned green. And the whole town let go at once. It sounded like a thousand trumpets.

I was a hero.

But the next morning, my phone buzzed. New tax: burping. $20 each.

I looked at the soda in my hand. You've got to be kidding me.

## Characters

| Character | Look |
|---|---|
| Toby (narrator) | thin man in his twenties, messy brown hair, round glasses, green hoodie, grey joggers, always holding his phone |
| Mayor Grimsby | short and round, purple suit, gold chain, tiny moustache, top hat, smug smile |
| Mr. Puff (the neighbor) | big man in striped pajamas and slippers, the one who floats away |
| The rich man | gold suit, sunglasses, money falling out of his pockets |
| Sniffers (the sensors) | small metal noses on lamp posts, benches and walls, with a light that is green when asleep and red when it catches one |
| Tax drones | black, one red eye, a loudspeaker underneath |
| The Big Nose | the machine under City Hall: a giant brass nose with pipes running to the whole town, and one big red button |

## Look and sound

- Bright toy-like 3D cartoon, a clean pastel town, bold colours. Funny, never gross.
- A fart is always the same three things: a soft green puff cloud, a short comic toot, and a red "−$10" flying up from the phone.
- Toby's bank balance sits in the top corner all video and drops with every "−$10".
- Captions: 2–4 words at a time, big bold white with a black outline, the spoken word in yellow, in the middle-lower part of the frame.
- Keep faces and text out of the top 10% and bottom 20% of the frame (the app's buttons cover them).
- Narrator: one young, dry, slightly tired male voice, a little faster than normal speech.
- Music: light sneaky pizzicato, a drum hit on each "−$10", silence for one beat before the last line.

## Shots

| # | Narration | On screen |
|---|---|---|
| 1 | In this town, farting costs $10. | Toby walks down the street. Green puff. "−$10" flies up from his phone. He sighs at the camera. |
| 2 | Sensors are everywhere… | Quick look around: Sniffers on a lamp post, a bench, a bus stop. A passer-by toots, a nose turns red, their phone shows "−$10". |
| 3 | My name is Toby… beans. Big mistake. | Last night: Toby at the table behind a mountain of beans, a tower of empty cans. |
| 4 | I got out of bed… almost broke. | Three fast cuts: bed, shoe, kitchen. A puff and "−$10" each time. Balance drops $130 → $40. |
| 5 | People here got creative… | A lady sadly eating plain rice. A man waving from inside a glass box. The rich man strolling past with a trail of puffs, laughing. |
| 6 | So I spent all night building the Silent Pants… | Garage at night, sparks. Reveal: shiny silver pants with a filter and a tiny fan. Toby tests them next to a Sniffer: it stays green. |
| 7 | Soon the whole town was wearing them… | A street full of people in silver pants. A "City income" chart with the arrow falling off the bottom. |
| 8 | The next morning, drones filled the sky… | Black drones over the rooftops, the mayor's face on their screens. Big text: "PANTS LICENSE $1,000". |
| 9 | Everyone panicked… | A man sprinting home in heart-print boxers. Mr. Puff swelling up, feet leaving the ground, drifting over the roofs. |
| 10 | Then I noticed something strange… | A TV: Mayor Grimsby at a podium, a big green puff, the Sniffer beside him stays green. Toby squints. |
| 11 | That night, I followed his car… | Toby on a bicycle behind a black car. Stairs down under City Hall. The Big Nose, pipes everywhere, sniffing. The red button glows. |
| 12 | No guards. No cameras. I pressed it. | Toby looks left, right. Close-up of his finger. Press. |
| 13 | Every screen in town turned green… | Screens: "FART TAX DISABLED". Wide shot of the town: green puffs rising from every house like fireworks, windows rattling, pigeons taking off. |
| 14 | I was a hero. | Toby carried on shoulders, confetti. |
| 15 | But the next morning… $20 each. | Phone close-up, it buzzes: "NEW TAX: BURPING · $20 EACH". |
| 16 | I looked at the soda… kidding me. | Toby holding a soda can, cheeks puffed, one eye twitching. He slowly looks at the camera. Cut to black. |

## How it gets made here

Reuse the `cartoon-3d` engine at 1080×1920: `episode.py` (free edge-tts voice + word timings for the captions), `sound.py` (music and toots synthesised, nothing to license), `render.cjs` (frame by frame), then ffmpeg. One voice line per shot so every cut lands on the narration.
