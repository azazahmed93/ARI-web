"""Loader for the ACS-derived DMA demographics dataset (data/dma_demographics.json)."""
import json
import os
from functools import lru_cache

_DATASET_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "dma_demographics.json")


@lru_cache(maxsize=1)
def load_dma_dataset():
    """Load (and cache) the DMA demographics dataset."""
    with open(_DATASET_PATH, "r", encoding="utf-8") as f:
        return json.load(f)
