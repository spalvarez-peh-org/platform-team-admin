#!/bin/bash

echo "📋 Git Hooks Installation"
echo ""
echo "Choose your preferred setup:"
echo "  1) Quick hooks (⚡ fast) - formatting + linting only"
echo "  2) Full hooks (🔍 thorough) - all checks including tests"
echo ""
read -p "Enter your choice (1 or 2): " choice

case $choice in
    1)
        ./scripts/manage-hooks.sh quick
        ;;
    2)
        ./scripts/manage-hooks.sh full
        ;;
    *)
        echo "Invalid choice. Installing quick hooks by default..."
        ./scripts/manage-hooks.sh quick
        ;;
esac

echo ""
echo "💡 You can change this later with: ./scripts/manage-hooks.sh [quick|full|remove]"
