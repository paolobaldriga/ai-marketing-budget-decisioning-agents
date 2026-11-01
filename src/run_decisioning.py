"""
Multi-agent Marketing Budget Decisioning System
Measurement → Allocation → Explanation → Guardrail
"""

import numpy as np
import pandas as pd

np.random.seed(42)

CHANNELS = ["Meta", "Google", "TikTok", "Programmatic", "Email", "Influencer"]

def generate_market_state():
    """Synthetic weekly market signals."""
    data = []
    for ch in CHANNELS:
        data.append({
            "channel": ch,
            "current_share": np.random.uniform(0.08, 0.35),
            "incremental_roas": np.random.uniform(1.2, 4.5),
            "ltv_index": np.random.uniform(0.7, 1.6),
            "saturation": np.random.uniform(0.3, 0.95),  # 1 = fully saturated
            "recent_trend": np.random.uniform(-0.15, 0.20),
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
        saturated = state[state["saturation"] > 0.8]["channel"].tolist()
        if saturated:
            insights.append(f"Near saturation: {', '.join(saturated)}")
        return {"state": state, "insights": insights}

class AllocationAgent:
    def run(self, measurement, total_budget=1.0, max_share=0.40, min_share=0.05):
        state = measurement["state"].copy()
        # Simple value-based reallocation with constraints
        raw = state["expected_value"].clip(lower=0.1)
        raw = raw / raw.sum()
        # Smooth toward current share to avoid wild swings
        new_share = 0.6 * raw + 0.4 * state["current_share"]
        new_share = new_share.clip(min_share, max_share)
        new_share = new_share / new_share.sum()
        state["proposed_share"] = new_share
        state["delta_pp"] = (state["proposed_share"] - state["current_share"]) * 100
        return state

class ExplanationAgent:
    def run(self, allocation):
        moves = allocation[allocation["delta_pp"].abs() > 1.5].sort_values("delta_pp", ascending=False)
        if moves.empty:
            return "No material reallocation recommended this week. Current mix is close to optimal under current signals."

        lines = []
        for _, row in moves.iterrows():
            direction = "increase" if row["delta_pp"] > 0 else "decrease"
            lines.append(
                f"{direction.capitalize()} {row['channel']} by {abs(row['delta_pp']):.1f} pp "
                f"(expected value {row['expected_value']:.2f}, saturation {row['saturation']:.0%})."
            )
        top = allocation.loc[allocation["expected_value"].idxmax()]
        summary = (
            f"Primary move is driven by {top['channel']} showing the strongest combination of incremental return and remaining headroom. "
            + " ".join(lines[:3])
        )
        return summary

class GuardrailAgent:
    def run(self, allocation, max_share=0.40):
        issues = []
        if (allocation["proposed_share"] > max_share + 0.001).any():
            issues.append("Channel exceeds maximum share cap.")
        big_swings = allocation[allocation["delta_pp"].abs() > 12]
        if not big_swings.empty:
            issues.append(f"Large swings detected: {', '.join(big_swings['channel'])}")
        status = "OK" if not issues else "REVIEW"
        return {"status": status, "issues": issues}

def main():
    print("=== AI Marketing Budget Decisioning ===\n")
    state = generate_market_state()

    meas = MeasurementAgent().run(state)
    print("Measurement insights:")
    for i in meas["insights"]:
        print(" -", i)

    alloc = AllocationAgent().run(meas)
    print("\nProposed allocation:")
    print(alloc[["channel", "current_share", "proposed_share", "delta_pp", "expected_value"]].round(3).to_string(index=False))

    explanation = ExplanationAgent().run(alloc)
    print("\nExplanation Agent:")
    print(explanation)

    guard = GuardrailAgent().run(alloc)
    print(f"\nGuardrail: {guard['status']}")
    if guard["issues"]:
        for issue in guard["issues"]:
            print(" -", issue)

    print("\n--- Decision ready for CMO review ---")

if __name__ == "__main__":
    main()
