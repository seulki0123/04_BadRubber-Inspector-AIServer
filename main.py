import traceback

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError

from src import baler_router, defect_router, load_config
from src.utils import ProcessLogger

app = FastAPI(title="Inspector AI Server")
logger = ProcessLogger("Main")

config = load_config()
app.state.config = config
app.state.config["save_tmp_dir"] = "./tmp"

app.include_router(baler_router, prefix="/api") 
app.include_router(defect_router, prefix="/api")

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.log_error(
        f"Unhandled error: {str(exc)}\n{traceback.format_exc()}"
    )

    return JSONResponse(
        status_code=500,
        content={"status": "error", "message": str(exc)}
    )

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    print("VALIDATION ERROR TRIGGERED")
    logger.log_error(
        f"Validation error: {exc.errors()}\nBody: {exc.body}"
    )

    return JSONResponse(
        status_code=422,
        content={
            "status": "validation_error",
            "detail": exc.errors()
        }
    )