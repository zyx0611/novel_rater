# app/main.py
from fastapi import FastAPI
import argparse
from app import runner, api

app = FastAPI()
app.include_router(api.router)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=["api", "test"], default="api", help="Run mode")
    args = parser.parse_args()

    if args.mode == "test":
        runner.run_tests()
    else:
        import uvicorn
        uvicorn.run("app.main:app", host="0.0.0.0", port=8000)
