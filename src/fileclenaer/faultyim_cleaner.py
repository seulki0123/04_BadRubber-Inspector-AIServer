"""
FaultyImageCleaner — `production_information.save_image_dir` 아래 오래된 불량 이미지 삭제.

DefectService 저장 구조 (`get_save_path`):

    save_image_dir / <line> / <grade> / <YYYY-MM-DD> / *.jpg

동작·설명은 `meta_cleaner.MetaCleaner` 와 동일 (mtime + `retention_hours`).

구성 (`config.yaml` 의 `faultyim_cleaner` 섹션):

  faultyim_cleaner:
    enabled: true
    retention_hours: 720
    thread_interval: 3600
    file_extensions:
      - ".jpg"
    dry_run: false
    remove_empty_dirs: true
"""

import os

from ..utils import load_config

from .base_cleaner import BaseFileCleaner


class FaultyImageCleaner(BaseFileCleaner):
    DEFAULT_FILE_EXTENSIONS = [".jpg"]

    def __init__(self):
        cfg = load_config()
        prod = cfg.get("production") or {}
        cleaner_cfg = cfg.get("faultyim_cleaner") or {}

        save_dir = prod.get("save_image_dir") or "report/faulty_images"
        save_dir_abs = os.path.abspath(save_dir)
        root = os.path.dirname(save_dir_abs) or os.sep
        default_target = os.path.basename(save_dir_abs) or "faulty_images"

        super().__init__(
            name=self.__class__.__name__,
            root=root,
            cleaner_cfg=cleaner_cfg,
            default_target_dirs=[default_target],
            default_file_extensions=self.DEFAULT_FILE_EXTENSIONS,
            default_remove_empty_dirs=True,
        )
