# Data

## Recommended: Sample Media Spends Data (Kaggle)

Download from:  
https://www.kaggle.com/datasets/yugagrawal95/sample-media-spends-data

Place the CSV file as:  
`data/media_spends.csv`

The dataset contains weekly marketing spend across channels (Facebook, Google, Email, YouTube, Affiliate, etc.) plus sales. It is explicitly suited for Media Mix Modeling and budget allocation.

The pipeline will automatically detect the file and use it. If the file is missing, it falls back to synthetic data.

## Expected usage

The loader aggregates the latest weeks by channel, computes:
- current budget share
- ROAS proxy (sales / spend)
- simple saturation estimate
- recent trend

and feeds these signals to the Measurement → Allocation → Explanation → Guardrail agents.
