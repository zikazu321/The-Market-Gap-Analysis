"""
File: protein_sources.py
Project: pages
File Created: Sunday, 5th April 2026 1:14:13 AM
Author: Zabdiel Addo
Email: zabdiel.addo@ashesi.edu.gh
Version: 1.0.0
Brief: <<brief>>
-----
Last Modified: Sunday, 5th April 2026 1:16:49 AM
Modified By: Zabdiel Addo
-----
Copyright ©2026 Zabdiel Addo
"""

import re

import plotly.graph_objects as go
import streamlit as st


PROTEIN_GROUPS = {
    "Pea / Pea Protein": ["pea protein", "pea"],
    "Soy / Soya": ["soy protein", "soy", "soya"],
    "Peanut": ["peanut", "peanuts"],
    "Whey": ["whey protein", "whey"],
    "Milk Protein": ["milk protein", "casein"],
    "Egg": ["egg white", "egg"],
    "Almond": ["almond"],
    "Oat": ["oat protein", "oats", "oat"],
    "Chickpea": ["chickpea", "chickpeas"],
    "Quinoa": ["quinoa"],
    "Lentil": ["lentil", "lentils"],
    "Cashew": ["cashew"],
}


def _has_term(text, terms):
    t = str(text).lower()
    return any(re.search(rf"\b{re.escape(k)}\b", t) for k in terms)


def render(
    filtered,
    selected_cats,
    PLOTLY_LAYOUT,
    AXIS_STYLE,
    AXIS_FONT,
    AXIS_TITLE_FONT,
    SMALL_AXIS_FONT,
    LOW_SUGAR,
    HIGH_PROTEIN,
):

    st.markdown("## Protein Sources")
    st.markdown(
        "Analysis of which protein-bearing ingredients appear most frequently "
        "in products that already meet both the low sugar and high protein thresholds. "
        "These are the formulation benchmarks for the recommended new product."
    )

    good = filtered[
        (filtered["proteins_100g"] >= HIGH_PROTEIN)
        & (filtered["sugars_100g"] <= LOW_SUGAR)
        & filtered["ingredients_text_clean"].notna()
    ].copy()

    # ── COUNT PER SOURCE ──────────────────────────────────────────
    protein_counts = {
        group: good["ingredients_text_clean"].apply(lambda x: _has_term(x, terms)).sum()
        for group, terms in PROTEIN_GROUPS.items()
    }

    import pandas as pd

    ps_df = pd.Series(protein_counts).sort_values(ascending=False).reset_index()
    ps_df.columns = ["Source", "Product Count"]
    ps_df["Pct of Target-Zone Products"] = (
        ps_df["Product Count"] / len(good) * 100
    ).round(1)
    top_3 = ps_df.head(3)["Source"].tolist()

    # ── TOP 3 KPI CARDS ───────────────────────────────────────────
    k1, k2, k3 = st.columns(3)
    for col, src in zip([k1, k2, k3], top_3):
        row = ps_df[ps_df["Source"] == src].iloc[0]
        with col:
            st.markdown(
                f'<div class="kpi-card">'
                f'<div class="kpi-label">#{top_3.index(src) + 1} Protein Source</div>'
                f'<div class="kpi-value">{src}</div>'
                f'<div class="kpi-sub">Found in {int(row["Product Count"]):,} products '
                f"({row['Pct of Target-Zone Products']:.1f}%)</div>"
                f"</div>",
                unsafe_allow_html=True,
            )

    st.markdown(
        f'<p class="caveat">Based on {len(good):,} target-zone products with ingredient text available.</p>',
        unsafe_allow_html=True,
    )

    # ── FREQUENCY BAR ─────────────────────────────────────────────
    st.markdown(
        '<div class="section-header">Protein Source Frequency</div>',
        unsafe_allow_html=True,
    )

    ps_plot = ps_df.sort_values("Product Count", ascending=True)
    bar_colours = ["#1B4F72" if s in top_3 else "#A9C4D9" for s in ps_plot["Source"]]

    fig_ps = go.Figure()
    fig_ps.add_trace(
        go.Bar(
            x=ps_plot["Product Count"],
            y=ps_plot["Source"],
            orientation="h",
            marker_color=bar_colours,
            text=ps_plot.apply(
                lambda r: (
                    f"{int(r['Product Count']):,}  ({r['Pct of Target-Zone Products']}%)"
                ),
                axis=1,
            ),
            textposition="outside",
            textfont=dict(size=10, color="#222528"),
            hovertemplate="<b>%{y}</b><br>Products: %{x:,}<extra></extra>",
        )
    )
    fig_ps.update_layout(
        **PLOTLY_LAYOUT,
        title=dict(
            text=f"Protein Sources in Target-Zone Products (sugar \u2264 {LOW_SUGAR}g, protein \u2265 {HIGH_PROTEIN}g)",
            font=dict(size=13, color="#1C2833"),
            x=0,
        ),
        xaxis=dict(
            **AXIS_STYLE,
            title="Number of Products Containing Ingredient",
            tickfont=AXIS_FONT,
            title_font=AXIS_TITLE_FONT,
        ),
        yaxis=dict(
            **AXIS_STYLE, title="", tickfont=AXIS_FONT, title_font=AXIS_TITLE_FONT
        ),
        height=420,
        showlegend=False,
    )
    st.plotly_chart(fig_ps, use_container_width=True)

    # ── HEATMAP BY CATEGORY ───────────────────────────────────────
    st.markdown(
        '<div class="section-header">Protein Source by Category</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        "Which categories rely most heavily on each protein source "
        "among their target-zone products."
    )

    cat_source_rows = []
    for cat in selected_cats:
        cat_good = good[good["final_category"] == cat]
        if len(cat_good) == 0:
            continue
        for src, terms in PROTEIN_GROUPS.items():
            count = (
                cat_good["ingredients_text_clean"]
                .apply(lambda x: _has_term(x, terms))
                .sum()
            )
            cat_source_rows.append(
                {
                    "Category": cat,
                    "Source": src,
                    "Pct": round(count / len(cat_good) * 100, 1)
                    if len(cat_good)
                    else 0,
                }
            )

    cat_src_df = pd.DataFrame(cat_source_rows)
    if not cat_src_df.empty:
        pivot = cat_src_df.pivot_table(
            index="Category", columns="Source", values="Pct", fill_value=0
        ).round(1)

        fig_heat = go.Figure(
            data=go.Heatmap(
                z=pivot.values,
                x=pivot.columns.tolist(),
                y=pivot.index.tolist(),
                colorscale=[[0, "#F7F9FC"], [1, "#1B4F72"]],
                hovertemplate=(
                    "<b>%{y}</b><br>Source: %{x}<br>"
                    "% of target-zone products: %{z:.1f}%<extra></extra>"
                ),
                showscale=True,
                colorbar=dict(title="% Products", tickfont=dict(size=10)),
            )
        )
        fig_heat.update_layout(
            **PLOTLY_LAYOUT,
            title=dict(
                text="% of Target-Zone Products Containing Each Protein Source",
                font=dict(size=13, color="#1C2833"),
                x=0,
            ),
            xaxis=dict(**AXIS_STYLE, title="", tickfont=SMALL_AXIS_FONT),
            yaxis=dict(**AXIS_STYLE, title="", tickfont=SMALL_AXIS_FONT),
            height=400,
        )
        st.plotly_chart(fig_heat, use_container_width=True)