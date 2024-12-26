from fastapi import FastAPI
from pydantic import BaseModel
from transformers import pipeline

app = FastAPI()

# Define the data model for the request body
class TextData(BaseModel):
    text: str

# Initialize the sentiment analysis pipeline
classifier = pipeline("text-classification", model="SamLowe/roberta-base-go_emotions", top_k=None)

@app.get("/")
def index():
    return {"message": "app root"}

@app.post("/analyse", response_model=dict)
def analyse(data: TextData):
    prediction = classifier(data.text)
    return {
        "sentiment": prediction
    }