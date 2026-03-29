#!/usr/bin/env python3
"""
Kokoro TTS Local — Text-to-Speech using Kokoro-82M (ONNX Runtime)
For macOS 15.7.3 (Intel) — no PyTorch required!

Usage:
    python kokoro_tts_local.py                          # Interactive mode
    python kokoro_tts_local.py "Hello world"            # Quick generate
    python kokoro_tts_local.py -v am_adam "Hello"       # Specify voice
    python kokoro_tts_local.py -o output.mp3 "Hello"    # Save as MP3
    python kokoro_tts_local.py --list-voices            # List voices
    python kokoro_tts_local.py -f input.txt             # Read from file
    python kokoro_tts_local.py --no-play -f chapter1.txt -v bf_emma -s 0.9 -o chapter1.mp3
"""

import argparse
import os
import re
import shutil
import sys
import time
import subprocess
import warnings

warnings.filterwarnings("ignore")

# ── Voice catalog ────────────────────────────────────────────────────────────
VOICES = {
    "American Female": [
        "af_alloy", "af_aoede", "af_bella", "af_heart", "af_jessica",
        "af_kore", "af_nicole", "af_nova", "af_river", "af_sarah", "af_sky",
    ],
    "American Male": [
        "am_adam", "am_echo", "am_eric", "am_fenrir",
        "am_liam", "am_michael", "am_onyx", "am_puck",
    ],
    "British Female": ["bf_alice", "bf_emma", "bf_lily"],
    "British Male": ["bm_daniel", "bm_fable", "bm_george", "bm_lewis"],
    "Other Languages": [
        "ef_dora", "em_alex",
        "ff_siwis",
        "hf_alpha", "hf_beta",
        "hm_omega", "hm_psi",
        "if_sara", "im_nicola",
        "jf_alpha", "jf_gongitsune",
        "jf_nezumi", "jf_tebukuro",
        "jm_kumo",
        "pf_dora", "pm_alex",
        "zf_xiaobei", "zf_xiaoni",
        "zf_xiaoxiao", "zf_xiaoyi",
        "zm_yunjian", "zm_yunxia",
        "zm_yunxi", "zm_yunyang",
    ],
}

ALL_VOICES = []
for group in VOICES.values():
    ALL_VOICES.extend(group)

DEFAULT_VOICE = "af_heart"
SAMPLE_RATE = 24000

# ── Utilities ────────────────────────────────────────────────────────────────

def resolve_path(path):
    return os.path.abspath(os.path.expanduser(path))

def format_time(seconds):
    if seconds < 60:
        return f"{seconds:.0f}s"
    m, s = divmod(int(seconds), 60)
    if m < 60:
        return f"{m}m {s:02d}s"
    h, m = divmod(m, 60)
    return f"{h}h {m:02d}m"

def draw_progress(current, total, elapsed, bar_width=30):
    term_width = shutil.get_terminal_size((80, 20)).columns
    bar_width = min(bar_width, term_width - 45)
    pct = current / total if total > 0 else 0
    filled = int(bar_width * pct)
    bar = '█' * filled + '░' * (bar_width - filled)
    if current > 0 and pct < 1.0:
        eta = (elapsed / current) * (total - current)
        eta_str = f"~{format_time(eta)} left"
    elif pct >= 1.0:
        eta_str = "done!"
    else:
        eta_str = "estimating..."
    line = f"\r   ┃{bar}┃ {current}/{total} chunks  {format_time(elapsed)}  {eta_str}"
    sys.stdout.write(line.ljust(term_width - 1))
    sys.stdout.flush()

def detect_lang(voice):
    prefix = voice[:2] if len(voice) >= 2 else "af"
    mapping = {
        "af": "en-us", "am": "en-us",
        "bf": "en-gb", "bm": "en-gb",
        "ef": "es", "em": "es",
        "ff": "fr-fr",
        "hf": "hi", "hm": "hi",
        "if": "it", "im": "it",
        "jf": "ja", "jm": "ja",
        "pf": "pt-br", "pm": "pt-br",
        "zf": "zh", "zm": "zh",
    }
    return mapping.get(prefix, "en-us")

