import os
import json
from typing import Optional
from pydantic import BaseModel
from datetime import datetime


def tmp_logging(level: str, message: str):
    print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - [{level}] - {message}")

def get_save_path(
    save_dir: str,
    file_prefix: str,
    extension: str,
    timestamp: Optional[str] = None,
    suffix: str = ""
) -> str:
    os.makedirs(save_dir, exist_ok=True)
    filename = f"{file_prefix}{f'_{timestamp}' if timestamp else ''}{suffix}.{extension}"
    return os.path.join(save_dir, filename)


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


def pop_baler_from_tmp(save_tmp_dir: str, request_id: str) -> Optional[int]:
    """
    tmp 디렉토리에서 request_id.json을 읽어 baler 값을 반환하고
    파일이 존재하면 삭제한다.

    :param save_tmp_dir: tmp 저장 디렉토리
    :param request_id: 요청 id
    :return: baler 값 또는 None
    """
    baler_tmp_path = os.path.join(save_tmp_dir, f"{request_id}.json")

    if not os.path.exists(baler_tmp_path):
        return None

    try:
        with open(baler_tmp_path, "r", encoding="utf-8") as f:
            baler_json = json.load(f)

        baler_value = baler_json.get("baler")
        os.remove(baler_tmp_path)

        return baler_value

    except Exception as e:
        print(f"[Error] Failed to read baler tmp: {e}")
        return None