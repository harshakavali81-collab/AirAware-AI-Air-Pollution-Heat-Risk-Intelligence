"""Evaluation entry point; see train.py for a strict chronological split."""
from src.airaware.models.train import metrics, train_and_evaluate

__all__ = ["metrics", "train_and_evaluate"]
