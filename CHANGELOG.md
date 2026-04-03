# Changelog

All notable changes to Kokoro TTS Local are documented here.

Format follows [Keep a Changelog](https://keepachangelog.com/). Versions follow [Semantic Versioning](https://semver.org/).

---

## [1.0.1] — 2026-04-03

### Fixed
- Setup script now finds Homebrew on both Intel (`/usr/local/bin`) and Apple Silicon (`/opt/homebrew/bin`) when invoked from a parent script
- `.gitignore` updated to exclude build artifacts (venv, model files, launcher)

## [1.0.0] — 2026-03-29

### Added
- `kokoro_tts_local.py` — full TTS engine using Kokoro-82M via ONNX Runtime
- 67 voices across 11 languages (American, British, Spanish, French, Hindi, Italian, Japanese, Portuguese, Chinese)
- Interactive mode with `/voice`, `/speed`, `/play`, `/mp3`, `/voices` commands
- CLI with voice selection (`-v`), speed control (`-s`), file output (`-o`), file input (`-f`)
- WAV and MP3 output (MP3 via ffmpeg)
- Progress bar with ETA for long text generation
- Text splitting at sentence boundaries for chunked processing
- `setup_kokoro.sh` — automated installer (venv, dependencies, model download)
- `uninstall_kokoro.sh` — interactive cleanup with confirmation prompts
