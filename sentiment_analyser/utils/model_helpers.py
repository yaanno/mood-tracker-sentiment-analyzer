"""Helper utilities for model operations.

This module provides common functions for working with ML models,
including loading, caching, and batch processing.
"""

import json
from pathlib import Path
from typing import Any, Dict, List, Optional

import torch
from transformers import PreTrainedModel, PreTrainedTokenizer


def load_model_config(config_path: Path) -> Dict[str, Any]:
    """Load model configuration from file.

    Args:
        config_path: Path to model config file

    Returns:
        Model configuration dictionary
    """
    try:
        with config_path.open() as f:
            return json.load(f)
    except Exception as e:
        raise RuntimeError(f"Failed to load model config: {e}")


def get_device() -> torch.device:
    """Get appropriate device for model inference.

    Returns:
        torch.device for model execution
    """
    if torch.cuda.is_available():
        return torch.device("cuda")
    elif torch.backends.mps.is_available():
        return torch.device("mps")
    return torch.device("cpu")


def batch_tokenize(
    texts: List[str],
    tokenizer: PreTrainedTokenizer,
    max_length: Optional[int] = None,
    batch_size: int = 32,
) -> List[Dict[str, torch.Tensor]]:
    """Tokenize texts in batches.

    Args:
        texts: List of input texts
        tokenizer: Tokenizer to use
        max_length: Maximum sequence length
        batch_size: Batch size for processing

    Returns:
        List of tokenized batches
    """
    batches = []
    for i in range(0, len(texts), batch_size):
        batch_texts = texts[i : i + batch_size]
        batch_encoding = tokenizer(
            batch_texts,
            max_length=max_length,
            truncation=True,
            padding=True,
            return_tensors="pt",
        )
        batches.append(batch_encoding)
    return batches


def move_model_to_device(
    model: PreTrainedModel, device: Optional[torch.device] = None
) -> PreTrainedModel:
    """Move model to appropriate device.

    Args:
        model: Model to move
        device: Target device (defaults to auto-selected device)

    Returns:
        Model on target device
    """
    if device is None:
        device = get_device()

    return model.to(device)  # type: ignore
