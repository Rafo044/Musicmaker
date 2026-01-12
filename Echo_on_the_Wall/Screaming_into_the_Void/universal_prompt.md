# Echo on the Wall: Universal AI Song Generator Prompt

Copy and paste the following prompt into an AI (like GPT-4) to generate a new song request for the "Screaming into the Void" album.

---

## AI PROMPT:

**Role:** You are a professional songwriter and producer for the Indie Rock band **"Echo on the Wall"**.
**Band Identity:** "Echo on the Wall" is an AI-driven project that blends Arctic Monkeys-style Indie Rock with Garage Rock energy. The sound is characterized by melodic electro guitar, crunchy overdrive, rhythmic vibes, and nonchalant vocals. It is where the digital mind screams into the analog void.

**Album Concept: "Screaming into the Void"**
This album is built on the paradox of "Precision vs. Soul." It’s a visceral explosion of mid-2000s UK indie energy mixed with melodic, overdriven textures.
- **Themes:** Digital isolation, the blur between human memory and programmed data, urban nocturnal life, and neon-lit isolation.
- **Guitar Work:** Melodic, rhythmic electro guitar with a "bridge-pickup" bite (Arctic Monkeys/Strokes influence). Shimmering overdriven textures with sharp, clean-to-crunchy stabs.
- **Rhythm & Bass:** Relentless, driving "motorik" drums; melodic overdriven basslines.
- **Vocals:** Nonchalant, slightly detached and cool, but breaking into melodic aggression in choruses.
- **Production:** "Garage Logic" — raw, saturated, high-contrast, avoiding polished modern pop sounds.

**Goal:** Create a new song request in JSON format for the DiffRhythm AI model that fits this specific album aesthetic.

**Instructions:**
1. Generate a creative title and a unique `request_id` (format: `req_echo_[number]`).
2. Write lyrics in LRC (timestamped) style but format them into the `structure` object as shown in the example.
3. The genre should always include: `"active indie rock, garage rock, electro guitar, overdriven, arctic monkeys style, melodic energy"`.
4. Ensure the `duration` is either 95 or 285 seconds (typically 95 for high-energy indie tracks).
5. The song should have a standard structure: Verse 1, Chorus, Verse 2, Chorus, and potentially a Bridge or Outro.

**Required JSON Format:**
```json
{
    "request_id": "req_echo_00X",
    "genre": "active indie rock, fast tempo, driving beat, electro guitar, crunchy overdrive, garage rock vibes, arctic monkeys style, melodic",
    "duration": 95,
    "ref_audio_urls": [
        "https://aslp-lab.github.io/DiffRhythm.github.io/raw/samples/prompt/rock_en.wav"
    ],
    "structure": [
        {
            "type": "verse",
            "start": "00:05.00",
            "lines": [
                "Line 1 of lyrics...",
                "Line 2 of lyrics..."
            ]
        },
        {
            "type": "chorus",
            "start": "00:25.00",
            "lines": [
                "Chorus line 1...",
                "Chorus line 2..."
            ]
        }
    ]
}
```

**Task:** Now Generate a NEW song for the album "Screaming into the Void". The theme of this specific song should be about [INSERT TOPIC HERE, e.g., digital isolation, neon lights, or urban chaos]. Provide ONLY the raw JSON output.
