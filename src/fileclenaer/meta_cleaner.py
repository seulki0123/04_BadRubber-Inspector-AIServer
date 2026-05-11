"""
MetaCleaner — `production_information.save_meta_dir` 아래 오래된 메타 `.json` 삭제.

DefectService 저장 구조 (`get_save_path`):

    save_meta_dir / <line> / <grade> / <YYYY-MM-DD> / *.json

CaptureCleaner 와 동일하게 `save_meta_dir` 의 부모를 root, 폴더명을 target 으로 두면
라인·등급·날짜 하위까지 재귀적으로 정리된다.

보존 기간은 **파일 mtime** 기준 (`retention_hours`). 달력 일 자정 기준이 아니라
「마지막 수정으로부터 N시간 지난 파일 삭제」이다. 하루 단위로 맞추려면
`retention_hours: 24` 로 두면 된다.

구성 (`config.yaml` 의 `meta_cleaner` 섹션):

  meta_cleaner:
    enabled: true
    retention_hours: 720          # 예: 30일. 하루≈24
    thread_interval: 3600
    file_extensions:
      - ".json"
    dry_run: false
    remove_empty_dirs: true
"""

import os

from ..utils import load_config

from .base_cleaner import BaseFileCleaner


class MetaCleaner(BaseFileCleaner):
    DEFAULT_FILE_EXTENSIONS = [".json"]

    def __init__(self):
        cfg = load_config()
        prod = cfg.get("production") or {}
        cleaner_cfg = cfg.get("meta_cleaner") or {}

        save_dir = prod.get("save_meta_dir") or "report/metadatas"
        save_dir_abs = os.path.abspath(save_dir)
        root = os.path.dirname(save_dir_abs) or os.sep
        default_target = os.path.basename(save_dir_abs) or "metadatas"

        super().__init__(
            name=self.__class__.__name__,
            root=root,
            cleaner_cfg=cleaner_cfg,
            default_target_dirs=[default_target],
            default_file_extensions=self.DEFAULT_FILE_EXTENSIONS,
            default_remove_empty_dirs=True,
        )
