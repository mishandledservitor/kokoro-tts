#!/bin/bash
# ══════════════════════════════════════════════════════════════════════════════
# Kokoro TTS Local — Setup Script for macOS (Intel)
# Uses kokoro-onnx (ONNX Runtime) — no PyTorch required!
# ══════════════════════════════════════════════════════════════════════════════

set -e

INSTALL_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$INSTALL_DIR"

MODEL_URL="https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/kokoro-v1.0.onnx"
VOICES_URL="https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/voices-v1.0.bin"

echo ""
echo "╔══════════════════════════════════════════════════════════╗"
echo "║     🎙  KOKORO TTS LOCAL — macOS Intel Setup  🎙         ║"
echo "║     Powered by ONNX Runtime (no PyTorch needed)          ║"
echo "╚══════════════════════════════════════════════════════════╝"
echo ""
echo "   Install directory: $INSTALL_DIR"
echo ""

# ── 1. Check for Homebrew ────────────────────────────────────────────────────
echo "🔍 Step 1/5: Checking for Homebrew..."
if ! command -v brew &> /dev/null; then
    echo "   ⚠  Homebrew not found. Installing..."
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
else
    echo "   ✅ Homebrew found"
fi

# ── 2. Install ffmpeg (for MP3 support) ─────────────────────────────────────
echo ""
echo "🔍 Step 2/5: Checking for ffmpeg (MP3 encoding)..."
if ! command -v ffmpeg &> /dev/null; then
    echo "   📦 Installing ffmpeg..."
    brew install ffmpeg
else
    echo "   ✅ ffmpeg found"
fi

# ── 3. Check Python ─────────────────────────────────────────────────────────
echo ""
echo "🔍 Step 3/5: Checking Python..."
PYTHON_CMD=""

if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
    MAJOR=$(echo "$PYTHON_VERSION" | cut -d. -f1)
    MINOR=$(echo "$PYTHON_VERSION" | cut -d. -f2)
    if [ "$MAJOR" -ge 3 ] && [ "$MINOR" -ge 10 ]; then
        PYTHON_CMD="python3"
        echo "   ✅ Python $PYTHON_VERSION found"
    fi
fi

if [ -z "$PYTHON_CMD" ]; then
    echo "   ⚠  Python 3.10+ required. Installing via Homebrew..."
    brew install python@3.12
    PYTHON_CMD="python3"
fi

# ── 4. Create venv & install packages ───────────────────────────────────────
echo ""
echo "📦 Step 4/5: Setting up Python environment..."

if [ ! -d "$INSTALL_DIR/venv" ]; then
    echo "   🐍 Creating virtual environment..."
    $PYTHON_CMD -m venv "$INSTALL_DIR/venv"
else
    echo "   ✅ Virtual environment exists"
fi

source "$INSTALL_DIR/venv/bin/activate"

echo "   📦 Upgrading pip..."
pip install --upgrade pip setuptools wheel -q

echo "   📦 Installing kokoro-onnx + soundfile..."
pip install -U kokoro-onnx soundfile numpy -q

# ── 5. Download model files ─────────────────────────────────────────────────
echo ""
echo "📥 Step 5/5: Downloading model files..."

if [ ! -f "$INSTALL_DIR/kokoro-v1.0.onnx" ]; then
    echo "   📥 Downloading kokoro-v1.0.onnx (~300 MB)..."
    curl -L -o "$INSTALL_DIR/kokoro-v1.0.onnx" "$MODEL_URL"
    echo "   ✅ Model downloaded"
else
    echo "   ✅ kokoro-v1.0.onnx already exists"
fi

if [ ! -f "$INSTALL_DIR/voices-v1.0.bin" ]; then
    echo "   📥 Downloading voices-v1.0.bin..."
    curl -L -o "$INSTALL_DIR/voices-v1.0.bin" "$VOICES_URL"
    echo "   ✅ Voices downloaded"
else
    echo "   ✅ voices-v1.0.bin already exists"
fi

# ── Create launcher ─────────────────────────────────────────────────────────
cat > "$INSTALL_DIR/kokoro" << LAUNCHER
#!/bin/bash
SCRIPT_DIR="$INSTALL_DIR"
source "\$SCRIPT_DIR/venv/bin/activate"
exec python "\$SCRIPT_DIR/kokoro_tts_local.py" "\$@"
LAUNCHER

chmod +x "$INSTALL_DIR/kokoro"

# ── Done! ────────────────────────────────────────────────────────────────────
echo ""
echo "╔══════════════════════════════════════════════════════════╗"
echo "║                 ✅  SETUP COMPLETE!                      ║"
echo "╠══════════════════════════════════════════════════════════╣"
echo "║                                                          ║"
echo "║  Quick start:                                            ║"
echo "║    cd $INSTALL_DIR"
echo "║    ./kokoro \"Hello, this is Kokoro TTS!\"                 ║"
echo "║                                                          ║"
echo "║  Interactive mode:                                       ║"
echo "║    ./kokoro                                              ║"
echo "║                                                          ║"
echo "║  List voices:                                            ║"
echo "║    ./kokoro --list-voices                                ║"
echo "║                                                          ║"
echo "║  Narrate a file:                                         ║"
echo "║    ./kokoro --no-play -f chapter.txt -v bf_emma \\        ║"
echo "║      -s 0.9 -o chapter.mp3                               ║"
echo "║                                                          ║"
echo "║  Everything runs offline after setup.                    ║"
echo "║                                                          ║"
echo "╚══════════════════════════════════════════════════════════╝"
echo ""
