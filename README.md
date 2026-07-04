https://jewellerydashboard-uzrkmy3zvpewiql6ts7kuw.streamlit.app/
# 💎 Luxe Jewelry — Business Intelligence Dashboard

An interactive business intelligence dashboard for a luxury jewelry shop built with **Streamlit**, powered by real CRM data covering Customers, Products, Transactions, and Wishlists.

---

## 📊 Dashboard Features

- **Overview** — Total Revenue, Transactions, Avg Order Value, Gross Profit, Unique Customers
- **Sales Analytics** — Revenue by Category, Material, Gemstone, and Discount Level
- **Customers** — Revenue by Segment, Wishlist overlap, Top 10 Customers by Spend
- **Products** — Top 10 Products by Revenue, Profit Margin % by Category
- **Reminders 🎂** — Upcoming Birthdays & Anniversaries for personalized outreach

---

## 📁 Dataset

The dataset is a synthetic CRM dataset for a luxury jewelry shop containing:

| Table | Records | Description |
|---|---|---|
| Customers | 100 | Name, Email, JoinDate, Birthdate, AnniversaryDate, Segment |
| Products | 100 | SKU, Category, Material, Gemstone, Price, Cost |
| Transactions | 100 | Purchase history with Channel and Discount info |
| Wishlists | 100 | Customer product wishlists |

All four tables are combined into a single denormalized dataset (`data.xlsx`) with **100 rows and 20 columns**. All monetary values are in **Indian Rupees (₹)** at a conversion rate of ₹94.55 per USD.

---

## 🛠️ Tech Stack

- **Python 3.11**
- **Streamlit** — Dashboard framework
- **Pandas** — Data processing
- **Plotly Express** — Interactive charts
- **OpenPyXL** — Excel file handling

---

## ⚙️ Run Locally

**Using Anaconda / Python:**
```bash
pip install -r requirements.txt
streamlit run app.py
```

**Using Docker:**
```bash
docker compose up --build
```
Then open `http://localhost:8501` in your browser.

---

## 📂 Project Structure

```
jewelry-dashboard/
├── app.py                  # Main Streamlit dashboard
├── data.xlsx               # Combined CRM dataset (100 rows × 20 columns)
├── requirements.txt        # Python dependencies
├── Dockerfile              # Docker container setup
├── docker-compose.yml      # Docker Compose config
└── README.md               # This file
```