# ── MP3 conversion ───────────────────────────────────────────────────────────

def wav_to_mp3(wav_path, mp3_path, bitrate="192k"):
    for encoder in ["ffmpeg", "lame"]:
        try:
            if encoder == "ffmpeg":
                cmd = ["ffmpeg", "-y", "-i", wav_path, "-codec:a", "libmp3lame",
                       "-b:a", bitrate, "-loglevel", "error", mp3_path]
            else:
                cmd = ["lame", "--cbr", "-b", bitrate.replace("k", ""), wav_path, mp3_path]
            subprocess.run(cmd, check=True, capture_output=True)
            return True
        except (FileNotFoundError, subprocess.CalledProcessError):
            continue
    return False

def check_mp3_support():
    for cmd in ["ffmpeg", "lame"]:
        try:
            subprocess.run([cmd, "--version"], capture_output=True, check=False)
            return cmd
        except FileNotFoundError:
            continue
    return None

# ── Core ─────────────────────────────────────────────────────────────────────

def find_model_files():
    """Find kokoro-v1.0.onnx and voices-v1.0.bin relative to the script."""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    cwd = os.getcwd()

    for d in [cwd, script_dir]:
        model = os.path.join(d, "kokoro-v1.0.onnx")
        voices = os.path.join(d, "voices-v1.0.bin")
        if os.path.isfile(model) and os.path.isfile(voices):
            return model, voices

    print("⚠  Model files not found!")
    print("   Expected: kokoro-v1.0.onnx and voices-v1.0.bin")
    print(f"   Looked in: {cwd}")
    if cwd != script_dir:
        print(f"              {script_dir}")
    print("\n   Run setup_kokoro.sh to download them, or get them from:")
    print("   https://github.com/thewh1teagle/kokoro-onnx/releases/tag/model-files-v1.0")
    sys.exit(1)

def load_kokoro():
    """Load the Kokoro ONNX model."""
    model_path, voices_path = find_model_files()
    print(f"⏳ Loading Kokoro model...")
    start = time.time()
    from kokoro_onnx import Kokoro
    kokoro = Kokoro(model_path, voices_path)
    elapsed = time.time() - start
    print(f"✅ Model loaded in {elapsed:.1f}s")
    return kokoro

def split_text(text, max_chars=400):
    """Split text into chunks at sentence boundaries for long-form generation."""
    # Split on paragraph breaks first
    paragraphs = re.split(r'\n\s*\n', text)
    chunks = []

    for para in paragraphs:
        para = para.strip()
        if not para:
            continue
        if len(para) <= max_chars:
            chunks.append(para)
            continue
        # Split long paragraphs on sentences
        sentences = re.split(r'(?<=[.!?])\s+', para)
        current = ""
        for sent in sentences:
            if len(current) + len(sent) + 1 <= max_chars:
                current = (current + " " + sent).strip()
            else:
                if current:
                    chunks.append(current)
                current = sent
        if current:
            chunks.append(current)

    return chunks if chunks else [text]

def print_voices():
    print("\n╔══════════════════════════════════════════════╗")
    print("║         🎙  KOKORO VOICE CATALOG  🎙         ║")
    print("╚══════════════════════════════════════════════╝\n")
    for category, voices in VOICES.items():
        print(f"  ┌─ {category} ─{'─' * (38 - len(category))}┐")
        for v in voices:
            marker = " ★" if v == DEFAULT_VOICE else ""
            print(f"  │   {v}{marker}")
        print(f"  └{'─' * 42}┘\n")
    print(f"  ★ = default voice ({DEFAULT_VOICE})\n")

