import os
import json
from pydantic import BaseModel


def get_save_path(
    save_dir: str,
    file_prefix: str,
    timestamp: str,
    extension: str,
    suffix: str = ""
) -> str:
    os.makedirs(save_dir, exist_ok=True)
    filename = f"{file_prefix}_{timestamp}{suffix}.{extension}"
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