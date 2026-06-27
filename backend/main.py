from fastapi import FastAPI
from routes.library import router as library_router
from utils.database import Base, engine

Base.metadata.create_all(engine)

app = FastAPI()
app.include_router(library_router)

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000)
