# AI Marketing Budget Decisioning Agents

**A multi-agent system that automates and explains where the next euro of marketing budget should go.**

This is not an analytics model. It is a decisioning system designed for CMOs and Heads of Growth who want AI to drive marketing transformation — not just produce more reports.

> Portfolio piece by Paolo Baldriga — Marketing Measurement & AI Executive focused on transformation.

## Data

The system can run on:

1. **Kaggle Sample Media Spends Data** (recommended)  
   Download: https://www.kaggle.com/datasets/yugagrawal95/sample-media-spends-data  
   Place the CSV as `data/media_spends.csv`

2. Synthetic data (automatic fallback if the file is missing)

See `data/README.md` for details.

## The idea

Every week the system:

1. **Measurement Agent** reads the latest signals (expected value, saturation, performance).
2. **Allocation Agent** proposes a new budget distribution under business constraints.
3. **Explanation Agent** writes a clear, board-ready rationale for the change.
4. **Guardrail Agent** checks risks and flags unsafe moves.

The output is a decision, not a dashboard.

## Quick start

```bash
pip install -r requirements.txt
# Optional: download Kaggle dataset and place as data/media_spends.csv
python src/run_decisioning.py
```

## Author

Paolo Baldriga  
Marketing Measurement & AI Executive  
Hamburg / Rome  
[GitHub](https://github.com/paolobaldriga)

---

*Independent portfolio project. Built to demonstrate AI decisioning for marketing transformation.*
