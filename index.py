import uvicorn
from fastapi import FastAPI
from requests import Request
from routes.event_routes import event_router
from routes.user_routes import user_router
import logging
import time

app = FastAPI()

logger = logging.getLogger(__name__)
logging.getLogger("watchfiles.main").setLevel(logging.WARNING)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(message)s",
    filename='logs.txt'
)


@app.middleware("http")
async def logging_info(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    logging.info(
        f"{request.client} -  method: {request.method} - path: {request.scope['path']}- status_code: {response.status_code} - process_time: {process_time}")
    return response


# Including the router
app.include_router(user_router)
app.include_router(event_router)

if __name__ == "__main__":
    uvicorn.run("index:app", host="127.0.0.1", port=8000, reload=True)
