#!/usr/bin/env python3
"""Design Token Sync Tool.

Syncs design tokens from a single source of truth (tokens.json) to multiple
target libraries (visual-kit for TypeScript, py-visual-kit for Python).

Usage:
    python sync.py                    # Sync all targets
    python sync.py --check            # Validate tokens only
    python sync.py --dry-run          # Preview changed keys without writing
    python sync.py --target ts        # Sync TypeScript only
    python sync.py --target python    # Sync Python only
    python sync.py --generate-types   # Generate TypeScript types
"""

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


# Configuration
SCRIPT_DIR = Path(__file__).parent
SOURCE_TOKENS = SCRIPT_DIR / "tokens.json"

# Default target paths (can be overridden via args)
DEFAULT_TARGETS = {
    "ts": Path(__file__).parent.parent / "visual-kit" / "tokens.json",
    "python": Path(__file__).parent.parent / "py-visual-kit" / "src" / "visual_kit" / "tokens.json",
}


def load_tokens(path: Path) -> dict[str, Any]:
    """Load tokens from JSON file."""
    with open(path, "r") as f:
        return json.load(f)


def validate_tokens(tokens: dict[str, Any]) -> list[str]:
    """Validate token structure. Returns list of errors."""
    errors: list[str] = []

    def is_color_value(value: str) -> bool:
        return value.startswith("#") or value.startswith("rgb")

    required_sections = ["palettes", "diagram", "semantic", "geometry", "glass"]
    for section in required_sections:
        if section not in tokens:
            errors.append(f"Missing required section: {section}")

    # Validate palettes
    if "palettes" in tokens:
        for palette_name, palette in tokens["palettes"].items():
            if not isinstance(palette, dict):
                errors.append(f"Palette '{palette_name}' should be an object")
                continue
            for color_name, color_value in palette.items():
                if not isinstance(color_value, str):
                    errors.append(f"Color '{palette_name}.{color_name}' should be a string")
                elif not is_color_value(color_value):
                    errors.append(f"Color '{palette_name}.{color_name}' should be hex or rgb format")

    # Validate diagram themes
    if "diagram" in tokens:
        required_theme_props = ["bg", "fg", "muted", "panel", "panel2", "border", "noteBg", "noteBorder"]
        for theme_name, theme in tokens["diagram"].items():
            if not isinstance(theme, dict):
                errors.append(f"Diagram theme '{theme_name}' should be an object")
                continue
            for prop in required_theme_props:
                if prop not in theme:
                    errors.append(f"Diagram theme '{theme_name}' missing property: {prop}")

    # Validate optional gradients
    if "gradients" in tokens:
        gradients = tokens["gradients"]
        if not isinstance(gradients, dict):
            errors.append("Gradients should be an object")
        else:
            for gradient_name, gradient_values in gradients.items():
                if not isinstance(gradient_values, list):
                    errors.append(f"Gradient '{gradient_name}' should be a list")
                    continue
                if len(gradient_values) < 2:
                    errors.append(f"Gradient '{gradient_name}' should have at least 2 colors")
                for idx, color in enumerate(gradient_values):
                    if not isinstance(color, str) or not is_color_value(color):
                        errors.append(
                            f"Gradient '{gradient_name}' color at index {idx} should be hex or rgb string"
                        )

    # Validate optional shadows
    if "shadows" in tokens:
        shadows = tokens["shadows"]
        if not isinstance(shadows, dict):
            errors.append("Shadows should be an object")
        else:
            for shadow_name, shadow_value in shadows.items():
                if not isinstance(shadow_value, str):
                    errors.append(f"Shadow '{shadow_name}' should be a string")

    return errors


def strip_metadata(tokens: dict[str, Any]) -> dict[str, Any]:
    """Remove $-prefixed metadata fields for output."""
    return {k: v for k, v in tokens.items() if not k.startswith("$")}


def load_existing_tokens(path: Path) -> dict[str, Any] | None:
    """Load existing target tokens if the file exists and is valid JSON."""
    if not path.exists():
        return None
    try:
        with open(path, "r") as f:
            data = json.load(f)
    except (OSError, json.JSONDecodeError):
        return None
    if isinstance(data, dict):
        return data
    return None


