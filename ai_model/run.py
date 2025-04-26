#!/usr/bin/env python3
import os
import joblib
import click
import tensorflow as tf

from src.hybrid_train_model import build_and_save_hybrid_model
from src.inference import predict

# Artifact paths
MODEL_DIR      = "outputs/models"
HYBRID_MODEL   = os.path.join(MODEL_DIR, "hybrid_travel_recommender_model.keras")
SCALER_FILE    = os.path.join(MODEL_DIR, "scaler.joblib")
ENCODER_FILE   = os.path.join(MODEL_DIR, "encoder.joblib")
CF_FILE        = os.path.join(MODEL_DIR, "cf_model.joblib")
CB_FILE        = os.path.join(MODEL_DIR, "cb_recommender.joblib")
CLUSTER_FILE   = os.path.join(MODEL_DIR, "clusters.joblib")

# Ensure output dir exists
os.makedirs(MODEL_DIR, exist_ok=True)

@click.group()
def cli():
    pass

@cli.command()
def train():
    """
    Train & save the full hybrid model (CF + CB + clustering + MLP).
    """
    build_and_save_hybrid_model(
        model_path=HYBRID_MODEL,
        scaler_path=SCALER_FILE,
        encoder_path=ENCODER_FILE,
        cf_path=CF_FILE,
        cb_path=CB_FILE,
        cluster_path=CLUSTER_FILE,
    )
    click.echo("✅ Hybrid model trained and saved.")

@cli.command()
@click.argument("user_id")
@click.argument("item_id")
def infer(user_id, item_id):
    """
    Load artifacts & predict a rating for (user_id, item_id).
    """
    score = predict(
        user_id,
        item_id,
        model_path=HYBRID_MODEL,
        scaler_path=SCALER_FILE,
        encoder_path=ENCODER_FILE,
        cf_path=CF_FILE,
        cb_path=CB_FILE,
        cluster_path=CLUSTER_FILE,
    )
    click.echo(f"Predicted rating for {user_id}→{item_id}: {score:.3f}")

if __name__ == "__main__":
    cli()
