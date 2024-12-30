
# Sentiment Analyzer

## Overview

The Sentiment Analyzer is a machine learning-based application designed to analyze the sentiment of text inputs. It uses transformer models to classify text into various emotion categories and provides a confidence score for each category.

## Features

- **Text Cleaning and Normalization**: Preprocess text data by removing unwanted elements like URLs, emails, and emojis.
- **Sentiment Analysis**: Analyze text to determine the sentiment and provide confidence scores for various emotions.
- **Caching**: Cache sentiment analysis results to improve performance and reduce redundant computations.
- **Error Handling**: Custom exceptions and error handling mechanisms to ensure robust operation.
- **Rate Limiting**: Limit the number of requests to prevent abuse and ensure fair usage.
- **Logging**: Detailed logging for monitoring and debugging purposes.

## Installation

1. **Clone the repository**:
    ```sh
    git clone https://github.com/yaanno/mood-tracker-sentiment-analyzer
    cd sentiment-analyzer
    ```

2. **Create a virtual environment**:
    Install a Python version manager (the project uses 3.9).
    ```sh
    pyenv activate 3.9.21
    ```

3. **Install dependencies**:
    ```sh
    poetry install
    ```

## Configuration

Configuration settings are managed using environment variables. Create a `.env` file in the project root and set the necessary variables:

```
MODEL_NAME=your_model_name
ENVIRONMENT=development
LOG_TO_FILE=True
FILE_PATH=logs/app.log
```

## Usage

### Running the Application

To start the FastAPI application, run:

```sh
poetry run uvicorn sentiment_analyser.main:app --reload
```

### API Endpoints

- **Health Check**: `GET /api/v1/health`
- **Analyze Sentiment**: `POST /api/v1/sentiment`
    - Request Body:
        ```json
        {
            "text": "Your text to analyze"
        }
        ```
    - Response:
        ```json
        {
            "text": "Your text to analyze",
            "scores": [
                {
                    "label": "joy",
                    "score": 0.95
                },
                ...
            ],
            "status": "success",
            "message": "Analysis completed successfully",
            "model_name": "your_model_name"
        }
        ```

## Testing

To run the tests, use:

```sh
pytest
```

## Linting
The project uses Ruff for linting:
```sh
ruff
```

## Project Structure

The structure might change in time so take this with a dash of salt :)

```
sentiment-analyser/
├── sentiment_analyser/
│   ├── api/
│   │   └── v1/
│   │       └── endpoints/
│   │           └── sentiment.py
│   ├── core/
│   │   ├── config.py
│   │   ├── exceptions.py
│   │   ├── logging.py
│   │   └── middleware.py
│   ├── models/
│   │   └── api/
│   │       └── schema.py
│   ├── services/
│   │   └── sentiment/
│   │       ├── analyzer.py
│   │       ├── cache.py
│   │       └── service.py
│   ├── utils/
│   │   ├── errors.py
│   │   ├── model_helpers.py
│   │   ├── text.py
│   │   └── validators.py
│   └── main.py
├── tests/
│   ├── test_api/
│   │   ├── test_health.py
│   │   └── test_sentiment.py
├── .env
├── requirements.txt
└── README.md
```

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
