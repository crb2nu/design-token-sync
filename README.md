# design-token-sync

Design token synchronization tool for FlexInfer visual libraries.

`design-token-sync` keeps a single source of truth (`tokens.json`) and syncs it to downstream libraries:
- `visual-kit` (TypeScript)
- `py-visual-kit` (Python)

## Installation

```bash
pip install -e ".[dev]"
```

## Usage

```bash
# Validate only
python sync.py --check

# Sync both TypeScript and Python targets
python sync.py

# Preview changed token keys without writing files
python sync.py --dry-run

# Sync only TypeScript target
python sync.py --target ts

# Sync only Python target
python sync.py --target python

# Also generate type definitions
python sync.py --generate-types
```

## Development

```bash
ruff check sync.py tests
pytest -v
```

## Repository Layout

- `tokens.json`: source-of-truth token file
- `sync.py`: CLI sync tool and validators
- `tests/`: unit tests for validation and generation logic
