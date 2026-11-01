"""
Multi-agent Marketing Budget Decisioning System
Measurement → Allocation → Explanation → Guardrail

Generic version: works with any CSV that has channel activity + sales.
"""

import numpy as np
import pandas as pd
from pathlib import Path

np.random.seed(42)

# =============================================================================
# CONFIGURATION — edit these to match your dataset
# =============================================================================
DATA_PATH = "data/media_spends.csv"
DATE_COLUMN = "Calendar_Week"          # or None if no date
SALES_COLUMN = "Sales"

# Map friendly channel names → column names in your CSV
CHANNEL_COLUMNS = {
    "Facebook": "Facebook_Impressions",
    "Google": "Google_Impressions",
    "Email": "Email_Impressions",
    "YouTube Paid": "Paid_Views",
    "Affiliate": "Affiliate_Impressions",
}

LOOKBACK_WEEKS = 12
MAX_CHANNEL_SHARE = 0.40
MIN_CHANNEL_SHARE = 0.05
# =============================================================================

def load_market_state(path=DATA_PATH):
    """Load any CSV and turn channel activity + sales into market state."""
    p = Path(path)
    if not p.exists():
        print(f"File not found: {path}")
        return None

    df = pd.read_csv(p)
    df.columns = [c.strip() for c in df.columns]

    if DATE_COLUMN and DATE_COLUMN in df.columns:
        df[DATE_COLUMN] = pd.to_datetime(df[DATE_COLUMN], errors="coerce")
        latest = df[DATE_COLUMN].max()
        recent = df[df[DATE_COLUMN] >= latest - pd.Timedelta(weeks=LOOKBACK_WEEKS)].copy()
    else:
        recent = df.tail(200).copy()

    if recent.empty or SALES_COLUMN not in recent.columns:
        print("Could not prepare data. Check DATE_COLUMN and SALES_COLUMN.")
        return None

    total_sales = recent[SALES_COLUMN].sum()
    records = []

    for channel, col in CHANNEL_COLUMNS.items():
        if col not in recent.columns:
            print(f"Warning: column '{col}' not found, skipping {channel}")
            continue
        activity = recent[col].fillna(0).sum()
        if activity <= 0:
            continue

        efficiency = (total_sales / (activity + 1)) * 800
        efficiency = float(np.clip(efficiency, 0.9, 7.5))
        sat = activity / (recent[col].max() * max(len(recent), 1) + 1)
        saturation = float(np.clip(sat, 0.15, 0.92))

        records.append({
            "channel": channel,
            "activity": activity,
            "incremental_roas": round(efficiency, 2),
            "ltv_index": round(float(np.random.uniform(0.85, 1.4)), 2),
            "saturation": round(saturation, 2),
        })

    if not records:
        return None

    state = pd.DataFrame(records)
    state["current_share"] = state["activity"] / state["activity"].sum()
    state["expected_value"] = (
        state["incremental_roas"] * state["ltv_index"] * (1 - state["saturation"] * 0.55)
    )
    return state[["channel", "current_share", "incremental_roas", "ltv_index", "saturation", "expected_value"]]

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
    def run(self, measurement, max_share=MAX_CHANNEL_SHARE, min_share=MIN_CHANNEL_SHARE):
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
        return f"Primary opportunity is {top['channel']}. " + " ".join(lines)

class GuardrailAgent:
    def run(self, allocation, max_share=MAX_CHANNEL_SHARE):
        issues = []
        if (allocation["proposed_share"] > max_share + 0.005).any():
            issues.append("A channel exceeds the maximum share cap.")
        big = allocation[allocation["delta_pp"].abs() > 15]
        if not big.empty:
            issues.append(f"Large swings: {', '.join(big['channel'])}")
        return {"status": "OK" if not issues else "REVIEW", "issues": issues}

def run_decisioning(path=DATA_PATH):
    """Main entry point. Returns the full result for notebooks or scripts."""
    state = load_market_state(path)
    if state is None:
        return None

    meas = MeasurementAgent().run(state)
    alloc = AllocationAgent().run(meas)
    explanation = ExplanationAgent().run(alloc)
    guard = GuardrailAgent().run(alloc)

    return {
        "state": state,
        "allocation": alloc,
        "insights": meas["insights"],
        "explanation": explanation,
        "guardrail": guard,
    }

def main():
    print("=== AI Marketing Budget Decisioning ===\n")
    result = run_decisioning()
    if result is None:
        print("Could not run. Check DATA_PATH and CHANNEL_COLUMNS at the top of the file.")
        return

    print("Measurement insights:")
    for i in result["insights"]:
        print(" -", i)

    print("\nProposed allocation:")
    cols = ["channel", "current_share", "proposed_share", "delta_pp", "expected_value"]
    print(result["allocation"][cols].round(3).to_string(index=False))

    print("\nExplanation Agent:")
    print(result["explanation"])

    print(f"\nGuardrail: {result['guardrail']['status']}")
    for issue in result["guardrail"]["issues"]:
        print(" -", issue)

    print("\n--- Decision ready for review ---")

if __name__ == "__main__":
    main()
