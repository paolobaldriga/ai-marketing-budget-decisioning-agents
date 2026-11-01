"""
Multi-agent Marketing Budget Decisioning System
Measurement → Allocation → Explanation → Guardrail

Uses the real Kaggle Sample Media Spends Data (impressions + sales).
"""

import numpy as np
import pandas as pd
from pathlib import Path

np.random.seed(42)

def load_kaggle_media_spends(path="data/media_spends.csv"):
    """Load the real Kaggle Sample Media Spends Data."""
    p = Path(path)
    if not p.exists():
        return None

    df = pd.read_csv(p)
    df.columns = [c.strip() for c in df.columns]

    channel_map = {
        "Facebook": "Facebook_Impressions",
        "Google": "Google_Impressions",
        "Email": "Email_Impressions",
        "YouTube Paid": "Paid_Views",
        "Affiliate": "Affiliate_Impressions",
    }

    df["Calendar_Week"] = pd.to_datetime(df["Calendar_Week"], errors="coerce")
    latest = df["Calendar_Week"].max()
    recent = df[df["Calendar_Week"] >= latest - pd.Timedelta(weeks=12)].copy()

    if recent.empty:
        recent = df.tail(200)

    total_sales = recent["Sales"].sum()
    records = []
    for channel, col in channel_map.items():
        if col not in recent.columns:
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
        return f"Primary opportunity is {top['channel']}. " + " ".join(lines)

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
    source = "Kaggle Sample Media Spends Data (real)"
    if state is None:
        state = generate_synthetic_state()
        source = "synthetic fallback"

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
