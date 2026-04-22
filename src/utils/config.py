"""Grade Selection-aware config loader for the Inspector AI server.

Resolves a single `config.yaml` into:

    - `production`: line/grade/save dirs/return_mode  (ready for routes)
    - `defect_detection`: dict consumed by `defect_detection.Detector`
    - `baler_classification`: dict consumed by `baler_classification.Classifier`

The `production_information.line/grade` drives which profile is selected from
the shared `src/Profiles/profiles/registry.yaml`. Foundation-level defaults
for `return_mode` and `show` live inside each base profile; end-users tweak
them via the dedicated `production_information.return_mode` and
`defect_detection.show` paths (not under `overrides:`).
"""
from __future__ import annotations
from typing import Optional

import yaml

from profiles import (  # noqa: E402
    build_runtime_overrides,
    load_profile,
    to_baler_classification_config,
    to_defect_detection_config,
)


def _read_config_yaml(path: str) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def load_config(
    config_path: str = "config.yaml",
    *,
    override_line: Optional[str] = None,
    override_grade: Optional[str] = None,
) -> dict:
    raw = _read_config_yaml(config_path)

    prod = raw.get("production_information") or {}
    line = override_line or prod.get("line")
    grade = override_grade or prod.get("grade")
    if not line or not grade:
        raise ValueError(
            "config.yaml: `production_information.line` and `.grade` are required."
        )

    checkpoint_root = raw.get("checkpoint_root")
    if not isinstance(checkpoint_root, str) or not checkpoint_root.strip():
        raise ValueError(
            f"{config_path}: top-level `checkpoint_root:` is required "
            "(absolute path that every profile checkpoint is anchored to)."
        )
    checkpoint_root = checkpoint_root.strip()

    # Defect-side runtime overrides: defect_detection.overrides + legacy paths
    # (production_information.return_mode, defect_detection.show).
    defect_extra = build_runtime_overrides(raw, section="defect_detection")

    # Baler-side runtime overrides: everything under baler_classification.overrides
    # is treated as an override to the Profile's `baler_classifier` section.
    baler_sub = raw.get("baler_classification") or {}
    baler_overrides_raw = baler_sub.get("overrides") or {}
    combined = dict(defect_extra or {})
    if baler_overrides_raw:
        combined["baler_classifier"] = {
            **(combined.get("baler_classifier") or {}),
            **(baler_overrides_raw.get("classifier") or baler_overrides_raw),
        }

    resolved = load_profile(
        line, grade, checkpoint_root, extra_overrides=combined or None
    )

    defect_cfg = to_defect_detection_config(resolved)
    baler_cfg = to_baler_classification_config(resolved)

    production = {
        "line": line,
        "grade": str(grade),
        "save_meta_dir": prod.get("save_meta_dir"),
        "save_image_dir": prod.get("save_image_dir"),
        "return_mode": resolved.get("return_mode"),
    }

    return {
        "production": production,
        "defect_detection": defect_cfg,
        "baler_classification": baler_cfg,
        "log_dir": raw.get("log_dir") or {},
    }
