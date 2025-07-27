# Platform Team Admin

Infrastructure as Code for managing platform team resources using Pulumi.

## Development Setup

This repository includes VS Code configuration (`.vscode/`) for consistent development experience:

- **Extensions**: Recommended tools for Python, formatting, and linting
- **Settings**: Automatic formatting with Black, import sorting with isort, linting with Ruff
- **Tasks**: Shortcuts for running tests, coverage, and quality checks

### Quick Start
1. Install recommended VS Code extensions (you'll be prompted)
2. Install git hooks: `./scripts/install-githooks.sh`
3. Install dependencies: `uv sync --group lint --group test`

The VS Code settings ensure your editor matches our CI pipeline. You can override any settings in your personal VS Code configuration if needed.