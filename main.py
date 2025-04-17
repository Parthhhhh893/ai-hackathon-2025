
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware


load_dotenv()

origins = [
    "http://localhost:5173",  # Your frontend running locally on port 5173
    "http://localhost:8005",  # Local backend for testing
    "http://localhost:8006",  # Local backend for testing

    "http://localhost:5174"
]


app = FastAPI(docs_url='/api/docs/')


# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # List of allowed origins
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all headers
)

app.include_router(backend_routers)


@app.get("/health")
async def health_check():
    return {"status": "ok"}  # Global health check




