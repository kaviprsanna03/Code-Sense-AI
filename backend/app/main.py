from fastapi import FastAPI

app = FastAPI(title="CodeSense AI")


@app.get("/health")
def health_check():
    return {"status": "healthy"}