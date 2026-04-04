"""
File: app.py
Project: The-Market-Gap-Analysis
File Created: Friday, 3rd April 2026 10:35:53 PM
Author: Zabdiel Addo
Email: zabdiel.addo@ashesi.edu.gh
Version: 1.0.0
Brief: <<brief>>
-----
Last Modified: Saturday, 4th April 2026 8:02:59 PM
Modified By: Zabdiel Addo
-----
Copyright ©2026 Zabdiel Addo
"""

"""
Sugar Trap — Snack Market Gap Analysis
Helix CPG Partners | Strategic Dashboard
"""

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from plotly.subplots import make_subplots

# ─────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────

st.set_page_config(
    page_title="Sugar Trap | Helix CPG",
    page_icon=None,
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────
# THEME & STYLE
# ─────────────────────────────────────────────

COLOURS = {
    "primary": "#1B4F72",
    "accent": "#E74C3C",
    "positive": "#1A7A4A",
    "neutral": "#5D6D7E",
    "warning": "#D4880A",
    "bg_card": "#F7F9FC",
    "border": "#DDE3EC",
    "text_main": "#1C2833",
    "text_sub": "#5D6D7E",
}

CATEGORY_PALETTE = [
    "#1B4F72",
    "#2E86C1",
    "#1A7A4A",
    "#27AE60",
    "#7D6608",
    "#D4AC0D",
    "#784212",
    "#CA6F1E",
    "#6C3483",
    "#A569BD",
    "#922B21",
    "#E74C3C",
    "#0E6655",
    "#17A589",
]

LOW_SUGAR = 6.0
HIGH_PROTEIN = 8.5

st.markdown(
    """
<style>
    /* Global font */
    html, body, [class*="css"] {
        font-family: 'Georgia', 'Times New Roman', serif;
    }
    h1, h2, h3 {
        font-family: 'Georgia', serif;
        color: #1C2833;
        letter-spacing: -0.3px;
    }

    /* Remove default Streamlit top padding */
    .block-container { padding-top: 1.8rem; padding-bottom: 2rem; }

    /* KPI cards */
    .kpi-card {
        background: #F7F9FC;
        border: 1px solid #DDE3EC;
        border-left: 4px solid #1B4F72;
        border-radius: 4px;
        padding: 1.1rem 1.3rem;
        margin-bottom: 0.5rem;
    }
    .kpi-label {
        font-size: 0.72rem;
        font-family: 'Arial', sans-serif;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        color: #5D6D7E;
        margin-bottom: 0.25rem;
    }
    .kpi-value {
        font-size: 1.85rem;
        font-weight: 700;
        color: #1B4F72;
        line-height: 1.1;
        font-family: 'Georgia', serif;
    }
    .kpi-sub {
        font-size: 0.75rem;
        color: #5D6D7E;
        margin-top: 0.2rem;
        font-family: 'Arial', sans-serif;
    }

    /* Section headers */
    .section-header {
        font-size: 0.7rem;
        font-family: 'Arial', sans-serif;
        text-transform: uppercase;
        letter-spacing: 0.12em;
        color: #5D6D7E;
        border-bottom: 1px solid #DDE3EC;
        padding-bottom: 0.4rem;
        margin-bottom: 1rem;
        margin-top: 1.5rem;
    }

    /* Insight box */
    .insight-box {
        background: #EAF2F8;
        border-left: 4px solid #1B4F72;
        border-radius: 4px;
        padding: 1.2rem 1.4rem;
        margin: 1rem 0;
        font-family: 'Georgia', serif;
        font-size: 0.95rem;
        color: #1C2833;
        line-height: 1.65;
    }
    .insight-box strong {
        color: #1B4F72;
    }

    /* Recommendation box */
    .rec-box {
        background: #FDFEFE;
        border: 1px solid #DDE3EC;
        border-top: 3px solid #1B4F72;
        border-radius: 4px;
        padding: 1.8rem 2rem;
        margin: 1rem 0;
    }
    .rec-title {
        font-size: 0.68rem;
        font-family: 'Arial', sans-serif;
        text-transform: uppercase;
        letter-spacing: 0.12em;
        color: #5D6D7E;
        margin-bottom: 0.6rem;
    }
    .rec-body {
        font-family: 'Georgia', serif;
        font-size: 1.05rem;
        color: #1C2833;
        line-height: 1.7;
    }

    /* Sidebar */
    [data-testid="stSidebar"] {
        background: #4a69b0;
        border-right: 1px solid #C7D2DE;
    }
    [data-testid="stSidebar"] .stMarkdown p {
        font-size: 0.78rem;
        color: #1C2833;
        font-family: 'Arial', sans-serif;
    }

    /* Caveat text */
    .caveat {
        font-size: 0.72rem;
        color: #7F8C8D;
        font-family: 'Arial', sans-serif;
        font-style: italic;
        margin-top: 0.3rem;
    }

    /* Table styling */
    .stDataFrame { border: 1px solid #DDE3EC; border-radius: 4px; }

    /* Divider */
    hr { border: none; border-top: 1px solid #DDE3EC; margin: 1.5rem 0; }
</style>
""",
    unsafe_allow_html=True,
)


# ─────────────────────────────────────────────
# DATA LOADING
# ─────────────────────────────────────────────


@st.cache_data
def load_data():
    df = pd.read_csv("snack_gap_final.csv")

    # Ensure boolean flags
    for flag in ["in_target_zone", "high_demand", "opportunity"]:
        df[flag] = df[flag].astype(bool)

    # Null-safe display fields
    df["brand_display"] = df["brands"].fillna("Unknown Brand")
    df["country_display"] = df["countries_tags"].fillna("Unknown")

    # Compute gap score per category
    cat_stats = (
        df.groupby("final_category")
        .agg(
            total_products=("final_category", "size"),
            target_zone_count=("in_target_zone", "sum"),
            target_zone_rate=("in_target_zone", "mean"),
            high_demand_rate=("high_demand", "mean"),
            opportunity_rate=("opportunity", "mean"),
            avg_sugar=("sugars_100g", "mean"),
            avg_protein=("proteins_100g", "mean"),
            avg_fat=("fat_100g", "mean"),
            avg_fiber=("fiber_100g", "mean"),
            avg_health_score=("health_score", "mean"),
        )
        .round(3)
    )
    cat_stats["gap_score"] = (
        cat_stats["high_demand_rate"] * (1 - cat_stats["target_zone_rate"])
    ).round(3)
    cat_stats["target_zone_share_pct"] = (cat_stats["target_zone_rate"] * 100).round(1)
    cat_stats["high_demand_pct"] = (cat_stats["high_demand_rate"] * 100).round(1)
    cat_stats["opportunity_pct"] = (cat_stats["opportunity_rate"] * 100).round(1)

    return df, cat_stats


df, cat_stats = load_data()
ALL_CATEGORIES = sorted(df["final_category"].unique())


# ─────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────

with st.sidebar:
    st.markdown("### Sugar Trap")
    st.markdown("**Helix CPG Partners**")
    st.markdown("Snack Market Gap Analysis")
    st.markdown("---")

    st.markdown("**Category Filter**")
    selected_cats = st.multiselect(
        label="Categories",
        options=ALL_CATEGORIES,
        default=ALL_CATEGORIES,
        label_visibility="collapsed",
    )

    st.markdown("**Nutrition Filters**")
    sugar_range = st.slider(
        "Sugar (g/100g)",
        min_value=0.0,
        max_value=100.0,
        value=(0.0, 100.0),
        step=0.5,
    )
    protein_range = st.slider(
        "Protein (g/100g)",
        min_value=0.0,
        max_value=100.0,
        value=(0.0, 100.0),
        step=0.5,
    )

    st.markdown("**Segment Filters**")
    show_target_only = st.checkbox("Target zone only", value=False)
    show_demand_only = st.checkbox("High demand only", value=False)
    show_opportunity = st.checkbox("Opportunity only", value=False)

    st.markdown("---")
    st.markdown(
        f"<p>Low sugar threshold: <strong>{LOW_SUGAR}g</strong><br>"
        f"High protein threshold: <strong>{HIGH_PROTEIN}g</strong><br>"
        f"Source: Open Food Facts<br>"
        f"n = {len(df):,} products</p>",
        unsafe_allow_html=True,
    )


# ─────────────────────────────────────────────
# APPLY FILTERS
# ─────────────────────────────────────────────

if not selected_cats:
    selected_cats = ALL_CATEGORIES

filtered = df[
    df["final_category"].isin(selected_cats)
    & df["sugars_100g"].between(sugar_range[0], sugar_range[1])
    & df["proteins_100g"].between(protein_range[0], protein_range[1])
].copy()

if show_target_only:
    filtered = filtered[filtered["in_target_zone"]]
if show_demand_only:
    filtered = filtered[filtered["high_demand"]]
if show_opportunity:
    filtered = filtered[filtered["opportunity"]]

filtered_cat_stats = cat_stats[cat_stats.index.isin(selected_cats)].copy()


# ─────────────────────────────────────────────
# PLOTLY DEFAULTS
# ─────────────────────────────────────────────
PLOTLY_LAYOUT = dict(
    font_family="Arial, sans-serif",
    font_color="#1C2833",
    paper_bgcolor="white",
    plot_bgcolor="white",
    margin=dict(l=50, r=30, t=50, b=50),
    hoverlabel=dict(
        bgcolor="white",
        bordercolor="#DDE3EC",
        font_size=12,
        font_family="Arial",
        font_color="#1C2833",
    ),
    legend=dict(
        font=dict(size=11, color="#1C2833"),
        title=dict(font=dict(size=11, color="#1C2833")),
    ),
)

AXIS_STYLE = dict(
    showgrid=True,
    gridcolor="#D9E2EC",
    gridwidth=1,
    linecolor="#AAB7C4",
    linewidth=1.2,
    tickfont=dict(size=12, color="#1C2833"),
    title_font=dict(size=13, color="#1C2833"),
)


# ─────────────────────────────────────────────
# NAVIGATION
# ─────────────────────────────────────────────

PAGES = [
    "Market Overview",
    "Nutrient Matrix",
    "Market Gap",
    "Protein Sources",
    "Benchmark Shortlist",
    "Recommendation",
]

st.markdown(
    '<p style="font-size:0.68rem;font-family:Arial;text-transform:uppercase;'
    'letter-spacing:0.12em;color:#5D6D7E;margin-bottom:0.3rem;">Navigation</p>',
    unsafe_allow_html=True,
)

page = st.radio(
    label="Page",
    options=PAGES,
    horizontal=True,
    label_visibility="collapsed",
)

st.markdown("<hr>", unsafe_allow_html=True)


# ═══════════════════════════════════════════════
# PAGE 1 — MARKET OVERVIEW
# ═══════════════════════════════════════════════

if page == "Market Overview":
    st.markdown("## Market Overview")
    st.markdown(
        "A high-level view of the snack market composition, nutritional profile, "
        "and the scale of the healthy snacking gap."
    )

    # KPI ROW
    n_total = len(filtered)
    n_target = filtered["in_target_zone"].sum()
    n_demand = filtered["high_demand"].sum()
    n_opp = filtered["opportunity"].sum()
    pct_target = n_target / n_total * 100 if n_total else 0
    pct_demand = n_demand / n_total * 100 if n_total else 0
    pct_opp = n_opp / n_total * 100 if n_total else 0

    top_gap_cat = (
        filtered_cat_stats["gap_score"].idxmax() if len(filtered_cat_stats) else "N/A"
    )

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

    st.markdown(
        '<div class="section-header">Category Distribution</div>',
        unsafe_allow_html=True,
    )

    col_l, col_r = st.columns([3, 2])

    with col_l:
        cat_counts = (
            filtered["final_category"]
            .value_counts()
            .reset_index()
            .rename(columns={"index": "Category", "final_category": "Products"})
        )
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
            xaxis=dict(**AXIS_STYLE, title="Number of Products"),
            yaxis=dict(**AXIS_STYLE, title=""),
            height=420,
            showlegend=False,
        )
        st.plotly_chart(fig_cat, use_container_width=True)

    with col_r:
        # Average sugar vs protein per category
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
            xaxis=dict(**AXIS_STYLE, title="g per 100g"),
            yaxis=dict(**AXIS_STYLE, title=""),
            barmode="overlay",
            height=420,
            legend=dict(orientation="h", y=-0.12, x=0, font=dict(size=10)),
        )
        st.plotly_chart(fig_avg, use_container_width=True)

    # Health score by category
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
        xaxis=dict(**AXIS_STYLE, title=""),
        yaxis=dict(**AXIS_STYLE, title="Health Score"),
        height=360,
        showlegend=False,
    )
    st.plotly_chart(fig_hs, use_container_width=True)


