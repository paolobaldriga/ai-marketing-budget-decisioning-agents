# AI Marketing Budget Decisioning Agents

**A multi-agent system that automates and explains where the next euro of marketing budget should go.**

This is not an analytics model. It is a decisioning system designed for CMOs and Heads of Growth who want AI to drive marketing transformation — not just produce more reports.

> Portfolio piece by Paolo Baldriga — Marketing Measurement & AI Executive focused on transformation.

## Use with your own data

1. Put your CSV in the `data/` folder.
2. Open `src/run_decisioning.py` and edit the **CONFIGURATION** section at the top:
   - `DATA_PATH`
   - `SALES_COLUMN`
   - `CHANNEL_COLUMNS` (map channel names to your column names)
   - `DATE_COLUMN` (or set to `None`)
3. Run:
   ```bash
   python src/run_decisioning.py
   ```
   or open `notebooks/decisioning_demo.ipynb`.

The included `data/media_spends.csv` is the real Kaggle Sample Media Spends Data and works out of the box.

## The idea

Every week the system:

1. **Measurement Agent** reads the latest signals.
2. **Allocation Agent** proposes a new budget distribution under constraints.
3. **Explanation Agent** writes a clear rationale.
4. **Guardrail Agent** checks risks.

## Author

Paolo Baldriga  
Marketing Measurement & AI Executive  
Hamburg / Rome  
[GitHub](https://github.com/paolobaldriga)

---

*Independent portfolio project. Built to demonstrate AI decisioning for marketing transformation.*
