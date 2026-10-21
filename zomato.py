
import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path

# ==========================================
# 1. PAGE CONFIGURATION
# ==========================================
st.set_page_config(
    page_title="Zomato Analytics Dashboard",
    page_icon="🍽️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ==========================================
# 2. DASHBOARD THEME
# ==========================================
st.markdown("""
<style>
.stApp {
    background: linear-gradient(135deg, #101014, #211218);
    color: #FFFFFF;
}
[data-testid="stHeader"] {
    background: transparent;
}
[data-testid="stSidebar"] {
    display: none;
}
h1, h2, h3 {
    color: #FFFFFF !important;
}
.hero {
    background: linear-gradient(110deg, #7F1028, #E23744);
    padding: 26px;
    border-radius: 18px;
    margin-bottom: 22px;
    box-shadow: 0 8px 28px rgba(226,55,68,0.18);
}
.hero h1 {
    color: white !important;
    font-size: 34px;
    margin: 0;
}
.hero p {
    color: #FFE1E5;
    margin: 8px 0 0 0;
}
.filter-panel {
    background: #211920;
    border: 1px solid #49313A;
    border-radius: 16px;
    padding: 18px;
    margin-bottom: 20px;
}
.section-title {
    background: #281A21;
    border-left: 4px solid #E23744;
    border-radius: 6px;
    padding: 12px 15px;
    margin: 22px 0 14px 0;
    font-size: 19px;
    font-weight: bold;
    color: white;
}
.kpi-card {
    background: linear-gradient(145deg, #2A1D24, #19171C);
    border: 1px solid #49313A;
    padding: 18px;
    border-radius: 15px;
    min-height: 112px;
    box-shadow: 0 4px 16px rgba(0,0,0,0.2);
}
.kpi-label {
    color: #C6B5BD;
    font-size: 13px;
}
.kpi-value {
    color: #FF5364;
    font-size: 27px;
    font-weight: 800;
    margin-top: 10px;
}
.kpi-note {
    color: #AFA2A8;
    font-size: 11px;
    margin-top: 5px;
}
div[data-testid="stPlotlyChart"] {
    background: #19171C;
    border: 1px solid #382A31;
    border-radius: 14px;
    padding: 6px;
}
div[data-testid="stDataFrame"] {
    border: 1px solid #49313A;
    border-radius: 12px;
}
.stDownloadButton button {
    background: #E23744;
    color: white;
    border: none;
    border-radius: 9px;
    font-weight: bold;
}
.stDownloadButton button:hover {
    background: #B91C35;
    color: white;
}
hr {
    border-color: #49313A;
}
</style>
""", unsafe_allow_html=True)

# ==========================================
# 3. AUTOMATIC CSV LOADING
# ==========================================
import os
import pandas as pd

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

dataset_path = os.path.join(
    BASE_DIR,
    "Zomato restaurant dataset.csv"
)

if not os.path.exists(dataset_path):
    raise FileNotFoundError(
        f"Dataset not found at: {dataset_path}"
    )

df = pd.read_csv(dataset_path)

# ==========================================
# 4. CHECK REQUIRED COLUMNS
# ==========================================
required_columns = [
    "Restaurant ID",
    "Restaurant Name",
    "Country Code",
    "City",
    "Address",
    "Locality",
    "Locality Verbose",
    "Longitude",
    "Latitude",
    "Cuisines",
    "Average Cost for two",
    "Currency",
    "Has Table booking",
    "Has Online delivery",
    "Is delivering now",
    "Switch to order menu",
    "Price range",
    "Aggregate rating",
    "Rating color",
    "Rating text",
    "Votes"
]

missing_columns = [
    col for col in required_columns if col not in data.columns
]

if missing_columns:
    st.error(
        "Missing CSV columns: " + ", ".join(missing_columns)
    )
    st.stop()

# ==========================================
# 5. CLEAN DATA
# ==========================================
data = data.copy()

numeric_columns = [
    "Restaurant ID",
    "Country Code",
    "Longitude",
    "Latitude",
    "Average Cost for two",
    "Price range",
    "Aggregate rating",
    "Votes"
]

for col in numeric_columns:
    data[col] = pd.to_numeric(data[col], errors="coerce")

text_columns = [
    "Restaurant Name",
    "City",
    "Cuisines",
    "Currency",
    "Has Table booking",
    "Has Online delivery",
    "Is delivering now",
    "Rating text"
]

for col in text_columns:
    data[col] = data[col].replace(r"^\s*$", pd.NA, regex=True)

data = data.dropna(
    subset=["Restaurant ID", "Restaurant Name"]
)

if data.empty:
    st.error("The CSV contains no valid restaurant records.")
    st.stop()

# ==========================================
# 6. COUNTRY CODE TO COUNTRY NAME
# ==========================================
country_mapping = {
    1: "India",
    14: "Australia",
    30: "Brazil",
    37: "Canada",
    94: "Indonesia",
    148: "New Zealand",
    162: "Philippines",
    166: "Qatar",
    184: "Singapore",
    189: "South Africa",
    191: "Sri Lanka",
    208: "Turkey",
    214: "United Arab Emirates",
    215: "United Kingdom",
    216: "United States"
}

# Use Country if it already exists; otherwise create it.
if "Country" not in data.columns:
    data["Country"] = data["Country Code"].map(country_mapping)
else:
    data["Country"] = data["Country"].replace(
        r"^\s*$", pd.NA, regex=True
    )
    mapped_countries = data["Country Code"].map(country_mapping)
    data["Country"] = data["Country"].fillna(mapped_countries)

# Report unmapped country codes instead of silently hiding records.
unmapped_codes = sorted(
    data.loc[data["Country"].isna(), "Country Code"]
    .dropna()
    .unique()
    .tolist()
)

if unmapped_codes:
    st.warning(
        "Some country codes do not have a country-name mapping: "
        + ", ".join(map(str, unmapped_codes))
        + ". Add these codes to country_mapping if needed."
    )

# ==========================================
# 7. DASHBOARD HEADER
# ==========================================
st.markdown("""
<div class="hero">
    <h1>🍽️ Zomato Restaurant Analytics</h1>
    <p>
        Discover restaurant ratings, popular cuisines,
        pricing trends and customer preferences.
    </p>
</div>
""", unsafe_allow_html=True)

# ==========================================
# 8. COUNTRY AND CITY FILTERS ONLY
# ==========================================
st.markdown("""
<div style="text-align:center; padding:4px;">
    <h3 style="color:#FF5364 !important;">
        🎯 Explore & Filter Restaurants
    </h3>
    <p style="color:#B9AAB1;">
        Select a country and city to update the dashboard.
    </p>
</div>
""", unsafe_allow_html=True)

left_space, filter_area, right_space = st.columns([1, 3, 1])

with filter_area:
    st.markdown('<div class="filter-panel">', unsafe_allow_html=True)

    country_options = sorted(
        data["Country"].dropna().unique().tolist(),
        key=lambda x: str(x).lower()
    )

    selected_country = st.selectbox(
        "🌍 Country",
        options=["All"] + country_options,
        format_func=lambda x: "All Countries" if x == "All" else str(x),
        key="country_filter"
    )

    if selected_country == "All":
        city_source = data
    else:
        city_source = data[data["Country"] == selected_country]

    city_options = sorted(
        city_source["City"].dropna().unique().tolist(),
        key=lambda x: str(x).lower()
    )

    selected_city = st.selectbox(
        "📍 City",
        options=["All"] + city_options,
        format_func=lambda x: "All Cities" if x == "All" else str(x),
        key="city_filter"
    )

    st.markdown("</div>", unsafe_allow_html=True)

st.markdown("---")

# ==========================================
# 9. APPLY COUNTRY AND CITY FILTERS
# ==========================================
filtered = data.copy()

if selected_country != "All":
    filtered = filtered[filtered["Country"] == selected_country]

if selected_city != "All":
    filtered = filtered[filtered["City"] == selected_city]

if filtered.empty:
    st.warning(
        "No restaurants match the selected country and city. "
        "Please change your selections."
    )
    st.stop()

# ==========================================
# 10. KPI CALCULATIONS
# ==========================================
total_restaurants = filtered["Restaurant ID"].nunique()
average_rating = filtered["Aggregate rating"].mean()
total_votes = filtered["Votes"].fillna(0).sum()
average_cost = filtered["Average Cost for two"].mean()

delivery_yes = (
    filtered["Has Online delivery"]
    .astype(str).str.strip().str.lower()
    .isin(["yes", "true", "1"])
)

booking_yes = (
    filtered["Has Table booking"]
    .astype(str).str.strip().str.lower()
    .isin(["yes", "true", "1"])
)

delivery_percentage = delivery_yes.mean() * 100
booking_percentage = booking_yes.mean() * 100

def show_kpi(title, value, note):
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-label">{title}</div>
        <div class="kpi-value">{value}</div>
        <div class="kpi-note">{note}</div>
    </div>
    """, unsafe_allow_html=True)

# ==========================================
# 11. KPI CARDS
# ==========================================
st.markdown(
    '<div class="section-title">📊 Key Performance Indicators</div>',
    unsafe_allow_html=True
)

k1, k2, k3, k4, k5 = st.columns(5)

with k1:
    show_kpi("Total Restaurants", f"{total_restaurants:,}",
             "Unique restaurant IDs")

with k2:
    show_kpi(
        "Average Rating",
        f"{average_rating:.2f}" if pd.notna(average_rating) else "N/A",
        "Out of 5.00"
    )

with k3:
    show_kpi("Total Votes", f"{total_votes:,.0f}",
             "Customer engagement")

with k4:
    show_kpi(
        "Average Cost",
        f"{average_cost:,.0f}" if pd.notna(average_cost) else "N/A",
        "For two people; currency varies"
    )

with k5:
    show_kpi("Online Delivery", f"{delivery_percentage:.1f}%",
             "Restaurants offering delivery")

st.caption(
    f"Displaying {len(filtered):,} filtered records "
    f"from {len(data):,} valid dataset records."
)

# ==========================================
# 12. CHART STYLE HELPER
# ==========================================
COLORS = [
    "#E23744", "#FF8A65", "#F6BD60",
    "#7BDCB5", "#8E9AFF", "#C084FC",
    "#36CFC9", "#F472B6"
]

def style_chart(fig, height=370):
    fig.update_layout(
        template="plotly_dark",
        height=height,
        paper_bgcolor="#19171C",
        plot_bgcolor="#19171C",
        font=dict(color="#F3F4F6", size=12),
        margin=dict(l=20, r=20, t=60, b=25),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="left",
            x=0
        )
    )
    fig.update_xaxes(showgrid=False)
    fig.update_yaxes(gridcolor="#342A30")
    return fig

# ==========================================
# 13. CITY AND RATING CHARTS
# ==========================================
st.markdown(
    '<div class="section-title">📍 Restaurant Distribution & Ratings</div>',
    unsafe_allow_html=True
)

c1, c2 = st.columns(2)

with c1:
    city_data = (
        filtered.groupby("City")["Restaurant ID"]
        .nunique()
        .nlargest(10)
        .sort_values()
        .reset_index(name="Restaurants")
    )

    fig_city = px.bar(
        city_data,
        x="Restaurants",
        y="City",
        orientation="h",
        text="Restaurants",
        title="Top 10 Cities by Restaurant Count",
        color="Restaurants",
        color_continuous_scale=["#651426", "#E23744", "#FF8A65"]
    )
    fig_city.update_traces(textposition="outside")
    fig_city.update_layout(coloraxis_showscale=False)

    st.plotly_chart(style_chart(fig_city), use_container_width=True)

with c2:
    rating_data = filtered.dropna(subset=["Aggregate rating"])

    fig_rating = px.histogram(
        rating_data,
        x="Aggregate rating",
        nbins=20,
        title="Restaurant Rating Distribution",
        color_discrete_sequence=["#E23744"]
    )

    st.plotly_chart(style_chart(fig_rating), use_container_width=True)

# ==========================================
# 14. CUISINE AND PRICE CHARTS
# ==========================================


# ==========================================
# 15. RESTAURANT SERVICES
# ==========================================
st.markdown(
    '<div class="section-title">🛵 Restaurant Services</div>',
    unsafe_allow_html=True
)

c5, c6 = st.columns(2)

with c5:
    delivery_counts = (
        filtered["Has Online delivery"]
        .fillna("Unknown").astype(str)
        .value_counts()
        .rename_axis("Online Delivery")
        .reset_index(name="Restaurants")
    )

    fig_delivery = px.pie(
        delivery_counts,
        names="Online Delivery",
        values="Restaurants",
        hole=0.58,
        title="Online Delivery Availability",
        color_discrete_sequence=COLORS
    )
    fig_delivery.update_traces(textinfo="label+percent")

    st.plotly_chart(style_chart(fig_delivery), use_container_width=True)

with c6:
    booking_counts = (
        filtered["Has Table booking"]
        .fillna("Unknown").astype(str)
        .value_counts()
        .rename_axis("Table Booking")
        .reset_index(name="Restaurants")
    )

    fig_booking = px.bar(
        booking_counts,
        x="Table Booking",
        y="Restaurants",
        text="Restaurants",
        title="Table Booking Availability",
        color="Table Booking",
        color_discrete_sequence=COLORS
    )
    fig_booking.update_traces(textposition="outside")

    st.plotly_chart(style_chart(fig_booking), use_container_width=True)

# Line Chart: Average Rating by Price Range

st.markdown(
    '<div class="section-title">📈 Restaurant Rating Trends</div>',
    unsafe_allow_html=True
)

rating_data = (
    filtered.dropna(subset=["Price range", "Aggregate rating"])
    .groupby("Price range")["Aggregate rating"]
    .mean()
    .reset_index(name="Average Rating")
    .sort_values("Price range")
)

if not rating_data.empty:
    fig_line = px.line(
        rating_data,
        x="Price range",
        y="Average Rating",
        markers=True,
        title="Average Restaurant Rating by Price Range",
        labels={
            "Price range": "Price Range",
            "Average Rating": "Average Rating"
        }
    )

    fig_line.update_traces(line=dict(width=3))
    st.plotly_chart(style_chart(fig_line), use_container_width=True)
else:
    st.info("No rating data available for the selected filters.")



# ==========================================
# 17. TOP RATED RESTAURANTS
# ==========================================
st.markdown(
    '<div class="section-title">🏆 Top Rated Restaurants</div>',
    unsafe_allow_html=True
)

top_n = st.slider(
    "Number of restaurants",
    min_value=5,
    max_value=20,
    value=10
)

top_restaurants = (
    filtered.dropna(subset=["Aggregate rating"])
    .sort_values(
        ["Aggregate rating", "Votes"],
        ascending=[False, False]
    )
    [[
        "Restaurant Name",
        "Country",
        "City",
        "Cuisines",
        "Aggregate rating",
        "Rating text",
        "Votes",
        "Average Cost for two",
        "Currency"
    ]]
    .head(top_n)
)

st.dataframe(
    top_restaurants,
    use_container_width=True,
    hide_index=True
)

# ==========================================
# 18. SEARCH AND DATA TABLE
# ==========================================
st.markdown(
    '<div class="section-title">📋 Restaurant Dataset Explorer</div>',
    unsafe_allow_html=True
)

search = st.text_input(
    "🔎 Search restaurant name, city or cuisine"
)

table_data = filtered.copy()

if search.strip():
    mask = (
        table_data["Restaurant Name"]
        .fillna("").astype(str)
        .str.contains(search, case=False, na=False)
        |
        table_data["City"]
        .fillna("").astype(str)
        .str.contains(search, case=False, na=False)
        |
        table_data["Cuisines"]
        .fillna("").astype(str)
        .str.contains(search, case=False, na=False)
    )
    table_data = table_data[mask]

st.dataframe(
    table_data,
    use_container_width=True,
    hide_index=True
)

# ==========================================
# 19. DOWNLOAD FILTERED DATA
# ==========================================
st.markdown("---")

st.download_button(
    "⬇️ Download Filtered CSV",
    data=table_data.to_csv(index=False).encode("utf-8"),
    file_name="zomato_filtered_data.csv",
    mime="text/csv"
)

# ==========================================
# 20. FOOTER
# ==========================================
st.markdown("""
<p style="text-align:center;color:#AFA2A8;padding:15px;">
Zomato Restaurant Analytics Dashboard |
Python · Streamlit · Pandas · Plotly
</p>
""", unsafe_allow_html=True)

