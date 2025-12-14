import argparse
from pathlib import Path
import pandas as pd


def generate_sample(input_path: Path, output_path: Path, n_rows: int, seed: int):
    if not input_path.exists():
        raise FileNotFoundError(f"Input file not found: {input_path}")

    df = pd.read_csv(input_path)

    if n_rows > len(df):
        raise ValueError(
            f"Sample size ({n_rows}) is larger than dataset size ({len(df)})"
        )

    sample_df = df.sample(n=n_rows, random_state=seed)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    sample_df.to_csv(output_path, index=False)

    print(f"Sample dataset created: {output_path} ({n_rows} rows)")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Generate sample dataset for GitHub repository"
    )
    parser.add_argument(
        "--input",
        type=Path,
        required=True,
        help="Path to raw input CSV file",
    )
    parser.add_argument(
        "--output",
        type=Path,
        required=True,
        help="Path to output sample CSV file",
    )
    parser.add_argument(
        "--rows",
        type=int,
        default=100,
        help="Number of rows to sample",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=42,
        help="Random seed for reproducibility",
    )

    args = parser.parse_args()

    generate_sample(
        input_path=args.input,
        output_path=args.output,
        n_rows=args.rows,
        seed=args.seed,
    )