def changed_key_paths(before: Any, after: Any, prefix: str = "") -> list[str]:
    """Return leaf key paths that differ between two token structures."""
    if isinstance(before, dict) and isinstance(after, dict):
        paths: list[str] = []
        for key in sorted(set(before.keys()) | set(after.keys())):
            key_path = f"{prefix}.{key}" if prefix else key
            paths.extend(changed_key_paths(before.get(key), after.get(key), key_path))
        return paths
    if before != after:
        return [prefix or "<root>"]
    return []


def print_change_summary(changed_paths: list[str], preview_limit: int = 8) -> None:
    """Print a concise summary of changed keys."""
    if not changed_paths:
        print("    No token key changes detected.")
        return
    preview = ", ".join(changed_paths[:preview_limit])
    if len(changed_paths) > preview_limit:
        preview = f"{preview}, +{len(changed_paths) - preview_limit} more"
    print(f"    Changed keys ({len(changed_paths)}): {preview}")


def sync_to_target(tokens: dict[str, Any], target_path: Path, dry_run: bool = False) -> list[str]:
    """Sync tokens to a target file and return changed key paths."""
    clean_tokens = strip_metadata(tokens)
    existing_tokens = load_existing_tokens(target_path) or {}
    changed_paths = changed_key_paths(existing_tokens, clean_tokens)

    if dry_run:
        print(f"  [DRY RUN] Would sync to: {target_path}")
        print_change_summary(changed_paths)
        return changed_paths

    target_path.parent.mkdir(parents=True, exist_ok=True)
    with open(target_path, "w") as f:
        json.dump(clean_tokens, f, indent=2)
        f.write("\n")

    print(f"  Synced to: {target_path}")
    print_change_summary(changed_paths)
    return changed_paths


def generate_typescript_types(tokens: dict[str, Any], output_path: Path) -> None:
    """Generate TypeScript type definitions from tokens."""
    clean_tokens = strip_metadata(tokens)

    lines = [
        "// Auto-generated by design-token-sync - DO NOT EDIT",
        f"// Generated at: {datetime.now(timezone.utc).isoformat()}",
        "",
        "export interface DiagramTheme {",
        "  bg: string;",
        "  fg: string;",
        "  muted: string;",
        "  panel: string;",
        "  panel2: string;",
        "  border: string;",
        "  noteBg: string;",
        "  noteBorder: string;",
        "  accent?: string;",
        "  accent2?: string;",
        "  glow?: string;",
        "  gradientStart?: string;",
        "  gradientEnd?: string;",
        "}",
        "",
        "export interface SemanticColors {",
        "  bg: Record<string, string>;",
        "  text: Record<string, string>;",
        "  status: Record<string, string>;",
        "}",
        "",
        "export interface GeometryTokens {",
        "  radius: Record<string, string>;",
        "  space: Record<string, string>;",
        "}",
        "",
        "export interface GlassTokens {",
        "  bg: string;",
        "  blur: string;",
        "  border: string;",
        "  shadow: string;",
        "  text: string;",
        "}",
        "",
        "export interface DesignTokens {",
        "  palettes: Record<string, Record<string, string>>;",
        "  diagram: Record<string, DiagramTheme>;",
        "  semantic: SemanticColors;",
        "  geometry: GeometryTokens;",
        "  glass: GlassTokens;",
        "  gradients: Record<string, string[]>;",
        "  shadows: Record<string, string>;",
        "}",
        "",
    ]

    # Generate palette type with actual keys
    palette_names = list(clean_tokens.get("palettes", {}).keys())
    lines.append(f"export type PaletteName = {' | '.join(repr(p) for p in palette_names)};")
    lines.append("")

    # Generate diagram theme names
    theme_names = list(clean_tokens.get("diagram", {}).keys())
    lines.append(f"export type DiagramThemeName = {' | '.join(repr(t) for t in theme_names)};")
    lines.append("")

    # Export the tokens constant
    lines.append("import tokensJson from './tokens.json';")
    lines.append("")
    lines.append("export const tokens = tokensJson as DesignTokens;")
    lines.append("")
    lines.append("export function getPalette(name: PaletteName): Record<string, string> {")
    lines.append("  return tokens.palettes[name];")
    lines.append("}")
    lines.append("")
    lines.append("export function getDiagramTheme(name: DiagramThemeName): DiagramTheme {")
    lines.append("  return tokens.diagram[name];")
    lines.append("}")
    lines.append("")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w") as f:
        f.write("\n".join(lines))

    print(f"  Generated TypeScript types: {output_path}")


