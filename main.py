import os
from preprocessing import preprocessing
import q1_event_sequence
import q2_behavioral_baseline
import q3_leading_indicators

DATA_FILE = "MC1_final_00.json"
OUTPUT_DIR = "output"

if __name__ == "__main__":
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    print("Loading and preprocessing data...")
    df = preprocessing(DATA_FILE)
    print(f"Data loaded: {df.shape[0]} rows, {df.shape[1]} columns")

    print("\nRunning Q1 — Event Sequence...")
    q1_event_sequence.run(df, OUTPUT_DIR)

    print("Running Q2 — Behavioral Baseline vs Anomaly...")
    q2_behavioral_baseline.run(df, OUTPUT_DIR)

    print("Running Q3 — Leading Indicators...")
    q3_leading_indicators.run(df, OUTPUT_DIR)

    print(f"\nAll figures saved to '{OUTPUT_DIR}/'")
