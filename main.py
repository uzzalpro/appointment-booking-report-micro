from app import start_application
from fastapi.middleware.cors import CORSMiddleware
import debugpy
import uvicorn

# Enable debugpy
debugpy.listen(("localhost", 5680))
print("Waiting for debugger to attach...")

# Start the FastAPI application
app = start_application()

# Allow CORS for all origins, methods, and headers (adjust as needed)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Change this to restrict allowed origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows GET, POST, OPTIONS, etc.
    allow_headers=["*"],  # Allows all headers
)


if __name__ == "__main__":
    uvicorn.run("main:app", host="localhost", port=8000, reload=True)

    # docker compose -f docker-compose-dev.yml up -d --build redis