def generate_python_types(tokens: dict[str, Any], output_path: Path) -> None:
    """Generate Python type stubs from tokens."""
    clean_tokens = strip_metadata(tokens)

    palette_names = list(clean_tokens.get("palettes", {}).keys())
    theme_names = list(clean_tokens.get("diagram", {}).keys())

    lines = [
        '"""Auto-generated type hints for design tokens - DO NOT EDIT."""',
        f"# Generated at: {datetime.now(timezone.utc).isoformat()}",
        "",
        "from typing import Literal",
        "",
        f"PaletteName = Literal[{', '.join(repr(p) for p in palette_names)}]",
        f"DiagramThemeName = Literal[{', '.join(repr(t) for t in theme_names)}]",
        "",
    ]

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w") as f:
        f.write("\n".join(lines))

    print(f"  Generated Python types: {output_path}")


def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Design Token Sync Tool")
    parser.add_argument("--check", action="store_true", help="Validate tokens only")
    parser.add_argument("--dry-run", action="store_true",
                        help="Show target changes without writing files")
    parser.add_argument("--target", choices=["ts", "python", "all"], default="all",
                        help="Target to sync (default: all)")
    parser.add_argument("--generate-types", action="store_true",
                        help="Also generate TypeScript/Python type definitions")
    parser.add_argument("--ts-path", type=Path, help="Override TypeScript target path")
    parser.add_argument("--python-path", type=Path, help="Override Python target path")
    parser.add_argument("--source", type=Path, default=SOURCE_TOKENS,
                        help="Source tokens.json path")

    args = parser.parse_args()

    # Load source tokens
    if not args.source.exists():
        print(f"Error: Source file not found: {args.source}", file=sys.stderr)
        return 1

    print(f"Loading tokens from: {args.source}")
    tokens = load_tokens(args.source)

    # Validate
    print("Validating tokens...")
    errors = validate_tokens(tokens)
    if errors:
        print("Validation errors:", file=sys.stderr)
        for error in errors:
            print(f"  - {error}", file=sys.stderr)
        return 1
    print("  Validation passed!")

    if args.check:
        return 0

    # Determine targets
    targets: dict[str, Path] = {}
    if args.target in ("ts", "all"):
        targets["ts"] = args.ts_path or DEFAULT_TARGETS["ts"]
    if args.target in ("python", "all"):
        targets["python"] = args.python_path or DEFAULT_TARGETS["python"]

    # Sync to targets
    print("Syncing tokens...")
    for target_path in targets.values():
        sync_to_target(tokens, target_path, dry_run=args.dry_run)

    # Generate types if requested
    if args.generate_types:
        print("Generating type definitions...")
        if args.dry_run:
            if "ts" in targets:
                ts_types_path = targets["ts"].parent / "tokens.types.ts"
                print(f"  [DRY RUN] Would generate TypeScript types: {ts_types_path}")
            if "python" in targets:
                py_types_path = targets["python"].parent / "token_types.py"
                print(f"  [DRY RUN] Would generate Python types: {py_types_path}")
        else:
            if "ts" in targets:
                ts_types_path = targets["ts"].parent / "tokens.types.ts"
                generate_typescript_types(tokens, ts_types_path)
            if "python" in targets:
                py_types_path = targets["python"].parent / "token_types.py"
                generate_python_types(tokens, py_types_path)

    print("Done!")
    return 0


if __name__ == "__main__":
    sys.exit(main())
