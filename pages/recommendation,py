/*
 * File: recommendation,py
 * Project: pages
 * File Created: Sunday, 5th April 2026 1:14:23 AM
 * Author: Zabdiel Addo
 * Email: zabdiel.addo@ashesi.edu.gh
 * Version: 1.0.0
 * Brief: <<brief>>
 * -----
 * Last Modified: Sunday, 5th April 2026 1:14:24 AM
 * Modified By: Zabdiel Addo
 * -----
 * Copyright ©2026 Zabdiel Addo
 */

import re

import pandas as pd
import plotly.graph_objects as go
import streamlit as st


PROTEIN_GROUPS = {
    "Pea / Pea Protein": ["pea protein", "pea"],
    "Soy / Soya":        ["soy protein", "soy", "soya"],
    "Peanut":            ["peanut", "peanuts"],
    "Whey":              ["whey protein", "whey"],
    "Milk Protein":      ["milk protein", "casein"],
    "Egg":               ["egg white", "egg"],
    "Almond":            ["almond"],
    "Oat":               ["oat protein", "oats", "oat"],
}


def render(filtered, filtered_cat_stats, PLOTLY_LAYOUT, AXIS_STYLE,
           AXIS_FONT, AXIS_TITLE_FONT, LOW_SUGAR, HIGH_PROTEIN):

    st.markdown("## Recommendation")
    st.markdown(
        "A data-driven brief for the R&D team, generated from the analysis pipeline. "
        "All figures update when sidebar filters are applied."
    )

    best_cat = filtered_cat_stats["gap_score"].idxmax() if len(filtered_cat_stats) else "N/A"

    if best_cat == "N/A":
        st.warning("No data available for the current filter selection.")
        st.stop()

    best = filtered_cat_stats.loc[best_cat]
    gap_products = filtered[
        (filtered["final_category"] == best_cat) & filtered["opportunity"]
    ]

    avg_sugar_gap   = gap_products["sugars_100g"].mean()
    avg_protein_gap = gap_products["proteins_100g"].mean()

    # ── MAIN RECOMMENDATION BOX ───────────────────────────────────
    st.markdown(
        f'<div class="rec-box">'
        f'<div class="rec-title">Market Recommendation — Helix CPG Partners</div>'
        f'<div class="rec-body">'
        f"Based on analysis of <strong>{len(filtered):,} snack products</strong>, "
        f"the biggest market opportunity is in <strong>{best_cat}</strong>.<br><br>"
        f"This category has a high demand rate of <strong>{best['high_demand_pct']:.0f}%</strong> "
        f"— indicating strong, proven consumer interest — but only "
        f"<strong>{best['target_zone_share_pct']:.1f}%</strong> of its products currently meet "
        f"the Low Sugar + High Protein nutritional threshold. "
        f"The {int(best['opportunity_pct'] * best['total_products'] / 100):,} opportunity products "
        f"in this category average <strong>{avg_sugar_gap:.1f}g sugar</strong> and "
        f"<strong>{avg_protein_gap:.1f}g protein</strong> per 100g — "
        f"they are performing well commercially but failing nutritionally.<br><br>"
        f"<strong>The brief:</strong> Develop a {best_cat} product with at least "
        f"<strong>{HIGH_PROTEIN}g of protein</strong> and less than "
        f"<strong>{LOW_SUGAR}g of sugar</strong> per 100g. "
        f"This would position the product in a near-empty market quadrant "
        f"where consumer demand already exists but healthy supply is thin."
        f"</div>"
        f"</div>",
        unsafe_allow_html=True,
    )

    # ── SUPPORTING METRICS ────────────────────────────────────────
    st.markdown('<div class="section-header">Supporting Metrics</div>', unsafe_allow_html=True)

    m1, m2, m3, m4 = st.columns(4)
    metrics = [
        ("Gap Score",           f"{best['gap_score']:.3f}",  "higher = larger opportunity"),
        ("High Demand Rate",    f"{best['high_demand_pct']:.0f}%", f"{int(best['total_products']):,} total products"),
        ("Currently Healthy",   f"{best['target_zone_share_pct']:.1f}%", "very few healthy options exist"),
        ("Opportunity Products",
         f"{int(best['opportunity_pct'] * best['total_products'] / 100):,}",
         "high demand but not healthy"),
    ]
    for col, (label, value, sub) in zip([m1, m2, m3, m4], metrics):
        with col:
            st.markdown(
                f'<div class="kpi-card">'
                f'<div class="kpi-label">{label}</div>'
                f'<div class="kpi-value">{value}</div>'
                f'<div class="kpi-sub">{sub}</div>'
                f'</div>',
                unsafe_allow_html=True,
            )

    # ── FORMULATION BRIEF ─────────────────────────────────────────
    st.markdown('<div class="section-header">Formulation Brief</div>', unsafe_allow_html=True)

    good_in_cat = filtered[
        (filtered["final_category"] == best_cat) &
        filtered["in_target_zone"] &
        filtered["ingredients_text_clean"].notna()
    ]

    form_counts = {
        src: good_in_cat["ingredients_text_clean"].apply(
            lambda x: any(re.search(rf"\b{re.escape(t)}\b", str(x).lower()) for t in terms)
        ).sum()
        for src, terms in PROTEIN_GROUPS.items()
    }

    form_df = pd.Series(form_counts).sort_values(ascending=False).reset_index()
    form_df.columns = ["Protein Source", "Target-Zone Products"]
    form_top3 = form_df.head(3)["Protein Source"].tolist()

    col_form, col_chart = st.columns([2, 3])

    with col_form:
        st.markdown("**Nutritional targets**")
        st.dataframe(
            pd.DataFrame({
                "Nutrient": ["Protein", "Sugar", "Current avg protein", "Current avg sugar"],
                "Target": [
                    f">= {HIGH_PROTEIN}g per 100g",
                    f"<= {LOW_SUGAR}g per 100g",
                    f"{avg_protein_gap:.1f}g (opportunity products)",
                    f"{avg_sugar_gap:.1f}g (opportunity products)",
                ],
            }),
            use_container_width=True,
            hide_index=True,
        )
        st.markdown("**Recommended protein sources**")
        st.markdown(
            f"Based on existing target-zone {best_cat} products: "
            f"**{', '.join(form_top3) if form_top3 else 'insufficient data'}**"
        )

    with col_chart:
        form_plot = form_df[form_df["Target-Zone Products"] > 0].sort_values(
            "Target-Zone Products", ascending=True
        )
        if not form_plot.empty:
            fig_form = go.Figure()
            fig_form.add_trace(go.Bar(
                x=form_plot["Target-Zone Products"],
                y=form_plot["Protein Source"],
                orientation="h",
                marker_color=[
                    "#1B4F72" if s in form_top3 else "#A9C4D9"
                    for s in form_plot["Protein Source"]
                ],
                hovertemplate="<b>%{y}</b><br>Products: %{x}<extra></extra>",
            ))
            fig_form.update_layout(
                **PLOTLY_LAYOUT,
                title=dict(
                    text=f"Protein Sources in Healthy {best_cat} Products",
                    font=dict(size=12, color="#1C2833"), x=0,
                ),
                xaxis=dict(**AXIS_STYLE, title="Number of Products",
                           tickfont=AXIS_FONT, title_font=AXIS_TITLE_FONT),
                yaxis=dict(**AXIS_STYLE, title="", tickfont=AXIS_FONT, title_font=AXIS_TITLE_FONT),
                height=300,
                showlegend=False,
            )
            st.plotly_chart(fig_form, use_container_width=True)
        else:
            st.markdown(
                f'<p class="caveat">Insufficient ingredient data for {best_cat} '
                f'target-zone products to generate formulation recommendations.</p>',
                unsafe_allow_html=True,
            )

    # ── ANALYSIS SUMMARY ──────────────────────────────────────────
    st.markdown('<div class="section-header">Analysis Summary</div>', unsafe_allow_html=True)

    col_s1, col_s2 = st.columns(2)

    with col_s1:
        st.markdown("**Dataset**")
        st.dataframe(
            pd.DataFrame({
                "Metric": ["Total products", "Categories", "In target zone", "High demand", "Opportunity gap"],
                "Value": [
                    f"{len(filtered):,}",
                    str(filtered["final_category"].nunique()),
                    f"{filtered['in_target_zone'].sum():,} ({filtered['in_target_zone'].mean():.1%})",
                    f"{filtered['high_demand'].sum():,} ({filtered['high_demand'].mean():.1%})",
                    f"{filtered['opportunity'].sum():,} ({filtered['opportunity'].mean():.1%})",
                ],
            }),
            use_container_width=True,
            hide_index=True,
        )

    with col_s2:
        st.markdown("**Thresholds & Methodology**")
        st.dataframe(
            pd.DataFrame({
                "Parameter": [
                    "Low sugar threshold", "High protein threshold",
                    "High demand definition", "Gap score formula", "Data source",
                ],
                "Value": [
                    f"<= {LOW_SUGAR}g per 100g (WHO low-sugar benchmark: 5g)",
                    f">= {HIGH_PROTEIN}g per 100g (industry standard: 10g)",
                    "Above 75th percentile scan count",
                    "high_demand_rate x (1 - target_zone_rate)",
                    "Open Food Facts (openfoodfacts.org)",
                ],
            }),
            use_container_width=True,
            hide_index=True,
        )