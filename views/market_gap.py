"""
File: market_gap.py
Project: pages
File Created: Sunday, 5th April 2026 1:14:02 AM
Author: Zabdiel Addo
Email: zabdiel.addo@ashesi.edu.gh
Version: 1.0.0
Brief: <<brief>>
-----
Last Modified: Sunday, 5th April 2026 1:28:07 AM
Modified By: Zabdiel Addo
-----
Copyright ©2026 Zabdiel Addo
"""
import pandas as pd
import plotly.graph_objects as go
import streamlit as st


def render(
    filtered,
    filtered_cat_stats,
    PLOTLY_LAYOUT,
    AXIS_STYLE,
    AXIS_FONT,
    AXIS_TITLE_FONT,
    LEGEND_FONT,
    LOW_SUGAR,
    HIGH_PROTEIN,
):

    st.markdown("## Market Gap")
    st.markdown(
        "Categories ranked by gap score — the product of high consumer demand and low healthy supply. "
        "A high gap score identifies where the market opportunity is largest."
    )

    top_cat = (
        filtered_cat_stats["gap_score"].idxmax() if len(filtered_cat_stats) else "N/A"
    )
    top_row = filtered_cat_stats.loc[top_cat] if top_cat != "N/A" else None

    if top_row is not None:
        st.markdown(
            f'<div class="insight-box">'
            f"The highest-opportunity category is <strong>{top_cat}</strong> — "
            f"it has a high demand rate of <strong>{top_row['high_demand_pct']:.0f}%</strong> "
            f"but only <strong>{top_row['target_zone_share_pct']:.1f}%</strong> of its products "
            f"meet the nutritional threshold. Gap score: <strong>{top_row['gap_score']:.3f}</strong>."
            f"</div>",
            unsafe_allow_html=True,
        )

    st.markdown(
        '<div class="section-header">Opportunity Ranking</div>', unsafe_allow_html=True
    )

    gap_df = (
        filtered_cat_stats.reset_index()
        .rename(columns={"final_category": "Category"})
        .sort_values("gap_score", ascending=False)
    )

    col_a, col_b = st.columns([3, 2])

    # ── GAP SCORE BAR ─────────────────────────────────────────────
    with col_a:
        gap_plot = gap_df.sort_values("gap_score", ascending=True)
        bar_colours = [
            "#1B4F72" if c == top_cat else "#5D6D7E" for c in gap_plot["Category"]
        ]

        fig_gap = go.Figure()
        fig_gap.add_trace(
            go.Bar(
                x=gap_plot["gap_score"],
                y=gap_plot["Category"],
                orientation="h",
                marker_color=bar_colours,
                text=gap_plot["gap_score"].apply(lambda x: f"{x:.3f}"),
                textposition="outside",
                textfont=dict(size=10, color="#1F2225"),
                hovertemplate="<b>%{y}</b><br>Gap Score: %{x:.3f}<extra></extra>",
            )
        )
        fig_gap.update_layout(
            **PLOTLY_LAYOUT,
            title=dict(
                text="Gap Score by Category", font=dict(size=13, color="#1C2833"), x=0
            ),
            xaxis=dict(
                **AXIS_STYLE,
                title="Gap Score (high demand × low healthy supply)",
                tickfont=AXIS_FONT,
                title_font=AXIS_TITLE_FONT,
            ),
            yaxis=dict(
                **AXIS_STYLE, title="", tickfont=AXIS_FONT, title_font=AXIS_TITLE_FONT
            ),
            height=420,
            showlegend=False,
        )
        st.plotly_chart(fig_gap, use_container_width=True)

    # ── BUBBLE CHART ─────────────────────────────────────────────
    with col_b:
        fig_bubble = go.Figure()
        for _, row in gap_df.iterrows():
            colour = "#1B4F72" if row["Category"] == top_cat else "#5D6D7E"
            fig_bubble.add_trace(
                go.Scatter(
                    x=[row["high_demand_pct"]],
                    y=[row["target_zone_share_pct"]],
                    mode="markers+text",
                    marker=dict(
                        size=max(row["total_products"] / 200, 8),
                        color=colour,
                        opacity=0.7,
                        line=dict(color="white", width=1),
                    ),
                    text=[row["Category"].split(" ")[0]],
                    textposition="top center",
                    textfont=dict(size=8, color="#1B1E21"),
                    name=row["Category"],
                    showlegend=False,
                    hovertemplate=(
                        f"<b>{row['Category']}</b><br>"
                        f"High Demand: {row['high_demand_pct']:.0f}%<br>"
                        f"In Target Zone: {row['target_zone_share_pct']:.1f}%<br>"
                        f"Gap Score: {row['gap_score']:.3f}<extra></extra>"
                    ),
                )
            )
        fig_bubble.update_layout(
            **PLOTLY_LAYOUT,
            title=dict(
                text="Demand vs Healthy Supply",
                font=dict(size=13, color="#1C2833"),
                x=0,
            ),
            xaxis=dict(
                **AXIS_STYLE,
                title="High Demand Rate (%)",
                tickfont=AXIS_FONT,
                title_font=AXIS_TITLE_FONT,
            ),
            yaxis=dict(
                **AXIS_STYLE,
                title="In Target Zone (%)",
                tickfont=AXIS_FONT,
                title_font=AXIS_TITLE_FONT,
            ),
            height=420,
            annotations=[
                dict(
                    x=0.02,
                    y=0.98,
                    xref="paper",
                    yref="paper",
                    text="Upper-left = highest opportunity",
                    showarrow=False,
                    font=dict(size=9, color="#7F8C8D"),
                    align="left",
                )
            ],
        )
        st.plotly_chart(fig_bubble, use_container_width=True)

    # ── FULL TABLE ────────────────────────────────────────────────
    st.markdown(
        '<div class="section-header">Full Opportunity Table</div>',
        unsafe_allow_html=True,
    )

    table_df = gap_df[
        [
            "Category",
            "total_products",
            "gap_score",
            "high_demand_pct",
            "target_zone_share_pct",
            "opportunity_pct",
            "avg_sugar",
            "avg_protein",
        ]
    ].copy()
    table_df.columns = [
        "Category",
        "Products",
        "Gap Score",
        "High Demand %",
        "Target Zone %",
        "Opportunity %",
        "Avg Sugar (g)",
        "Avg Protein (g)",
    ]
    table_df = table_df.reset_index(drop=True)

    st.dataframe(
        table_df.style.format(
            {
                "Gap Score": "{:.3f}",
                "High Demand %": "{:.1f}%",
                "Target Zone %": "{:.1f}%",
                "Opportunity %": "{:.1f}%",
                "Avg Sugar (g)": "{:.1f}",
                "Avg Protein (g)": "{:.1f}",
            }
        ).background_gradient(subset=["Gap Score"], cmap="Blues"),
        use_container_width=True,
        hide_index=True,
    )

    # ── THREE-WAY COMPARISON ──────────────────────────────────────
    if top_cat != "N/A":
        st.markdown(
            f'<div class="section-header">Three-Way Comparison — {top_cat}</div>',
            unsafe_allow_html=True,
        )
        st.markdown(
            "Comparing all products in the top-opportunity category against "
            "the opportunity segment (high demand, not healthy) and target zone products."
        )

        cat_df = filtered[filtered["final_category"] == top_cat].copy()
        opp_df = cat_df[cat_df["opportunity"]]
        target_df = cat_df[cat_df["in_target_zone"]]

        nutrient_cols = ["sugars_100g", "proteins_100g", "fat_100g", "fiber_100g"]
        compare = pd.DataFrame(
            {
                f"All ({len(cat_df):,})": cat_df[nutrient_cols].mean(),
                f"Opportunity ({len(opp_df):,})": opp_df[nutrient_cols].mean(),
                f"Target Zone ({len(target_df):,})": target_df[nutrient_cols].mean(),
            }
        ).round(2)
        compare.index = ["Sugar (g)", "Protein (g)", "Fat (g)", "Fibre (g)"]
        st.dataframe(compare, use_container_width=True)

        fig_3way = go.Figure()
        sample_all = cat_df.sample(min(3000, len(cat_df)), random_state=42)
        fig_3way.add_trace(
            go.Scatter(
                x=sample_all["sugars_100g"],
                y=sample_all["proteins_100g"],
                mode="markers",
                marker=dict(size=4, color="#70767A", opacity=0.4),
                name=f"All ({len(cat_df):,})",
                hovertemplate="Sugar: %{x:.1f}g<br>Protein: %{y:.1f}g<extra></extra>",
            )
        )
        fig_3way.add_trace(
            go.Scatter(
                x=opp_df["sugars_100g"],
                y=opp_df["proteins_100g"],
                mode="markers",
                marker=dict(size=5, color="#E74C3C", opacity=0.6),
                name=f"Opportunity ({len(opp_df):,})",
                hovertemplate="Sugar: %{x:.1f}g<br>Protein: %{y:.1f}g<extra></extra>",
            )
        )
        fig_3way.add_trace(
            go.Scatter(
                x=target_df["sugars_100g"],
                y=target_df["proteins_100g"],
                mode="markers",
                marker=dict(size=6, color="#1A7A4A", opacity=0.8),
                name=f"Target Zone ({len(target_df):,})",
                hovertemplate="Sugar: %{x:.1f}g<br>Protein: %{y:.1f}g<extra></extra>",
            )
        )
        fig_3way.add_vline(
            x=LOW_SUGAR, line_dash="dash", line_color="#E74C3C", line_width=1.2
        )
        fig_3way.add_hline(
            y=HIGH_PROTEIN, line_dash="dash", line_color="#1B4F72", line_width=1.2
        )
        fig_3way.update_layout(
            **PLOTLY_LAYOUT,
            title=dict(
                text=f"{top_cat} — Gap Visualisation",
                font=dict(size=13, color="#1C2833"),
                x=0,
            ),
            xaxis=dict(
                **AXIS_STYLE,
                title="Sugar (g per 100g)",
                tickfont=AXIS_FONT,
                title_font=AXIS_TITLE_FONT,
            ),
            yaxis=dict(
                **AXIS_STYLE,
                title="Protein (g per 100g)",
                tickfont=AXIS_FONT,
                title_font=AXIS_TITLE_FONT,
            ),
            height=440,
            legend=dict(
                font=LEGEND_FONT,
                bgcolor="rgba(255,255,255,0.9)",
                bordercolor="#DDE3EC",
                borderwidth=1,
            ),
        )
        st.plotly_chart(fig_3way, use_container_width=True)