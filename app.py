import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import date

st.set_page_config(page_title="Luxe Jewelry Dashboard", page_icon="💎", layout="wide")

PRIMARY  = "#8B5E3C"
ACCENT   = "#C9A876"
PALETTE  = ["#8B5E3C", "#C9A876", "#5C4033", "#D8C4A0", "#3E2723", "#A9745B"]

USD_TO_INR = 94.55   # rate as of 1 July 2026

def inr(value):
    """Format a number as Indian Rupees with ₹ symbol and Indian comma grouping."""
    if value >= 1_00_00_000:
        return f"₹{value/1_00_00_000:.2f} Cr"
    elif value >= 1_00_000:
        return f"₹{value/1_00_000:.2f} L"
    else:
        return f"₹{value:,.0f}"

st.markdown("""
<style>
.stMetric { background-color: #FAF6F0; border-radius: 10px; padding: 12px; }
[data-testid="stMetricLabel"] { font-weight: 600; }
</style>
""", unsafe_allow_html=True)

DATE_COLS = ["JoinDate", "Birthdate", "AnniversaryDate", "PurchaseDate"]

@st.cache_data
def load_data(file) -> pd.DataFrame:
    df = pd.read_excel(file) if str(file).endswith((".xlsx", ".xls")) else pd.read_csv(file)
    for c in DATE_COLS:
        df[c] = pd.to_datetime(df[c])
    # Convert prices to INR
    df["ProductPrice_INR"] = df["ProductPrice"] * USD_TO_INR
    df["ProductCost_INR"]  = df["ProductCost"]  * USD_TO_INR
    df["Revenue"] = df["ProductPrice_INR"] * df["Quantity"] * (1 - df["DiscountApplied"] / 100)
    df["Profit"]  = df["Revenue"] - (df["ProductCost_INR"] * df["Quantity"])
    df["PurchaseMonth"] = df["PurchaseDate"].dt.to_period("M").astype(str)
    return df

def days_until_next(dt: pd.Timestamp, today: pd.Timestamp) -> int:
    try:
        this_year = dt.replace(year=today.year)
    except ValueError:
        this_year = dt.replace(year=today.year, day=28)
    if this_year < today:
        try:
            this_year = this_year.replace(year=today.year + 1)
        except ValueError:
            this_year = this_year.replace(year=today.year + 1, day=28)
    return int((this_year - today).days)

# ── Sidebar: data source ──────────────────────────────────────────────────────
st.sidebar.title("💎 Luxe Jewelry")
st.sidebar.caption("Business Intelligence Dashboard")
st.sidebar.caption(f"💱 1 USD = ₹{USD_TO_INR} (as of 1 Jul 2026)")

uploaded = st.sidebar.file_uploader("Upload data (.xlsx or .csv)", type=["xlsx","csv"])
try:
    df = load_data(uploaded) if uploaded is not None else load_data("data.xlsx")
except FileNotFoundError:
    st.error("No data file found. Please upload your jewelry data using the sidebar.")
    st.stop()

# ── Sidebar: filters ──────────────────────────────────────────────────────────
st.sidebar.header("Filters")
min_date, max_date = df["PurchaseDate"].min().date(), df["PurchaseDate"].max().date()
date_range = st.sidebar.date_input("Purchase date range", value=(min_date, max_date),
                                   min_value=min_date, max_value=max_date)
start_date, end_date = (date_range if isinstance(date_range, tuple) and len(date_range)==2
                        else (min_date, max_date))

categories = st.sidebar.multiselect("Category",         sorted(df["Category"].unique()),        default=sorted(df["Category"].unique()))
materials  = st.sidebar.multiselect("Material",         sorted(df["Material"].unique()),         default=sorted(df["Material"].unique()))
gemstones  = st.sidebar.multiselect("Gemstone",         sorted(df["Gemstone"].unique()),         default=sorted(df["Gemstone"].unique()))
channels   = st.sidebar.multiselect("Channel",          sorted(df["Channel"].unique()),          default=sorted(df["Channel"].unique()))
segments   = st.sidebar.multiselect("Customer Segment", sorted(df["CustomerSegment"].unique()),  default=sorted(df["CustomerSegment"].unique()))

