#!/bin/bash
# ══════════════════════════════════════════════════════════════════════════════
# Kokoro TTS Local — Uninstall Script
# ══════════════════════════════════════════════════════════════════════════════

INSTALL_DIR="$(cd "$(dirname "$0")" && pwd)"

echo ""
echo "╔══════════════════════════════════════════════════════════╗"
echo "║       🗑  KOKORO TTS LOCAL — UNINSTALL                   ║"
echo "╚══════════════════════════════════════════════════════════╝"
echo ""
echo "   Directory: $INSTALL_DIR"
echo ""

# ── 1. Virtual environment ───────────────────────────────────────────────────
if [ -d "$INSTALL_DIR/venv" ]; then
    SIZE=$(du -sh "$INSTALL_DIR/venv" 2>/dev/null | awk '{print $1}')
    echo "🐍 Virtual environment ($SIZE)"
    read -p "   Delete? [y/N] " c; [[ "$c" =~ ^[Yy]$ ]] && rm -rf "$INSTALL_DIR/venv" && echo "   ✅ Removed" || echo "   ⏭  Skipped"
fi

# ── 2. Model files ──────────────────────────────────────────────────────────
echo ""
for f in "$INSTALL_DIR/kokoro-v1.0.onnx" "$INSTALL_DIR/voices-v1.0.bin"; do
    if [ -f "$f" ]; then
        SIZE=$(du -sh "$f" 2>/dev/null | awk '{print $1}')
        echo "📦 $(basename $f) ($SIZE)"
        read -p "   Delete? [y/N] " c; [[ "$c" =~ ^[Yy]$ ]] && rm -f "$f" && echo "   ✅ Removed" || echo "   ⏭  Skipped"
    fi
done

# ── 3. Launcher ─────────────────────────────────────────────────────────────
echo ""
if [ -f "$INSTALL_DIR/kokoro" ]; then
    echo "🚀 Launcher script"
    read -p "   Delete? [y/N] " c; [[ "$c" =~ ^[Yy]$ ]] && rm -f "$INSTALL_DIR/kokoro" && echo "   ✅ Removed" || echo "   ⏭  Skipped"
fi

# ── 4. Output files ─────────────────────────────────────────────────────────
echo ""
OUTPUTS=$(find "$INSTALL_DIR" -maxdepth 1 -name "kokoro_output*" -o -name "*_tmp.wav" 2>/dev/null)
if [ -n "$OUTPUTS" ]; then
    echo "🔊 Output files:"
    echo "$OUTPUTS" | while read f; do echo "      $(basename $f)"; done
    read -p "   Delete all? [y/N] " c; [[ "$c" =~ ^[Yy]$ ]] && echo "$OUTPUTS" | xargs rm -f && echo "   ✅ Removed" || echo "   ⏭  Skipped"
fi

# ── 5. ffmpeg ────────────────────────────────────────────────────────────────
echo ""
echo "🍺 ffmpeg (may be used by other apps)"
read -p "   Uninstall via Homebrew? [y/N] " c
[[ "$c" =~ ^[Yy]$ ]] && brew uninstall ffmpeg 2>/dev/null && echo "   ✅ Removed" || echo "   ⏭  Kept"

# ── 6. Scripts themselves ────────────────────────────────────────────────────
echo ""
echo "📄 Scripts: kokoro_tts_local.py, setup_kokoro.sh, uninstall_kokoro.sh, README.md"
read -p "   Delete all scripts? (full removal) [y/N] " c
if [[ "$c" =~ ^[Yy]$ ]]; then
    rm -f "$INSTALL_DIR/kokoro_tts_local.py" "$INSTALL_DIR/setup_kokoro.sh" "$INSTALL_DIR/uninstall_kokoro.sh" "$INSTALL_DIR/README.md"
    echo "   ✅ Removed"
    rmdir "$INSTALL_DIR" 2>/dev/null && echo "   ✅ Removed empty directory"
fi

echo ""
echo "✅ Uninstall complete."
echo ""
