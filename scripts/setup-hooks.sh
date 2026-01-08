#!/bin/bash

# Install git hooks for this repository

HOOKS_DIR="scripts/hooks"
GIT_HOOKS_DIR=".git/hooks"

echo "📦 Installing git hooks..."

if [ ! -d "$HOOKS_DIR" ]; then
    echo "❌ Error: $HOOKS_DIR directory not found"
    exit 1
fi

# Copy hooks to .git/hooks
for hook_file in "$HOOKS_DIR"/*; do
    hook_name=$(basename "$hook_file")
    cp "$hook_file" "$GIT_HOOKS_DIR/$hook_name"
    chmod +x "$GIT_HOOKS_DIR/$hook_name"
    echo "✅ Installed $hook_name"
done

echo ""
echo "✨ Git hooks installed successfully!"
echo "Commit messages will now be validated against Conventional Commits format."
