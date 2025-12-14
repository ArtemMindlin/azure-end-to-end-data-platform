## Sample Data Generation

This script generates a small, reproducible sample of the original dataset to be committed to the repository. The full dataset is not versioned.

Usage:
```bash
python scripts/generate_sample.py \
  --input data/raw/products_macro.csv \
  --output data/sample/products_macro_sample.csv \
  --rows 100 \
  --seed 42
```