def generate_speech(kokoro, text, voice=DEFAULT_VOICE, speed=1.0, output_path=None):
    import soundfile as sf
    import numpy as np

    if output_path is None:
        output_path = resolve_path("./kokoro_output.wav")
    else:
        output_path = resolve_path(output_path)

    output_dir = os.path.dirname(output_path)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)

    _, ext = os.path.splitext(output_path)
    want_mp3 = ext.lower() == ".mp3"

    if want_mp3:
        mp3_method = check_mp3_support()
        if not mp3_method:
            print("⚠  MP3 requires ffmpeg. Install: brew install ffmpeg")
            print("   Falling back to WAV.")
            output_path = output_path.rsplit(".", 1)[0] + ".wav"
            want_mp3 = False
        else:
            print(f"   MP3 encoding via: {mp3_method}")

    lang = detect_lang(voice)
    chunks = split_text(text)
    word_count = len(text.split())
    total_chunks = len(chunks)

    print(f"\n🎙  Voice: {voice}  |  Speed: {speed}x  |  Lang: {lang}  |  Format: {'MP3' if want_mp3 else 'WAV'}")
    print(f"📝 {word_count:,} words  |  {total_chunks} chunk{'s' if total_chunks != 1 else ''}")
    print()

    start = time.time()
    all_samples = []

    for i, chunk in enumerate(chunks):
        samples, sr = kokoro.create(chunk, voice=voice, speed=speed, lang=lang)
        all_samples.append(samples)
        elapsed = time.time() - start
        draw_progress(i + 1, total_chunks, elapsed)

    elapsed = time.time() - start
    draw_progress(total_chunks, total_chunks, elapsed)
    print()

    if not all_samples:
        print("⚠  No audio generated.")
        return None

    full_audio = np.concatenate(all_samples)
    total_duration = len(full_audio) / SAMPLE_RATE

    if want_mp3:
        wav_tmp = output_path.rsplit(".", 1)[0] + "_tmp.wav"
        sf.write(wav_tmp, full_audio, SAMPLE_RATE)
        print("   🔄 Converting to MP3...")
        success = wav_to_mp3(wav_tmp, output_path)
        if success:
            os.remove(wav_tmp)
            mp3_size = os.path.getsize(output_path)
            wav_est = len(full_audio) * 2
            ratio = (1 - mp3_size / wav_est) * 100 if wav_est > 0 else 0
            print(f"   📦 MP3: {mp3_size / (1024*1024):.1f} MB ({ratio:.0f}% smaller than WAV)")
        else:
            print("   ⚠  MP3 failed. Keeping WAV.")
            fallback = output_path.rsplit(".", 1)[0] + ".wav"
            os.rename(wav_tmp, fallback)
            output_path = fallback
    else:
        sf.write(output_path, full_audio, SAMPLE_RATE)

    print(f"\n✅ Generated {format_time(total_duration)} of audio in {format_time(elapsed)}")
    rtf = elapsed / total_duration if total_duration > 0 else 0
    print(f"   Real-time factor: {rtf:.2f}x (1.0 = real-time)")
    print(f"💾 Saved to: {output_path}")
    return output_path

def play_audio(filepath):
    try:
        print("🔊 Playing...")
        subprocess.run(["afplay", filepath], check=True)
    except (FileNotFoundError, subprocess.CalledProcessError):
        print("⚠  Could not play. File saved at:", filepath)

