# Data

The file `media_spends.csv` is the real **Sample Media Spends Data** from Kaggle  
https://www.kaggle.com/datasets/yugagrawal95/sample-media-spends-data

It contains weekly impressions/views by channel (Facebook, Google, Email, YouTube, Affiliate) plus Sales, across multiple divisions.

Run:
```bash
python src/run_decisioning.py
```

The agents will use the most recent 12 weeks to propose a budget reallocation.
