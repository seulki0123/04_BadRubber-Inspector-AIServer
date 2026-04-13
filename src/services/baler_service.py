import time
from datetime import datetime

from fastapi import APIRouter, Request
from baler_classification import Classifier

from ..schemas.requests.baler import BalerRequestModel
from ..schemas.responses.baler import (
    BalerResponseModel,
    BalerResponseData
)
from ..utils import get_save_path, save_metadata, ProcessLogger


baler_router = APIRouter()
classifier = Classifier()
logger = ProcessLogger("BalerService")


@baler_router.post(
    "/classify",
    response_model=BalerResponseModel
)
def classify(request: BalerRequestModel, fastapi_request: Request):
    logger.log_info(f"Baler request: {request}")
    t0 = time.time()

    # 1. load config
    config = fastapi_request.app.state.config
    line = config["line"]
    grade = config["grade"]
    save_tmp_dir = config["save_tmp_dir"]

    # 2. classify baler
    side1 = request.images["side1"]

    try:
        _, class_name, confidence = classifier.classify(
            bottom_path=side1.part1,
            top_path=side1.part2
        )
    except Exception as e:
        logger.log_error(f"Baler classification error: {e}")
        class_name = "10"
        confidence = 0.0

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    # 3. create response data
    meta_path = get_save_path(
        save_dir=save_tmp_dir,
        file_prefix=request.id,
        extension="json"
    )
    
    response_data = BalerResponseData(
        id=request.id,
        production=line,
        grade=grade,
        baler=class_name,
        timestamp=timestamp,
        meta_path=meta_path
    )

    # 4. save metadata
    save_metadata(
        response_data=response_data,
        save_path=meta_path
    )

    # 5. return response
    res = BalerResponseModel(
        status="success",
        data=response_data
    )
    logger.log_info(f"Baler response: {res}")
    logger.log_info(f"Baler time: {(time.time() - t0)*1000}ms")
    return res