# ═══════════════════════════════════════════════
# PAGE 2 — NUTRIENT MATRIX
# ═══════════════════════════════════════════════

elif page == "Nutrient Matrix":
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

    # Quadrant lines
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

    # Target zone shading
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
        xaxis=dict(**AXIS_STYLE, title="Sugar (g per 100g)"),
        yaxis=dict(**AXIS_STYLE, title="Protein (g per 100g)"),
        height=560,
        legend=dict(
            title=dict(text="Category", font=dict(size=11)),
            font=dict(size=10),
            bgcolor="rgba(255,255,255,0.9)",
            bordercolor="#DDE3EC",
            borderwidth=1,
        ),
    )
    fig_scatter.update_traces(marker=dict(size=5))

    st.plotly_chart(fig_scatter, use_container_width=True)

    # Category grid
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
                        "<b>" + cat + "</b><br>"
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
        fig_grid.update_xaxes(**AXIS_STYLE, title_text="Sugar (g)")
        fig_grid.update_yaxes(**AXIS_STYLE, title_text="Protein (g)")

        st.plotly_chart(fig_grid, use_container_width=True)


# ═══════════════════════════════════════════════
# PAGE 3 — MARKET GAP
# ═══════════════════════════════════════════════

elif page == "Market Gap":
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

    with col_a:
        # Gap score bar
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
                hovertemplate=("<b>%{y}</b><br>Gap Score: %{x:.3f}<extra></extra>"),
            )
        )
        fig_gap.update_layout(
            **PLOTLY_LAYOUT,
            title=dict(
                text="Gap Score by Category", font=dict(size=13, color="#1C2833"), x=0
            ),
            xaxis=dict(
                **AXIS_STYLE, title="Gap Score (high demand × low healthy supply)"
            ),
            yaxis=dict(**AXIS_STYLE, title=""),
            height=420,
            showlegend=False,
        )
        st.plotly_chart(fig_gap, use_container_width=True)

    with col_b:
        # Bubble: high demand vs target zone share
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
            xaxis=dict(**AXIS_STYLE, title="High Demand Rate (%)"),
            yaxis=dict(**AXIS_STYLE, title="In Target Zone (%)"),
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

    # Full table
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

    # Three-way comparison for top category
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

        # Three-group scatter
        fig_3way = go.Figure()
        sample_all = cat_df.sample(min(3000, len(cat_df)), random_state=42)
        fig_3way.add_trace(
            go.Scatter(
                x=sample_all["sugars_100g"],
                y=sample_all["proteins_100g"],
                mode="markers",
                marker=dict(size=4, color="#BDC3C7", opacity=0.4),
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
            title=dict(text=f"{top_cat} — Gap Visualisation", font=dict(size=13), x=0),
            xaxis=dict(**AXIS_STYLE, title="Sugar (g per 100g)"),
            yaxis=dict(**AXIS_STYLE, title="Protein (g per 100g)"),
            height=440,
            legend=dict(
                font=dict(size=10),
                bgcolor="rgba(255,255,255,0.9)",
                bordercolor="#DDE3EC",
                borderwidth=1,
            ),
        )
        st.plotly_chart(fig_3way, use_container_width=True)


# ═══════════════════════════════════════════════
# PAGE 4 — PROTEIN SOURCES
# ═══════════════════════════════════════════════

elif page == "Protein Sources":
    st.markdown("## Protein Sources")
    st.markdown(
        "Analysis of which protein-bearing ingredients appear most frequently "
        "in products that already meet both the low sugar and high protein thresholds. "
        "These are the formulation benchmarks for the recommended new product."
    )

    import re

    good = filtered[
        (filtered["proteins_100g"] >= HIGH_PROTEIN)
        & (filtered["sugars_100g"] <= LOW_SUGAR)
        & filtered["ingredients_text_clean"].notna()
    ].copy()

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

    def has_term(text, terms):
        t = str(text).lower()
        return any(re.search(rf"\b{re.escape(k)}\b", t) for k in terms)

    protein_counts = {}
    for group, terms in PROTEIN_GROUPS.items():
        protein_counts[group] = (
            good["ingredients_text_clean"].apply(lambda x: has_term(x, terms)).sum()
        )

    ps_df = pd.Series(protein_counts).sort_values(ascending=False).reset_index()
    ps_df.columns = ["Source", "Product Count"]
    ps_df["Pct of Target-Zone Products"] = (
        ps_df["Product Count"] / len(good) * 100
    ).round(1)
    top_3 = ps_df.head(3)["Source"].tolist()

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

    st.markdown(
        '<div class="section-header">Protein Source Frequency</div>',
        unsafe_allow_html=True,
    )

    ps_plot = ps_df.sort_values("Product Count", ascending=True)
    bar_colours_ps = ["#1B4F72" if s in top_3 else "#A9C4D9" for s in ps_plot["Source"]]

    fig_ps = go.Figure()
    fig_ps.add_trace(
        go.Bar(
            x=ps_plot["Product Count"],
            y=ps_plot["Source"],
            orientation="h",
            marker_color=bar_colours_ps,
            text=ps_plot.apply(
                lambda r: (
                    f"{int(r['Product Count']):,}  ({r['Pct of Target-Zone Products']}%)"
                ),
                axis=1,
            ),
            textposition="outside",
            textfont=dict(size=10, color="#222528"),
            hovertemplate=("<b>%{y}</b><br>Products: %{x:,}<extra></extra>"),
        )
    )
    fig_ps.update_layout(
        **PLOTLY_LAYOUT,
        title=dict(
            text=f"Protein Sources in Target-Zone Products "
            f"(sugar \u2264 {LOW_SUGAR}g, protein \u2265 {HIGH_PROTEIN}g)",
            font=dict(size=13, color="#1C2833"),
            x=0,
        ),
        xaxis=dict(**AXIS_STYLE, title="Number of Products Containing Ingredient"),
        yaxis=dict(**AXIS_STYLE, title=""),
        height=420,
        showlegend=False,
    )
    st.plotly_chart(fig_ps, use_container_width=True)

    # By category
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
                .apply(lambda x: has_term(x, terms))
                .sum()
            )
            cat_source_rows.append(
                {
                    "Category": cat,
                    "Source": src,
                    "Count": count,
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
                    "<b>%{y}</b><br>"
                    "Source: %{x}<br>"
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
            xaxis=dict(tickfont=dict(size=10), title=""),
            yaxis=dict(tickfont=dict(size=10), title=""),
            height=400,
        )
        st.plotly_chart(fig_heat, use_container_width=True)


# ═══════════════════════════════════════════════
# PAGE 5 — BENCHMARK SHORTLIST
# ═══════════════════════════════════════════════

elif page == "Benchmark Shortlist":
    st.markdown("## Benchmark Shortlist")
    st.markdown(
        "The top-performing products already sitting in the target zone, "
        "ranked by composite health score then scan count. "
        "These are the products the R&D team should acquire, evaluate, and benchmark against."
    )

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

    st.markdown(
        '<div class="section-header">Shortlist Position on Nutrient Matrix</div>',
        unsafe_allow_html=True,
    )

    top20 = filtered[filtered["in_target_zone"]].nlargest(20, "health_score")
    all_sample = filtered.sample(min(5000, len(filtered)), random_state=42)

    fig_bench = go.Figure()

    # All products background
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

    # Target zone
    target_sample = filtered[filtered["in_target_zone"]]
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

    # Top 20
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
        xaxis=dict(**AXIS_STYLE, title="Sugar (g per 100g)"),
        yaxis=dict(**AXIS_STYLE, title="Protein (g per 100g)"),
        height=520,
        legend=dict(
            font=dict(size=10),
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


# ═══════════════════════════════════════════════
# PAGE 6 — RECOMMENDATION
# ═══════════════════════════════════════════════

elif page == "Recommendation":
    st.markdown("## Recommendation")
    st.markdown(
        "A data-driven brief for the R&D team, generated from the analysis pipeline. "
        "All figures update when sidebar filters are applied."
    )

    best_cat = (
        filtered_cat_stats["gap_score"].idxmax() if len(filtered_cat_stats) else "N/A"
    )

    if best_cat == "N/A":
        st.warning("No data available for the current filter selection.")
        st.stop()

    best = filtered_cat_stats.loc[best_cat]
    gap_products = filtered[
        (filtered["final_category"] == best_cat) & (filtered["opportunity"])
    ]

    avg_sugar_gap = gap_products["sugars_100g"].mean()
    avg_protein_gap = gap_products["proteins_100g"].mean()

    # Main recommendation
    st.markdown(
        f'<div class="rec-box">'
        f'<div class="rec-title">Market Recommendation — Helix CPG Partners</div>'
        f'<div class="rec-body">'
        f"Based on analysis of <strong>{len(filtered):,} snack products</strong>, "
        f"the biggest market opportunity is in "
        f"<strong>{best_cat}</strong>.<br><br>"
        f"This category has a high demand rate of "
        f"<strong>{best['high_demand_pct']:.0f}%</strong> — indicating strong, proven "
        f"consumer interest — but only "
        f"<strong>{best['target_zone_share_pct']:.1f}%</strong> of its products currently "
        f"meet the Low Sugar + High Protein nutritional threshold. "
        f"The {int(best['opportunity_pct'] * best['total_products'] / 100):,} opportunity "
        f"products in this category average "
        f"<strong>{avg_sugar_gap:.1f}g sugar</strong> and "
        f"<strong>{avg_protein_gap:.1f}g protein</strong> per 100g — "
        f"they are performing well commercially but failing nutritionally."
        f"<br><br>"
        f"<strong>The brief:</strong> Develop a {best_cat} product with "
        f"at least <strong>{HIGH_PROTEIN}g of protein</strong> and "
        f"less than <strong>{LOW_SUGAR}g of sugar</strong> per 100g. "
        f"This would position the product in a near-empty market quadrant "
        f"where consumer demand already exists but healthy supply is thin."
        f"</div>"
        f"</div>",
        unsafe_allow_html=True,
    )

    # Supporting metrics
    st.markdown(
        '<div class="section-header">Supporting Metrics</div>', unsafe_allow_html=True
    )

    m1, m2, m3, m4 = st.columns(4)
    metrics = [
        ("Gap Score", f"{best['gap_score']:.3f}", "higher = larger opportunity"),
        (
            "High Demand Rate",
            f"{best['high_demand_pct']:.0f}%",
            f"{int(best['total_products']):,} total products",
        ),
        (
            "Currently Healthy",
            f"{best['target_zone_share_pct']:.1f}%",
            "very few healthy options exist",
        ),
        (
            "Opportunity Products",
            f"{int(best['opportunity_pct'] * best['total_products'] / 100):,}",
            "high demand but not healthy",
        ),
    ]
    for col, (label, value, sub) in zip([m1, m2, m3, m4], metrics):
        with col:
            st.markdown(
                f'<div class="kpi-card">'
                f'<div class="kpi-label">{label}</div>'
                f'<div class="kpi-value">{value}</div>'
                f'<div class="kpi-sub">{sub}</div>'
                f"</div>",
                unsafe_allow_html=True,
            )

    # Formulation brief
    st.markdown(
        '<div class="section-header">Formulation Brief</div>', unsafe_allow_html=True
    )

    good_in_cat = filtered[
        (filtered["final_category"] == best_cat)
        & (filtered["in_target_zone"])
        & (filtered["ingredients_text_clean"].notna())
    ]

    import re

    PROTEIN_GROUPS = {
        "Pea / Pea Protein": ["pea protein", "pea"],
        "Soy / Soya": ["soy protein", "soy", "soya"],
        "Peanut": ["peanut", "peanuts"],
        "Whey": ["whey protein", "whey"],
        "Milk Protein": ["milk protein", "casein"],
        "Egg": ["egg white", "egg"],
        "Almond": ["almond"],
        "Oat": ["oat protein", "oats", "oat"],
    }

    form_counts = {}
    for src, terms in PROTEIN_GROUPS.items():
        form_counts[src] = (
            good_in_cat["ingredients_text_clean"]
            .apply(
                lambda x: any(
                    re.search(rf"\b{re.escape(t)}\b", str(x).lower()) for t in terms
                )
            )
            .sum()
        )

    form_df = pd.Series(form_counts).sort_values(ascending=False).reset_index()
    form_df.columns = ["Protein Source", "Target-Zone Products"]
    form_top3 = form_df.head(3)["Protein Source"].tolist()

    col_form, col_targets = st.columns([2, 3])

    with col_form:
        st.markdown("**Nutritional targets**")
        targets_table = pd.DataFrame(
            {
                "Nutrient": [
                    "Protein",
                    "Sugar",
                    "Current avg protein",
                    "Current avg sugar",
                ],
                "Target": [
                    f">= {HIGH_PROTEIN}g per 100g",
                    f"<= {LOW_SUGAR}g per 100g",
                    f"{avg_protein_gap:.1f}g (opportunity products)",
                    f"{avg_sugar_gap:.1f}g (opportunity products)",
                ],
            }
        )
        st.dataframe(targets_table, use_container_width=True, hide_index=True)

        st.markdown("**Recommended protein sources**")
        st.markdown(
            f"Based on existing target-zone {best_cat} products: "
            f"**{', '.join(form_top3) if form_top3 else 'insufficient data'}**"
        )

    with col_targets:
        if not form_df.empty and form_df["Target-Zone Products"].sum() > 0:
            form_plot = form_df[form_df["Target-Zone Products"] > 0].sort_values(
                "Target-Zone Products", ascending=True
            )
            fig_form = go.Figure()
            fig_form.add_trace(
                go.Bar(
                    x=form_plot["Target-Zone Products"],
                    y=form_plot["Protein Source"],
                    orientation="h",
                    marker_color=[
                        "#1B4F72" if s in form_top3 else "#A9C4D9"
                        for s in form_plot["Protein Source"]
                    ],
                    hovertemplate="<b>%{y}</b><br>Products: %{x}<extra></extra>",
                )
            )
            fig_form.update_layout(
                **PLOTLY_LAYOUT,
                title=dict(
                    text=f"Protein Sources in Healthy {best_cat} Products",
                    font=dict(size=12, color="#1C2833"),
                    x=0,
                ),
                xaxis=dict(**AXIS_STYLE, title="Number of Products"),
                yaxis=dict(**AXIS_STYLE, title=""),
                height=300,
                showlegend=False,
            )
            st.plotly_chart(fig_form, use_container_width=True)
        else:
            st.markdown(
                f'<p class="caveat">Insufficient ingredient data for {best_cat} '
                f"target-zone products to generate formulation recommendations.</p>",
                unsafe_allow_html=True,
            )

    # Full pipeline summary
    st.markdown(
        '<div class="section-header">Analysis Summary</div>', unsafe_allow_html=True
    )

    col_s1, col_s2 = st.columns(2)
    with col_s1:
        st.markdown("**Dataset**")
        summary_data = {
            "Metric": [
                "Total products",
                "Categories",
                "In target zone",
                "High demand",
                "Opportunity gap",
            ],
            "Value": [
                f"{len(filtered):,}",
                str(filtered["final_category"].nunique()),
                f"{filtered['in_target_zone'].sum():,} ({filtered['in_target_zone'].mean():.1%})",
                f"{filtered['high_demand'].sum():,} ({filtered['high_demand'].mean():.1%})",
                f"{filtered['opportunity'].sum():,} ({filtered['opportunity'].mean():.1%})",
            ],
        }
        st.dataframe(
            pd.DataFrame(summary_data),
            use_container_width=True,
            hide_index=True,
        )

    with col_s2:
        st.markdown("**Thresholds & Methodology**")
        method_data = {
            "Parameter": [
                "Low sugar threshold",
                "High protein threshold",
                "High demand definition",
                "Gap score formula",
                "Data source",
            ],
            "Value": [
                f"<= {LOW_SUGAR}g per 100g (WHO low-sugar benchmark: 5g)",
                f">= {HIGH_PROTEIN}g per 100g (industry standard: 10g)",
                "Above 75th percentile scan count",
                "high_demand_rate x (1 - target_zone_rate)",
                "Open Food Facts (openfoodfacts.org)",
            ],
        }
        st.dataframe(
            pd.DataFrame(method_data),
            use_container_width=True,
            hide_index=True,
        )
