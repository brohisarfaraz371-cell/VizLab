import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Online Retail Analysis", layout="wide")

@st.cache_data
def load_data():
    url = "https://archive.ics.uci.edu/ml/machine-learning-databases/00352/Online%20Retail.xlsx"
    df = pd.read_excel(url)
    df["InvoiceDate"] = pd.to_datetime(df["InvoiceDate"], errors="coerce")
    df = df.dropna(subset=["Description", "InvoiceDate"])
    df = df.drop_duplicates()

    df = df[
        (df["Quantity"] > 0) &
        (df["UnitPrice"] > 0) &
        (~df["InvoiceNo"].astype(str).str.startswith("C"))
    ].copy()

    df["Revenue"] = df["Quantity"] * df["UnitPrice"]
    df["Month"] = df["InvoiceDate"].dt.to_period("M").astype(str)
    return df

df = load_data()

st.title("Online Retail Sales Dashboard")
st.write("Explore cleaned retail transactions, product quantities, and revenue.")

countries = ["All Countries"] + sorted(df["Country"].unique().tolist())
selected_country = st.selectbox("Filter by country", countries)

filtered = df.copy()
if selected_country != "All Countries":
    filtered = filtered[filtered["Country"] == selected_country]

col1, col2 = st.columns(2)

col1.metric("Total Revenue", f"£{filtered['Revenue'].sum():,.2f}")
col2.metric("Transaction Records", f"{len(filtered):,}")

st.subheader("1. Monthly Revenue")
monthly = filtered.groupby("Month", as_index=False)["Revenue"].sum()
fig1 = px.line(
    monthly, x="Month", y="Revenue",
    markers=True, title="Revenue by Month"
)
st.plotly_chart(fig1, use_container_width=True)

st.subheader("2. Top 10 Products by Revenue")
products = (
    filtered.groupby("Description", as_index=False)["Revenue"]
    .sum()
    .nlargest(10, "Revenue")
    .sort_values("Revenue")
)
fig2 = px.bar(
    products, x="Revenue", y="Description",
    orientation="h", title="Top Products"
)
st.plotly_chart(fig2, use_container_width=True)

st.subheader("3. Quantity Distribution")
fig3 = px.histogram(
    filtered[filtered["Quantity"] <= filtered["Quantity"].quantile(0.99)],
    x="Quantity", nbins=40,
    title="Distribution of Quantities (up to 99th percentile)"
)
st.plotly_chart(fig3, use_container_width=True)

st.download_button(
    "Download Cleaned Data",
    data=filtered.to_csv(index=False).encode("utf-8"),
    file_name="cleaned_online_retail.csv",
    mime="text/csv"
)
