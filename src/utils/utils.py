import os
import json
from typing import Optional
from pydantic import BaseModel
from datetime import datetime
from functools import wraps

def get_save_path(
    save_dir: str,
    file_prefix: str,
    extension: str,
    timestamp: Optional[str] = None,
    suffix: str = ""
) -> str:
    today_str = datetime.now().strftime("%Y-%m-%d")
    dated_dir = os.path.join(save_dir, today_str)
    
    os.makedirs(dated_dir, exist_ok=True)
    
    filename = f"{file_prefix}{f'_{timestamp}' if timestamp else ''}{suffix}.{extension}"
    return os.path.join(dated_dir, filename)

def save_metadata(
    response_data: BaseModel,
    save_path: str
) -> str:
    with open(save_path, "w", encoding="utf-8") as f:
        json.dump(
            response_data.model_dump(by_alias=True),
            f,
            ensure_ascii=False,
            indent=4
        )

    return save_path


def pop_baler_from_handoff(baler_handoff_dir: str, request_id: str) -> Optional[str]:
    """baler classification 결과를 handoff 디렉토리에서 pop 한다.

    `/classify` 가 `<baler_handoff_dir>/<YYYY-MM-DD>/<request_id>.json` 으로
    떨어뜨려둔 baler 결과를, 같은 `request_id` 의 `/detect_fault` 요청이 도착했을 때
    읽어 들이고 즉시 삭제한다. 누락분(짝이 안 맞는 파일)은 BalerHandoffCleaner 가
    주기적으로 정리한다.

    날짜 하위 폴더 형태(get_save_path 의 dated_dir)와 평탄 형태 둘 다를
    호환적으로 탐색한다.

    :param baler_handoff_dir: handoff 루트 디렉토리
    :param request_id: 요청 id
    :return: baler 값 또는 None (파일 없음/읽기 실패)
    """
    candidates = [
        os.path.join(baler_handoff_dir, datetime.now().strftime("%Y-%m-%d"), f"{request_id}.json"),
        os.path.join(baler_handoff_dir, f"{request_id}.json"),
    ]

    baler_handoff_path = next((p for p in candidates if os.path.exists(p)), None)
    if baler_handoff_path is None:
        return None

    try:
        with open(baler_handoff_path, "r", encoding="utf-8") as f:
            baler_json = json.load(f)

        baler_value = baler_json.get("baler")
        os.remove(baler_handoff_path)

        return baler_value

    except Exception as e:
        print(f"[Error] Failed to read baler handoff: {e}")
        return None

def safe_call(func):
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        try:
            return func(self, *args, **kwargs)
        except Exception:
            # self.logger 있으면 쓰고, 없으면 print
            if hasattr(self, 'logger'):
                self.logger.error(f"Error in '{func.__name__}' function : {traceback.format_exc()}")
            else:
                raise Exception(f"Error in '{func.__name__}' function : {traceback.format_exc()}")
            return None
    return wrapper