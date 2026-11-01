import numpy as np
import pandas as pd

def recommend_budget(df, budget=1_000_000):

    summary = df.groupby('platform').agg({
        'impressions': 'sum',
        'clicks': 'sum',
        'spend': 'sum',
        'conversions': 'sum',
        'revenue': 'sum'
    }).reset_index()

    summary['ROAS'] = summary['revenue'] / summary['spend']
    summary['CPA'] = summary['spend'] / summary['conversions']
    summary['Conversion_Rate'] = (
        summary['conversions'] / summary['clicks'] * 100
    )

    summary['Score'] = (
        0.50 * summary['ROAS'] / summary['ROAS'].max() +
        0.25 * summary['Conversion_Rate'] /
        summary['Conversion_Rate'].max() +
        0.25 * summary['CPA'].min() / summary['CPA']
    )

    weights = summary['Score'].to_numpy(dtype=float)
    weights /= weights.sum()

    lower = np.full(len(weights), 0.10)
    upper = np.full(len(weights), 0.35)

    for _ in range(1000):

        weights = np.clip(weights, lower, upper)
        difference = 1 - weights.sum()

        if abs(difference) < 1e-10:
            break

        eligible = (
            weights < upper - 1e-10
            if difference > 0
            else weights > lower + 1e-10
        )

        if not eligible.any():
            break

        weights[eligible] += (
            difference *
            weights[eligible] /
            weights[eligible].sum()
        )

    summary['Allocation_Percentage'] = weights * 100
    summary['Recommended_Budget'] = (
        weights * budget
    ).round(0)

    difference = budget - summary['Recommended_Budget'].sum()

    if difference != 0:
        summary.loc[
            summary['Recommended_Budget'].idxmax(),
            'Recommended_Budget'
        ] += difference

    return summary
