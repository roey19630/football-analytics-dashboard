import os
import pandas as pd

# Path for the original and reduced dataset
original_file = "../data/male_players_23.csv"
reduced_file = "../data/reduced_data.csv"

def create_reduced_dataset():
    """Creates a reduced dataset with 500 representative rows."""
    chunk_size = 50000  # Number of rows to read per iteration
    total_rows_to_sample = 500  # Total representative rows
    sampled_data = []  # List to store partial samples

    print("Processing large dataset in chunks...")
    for chunk in pd.read_csv(original_file, chunksize=chunk_size):
        sampled_chunk = chunk.sample(n=min(len(chunk), 50), random_state=42)
        sampled_data.append(sampled_chunk)

    print("Creating reduced dataset...")
    final_sample = pd.concat(sampled_data).sample(n=total_rows_to_sample, random_state=42)
    final_sample.to_csv(reduced_file, index=False)
    print(f"✅ Reduced file saved at: {reduced_file}")

if __name__ == "__main__":
    create_reduced_dataset()