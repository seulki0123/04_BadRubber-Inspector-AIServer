from fastapi import FastAPI
from src import baler_router, defect_router, load_config

app = FastAPI(title="Inspector AI Server")

config = load_config()
app.state.config = config

app.include_router(baler_router, prefix="/api") 
app.include_router(defect_router, prefix="/api")