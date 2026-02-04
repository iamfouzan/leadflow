#!/bin/bash
# Quick setup script for UV package manager

set -e

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Installing UV Package Manager${NC}"
echo -e "${GREEN}========================================${NC}"

# Check if uv is already installed
if command -v uv &> /dev/null; then
    echo -e "${YELLOW}UV is already installed!${NC}"
    uv --version
    echo ""
    read -p "Do you want to reinstall? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo -e "${GREEN}Skipping UV installation${NC}"
        exit 0
    fi
fi

# Install UV
echo -e "${GREEN}Installing UV...${NC}"
curl -LsSf https://astral.sh/uv/install.sh | sh

# Add to PATH for current session
export PATH="$HOME/.cargo/bin:$PATH"

# Add to shell config if not already there
SHELL_CONFIG=""
if [ -f "$HOME/.bashrc" ]; then
    SHELL_CONFIG="$HOME/.bashrc"
elif [ -f "$HOME/.zshrc" ]; then
    SHELL_CONFIG="$HOME/.zshrc"
fi

if [ -n "$SHELL_CONFIG" ]; then
    if ! grep -q 'export PATH="$HOME/.cargo/bin:$PATH"' "$SHELL_CONFIG"; then
        echo 'export PATH="$HOME/.cargo/bin:$PATH"' >> "$SHELL_CONFIG"
        echo -e "${GREEN}Added UV to PATH in $SHELL_CONFIG${NC}"
    fi
fi

# Verify installation
if command -v uv &> /dev/null; then
    echo -e "${GREEN}========================================${NC}"
    echo -e "${GREEN}✓ UV installed successfully!${NC}"
    uv --version
    echo -e "${GREEN}========================================${NC}"
    echo ""
    echo -e "${YELLOW}Next steps:${NC}"
    echo "  1. Reload your shell: source ~/.bashrc (or ~/.zshrc)"
    echo "  2. Create venv: uv venv"
    echo "  3. Activate venv: source venv/bin/activate"
    echo "  4. Install deps: uv pip install -r requirements.txt"
    echo "  5. Run app: uvicorn app.main:app --reload"
    echo ""
    echo -e "${GREEN}UV is 10-100x faster than pip! 🚀${NC}"
else
    echo -e "${YELLOW}Installation completed but 'uv' not found in PATH${NC}"
    echo "Please run: source ~/.bashrc (or restart your terminal)"
fi