def interactive_mode(kokoro):
    voice = DEFAULT_VOICE
    speed = 1.0
    auto_play = True
    output_format = "wav"

    print("\n╔══════════════════════════════════════════════╗")
    print("║      🎧  KOKORO TTS — INTERACTIVE MODE  🎧    ║")
    print("╚══════════════════════════════════════════════╝")
    print(f"\n  Voice: {voice}  |  Speed: {speed}x  |  Format: {output_format.upper()}")
    print(f"  Autoplay: {'on' if auto_play else 'off'}")
    print("\n  Commands:")
    print("    /voice <n>       — change voice (e.g. /voice am_adam)")
    print("    /speed <0.5-2.0> — change speed")
    print("    /play            — toggle autoplay")
    print("    /mp3             — toggle MP3 output")
    print("    /voices          — list all voices")
    print("    /quit            — exit\n")

    output_dir = os.getcwd()

    while True:
        try:
            text = input("  ▶ ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n\n  👋 Goodbye!\n")
            break

        if not text:
            continue

        if text.startswith("/"):
            parts = text.split(maxsplit=1)
            cmd = parts[0].lower()
            arg = parts[1].strip() if len(parts) > 1 else ""

            if cmd in ("/quit", "/exit", "/q"):
                print("\n  👋 Goodbye!\n")
                break
            elif cmd == "/voice":
                if arg in ALL_VOICES:
                    voice = arg
                    print(f"  ✅ Voice: {voice}")
                else:
                    print(f"  ⚠  Unknown voice. Use /voices to see options.")
            elif cmd == "/speed":
                try:
                    s = float(arg)
                    if 0.1 <= s <= 3.0:
                        speed = s
                        print(f"  ✅ Speed: {speed}x")
                    else:
                        print("  ⚠  Speed must be 0.1–3.0")
                except ValueError:
                    print("  ⚠  Invalid speed")
            elif cmd == "/play":
                auto_play = not auto_play
                print(f"  ✅ Autoplay: {'on' if auto_play else 'off'}")
            elif cmd == "/mp3":
                if output_format == "wav":
                    if check_mp3_support():
                        output_format = "mp3"
                        print("  ✅ Format: MP3")
                    else:
                        print("  ⚠  No MP3 encoder. Install: brew install ffmpeg")
                else:
                    output_format = "wav"
                    print("  ✅ Format: WAV")
            elif cmd == "/voices":
                print_voices()
            else:
                print(f"  ⚠  Unknown command: {cmd}")
            continue

        output_path = os.path.join(output_dir, f"kokoro_output.{output_format}")
        filepath = generate_speech(kokoro, text, voice, speed, output_path)
        if filepath and auto_play:
            play_audio(filepath)

# ── Main ─────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Kokoro TTS Local — High-quality text-to-speech (ONNX Runtime)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                                  Interactive mode
  %(prog)s "Hello, world!"                  Quick generate & play
  %(prog)s -v af_bella "Good morning"       Use a specific voice
  %(prog)s -f article.txt -o out.mp3        Convert file to speech (MP3)
  %(prog)s --no-play -f chapter1.txt -v bf_emma -s 0.9 -o chapter1.mp3
  %(prog)s --list-voices                    Show all voices
        """
    )
    parser.add_argument("text", nargs="?", help="Text to speak")
    parser.add_argument("-v", "--voice", default=DEFAULT_VOICE,
                        help=f"Voice (default: {DEFAULT_VOICE})")
    parser.add_argument("-s", "--speed", type=float, default=1.0,
                        help="Speed 0.1-3.0 (default: 1.0)")
    parser.add_argument("-o", "--output", default=None,
                        help="Output path — .wav or .mp3")
    parser.add_argument("-f", "--file", default=None,
                        help="Read text from file")
    parser.add_argument("--list-voices", action="store_true",
                        help="List all available voices")
    parser.add_argument("--no-play", action="store_true",
                        help="Don't auto-play the audio")

    args = parser.parse_args()

    if args.list_voices:
        print_voices()
        sys.exit(0)

    text = args.text
    if args.file:
        filepath = resolve_path(args.file)
        if not os.path.isfile(filepath):
            print(f"⚠  File not found: {filepath}")
            print(f"   (working dir: {os.getcwd()})")
            sys.exit(1)
        with open(filepath, "r") as fh:
            text = fh.read().strip()
        if not text:
            print(f"⚠  File is empty: {filepath}")
            sys.exit(1)

    if args.voice not in ALL_VOICES:
        print(f"⚠  Unknown voice: {args.voice}")
        print_voices()
        sys.exit(1)

    kokoro = load_kokoro()

    if text:
        output = args.output or os.path.join(os.getcwd(), "kokoro_output.wav")
        filepath = generate_speech(kokoro, text, args.voice, args.speed, output)
        if filepath and not args.no_play:
            play_audio(filepath)
    else:
        interactive_mode(kokoro)

if __name__ == "__main__":
    main()
