#!/bin/bash

# Git Hooks Management Script
cp .git-hooks/commit-msg .git/hooks/commit-msg
cp .git-hooks/pre-push .git/hooks/pre-push
cp .git-hooks/pre-commit .git/hooks/pre-commit
chmod +x .git/hooks/commit-msg
chmod +x .git/hooks/pre-push
chmod +x .git/hooks/pre-commit
