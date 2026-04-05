"""
File: app.py
Project: The-Market-Gap-Analysis
Author: Zabdiel Addo
Email: zabdiel.addo@ashesi.edu.gh
Version: 2.0.0
"""

import pathlib

import pandas as pd
import streamlit as st

from views import (
    benchmark,
    market_gap,
    nutrient_matrix,
    overview,
    protein_sources,
    recommendation,
)

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
# INJECT CSS
# ─────────────────────────────────────────────

css_path = pathlib.Path(__file__).parent / "styles" / "main.css"
st.markdown(f"<style>{css_path.read_text()}</style>", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# CONSTANTS
# ─────────────────────────────────────────────

LOW_SUGAR = 6.0
HIGH_PROTEIN = 8.5

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
)

AXIS_STYLE = dict(
    showgrid=True,
    gridcolor="#D9E2EC",
    gridwidth=1,
    linecolor="#94A3B8",
    linewidth=1.4,
    tickcolor="#94A3B8",
)

AXIS_FONT = dict(size=13, color="#111827")
AXIS_TITLE_FONT = dict(size=14, color="#111827")
LEGEND_FONT = dict(size=10, color="#111827")
SMALL_AXIS_FONT = dict(size=10, color="#111827")

# ─────────────────────────────────────────────
# DATA LOADING
# ─────────────────────────────────────────────


@st.cache_data
def load_data():
    df = pd.read_csv("snack_gap_final.csv")

    for flag in ["in_target_zone", "high_demand", "opportunity"]:
        df[flag] = df[flag].astype(bool)

    df["brand_display"] = df["brands"].fillna("Unknown Brand")
    df["country_display"] = df["countries_tags"].fillna("Unknown")

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
    sugar_range = st.slider("Sugar (g/100g)", 0.0, 100.0, (0.0, 100.0), step=0.5)
    protein_range = st.slider("Protein (g/100g)", 0.0, 100.0, (0.0, 100.0), step=0.5)

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

# ─────────────────────────────────────────────
# SHARED KWARGS — passed into every page render
# ─────────────────────────────────────────────

shared = dict(
    PLOTLY_LAYOUT=PLOTLY_LAYOUT,
    AXIS_STYLE=AXIS_STYLE,
    AXIS_FONT=AXIS_FONT,
    AXIS_TITLE_FONT=AXIS_TITLE_FONT,
    LEGEND_FONT=LEGEND_FONT,
    LOW_SUGAR=LOW_SUGAR,
    HIGH_PROTEIN=HIGH_PROTEIN,
)

# ─────────────────────────────────────────────
# PAGE ROUTING
# ─────────────────────────────────────────────

if page == "Market Overview":
    overview.render(
        filtered, filtered_cat_stats, ALL_CATEGORIES, CATEGORY_PALETTE, **shared
    )

elif page == "Nutrient Matrix":
    nutrient_matrix.render(
        filtered, selected_cats, ALL_CATEGORIES, CATEGORY_PALETTE, **shared
    )

elif page == "Market Gap":
    market_gap.render(filtered, filtered_cat_stats, **shared)

elif page == "Protein Sources":
    protein_sources.render(
        filtered,
        selected_cats,
        PLOTLY_LAYOUT,
        AXIS_STYLE,
        AXIS_FONT,
        AXIS_TITLE_FONT,
        SMALL_AXIS_FONT,
        LOW_SUGAR,
        HIGH_PROTEIN,
    )

elif page == "Benchmark Shortlist":
    benchmark.render(filtered, **shared)

elif page == "Recommendation":
    recommendation.render(
        filtered,
        filtered_cat_stats,
        PLOTLY_LAYOUT,
        AXIS_STYLE,
        AXIS_FONT,
        AXIS_TITLE_FONT,
        LOW_SUGAR,
        HIGH_PROTEIN,
    )
