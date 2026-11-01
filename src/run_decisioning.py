"""
Multi-agent Marketing Budget Decisioning System
Measurement → Allocation → Explanation → Guardrail

Supports Kaggle Sample Media Spends Data or synthetic fallback.
"""

import numpy as np
import pandas as pd
from pathlib import Path

np.random.seed(42)

def load_kaggle_media_spends(path="data/media_spends.csv"):
    """Load and prepare the Kaggle Sample Media Spends dataset."""
    p = Path(path)
    if not p.exists():
        return None

    df = pd.read_csv(p)
    # Normalize column names
    df.columns = [c.strip().lower().replace(" ", "_") for c in df.columns]

    # Try to identify spend and sales columns (common patterns)
    spend_cols = [c for c in df.columns if any(x in c for x in ["spend", "cost", "facebook", "google", "email", "youtube", "affiliate"])]
    sales_cols = [c for c in df.columns if any(x in c for x in ["sales", "revenue", "gmv"])]

    if not spend_cols or not sales_cols:
        print("Could not auto-detect spend/sales columns. Falling back to synthetic.")
        return None

    # Use the most recent period available
    if "date" in df.columns or "week" in df.columns:
        date_col = "date" if "date" in df.columns else "week"
        df[date_col] = pd.to_datetime(df[date_col], errors="coerce")
        latest = df[date_col].max()
        recent = df[df[date_col] >= latest - pd.Timedelta(weeks=8)]
    else:
        recent = df.tail(100)

    # Aggregate by summing spend columns and sales
    records = []
    for col in spend_cols[:6]:  # limit to main channels
        channel = col.replace("_spend", "").replace("_cost", "").replace("_", " ").title()
        total_spend = recent[col].sum()
        # Proxy ROAS: overall sales / this channel spend (rough)
        total_sales = recent[sales_cols[0]].sum() if sales_cols else total_spend * 2
        roas = total_sales / total_spend if total_spend > 0 else 1.5
        records.append({
            "channel": channel,
            "spend": total_spend,
            "incremental_roas": min(max(roas, 0.8), 6.0),
            "ltv_index": np.random.uniform(0.9, 1.4),  # placeholder until real LTV join
            "saturation": min(0.9, total_spend / (recent[col].max() * len(recent) + 1e-6)),
        })

    state = pd.DataFrame(records)
    if state.empty or state["spend"].sum() == 0:
        return None

    state["current_share"] = state["spend"] / state["spend"].sum()
    state["expected_value"] = state["incremental_roas"] * state["ltv_index"] * (1 - state["saturation"] * 0.5)
    return state[["channel", "current_share", "incremental_roas", "ltv_index", "saturation", "expected_value"]]

def generate_synthetic_state():
    channels = ["Meta", "Google", "TikTok", "Programmatic", "Email", "Influencer"]
    data = []
    for ch in channels:
        data.append({
            "channel": ch,
            "current_share": np.random.uniform(0.08, 0.35),
            "incremental_roas": np.random.uniform(1.2, 4.5),
            "ltv_index": np.random.uniform(0.7, 1.6),
            "saturation": np.random.uniform(0.3, 0.95),
        })
    df = pd.DataFrame(data)
    df["current_share"] = df["current_share"] / df["current_share"].sum()
    df["expected_value"] = df["incremental_roas"] * df["ltv_index"] * (1 - df["saturation"] * 0.6)
    return df

class MeasurementAgent:
    def run(self, state):
        insights = []
        best = state.loc[state["expected_value"].idxmax()]
        worst = state.loc[state["expected_value"].idxmin()]
        insights.append(f"Highest expected value: {best['channel']} ({best['expected_value']:.2f})")
        insights.append(f"Lowest expected value: {worst['channel']} ({worst['expected_value']:.2f})")
        saturated = state[state["saturation"] > 0.75]["channel"].tolist()
        if saturated:
            insights.append(f"Near saturation: {', '.join(saturated)}")
        return {"state": state, "insights": insights}

class AllocationAgent:
    def run(self, measurement, max_share=0.40, min_share=0.05):
        state = measurement["state"].copy()
        raw = state["expected_value"].clip(lower=0.1)
        raw = raw / raw.sum()
        new_share = 0.65 * raw + 0.35 * state["current_share"]
        new_share = new_share.clip(min_share, max_share)
        new_share = new_share / new_share.sum()
        state["proposed_share"] = new_share
        state["delta_pp"] = (state["proposed_share"] - state["current_share"]) * 100
        return state

class ExplanationAgent:
    def run(self, allocation):
        moves = allocation[allocation["delta_pp"].abs() > 1.5].sort_values("delta_pp", ascending=False)
        if moves.empty:
            return "No material reallocation recommended. Current mix is close to optimal."

        lines = []
        for _, row in moves.head(3).iterrows():
            direction = "Increase" if row["delta_pp"] > 0 else "Decrease"
            lines.append(
                f"{direction} {row['channel']} by {abs(row['delta_pp']):.1f} pp "
                f"(value {row['expected_value']:.2f}, saturation {row['saturation']:.0%})."
            )
        top = allocation.loc[allocation["expected_value"].idxmax()]
        return (
            f"Primary opportunity is {top['channel']}. " + " ".join(lines)
        )

class GuardrailAgent:
    def run(self, allocation, max_share=0.40):
        issues = []
        if (allocation["proposed_share"] > max_share + 0.005).any():
            issues.append("A channel exceeds the maximum share cap.")
        big = allocation[allocation["delta_pp"].abs() > 15]
        if not big.empty:
            issues.append(f"Large swings: {', '.join(big['channel'])}")
        return {"status": "OK" if not issues else "REVIEW", "issues": issues}

def main():
    print("=== AI Marketing Budget Decisioning ===\n")

    state = load_kaggle_media_spends()
    source = "Kaggle Sample Media Spends Data"
    if state is None:
        state = generate_synthetic_state()
        source = "synthetic data (place data/media_spends.csv to use Kaggle dataset)"

    print(f"Data source: {source}\n")

    meas = MeasurementAgent().run(state)
    print("Measurement insights:")
    for i in meas["insights"]:
        print(" -", i)

    alloc = AllocationAgent().run(meas)
    print("\nProposed allocation:")
    cols = ["channel", "current_share", "proposed_share", "delta_pp", "expected_value"]
    print(alloc[cols].round(3).to_string(index=False))

    print("\nExplanation Agent:")
    print(ExplanationAgent().run(alloc))

    guard = GuardrailAgent().run(alloc)
    print(f"\nGuardrail: {guard['status']}")
    for issue in guard["issues"]:
        print(" -", issue)

    print("\n--- Decision ready for CMO review ---")

if __name__ == "__main__":
    main()
