# AI Marketing Budget Decisioning Agents

**A multi-agent system that automates and explains where the next euro of marketing budget should go.**

This is not an analytics model. It is a decisioning system designed for CMOs and Heads of Growth who want AI to drive marketing transformation — not just produce more reports.

> Portfolio piece by Paolo Baldriga — Marketing Measurement & AI Executive focused on transformation.

## The idea

Every week the system:

1. **Measurement Agent** reads the latest signals (expected incremental value, LTV, saturation, performance).
2. **Allocation Agent** proposes a new budget distribution under business constraints.
3. **Explanation Agent** writes a clear, board-ready rationale for the change.
4. **Guardrail Agent** checks risks and vetoes or flags unsafe moves.

The output is a decision, not a dashboard.

## Why this is relevant for a CMO heavily focused on AI

- Shows ownership of **AI-enabled decision systems**, not model building.
- Closes the loop: measure → decide → allocate → explain.
- Designed for human-in-the-loop or supervised autonomy.
- Language and outputs are executive, not technical.

## Quick start

```bash
pip install -r requirements.txt
python src/run_decisioning.py
```

Or open `notebooks/decisioning_demo.ipynb`.

## Example output

```
Proposed reallocation:
  Meta:     32% → 28%  (-4 pp)
  Google:   25% → 31%  (+6 pp)
  ...

Rationale (Explanation Agent):
"Shifting budget toward Google because incremental return on high-LTV segments is +18% and the channel is still below saturation. Meta shows diminishing returns in the last 3 weeks."

Guardrail: OK (no channel exceeds 40% cap)
```

## Architecture

- Lightweight agents (plain Python classes) so the logic is transparent.
- Synthetic market data (channels, LTV, incrementality proxies, saturation curves).
- Easy to replace the synthetic layer with real MMM / incrementality outputs.
- Modular: each agent can be improved or replaced independently.

## Author

Paolo Baldriga  
Marketing Measurement & AI Executive  
Hamburg / Rome  
[GitHub](https://github.com/paolobaldriga)

---

*Independent portfolio project. Synthetic data. Built to demonstrate AI decisioning for marketing transformation.*
