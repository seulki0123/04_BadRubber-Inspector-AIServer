import os
from datetime import datetime

import cv2
from fastapi import APIRouter, Request
from defect_detection import Detector

from ..schemas.requests.defect import DefectRequestModel
from ..schemas.responses.defect import (
    DefectResponseModel,
    DefectResponseData,
    ImageResult,
    DetectionItem
)
from ..utils import get_save_path, save_metadata


defect_router = APIRouter()
detector = Detector()


@defect_router.post(
    "/detect_fault",
    response_model=DefectResponseModel
)
def detect_fault(request: DefectRequestModel, fastapi_request: Request):

    # 1. load config
    config = fastapi_request.app.state.config
    line = config["line"]
    grade = config["grade"]
    save_meta_dir = config["save_meta_dir"]
    save_image_dir = config["save_image_dir"]

    os.makedirs(save_image_dir, exist_ok=True)

    # 2. create image items
    image_items = []
    for side_key, side in request.images.items():
        side_number = int(side_key.replace("side", ""))

        image_items.append({
            "side": side_number,
            "part": 1,
            "image_path": side.part1
        })

        if side.part2:
            image_items.append({
                "side": side_number,
                "part": 2,
                "image_path": side.part2
            })

    image_paths = [item["image_path"] for item in image_items]

    # 3. detect faults
    results = detector.detect(image_paths)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    # 4. create response images
    image_results = []
    total_detection_count = 0

    for item, batch_item in zip(image_items, results):
        detections = []

        for region_segmentations in batch_item.segmentation:
            for seg in region_segmentations:
                detections.append(
                    DetectionItem(
                        class_id=seg.class_id,
                        class_name=seg.class_name,
                        confidence=seg.confidence,
                        bbox=list(seg.bboxes_xyxy)
                    )
                )

        detection_count = len(detections)
        total_detection_count += detection_count

        if detection_count > 0:
            save_image_path = get_save_path(
                save_dir=save_image_dir,
                file_prefix=request.id,
                timestamp=timestamp,
                extension="jpg"
            )
            cv2.imwrite(save_image_path, batch_item.visualize())
        else:
            save_image_path = None

        image_results.append(
            ImageResult(
                side=item["side"],
                part=item["part"],
                image_path=item["image_path"],
                faulty_img_path=save_image_path,
                detections=detections,
                detection_count=detection_count
            )
        )

    # 5. create response data (timestamp는 util에서 생성)
    meta_path = get_save_path(
        save_dir=save_meta_dir,
        file_prefix=request.id,
        timestamp=timestamp,
        suffix="_defect",
        extension="json"
    )
    response_data = DefectResponseData(
        id=request.id,
        production=line,
        grade=grade,
        timestamp=timestamp,
        images=image_results,
        total_detection_count=total_detection_count,
        meta_path=meta_path
    )

    # 6. save metadata
    save_metadata(
        response_data=response_data,
        save_path=meta_path
    )

    # 7. return response
    return DefectResponseModel(
        status="success",
        data=response_data
    )