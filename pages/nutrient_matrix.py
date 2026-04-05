"""
File: nutrient_matrix.py
Project: pages
File Created: Sunday, 5th April 2026 1:14:37 AM
Author: Zabdiel Addo
Email: zabdiel.addo@ashesi.edu.gh
Version: 1.0.0
Brief: <<brief>>
-----
Last Modified: Sunday, 5th April 2026 1:16:21 AM
Modified By: Zabdiel Addo
-----
Copyright ©2026 Zabdiel Addo
"""

import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from plotly.subplots import make_subplots


def render(
    filtered,
    selected_cats,
    ALL_CATEGORIES,
    CATEGORY_PALETTE,
    PLOTLY_LAYOUT,
    AXIS_STYLE,
    AXIS_FONT,
    AXIS_TITLE_FONT,
    LEGEND_FONT,
    LOW_SUGAR,
    HIGH_PROTEIN,
):

    st.markdown("## Nutrient Matrix")
    st.markdown(
        "Sugar (x-axis) vs Protein (y-axis) for all products. "
        "The target zone — low sugar, high protein — sits in the upper-left quadrant. "
        "Use sidebar filters to isolate specific categories or segments."
    )

    # Sample for performance
    plot_df = filtered.dropna(subset=["sugars_100g", "proteins_100g"]).copy()
    if len(plot_df) > 8000:
        plot_df = plot_df.sample(8000, random_state=42)

    view = st.radio(
        "View",
        ["All categories (coloured)", "Single category"],
        horizontal=True,
        label_visibility="collapsed",
    )

    if view == "Single category":
        chosen = st.selectbox("Select category", options=selected_cats)
        plot_df = plot_df[plot_df["final_category"] == chosen]

    n_in_zone = (
        (plot_df["sugars_100g"] <= LOW_SUGAR)
        & (plot_df["proteins_100g"] >= HIGH_PROTEIN)
    ).sum()

    st.markdown(
        f'<div class="insight-box">'
        f"<strong>{n_in_zone:,}</strong> of <strong>{len(plot_df):,}</strong> plotted products "
        f"({n_in_zone / len(plot_df) * 100:.1f}%) sit in the target zone "
        f"(sugar &le; {LOW_SUGAR}g, protein &ge; {HIGH_PROTEIN}g)."
        f"</div>",
        unsafe_allow_html=True,
    )

    # ── MAIN SCATTER ──────────────────────────────────────────────
    fig_scatter = px.scatter(
        plot_df,
        x="sugars_100g",
        y="proteins_100g",
        color="final_category" if view == "All categories (coloured)" else None,
        color_discrete_sequence=CATEGORY_PALETTE,
        opacity=0.45,
        hover_data={
            "product_name_clean": True,
            "brand_display": True,
            "sugars_100g": ":.1f",
            "proteins_100g": ":.1f",
            "final_category": True,
        },
        labels={
            "sugars_100g": "Sugar (g per 100g)",
            "proteins_100g": "Protein (g per 100g)",
            "final_category": "Category",
            "product_name_clean": "Product",
            "brand_display": "Brand",
        },
    )

    fig_scatter.add_vline(
        x=LOW_SUGAR,
        line_dash="dash",
        line_color="#E74C3C",
        line_width=1.5,
        annotation_text=f"Sugar threshold ({LOW_SUGAR}g)",
        annotation_font_size=10,
        annotation_font_color="#E74C3C",
        annotation_position="top right",
    )
    fig_scatter.add_hline(
        y=HIGH_PROTEIN,
        line_dash="dash",
        line_color="#1B4F72",
        line_width=1.5,
        annotation_text=f"Protein threshold ({HIGH_PROTEIN}g)",
        annotation_font_size=10,
        annotation_font_color="#1B4F72",
        annotation_position="top right",
    )
    fig_scatter.add_shape(
        type="rect",
        x0=0,
        x1=LOW_SUGAR,
        y0=HIGH_PROTEIN,
        y1=plot_df["proteins_100g"].max() * 1.05,
        fillcolor="#1B4F72",
        opacity=0.06,
        line_width=0,
    )
    fig_scatter.add_annotation(
        x=LOW_SUGAR / 2,
        y=plot_df["proteins_100g"].max() * 0.98,
        text="Target Zone",
        showarrow=False,
        font=dict(size=10, color="#1B4F72"),
        bgcolor="rgba(27,79,114,0.08)",
        borderpad=4,
    )
    fig_scatter.update_layout(
        **PLOTLY_LAYOUT,
        title=dict(
            text="Nutrient Matrix: Sugar vs Protein",
            font=dict(size=14, color="#1C2833"),
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
        height=560,
        legend=dict(
            title=dict(text="Category", font=LEGEND_FONT),
            font=LEGEND_FONT,
            bgcolor="rgba(255,255,255,0.9)",
            bordercolor="#DDE3EC",
            borderwidth=1,
        ),
    )
    fig_scatter.update_traces(marker=dict(size=5))
    st.plotly_chart(fig_scatter, use_container_width=True)

    # ── PER-CATEGORY GRID ─────────────────────────────────────────
    if view == "All categories (coloured)" and len(selected_cats) > 1:
        st.markdown(
            '<div class="section-header">Per-Category Detail</div>',
            unsafe_allow_html=True,
        )

        grid_cats = selected_cats[:9]
        n_cols = 3
        n_rows = -(-len(grid_cats) // n_cols)

        fig_grid = make_subplots(
            rows=n_rows,
            cols=n_cols,
            subplot_titles=grid_cats,
            horizontal_spacing=0.08,
            vertical_spacing=0.12,
        )

        for i, cat in enumerate(grid_cats):
            row = i // n_cols + 1
            col = i % n_cols + 1
            sub = filtered[filtered["final_category"] == cat].dropna(
                subset=["sugars_100g", "proteins_100g"]
            )
            if len(sub) > 1500:
                sub = sub.sample(1500, random_state=42)

            colour = CATEGORY_PALETTE[ALL_CATEGORIES.index(cat) % len(CATEGORY_PALETTE)]

            fig_grid.add_trace(
                go.Scatter(
                    x=sub["sugars_100g"],
                    y=sub["proteins_100g"],
                    mode="markers",
                    marker=dict(size=4, color=colour, opacity=0.4),
                    name=cat,
                    showlegend=False,
                    hovertemplate=(
                        f"<b>{cat}</b><br>"
                        "Sugar: %{x:.1f}g<br>"
                        "Protein: %{y:.1f}g<extra></extra>"
                    ),
                ),
                row=row,
                col=col,
            )
            fig_grid.add_vline(
                x=LOW_SUGAR,
                line_dash="dash",
                line_color="#E74C3C",
                line_width=1,
                opacity=0.6,
                row=row,
                col=col,
            )
            fig_grid.add_hline(
                y=HIGH_PROTEIN,
                line_dash="dash",
                line_color="#1B4F72",
                line_width=1,
                opacity=0.6,
                row=row,
                col=col,
            )

        fig_grid.update_layout(
            **PLOTLY_LAYOUT,
            height=n_rows * 280,
            title=dict(text="Sugar vs Protein — Per Category", font=dict(size=13), x=0),
        )
        fig_grid.update_xaxes(
            **AXIS_STYLE,
            title_text="Sugar (g)",
            tickfont=AXIS_FONT,
            title_font=AXIS_TITLE_FONT,
        )
        fig_grid.update_yaxes(
            **AXIS_STYLE,
            title_text="Protein (g)",
            tickfont=AXIS_FONT,
            title_font=AXIS_TITLE_FONT,
        )
        st.plotly_chart(fig_grid, use_container_width=True)