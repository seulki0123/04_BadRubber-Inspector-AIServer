"""Runtime Grade Selection for the Inspector AI server.

`GradeSelector` holds the currently-loaded production profile together with its
`Detector` and baler `Classifier` instances. When a request arrives with a
`(production, grade)` pair that differs from the currently-loaded one, it
reloads the profile via `load_config(override_line=..., override_grade=...)`
and re-instantiates both models in-place. All switches are logged.

Thread-safe: FastAPI runs sync endpoints in a thread pool, so `ensure()`
serializes reloads with an `RLock` and reads under the same lock.
"""
from __future__ import annotations

import os
import threading
import time
from typing import Optional

from defect_detection import Detector
from baler_classification import Classifier

from .config import load_config
from .logger import ProcessLogger


class GradeSelector:
    def __init__(self, config_path: str = "config.yaml"):
        self._config_path = config_path
        self._lock = threading.RLock()
        self._logger = ProcessLogger("GradeSelector")

        config = load_config(config_path)
        config["production"]["save_tmp_dir"] = "./tmp"

        prod = config["production"]
        self._logger.log_info(
            f"Initial grade selection: line={prod['line']}, grade={prod['grade']}, "
            f"return_mode={prod.get('return_mode')}"
        )

        # if prod["save_meta_dir"] and os.path.exists(prod["save_meta_dir"]):
        #     raise ValueError(f"Save directory already exists: {prod['save_meta_dir']}")
        # if prod["save_image_dir"] and os.path.exists(prod["save_image_dir"]):
        #     raise ValueError(f"Save directory already exists: {prod['save_image_dir']}")

        self._config = config
        self._detector = Detector(config=config["defect_detection"])
        self._baler_classifier = Classifier(config=config["baler_classification"])


    @property
    def config(self) -> dict:
        with self._lock:
            return self._config

    @property
    def production(self) -> dict:
        with self._lock:
            return self._config["production"]

    @property
    def detector(self) -> Detector:
        with self._lock:
            return self._detector

    @property
    def baler_classifier(self) -> Classifier:
        with self._lock:
            return self._baler_classifier

    def ensure(
        self,
        line: Optional[str],
        grade: Optional[str],
    ) -> dict:
        """Reload the profile/models if `(line, grade)` differs from current.

        `None` on either argument keeps the current value. Returns the
        current `production` dict (after any reload).
        """
        with self._lock:
            cur = self._config["production"]
            cur_line = cur["line"]
            cur_grade = cur["grade"]

            target_line = line or cur_line
            target_grade = str(grade) if grade is not None else cur_grade

            if target_line == cur_line and target_grade == str(cur_grade):
                return self._config["production"]

            self._logger.log_info(
                f"Grade selection change requested: "
                f"({cur_line}, {cur_grade}) -> ({target_line}, {target_grade}); "
                f"reloading profile and models."
            )

            t0 = time.time()

            try:
                new_config = load_config(
                    self._config_path,
                    override_line=target_line,
                    override_grade=target_grade,
                )
            except Exception as e:
                self._logger.log_error(
                    f"Failed to load profile for ({target_line}, {target_grade}): {e}. "
                    f"Keeping current ({cur_line}, {cur_grade})."
                )
                raise

            new_config["production"]["save_tmp_dir"] = cur.get("save_tmp_dir", "./tmp")

            new_detector = Detector(config=new_config["defect_detection"])
            new_classifier = Classifier(config=new_config["baler_classification"])

            self._config = new_config
            self._detector = new_detector
            self._baler_classifier = new_classifier

            self._logger.log_info(
                f"Grade selection loaded: line={target_line}, grade={target_grade}, "
                f"return_mode={new_config['production'].get('return_mode')} "
                f"(reload took {(time.time() - t0) * 1000:.1f}ms)"
            )

            return self._config["production"]