mask = (
    (df["PurchaseDate"].dt.date >= start_date) &
    (df["PurchaseDate"].dt.date <= end_date)   &
    df["Category"].isin(categories)            &
    df["Material"].isin(materials)             &
    df["Gemstone"].isin(gemstones)             &
    df["Channel"].isin(channels)               &
    df["CustomerSegment"].isin(segments)
)
fdf = df[mask].copy()

# ── Header ────────────────────────────────────────────────────────────────────
st.title("💎 Luxe Jewelry — Business Dashboard")
st.caption(f"Showing {len(fdf):,} of {len(df):,} transactions  •  All amounts in Indian Rupees (₹)")

if fdf.empty:
    st.warning("No transactions match the selected filters.")
    st.stop()

tab1, tab2, tab3, tab4, tab5 = st.tabs(
    ["📊 Overview", "💰 Sales Analytics", "👤 Customers", "🛍️ Products", "🎂 Reminders"]
)

# ── Tab 1: Overview ───────────────────────────────────────────────────────────
with tab1:
    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Total Revenue",      inr(fdf["Revenue"].sum()))
    c2.metric("Transactions",       f"{len(fdf):,}")
    c3.metric("Avg Order Value",    inr(fdf["Revenue"].mean()))
    c4.metric("Gross Profit",       inr(fdf["Profit"].sum()))
    c5.metric("Unique Customers",   f"{fdf['CustomerID'].nunique():,}")

    col1, col2 = st.columns(2)
    with col1:
        monthly = fdf.groupby("PurchaseMonth")["Revenue"].sum().reset_index()
        fig = px.line(monthly, x="PurchaseMonth", y="Revenue", markers=True,
                      title="Revenue Trend by Month (₹)",
                      labels={"Revenue": "Revenue (₹)"},
                      color_discrete_sequence=[PRIMARY])
        fig.update_layout(yaxis_tickprefix="₹", yaxis_tickformat=",.0f")
        st.plotly_chart(fig, use_container_width=True)
    with col2:
        chan = fdf.groupby("Channel")["Revenue"].sum().reset_index()
        fig = px.pie(chan, names="Channel", values="Revenue",
                     title="Revenue by Channel (₹)", hole=0.45,
                     color_discrete_sequence=PALETTE)
        st.plotly_chart(fig, use_container_width=True)

# ── Tab 2: Sales Analytics ────────────────────────────────────────────────────
with tab2:
    col1, col2 = st.columns(2)
    with col1:
        cat = fdf.groupby("Category")["Revenue"].sum().sort_values(ascending=False).reset_index()
        fig = px.bar(cat, x="Category", y="Revenue", title="Revenue by Category (₹)",
                     color="Category", color_discrete_sequence=PALETTE,
                     labels={"Revenue": "Revenue (₹)"})
        fig.update_layout(yaxis_tickprefix="₹", yaxis_tickformat=",.0f")
        st.plotly_chart(fig, use_container_width=True)
    with col2:
        mat = fdf.groupby("Material")["Revenue"].sum().sort_values(ascending=False).reset_index()
        fig = px.bar(mat, x="Material", y="Revenue", title="Revenue by Material (₹)",
                     color="Material", color_discrete_sequence=PALETTE,
                     labels={"Revenue": "Revenue (₹)"})
        fig.update_layout(yaxis_tickprefix="₹", yaxis_tickformat=",.0f")
        st.plotly_chart(fig, use_container_width=True)

    col3, col4 = st.columns(2)
    with col3:
        gem = fdf.groupby("Gemstone")["Revenue"].sum().reset_index()
        fig = px.pie(gem, names="Gemstone", values="Revenue",
                     title="Revenue by Gemstone (₹)",
                     color_discrete_sequence=PALETTE)
        st.plotly_chart(fig, use_container_width=True)
    with col4:
        disc = fdf.groupby("DiscountApplied")["Revenue"].sum().reset_index()
        fig = px.bar(disc, x="DiscountApplied", y="Revenue",
                     title="Revenue by Discount Level (%)",
                     labels={"Revenue": "Revenue (₹)", "DiscountApplied": "Discount (%)"},
                     color_discrete_sequence=[ACCENT])
        fig.update_layout(yaxis_tickprefix="₹", yaxis_tickformat=",.0f")
        st.plotly_chart(fig, use_container_width=True)

