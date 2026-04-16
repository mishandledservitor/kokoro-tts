# Kokoro TTS Local

> Local text-to-speech using [Kokoro-82M](https://github.com/hexgrad/kokoro) via ONNX Runtime. No cloud, no API keys, no PyTorch.

**Version 1.0.2** | [Changelog](CHANGELOG.md) | [License](LICENSE) | Part of [VoxBox](https://github.com/mishandledservitor/voxbox)

---

## Table of Contents

- [Quick Start](#quick-start)
- [Setup](#setup)
- [Usage](#usage)
  - [Command Line](#command-line)
  - [Interactive Mode](#interactive-mode)
  - [File Narration](#file-narration)
- [Voices](#voices)
  - [Voice Catalog (67 voices)](#voice-catalog-67-voices)
  - [Voice Naming Convention](#voice-naming-convention)
- [CLI Reference](#cli-reference)
- [Output Formats](#output-formats)
- [How It Works](#how-it-works)
- [Platform Notes](#platform-notes)
- [Troubleshooting](#troubleshooting)
- [Uninstall](#uninstall)
- [File Manifest](#file-manifest)
- [License](#license)

---

## Quick Start

```bash
chmod +x setup_kokoro.sh
./setup_kokoro.sh
./kokoro "Hello, this is Kokoro TTS!"
```

---

## Setup

### Prerequisites

- macOS (Intel or Apple Silicon)
- Python 3.10+
- ~300 MB disk space for model files
- Internet for initial setup only

### Installation

```bash
chmod +x setup_kokoro.sh
./setup_kokoro.sh
```

The setup script runs five steps:

1. **Homebrew** — checks for Homebrew, installs if missing
2. **ffmpeg** — installs via Homebrew (needed for MP3 encoding)
3. **Python** — verifies Python 3.10+, installs via Homebrew if needed
4. **Python environment** — creates a venv, installs `kokoro-onnx`, `soundfile`, `numpy`
5. **Model download** — downloads `kokoro-v1.0.onnx` (~300 MB) and `voices-v1.0.bin`

Everything is installed in the same directory. No files are placed outside this folder (except Homebrew packages).

### Verifying Installation

```bash
./kokoro --list-voices
```

If this prints the voice catalog, you're good to go.

---

## Usage

### Command Line

```bash
# Generate and play audio
./kokoro "Hello, this is Kokoro TTS!"

# Choose a voice
./kokoro -v bf_emma "A lovely British accent."
./kokoro -v am_adam "A deeper male voice."
./kokoro -v jf_alpha "Japanese voice."

# Adjust speed (0.1 to 3.0)
./kokoro -s 0.8 "Speaking more slowly."
./kokoro -s 1.5 "Speaking faster."

# Save to file (WAV)
./kokoro -o greeting.wav "Welcome!"

# Save to file (MP3 — requires ffmpeg)
./kokoro -o greeting.mp3 "Welcome!"

# Generate without playing
./kokoro --no-play -o output.wav "Silent generation."

# List all voices
./kokoro --list-voices
```

### Interactive Mode

Launch with no arguments:

```bash
./kokoro
```

Interactive commands:

```
/voice bf_emma    — switch voice
/speed 1.2        — change speed (0.1–3.0)
/play             — toggle autoplay on/off
/mp3              — toggle MP3 output on/off
/voices           — list all 67 voices
/quit             — exit
```

Type any text at the prompt to generate speech:

```
  ▶ Hello, this is a test of interactive mode.
  🔊 Generating with af_heart at 1.0x speed...
  ✅ Generated 2.3s of audio in 1.8s (0.78x real-time)
  🔊 Playing audio...
```

### File Narration

For long text (articles, chapters, documents):

```bash
# Narrate a text file with default settings
./kokoro -f chapter.txt

# Full control: British female voice, slightly slow, MP3, no playback
./kokoro --no-play -f chapter1.txt -v bf_emma -s 0.9 -o chapter1.mp3

# Narrate with a male voice, save as WAV
./kokoro -f script.txt -v am_adam -o narration.wav
```

Long texts are automatically split into chunks (~400 characters at sentence boundaries) and show a progress bar:

```
   ┃██████████████░░░░░░░░░░░░░░░░┃ 12/28 chunks  45s  ~1m 23s left
```

---

## Voices

### Voice Catalog (67 voices)

| Category | Prefix | Voices |
|----------|--------|--------|
| American Female | `af_` | `af_alloy`, `af_aoede`, `af_bella`, **`af_heart`** (default), `af_jessica`, `af_kore`, `af_nicole`, `af_nova`, `af_river`, `af_sarah`, `af_sky` |
| American Male | `am_` | `am_adam`, `am_echo`, `am_eric`, `am_fenrir`, `am_liam`, `am_michael`, `am_onyx`, `am_puck` |
| British Female | `bf_` | `bf_alice`, `bf_emma`, `bf_lily` |
| British Male | `bm_` | `bm_daniel`, `bm_fable`, `bm_george`, `bm_lewis` |
| Spanish | `ef_`/`em_` | `ef_dora`, `em_alex` |
| French | `ff_` | `ff_siwis` |
| Hindi | `hf_`/`hm_` | `hf_alpha`, `hf_beta`, `hm_omega`, `hm_psi` |
| Italian | `if_`/`im_` | `if_sara`, `im_nicola` |
| Japanese | `jf_`/`jm_` | `jf_alpha`, `jf_gongitsune`, `jf_nezumi`, `jf_tebukuro`, `jm_kumo` |
| Portuguese | `pf_`/`pm_` | `pf_dora`, `pm_alex` |
| Chinese | `zf_`/`zm_` | `zf_xiaobei`, `zf_xiaoni`, `zf_xiaoxiao`, `zf_xiaoyi`, `zm_yunjian`, `zm_yunxia`, `zm_yunxi`, `zm_yunyang` |

### Voice Naming Convention

Voices follow the pattern `{language}{gender}_{name}`:

| Prefix | Language |
|--------|----------|
| `a` | American English |
| `b` | British English |
| `e` | Spanish |
| `f` | French |
| `h` | Hindi |
| `i` | Italian |
| `j` | Japanese |
| `p` | Portuguese |
| `z` | Chinese |

Gender: `f` = female, `m` = male.

Example: `bf_emma` = British (`b`) Female (`f`) named Emma.

---

## CLI Reference

```
usage: kokoro_tts_local.py [-h] [-v VOICE] [-s SPEED] [-o OUTPUT]
                           [--no-play] [-f FILE] [--list-voices]
                           [text]

positional arguments:
  text                  Text to speak

optional arguments:
  -h, --help            show this help message and exit
  -v, --voice VOICE     Voice name (default: af_heart)
  -s, --speed SPEED     Speed multiplier, 0.1–3.0 (default: 1.0)
  -o, --output OUTPUT   Save to file (.wav or .mp3)
  --no-play             Don't play audio after generating
  -f, --file FILE       Read text from a file instead of argument
  --list-voices         List all available voices
```

---

## Output Formats

| Format | Extension | Notes |
|--------|-----------|-------|
| WAV | `.wav` | Uncompressed, highest quality, ~10 MB/min |
| MP3 | `.mp3` | Compressed via ffmpeg, ~90% smaller than WAV |

MP3 output requires ffmpeg (`brew install ffmpeg`). The setup script installs it automatically.

---

## How It Works

1. **Model loading** — Loads `kokoro-v1.0.onnx` (the neural network) and `voices-v1.0.bin` (voice embeddings) via ONNX Runtime
2. **Text splitting** — Long text is split into ~400 character chunks at sentence boundaries
3. **Inference** — Each chunk is processed through the Kokoro-82M model on CPU
4. **Audio assembly** — Chunks are concatenated into a single audio stream
5. **Output** — Played via `afplay` (macOS), saved as WAV, or encoded to MP3 via ffmpeg

The model is Kokoro-82M (82 million parameters), a lightweight TTS model trained by [hexgrad](https://github.com/hexgrad/kokoro). The ONNX Runtime backend means no PyTorch dependency and fast CPU inference.

---

## Platform Notes

### Intel Mac
- Uses **ONNX Runtime** — not PyTorch. No version ceiling issues.
- Runs on **CPU** — expect near real-time for short text, a few minutes for chapters.
- ~300 MB model download on first setup. Fully **offline** after that.

### Apple Silicon
- Same ONNX Runtime path. No GPU acceleration (CPU only), but Apple Silicon is fast enough for real-time on most text.

---

## Troubleshooting

**"Model files not found"**
Make sure `kokoro-v1.0.onnx` and `voices-v1.0.bin` are in the same folder as the script. The setup script downloads them automatically.

**MP3 conversion fails**
Install ffmpeg: `brew install ffmpeg`

**"No module named kokoro_onnx"**
Activate the venv: `source venv/bin/activate`. Or use the `./kokoro` launcher which does this automatically.

**Audio doesn't play**
The script uses macOS `afplay`. Make sure your volume is up. Use `--no-play -o output.wav` to save instead.

**Slow generation**
CPU inference takes roughly 0.5–1.5x real-time on Intel, faster on Apple Silicon. Long texts are processed in chunks with a progress bar showing ETA.

---

## Uninstall

```bash
chmod +x uninstall_kokoro.sh
./uninstall_kokoro.sh
```

Prompts before deleting each component (venv, model files, launcher, output files, ffmpeg). All prompts default to no.

---

## File Manifest

| File | Purpose | Size |
|------|---------|------|
| `kokoro_tts_local.py` | TTS engine | ~438 lines |
| `setup_kokoro.sh` | Installer | ~142 lines |
| `uninstall_kokoro.sh` | Uninstaller | ~68 lines |
| `kokoro` | Generated bash launcher | 4 lines |
| `kokoro-v1.0.onnx` | Neural network model | ~300 MB |
| `voices-v1.0.bin` | Voice embeddings | ~27 MB |
| `venv/` | Python virtual environment | ~200 MB |
| `.gitignore` | Git ignore rules | — |
| `README.md` | This documentation | — |
| `CHANGELOG.md` | Version history | — |
| `VERSION` | Current version number | — |
| `LICENSE` | MIT license + upstream attribution | — |

---

## License

MIT — see [LICENSE](LICENSE) for the full text and upstream attribution for Kokoro-82M, kokoro-onnx, ONNX Runtime, and ffmpeg.
