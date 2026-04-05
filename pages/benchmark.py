"""
File: benchmark.py
Project: pages
File Created: Sunday, 5th April 2026 1:13:51 AM
Author: Zabdiel Addo
Email: zabdiel.addo@ashesi.edu.gh
Version: 1.0.0
Brief: <<brief>>
-----
Last Modified: Sunday, 5th April 2026 1:17:00 AM
Modified By: Zabdiel Addo
-----
Copyright ©2026 Zabdiel Addo
"""
import pandas as pd
import plotly.graph_objects as go
import streamlit as st


def render(
    filtered,
    PLOTLY_LAYOUT,
    AXIS_STYLE,
    AXIS_FONT,
    AXIS_TITLE_FONT,
    LEGEND_FONT,
    LOW_SUGAR,
    HIGH_PROTEIN,
):

    st.markdown("## Benchmark Shortlist")
    st.markdown(
        "The top-performing products already sitting in the target zone, "
        "ranked by composite health score then scan count. "
        "These are the products the R&D team should acquire, evaluate, and benchmark against."
    )

    # ── RANKED TABLE ──────────────────────────────────────────────
    benchmark = (
        filtered[filtered["in_target_zone"]][
            [
                "product_name_clean",
                "final_category",
                "brand_display",
                "sugars_100g",
                "proteins_100g",
                "fat_100g",
                "fiber_100g",
                "health_score",
                "scans_n",
                "nutriscore_grade",
            ]
        ]
        .dropna(subset=["product_name_clean"])
        .sort_values(["health_score", "scans_n"], ascending=[False, False])
        .head(30)
        .reset_index(drop=True)
    )
    benchmark.index += 1

    n_show = st.slider("Number of products to display", 5, 30, 20)
    benchmark_show = benchmark.head(n_show).copy()
    benchmark_show.columns = [
        "Product",
        "Category",
        "Brand",
        "Sugar (g)",
        "Protein (g)",
        "Fat (g)",
        "Fibre (g)",
        "Health Score",
        "Scans",
        "Nutriscore",
    ]
    benchmark_show["Scans"] = benchmark_show["Scans"].apply(
        lambda x: f"{int(x):,}" if pd.notna(x) else "N/A"
    )
    benchmark_show["Nutriscore"] = (
        benchmark_show["Nutriscore"].str.upper().fillna("N/A")
    )

    st.dataframe(
        benchmark_show.style.format(
            {
                "Sugar (g)": "{:.1f}",
                "Protein (g)": "{:.1f}",
                "Fat (g)": "{:.1f}",
                "Fibre (g)": "{:.1f}",
                "Health Score": "{:.1f}",
            }
        )
        .background_gradient(subset=["Health Score", "Protein (g)"], cmap="Blues")
        .background_gradient(subset=["Sugar (g)"], cmap="Reds_r"),
        use_container_width=True,
        hide_index=False,
    )

    # ── SCATTER POSITION ──────────────────────────────────────────
    st.markdown(
        '<div class="section-header">Shortlist Position on Nutrient Matrix</div>',
        unsafe_allow_html=True,
    )

    top20 = filtered[filtered["in_target_zone"]].nlargest(20, "health_score")
    all_sample = filtered.sample(min(5000, len(filtered)), random_state=42)
    target_sample = filtered[filtered["in_target_zone"]]

    fig_bench = go.Figure()

    fig_bench.add_trace(
        go.Scatter(
            x=all_sample["sugars_100g"],
            y=all_sample["proteins_100g"],
            mode="markers",
            marker=dict(size=4, color="#BDC3C7", opacity=0.25),
            name="All products",
            hovertemplate="Sugar: %{x:.1f}g<br>Protein: %{y:.1f}g<extra></extra>",
        )
    )
    fig_bench.add_trace(
        go.Scatter(
            x=target_sample["sugars_100g"],
            y=target_sample["proteins_100g"],
            mode="markers",
            marker=dict(size=5, color="#1B4F72", opacity=0.4),
            name=f"Target zone ({len(target_sample):,})",
            hovertemplate="Sugar: %{x:.1f}g<br>Protein: %{y:.1f}g<extra></extra>",
        )
    )
    fig_bench.add_trace(
        go.Scatter(
            x=top20["sugars_100g"],
            y=top20["proteins_100g"],
            mode="markers+text",
            marker=dict(
                size=10,
                color="#E74C3C",
                opacity=0.9,
                line=dict(color="white", width=1.5),
            ),
            text=top20["product_name_clean"].str[:18],
            textposition="top right",
            textfont=dict(size=8, color="#E74C3C"),
            name="Top 20 benchmark",
            hovertemplate=(
                "<b>%{text}</b><br>"
                "Sugar: %{x:.1f}g<br>"
                "Protein: %{y:.1f}g<extra></extra>"
            ),
        )
    )

    fig_bench.add_vline(
        x=LOW_SUGAR, line_dash="dash", line_color="#E74C3C", line_width=1.2
    )
    fig_bench.add_hline(
        y=HIGH_PROTEIN, line_dash="dash", line_color="#1B4F72", line_width=1.2
    )
    fig_bench.add_shape(
        type="rect",
        x0=0,
        x1=LOW_SUGAR,
        y0=HIGH_PROTEIN,
        y1=filtered["proteins_100g"].max() * 1.05,
        fillcolor="#1B4F72",
        opacity=0.05,
        line_width=0,
    )
    fig_bench.update_layout(
        **PLOTLY_LAYOUT,
        title=dict(
            text="Top 20 Benchmark Products — Position on Nutrient Matrix",
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
        height=520,
        legend=dict(
            font=LEGEND_FONT,
            bgcolor="rgba(255,255,255,0.9)",
            bordercolor="#DDE3EC",
            borderwidth=1,
        ),
    )
    st.plotly_chart(fig_bench, use_container_width=True)

    st.markdown(
        f'<p class="caveat">'
        f"These {len(top20)} products demonstrate the target zone is commercially viable. "
        f"The opportunity is a product with equivalent nutrition and stronger brand positioning."
        f"</p>",
        unsafe_allow_html=True,
    )