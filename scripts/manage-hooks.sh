#!/bin/bash

# Git Hooks Management Script

case "$1" in
    "quick")
        echo "🚀 Installing QUICK pre-commit hooks (formatting + linting only)..."
        cp .git-hooks/commit-msg .git/hooks/commit-msg
        cp .git-hooks/pre-push .git/hooks/pre-push
        cp .git-hooks/pre-commit-quick .git/hooks/pre-commit
        chmod +x .git/hooks/commit-msg
        chmod +x .git/hooks/pre-push  
        chmod +x .git/hooks/pre-commit
        echo "✅ Quick hooks installed!"
        echo "   • Pre-commit: formatting + linting only (⚡ fast)"
        echo "   • Tests will run in CI pipeline"
        ;;
    "full")
        echo "🔍 Installing FULL pre-commit hooks (all checks including tests)..."
        cp .git-hooks/commit-msg .git/hooks/commit-msg
        cp .git-hooks/pre-push .git/hooks/pre-push
        cp .git-hooks/pre-commit .git/hooks/pre-commit
        chmod +x .git/hooks/commit-msg
        chmod +x .git/hooks/pre-push
        chmod +x .git/hooks/pre-commit
        echo "✅ Full hooks installed!"
        echo "   • Pre-commit: all static analysis + tests (🐌 slower but thorough)"
        ;;
    "remove")
        echo "🗑️  Removing all git hooks..."
        rm -f .git/hooks/pre-commit
        rm -f .git/hooks/commit-msg
        rm -f .git/hooks/pre-push
        echo "✅ All hooks removed!"
        ;;
    *)
        echo "Git Hooks Management"
        echo ""
        echo "Usage: $0 [quick|full|remove]"
        echo ""
        echo "Options:"
        echo "  quick  - Install quick pre-commit hooks (formatting + linting only)"
        echo "  full   - Install full pre-commit hooks (all checks + tests)"
        echo "  remove - Remove all git hooks"
        echo ""
        echo "Current hooks status:"
        if [ -f ".git/hooks/pre-commit" ]; then
            if grep -q "Running quick pre-commit" .git/hooks/pre-commit 2>/dev/null; then
                echo "  ⚡ Quick pre-commit hook installed"
            else
                echo "  🔍 Full pre-commit hook installed"
            fi
        else
            echo "  ❌ No pre-commit hook installed"
        fi
        
        if [ -f ".git/hooks/commit-msg" ]; then
            echo "  ✅ Commit message validation installed"
        else
            echo "  ❌ No commit message validation"
        fi
        
        if [ -f ".git/hooks/pre-push" ]; then
            echo "  ✅ Pre-push tag validation installed"
        else
            echo "  ❌ No pre-push validation"
        fi
        ;;
esac
