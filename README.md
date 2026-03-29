# Kokoro TTS Local — macOS Intel

Local text-to-speech using [Kokoro-82M](https://github.com/hexgrad/kokoro) via ONNX Runtime. No cloud, no API keys, no PyTorch.

> **Your system:** macOS 15.7.3 (24G419), Intel — this uses `kokoro-onnx` which runs on ONNX Runtime, sidestepping the PyTorch 2.4+ requirement that Intel Macs can't satisfy.

---

## Setup

Unzip, `cd` into the folder, and run:

```bash
chmod +x setup_kokoro.sh
./setup_kokoro.sh
```

This installs everything **in the same folder**: Python venv, `kokoro-onnx`, ffmpeg, and downloads the model files (~300 MB). No surprises about where things go.

---

## Usage

```bash
# Quick generate & play
./kokoro "Hello, this is Kokoro TTS!"

# Choose a voice
./kokoro -v bf_emma "A lovely British accent."
./kokoro -v am_adam "A deeper male voice."

# Adjust speed
./kokoro -s 0.8 "Speaking more slowly."

# Save as MP3
./kokoro -o greeting.mp3 "Welcome to the presentation."

# Narrate a chapter — no playback, British female, slightly slow, MP3
./kokoro --no-play -f chapter1.txt -v bf_emma -s 0.9 -o chapter1.mp3

# Interactive mode
./kokoro

# List all voices
./kokoro --list-voices
```

### Interactive Commands

```
/voice bf_emma    — switch voice
/speed 1.2        — change speed
/play             — toggle autoplay
/mp3              — toggle MP3 output
/voices           — list all voices
/quit             — exit
```

### Progress Bar

Long texts show a live progress bar with ETA:

```
   ┃██████████████░░░░░░░░░░░░░░░░┃ 12/28 chunks  45s  ~1m 23s left
```

---

## Voices (67 total)

| Category         | Voices |
|-----------------|--------|
| American Female  | af_alloy, af_aoede, af_bella, **af_heart** ★, af_jessica, af_kore, af_nicole, af_nova, af_river, af_sarah, af_sky |
| American Male    | am_adam, am_echo, am_eric, am_fenrir, am_liam, am_michael, am_onyx, am_puck |
| British Female   | bf_alice, bf_emma, bf_lily |
| British Male     | bm_daniel, bm_fable, bm_george, bm_lewis |
| Spanish          | ef_dora, em_alex |
| French           | ff_siwis |
| Hindi            | hf_alpha, hf_beta, hm_omega, hm_psi |
| Italian          | if_sara, im_nicola |
| Japanese         | jf_alpha, jf_gongitsune, jf_nezumi, jf_tebukuro, jm_kumo |
| Portuguese       | pf_dora, pm_alex |
| Chinese          | zf_xiaobei, zf_xiaoni, zf_xiaoxiao, zf_xiaoyi, zm_yunjian, zm_yunxia, zm_yunxi, zm_yunyang |

★ = default

---

## Intel Mac Notes

- Uses **ONNX Runtime** — not PyTorch. No version ceiling issues on Intel Mac.
- Runs on **CPU** — expect near real-time for short text, a few minutes for chapters.
- ~300 MB model download on first setup. Fully **offline** after that.
- MP3 output via ffmpeg (~90% smaller than WAV).

---

## Troubleshooting

**"Model files not found"** — Make sure `kokoro-v1.0.onnx` and `voices-v1.0.bin` are in the same folder as the script. The setup script downloads them automatically.

**MP3 conversion fails** — `brew install ffmpeg`

**"No module named kokoro_onnx"** — Activate the venv: `source venv/bin/activate`

---

## Uninstall

```bash
chmod +x uninstall_kokoro.sh
./uninstall_kokoro.sh
```

Asks before deleting each component. Defaults to no.

---

## What's in the Zip

| File | Purpose |
|------|---------|
| `setup_kokoro.sh` | Installer — run this first |
| `kokoro_tts_local.py` | The TTS script |
| `uninstall_kokoro.sh` | Clean removal |
| `README.md` | This guide |