# ── Tab 3: Customers ──────────────────────────────────────────────────────────
with tab3:
    col1, col2 = st.columns(2)
    with col1:
        seg = fdf.groupby("CustomerSegment")["Revenue"].sum().reset_index()
        fig = px.pie(seg, names="CustomerSegment", values="Revenue",
                     title="Revenue by Customer Segment (₹)",
                     color_discrete_sequence=PALETTE)
        st.plotly_chart(fig, use_container_width=True)
    with col2:
        wl = fdf["OnWishlist"].value_counts().reset_index()
        wl.columns = ["OnWishlist", "Count"]
        fig = px.bar(wl, x="OnWishlist", y="Count",
                     title="Purchases also Wishlisted by Buyer",
                     color_discrete_sequence=[PRIMARY])
        st.plotly_chart(fig, use_container_width=True)

    st.subheader("Top Customers by Spend (₹)")
    top_cust = (
        fdf.groupby(["CustomerID","CustomerName","Email","CustomerSegment"])["Revenue"]
        .sum().reset_index()
        .sort_values("Revenue", ascending=False)
        .head(10)
    )
    top_cust["Revenue (₹)"] = top_cust["Revenue"].apply(inr)
    st.dataframe(top_cust[["CustomerName","Email","CustomerSegment","Revenue (₹)"]],
                 use_container_width=True, hide_index=True)

# ── Tab 4: Products ───────────────────────────────────────────────────────────
with tab4:
    st.subheader("Top Products by Revenue (₹)")
    top_prod = (
        fdf.groupby(["SKU","Category","Material","Gemstone"])["Revenue"]
        .sum().reset_index()
        .sort_values("Revenue", ascending=False)
        .head(10)
    )
    top_prod["Revenue (₹)"] = top_prod["Revenue"].apply(inr)
    st.dataframe(top_prod[["SKU","Category","Material","Gemstone","Revenue (₹)"]],
                 use_container_width=True, hide_index=True)

    st.subheader("Profit Margin % by Category")
    margin = fdf.groupby("Category")[["Profit","Revenue"]].sum().reset_index()
    margin["Margin %"] = margin.apply(
        lambda r: (r["Profit"] / r["Revenue"] * 100) if r["Revenue"] else 0, axis=1)
    fig = px.bar(margin, x="Category", y="Margin %",
                 title="Profit Margin % by Category",
                 color_discrete_sequence=[ACCENT])
    st.plotly_chart(fig, use_container_width=True)

# ── Tab 5: Reminders ──────────────────────────────────────────────────────────
with tab5:
    st.subheader("🎂 Upcoming Birthdays & Anniversaries")
    st.caption("Plan personalized outreach, gifting offers, or loyalty campaigns.")

    days_ahead = st.slider("Look ahead (days)", 1, 90, 30)
    today = pd.Timestamp(date.today())

    cust_unique = df.drop_duplicates(subset="CustomerID")[
        ["CustomerID","CustomerName","Email","Birthdate","AnniversaryDate","CustomerSegment"]
    ].copy()
    cust_unique["DaysToBirthday"]   = cust_unique["Birthdate"].apply(lambda d: days_until_next(d, today))
    cust_unique["DaysToAnniversary"]= cust_unique["AnniversaryDate"].apply(lambda d: days_until_next(d, today))

    bday  = cust_unique[cust_unique["DaysToBirthday"]    <= days_ahead].sort_values("DaysToBirthday")
    anniv = cust_unique[cust_unique["DaysToAnniversary"] <= days_ahead].sort_values("DaysToAnniversary")

    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"**🎉 Birthdays in the next {days_ahead} days** ({len(bday)})")
        st.dataframe(bday[["CustomerName","Email","Birthdate","DaysToBirthday","CustomerSegment"]],
                     hide_index=True, use_container_width=True)
    with col2:
        st.markdown(f"**💍 Anniversaries in the next {days_ahead} days** ({len(anniv)})")
        st.dataframe(anniv[["CustomerName","Email","AnniversaryDate","DaysToAnniversary","CustomerSegment"]],
                     hide_index=True, use_container_width=True)

# ── Raw data ──────────────────────────────────────────────────────────────────
st.divider()
with st.expander("View filtered transaction data"):
    display_df = fdf.copy()
    display_df["Revenue (₹)"] = display_df["Revenue"].apply(inr)
    display_df["Profit (₹)"]  = display_df["Profit"].apply(inr)
    st.dataframe(display_df, use_container_width=True)
