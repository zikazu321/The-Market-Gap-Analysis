"""
File: overview.py
Project: pages
File Created: Sunday, 5th April 2026 1:13:42 AM
Author: Zabdiel Addo
Email: zabdiel.addo@ashesi.edu.gh
Version: 1.0.0
Brief: <<brief>>
-----
Last Modified: Sunday, 5th April 2026 1:16:09 AM
Modified By: Zabdiel Addo
-----
Copyright ©2026 Zabdiel Addo
"""

import plotly.graph_objects as go
import streamlit as st


def render(
    filtered,
    filtered_cat_stats,
    ALL_CATEGORIES,
    CATEGORY_PALETTE,
    PLOTLY_LAYOUT,
    AXIS_STYLE,
    AXIS_FONT,
    AXIS_TITLE_FONT,
    LOW_SUGAR,
    HIGH_PROTEIN,
):

    st.markdown("## Market Overview")
    st.markdown(
        "A high-level view of the snack market composition, nutritional profile, "
        "and the scale of the healthy snacking gap."
    )

    # ── KPI ROW ───────────────────────────────────────────────────
    n_total = len(filtered)
    n_target = filtered["in_target_zone"].sum()
    n_demand = filtered["high_demand"].sum()
    n_opp = filtered["opportunity"].sum()
    pct_target = n_target / n_total * 100 if n_total else 0
    pct_demand = n_demand / n_total * 100 if n_total else 0
    pct_opp = n_opp / n_total * 100 if n_total else 0

    k1, k2, k3, k4 = st.columns(4)

    with k1:
        st.markdown(
            f'<div class="kpi-card">'
            f'<div class="kpi-label">Products Analysed</div>'
            f'<div class="kpi-value">{n_total:,}</div>'
            f'<div class="kpi-sub">after cleaning & classification</div>'
            f"</div>",
            unsafe_allow_html=True,
        )
    with k2:
        st.markdown(
            f'<div class="kpi-card">'
            f'<div class="kpi-label">In Target Zone</div>'
            f'<div class="kpi-value">{pct_target:.1f}%</div>'
            f'<div class="kpi-sub">Low sugar + high protein ({n_target:,} products)</div>'
            f"</div>",
            unsafe_allow_html=True,
        )
    with k3:
        st.markdown(
            f'<div class="kpi-card">'
            f'<div class="kpi-label">High Demand</div>'
            f'<div class="kpi-value">{pct_demand:.1f}%</div>'
            f'<div class="kpi-sub">Above 75th pct scan count ({n_demand:,} products)</div>'
            f"</div>",
            unsafe_allow_html=True,
        )
    with k4:
        st.markdown(
            f'<div class="kpi-card">'
            f'<div class="kpi-label">Opportunity Gap</div>'
            f'<div class="kpi-value">{pct_opp:.1f}%</div>'
            f'<div class="kpi-sub">High demand, not in target zone</div>'
            f"</div>",
            unsafe_allow_html=True,
        )

    st.markdown(
        '<p class="caveat">High demand signal is based on scan count data available for 45% of products. '
        "Remaining products are classified as low demand by default.</p>",
        unsafe_allow_html=True,
    )

    # ── CATEGORY DISTRIBUTION ─────────────────────────────────────
    st.markdown(
        '<div class="section-header">Category Distribution</div>',
        unsafe_allow_html=True,
    )

    col_l, col_r = st.columns([3, 2])

    with col_l:
        cat_counts = filtered["final_category"].value_counts().reset_index()
        cat_counts.columns = ["Category", "Products"]
        cat_counts = cat_counts.sort_values("Products", ascending=True)

        cat_colour_map = {
            cat: CATEGORY_PALETTE[i % len(CATEGORY_PALETTE)]
            for i, cat in enumerate(ALL_CATEGORIES)
        }

        fig_cat = go.Figure()
        fig_cat.add_trace(
            go.Bar(
                x=cat_counts["Products"],
                y=cat_counts["Category"],
                orientation="h",
                marker_color=[
                    cat_colour_map.get(c, "#1B4F72") for c in cat_counts["Category"]
                ],
                text=cat_counts["Products"].apply(lambda x: f"{x:,}"),
                textposition="outside",
                textfont=dict(size=10, color="#2C353D"),
                hovertemplate="<b>%{y}</b><br>Products: %{x:,}<extra></extra>",
            )
        )
        fig_cat.update_layout(
            **PLOTLY_LAYOUT,
            title=dict(
                text="Product Count by Category",
                font=dict(size=13, color="#1C2833"),
                x=0,
            ),
            xaxis=dict(
                **AXIS_STYLE,
                title="Number of Products",
                tickfont=AXIS_FONT,
                title_font=AXIS_TITLE_FONT,
            ),
            yaxis=dict(
                **AXIS_STYLE, title="", tickfont=AXIS_FONT, title_font=AXIS_TITLE_FONT
            ),
            height=420,
            showlegend=False,
        )
        st.plotly_chart(fig_cat, use_container_width=True)

    with col_r:
        avg_df = (
            filtered.groupby("final_category")[["sugars_100g", "proteins_100g"]]
            .mean()
            .round(1)
            .reset_index()
            .sort_values("sugars_100g", ascending=False)
        )
        avg_df.columns = ["Category", "Avg Sugar (g)", "Avg Protein (g)"]

        fig_avg = go.Figure()
        fig_avg.add_trace(
            go.Bar(
                name="Avg Sugar",
                x=avg_df["Avg Sugar (g)"],
                y=avg_df["Category"],
                orientation="h",
                marker_color="#E74C3C",
                opacity=0.8,
                hovertemplate="<b>%{y}</b><br>Avg Sugar: %{x:.1f}g<extra></extra>",
            )
        )
        fig_avg.add_trace(
            go.Bar(
                name="Avg Protein",
                x=avg_df["Avg Protein (g)"],
                y=avg_df["Category"],
                orientation="h",
                marker_color="#1B4F72",
                opacity=0.8,
                hovertemplate="<b>%{y}</b><br>Avg Protein: %{x:.1f}g<extra></extra>",
            )
        )
        fig_avg.add_vline(
            x=LOW_SUGAR,
            line_dash="dash",
            line_color="#E74C3C",
            opacity=0.5,
            annotation_text="Sugar threshold",
            annotation_font_size=9,
            annotation_font_color="#E74C3C",
        )
        fig_avg.add_vline(
            x=HIGH_PROTEIN,
            line_dash="dash",
            line_color="#1B4F72",
            opacity=0.5,
            annotation_text="Protein threshold",
            annotation_font_size=9,
            annotation_font_color="#1B4F72",
            annotation_position="bottom right",
        )
        fig_avg.update_layout(
            **PLOTLY_LAYOUT,
            title=dict(
                text="Average Sugar vs Protein by Category",
                font=dict(size=13, color="#1C2833"),
                x=0,
            ),
            xaxis=dict(
                **AXIS_STYLE,
                title="g per 100g",
                tickfont=AXIS_FONT,
                title_font=AXIS_TITLE_FONT,
            ),
            yaxis=dict(
                **AXIS_STYLE, title="", tickfont=AXIS_FONT, title_font=AXIS_TITLE_FONT
            ),
            barmode="overlay",
            height=420,
            legend=dict(orientation="h", y=-0.12, x=0, font=dict(size=10)),
        )
        st.plotly_chart(fig_avg, use_container_width=True)

    # ── HEALTH SCORE ──────────────────────────────────────────────
    st.markdown(
        '<div class="section-header">Composite Health Score by Category</div>',
        unsafe_allow_html=True,
    )

    hs_df = (
        filtered.groupby("final_category")["health_score"]
        .mean()
        .round(1)
        .reset_index()
        .sort_values("health_score", ascending=True)
    )
    hs_df.columns = ["Category", "Health Score"]
    hs_colours = ["#1A7A4A" if v >= 0 else "#E74C3C" for v in hs_df["Health Score"]]

    fig_hs = go.Figure()
    fig_hs.add_trace(
        go.Bar(
            x=hs_df["Category"],
            y=hs_df["Health Score"],
            marker_color=hs_colours,
            text=hs_df["Health Score"].apply(lambda x: f"{x:.1f}"),
            textposition="outside",
            textfont=dict(size=10, color="#222427"),
            hovertemplate="<b>%{x}</b><br>Health Score: %{y:.1f}<extra></extra>",
        )
    )
    fig_hs.add_hline(y=0, line_color="#DDE3EC", line_width=1.5)
    fig_hs.update_layout(
        **PLOTLY_LAYOUT,
        title=dict(
            text="Average Composite Health Score — Protein & Fibre rewarded | Sugar & Fat penalised",
            font=dict(size=13, color="#1C2833"),
            x=0,
        ),
        xaxis=dict(
            **AXIS_STYLE, title="", tickfont=AXIS_FONT, title_font=AXIS_TITLE_FONT
        ),
        yaxis=dict(
            **AXIS_STYLE,
            title="Health Score",
            tickfont=AXIS_FONT,
            title_font=AXIS_TITLE_FONT,
        ),
        height=360,
        showlegend=False,
    )
    st.plotly_chart(fig_hs, use_container_width=True)