# Data

## Included sample (works immediately)

`media_spends.csv` is already in the repo. It has the same structure as the Kaggle dataset (weekly channel spend + sales).

Run:
```bash
python src/run_decisioning.py
```
It will automatically use this file and produce a budget decision.

## Real Kaggle dataset (optional)

Full original data:  
https://www.kaggle.com/datasets/yugagrawal95/sample-media-spends-data

You can replace `data/media_spends.csv` with the original file if you want the complete dataset. The loader will pick it up.
