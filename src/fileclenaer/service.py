"""
FileCleanerService — fileclenaer 모듈의 thread 기동/관리 진입점.

LogCleaner / MetaCleaner / FaultyImageCleaner 인스턴스를 만들고, 각자
thread_interval 로 CustomThread 를 띄운다.
"""

from ..utils import CustomThread

from .faultyim_cleaner import FaultyImageCleaner
from .log_cleaner import LogCleaner
from .meta_cleaner import MetaCleaner


class FileCleanerService:
    """파일 정리 서비스 묶음."""

    def __init__(self):
        self.log_cleaner = LogCleaner()
        self.meta_cleaner = MetaCleaner()
        self.faulty_image_cleaner = FaultyImageCleaner()

    def run(self):
        cleaners = [
            self.log_cleaner,
            self.meta_cleaner,
            self.faulty_image_cleaner,
        ]
        for cleaner in cleaners:
            CustomThread(
                name=cleaner.__class__.__name__,
                task=cleaner.task,
                interval=cleaner.thread_interval,
            ).start()
