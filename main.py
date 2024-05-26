from fastapi import FastAPI
from app.middleware.cors import setup_cors
from routes.route import router

app = FastAPI()

app.include_router(router)
setup_cors(app)

