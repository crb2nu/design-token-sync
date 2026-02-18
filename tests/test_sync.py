from pathlib import Path

import sync


def _sample_tokens() -> dict:
    return {
        "$schema": "./tokens.schema.json",
        "palettes": {"brand": {"primary": "#3B82F6"}},
        "diagram": {
            "light": {
                "bg": "#fff",
                "fg": "#111",
                "muted": "#777",
                "panel": "#eee",
                "panel2": "#ddd",
                "border": "#ccc",
                "noteBg": "#fef3c7",
                "noteBorder": "#f59e0b",
            }
        },
        "semantic": {"bg": {"deep": "#000"}, "text": {"main": "#fff"}, "status": {"ok": "#0f0"}},
        "geometry": {"radius": {"s": "4px"}, "space": {"s": "8px"}},
        "glass": {
            "bg": "rgba(0,0,0,0.5)",
            "blur": "blur(10px)",
            "border": "rgba(255,255,255,0.1)",
            "shadow": "0 2px 10px rgba(0,0,0,0.3)",
            "text": "#fff",
        },
    }


def test_validate_tokens_passes_for_valid_shape() -> None:
    errors = sync.validate_tokens(_sample_tokens())
    assert errors == []


def test_validate_tokens_reports_missing_sections() -> None:
    errors = sync.validate_tokens({"palettes": {}})
    assert "Missing required section: diagram" in errors
    assert "Missing required section: semantic" in errors


def test_strip_metadata_removes_prefixed_keys() -> None:
    stripped = sync.strip_metadata(_sample_tokens())
    assert "$schema" not in stripped
    assert "palettes" in stripped


def test_sync_to_target_writes_stripped_json(tmp_path: Path) -> None:
    target = tmp_path / "out" / "tokens.json"
    sync.sync_to_target(_sample_tokens(), target)
    content = target.read_text()
    assert '"$schema"' not in content
    assert '"palettes"' in content


def test_generate_typescript_types_includes_named_unions(tmp_path: Path) -> None:
    output = tmp_path / "tokens.types.ts"
    sync.generate_typescript_types(_sample_tokens(), output)
    content = output.read_text()
    assert "export type PaletteName = 'brand';" in content
    assert "export type DiagramThemeName = 'light';" in content


def test_changed_key_paths_reports_nested_changes() -> None:
    before = {"palettes": {"brand": {"primary": "#111111"}}}
    after = {"palettes": {"brand": {"primary": "#222222", "secondary": "#333333"}}}
    paths = sync.changed_key_paths(before, after)
    assert "palettes.brand.primary" in paths
    assert "palettes.brand.secondary" in paths


def test_sync_to_target_dry_run_does_not_write(tmp_path: Path) -> None:
    target = tmp_path / "out" / "tokens.json"
    changed = sync.sync_to_target(_sample_tokens(), target, dry_run=True)
    assert target.exists() is False
    assert "palettes" in changed
