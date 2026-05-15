"""
BalerHandoffCleaner — `production_information.baler_handoff_dir` 에 남는
짝-안-맞는 baler handoff JSON 정리.

`/classify` -> `/detect_fault` 두 요청 사이의 임시 인계용 디렉토리이므로
정상 경로에서는 defect 단계가 `pop_baler_from_handoff` 로 즉시 삭제한다.
단, classify 만 들어오고 같은 id 의 defect 가 안 오는 경우(예: 누락/오류)에는
파일이 남기 때문에 짧은 보존 기간으로 주기적으로 청소한다.

BalerService 저장 구조 (`get_save_path`):

    baler_handoff_dir / <YYYY-MM-DD> / <request_id>.json

동작·설명은 `meta_cleaner.MetaCleaner` 와 동일 (mtime + `retention_hours`).

구성 (`config.yaml` 의 `baler_handoff_cleaner` 섹션):

  baler_handoff_cleaner:
    enabled: true
    retention_hours: 24
    thread_interval: 3600
    file_extensions:
      - ".json"
    dry_run: false
    remove_empty_dirs: true
"""

import os

from ..utils import load_config

from .base_cleaner import BaseFileCleaner


class BalerHandoffCleaner(BaseFileCleaner):
    DEFAULT_FILE_EXTENSIONS = [".json"]

    def __init__(self):
        cfg = load_config()
        prod = cfg.get("production") or {}
        cleaner_cfg = cfg.get("baler_handoff_cleaner") or {}

        handoff_dir = prod.get("baler_handoff_dir") or "./tmp"
        handoff_dir_abs = os.path.abspath(handoff_dir)
        root = os.path.dirname(handoff_dir_abs) or os.sep
        default_target = os.path.basename(handoff_dir_abs) or "tmp"

        super().__init__(
            name=self.__class__.__name__,
            root=root,
            cleaner_cfg=cleaner_cfg,
            default_target_dirs=[default_target],
            default_file_extensions=self.DEFAULT_FILE_EXTENSIONS,
            default_remove_empty_dirs=True,
        )
