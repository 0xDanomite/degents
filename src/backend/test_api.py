# src/backend/test_api.py
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import uvicorn

app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class TestResponse(BaseModel):
    status: str
    message: str
    details: Optional[dict] = None

@app.get("/api/test")
async def test_endpoint():
    try:
        # Run the setup test
        from test_setup import test_setup
        success = test_setup()

        if success:
            return TestResponse(
                status="success",
                message="All components initialized successfully",
                details={"initialized": True}
            )
        else:
            raise HTTPException(status_code=500, detail="Setup test failed")

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
