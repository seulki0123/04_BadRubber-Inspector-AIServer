"""Grade Selection-aware config loader for the Inspector AI server.

Resolves a single `config.yaml` into:

    - `production`: line/grade/save dirs/return_mode  (ready for routes)
    - `defect_detection`: dict consumed by `defect_detection.Detector`
    - `baler_classification`: dict consumed by `baler_classification.Classifier`

The `production_information.line/grade` selects the foundation profile by
convention (`products/<LINE>/_<grade>.py`); everything else (classes, checkpoints,
thresholds, `return_mode`, `show`) lives inside that base profile module.
"""
from __future__ import annotations
from typing import Optional

import yaml

from profiles import (  # noqa: E402
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

    resolved = load_profile(line, grade, checkpoint_root)

    defect_cfg = to_defect_detection_config(resolved)
    baler_cfg = to_baler_classification_config(resolved)

    production = {
        "line": line,
        "grade": str(grade),
        "save_meta_dir": prod["save_meta_dir"],
        "save_image_dir": prod["save_image_dir"],
        "baler_handoff_dir": prod["baler_handoff_dir"],
        "return_mode": resolved["return_mode"],
    }

    return {
        "production": production,
        "defect_detection": defect_cfg,
        "baler_classification": baler_cfg,
        "log_dir": raw["log_dir"],
        "log_cleaner": raw["log_cleaner"],
        "meta_cleaner": raw["meta_cleaner"],
        "faultyim_cleaner": raw["faultyim_cleaner"],
        "baler_handoff_cleaner": raw["baler_handoff_cleaner"],
    }
