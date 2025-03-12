import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# Centering image using st.image() with CSS styling
st.markdown(
    """
    <style>
    .centered-image {
        display: flex;
        justify-content: center;
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.markdown('<div class="centered-image">', unsafe_allow_html=True)
st.image("images/MRA logo 9.2015-colorLG.jpg", width=500)
st.markdown('</div>', unsafe_allow_html=True)


# Section 1: Title & Explanation
st.title("MRA EBITDA Valuation Calculator")

st.markdown("""
### What is EBITDA?  
EBITDA (Earnings Before Interest, Taxes, Depreciation, and Amortization) is a key financial metric used to analyze a restaurant's operational performance.  
It provides a holistic view of business profitability before accounting for non-operating expenses.

### Why is EBITDA Important?  
- Helps compare operational profitability across businesses.  
- Excludes tax and financing decisions to show core earnings.  
- Useful for investors evaluating a restaurant’s financial health.
""")

# Section 2: EBITDA Calculator Inputs
st.subheader("Enter Financial Information")
net_sales = st.number_input("Net Sales ($)", min_value=0.00, format="%.2f")
cogs = st.number_input("Cost of Goods Sold (COGS) ($)", min_value=0.00, format="%.2f")
employee_cost = st.number_input("Employee Cost ($)", min_value=0.00, format="%.2f")
other_operating_cost = st.number_input("Other Operating Cost ($)", min_value=0.00, format="%.2f")

# Prevent NaN errors by ensuring calculations only happen if net_sales > 0
if net_sales > 0:
    total_expenses = cogs + employee_cost + other_operating_cost
    ebitda = net_sales - total_expenses
    ebitda_margin = (ebitda / net_sales) * 100
else:
    total_expenses, ebitda, ebitda_margin = 0, 0, 0

# Display results
st.write(f"### Total Operating Expenses: **${total_expenses:,.2f}**")
st.write(f"### EBITDA: **${ebitda:,.2f}**")
st.write(f"### EBITDA Margin: **{ebitda_margin:.2f}%**")

# Preventing Pie Chart NaN issues
if total_expenses == 0 and ebitda == 0:
    st.write("⚠️ **Enter values above to generate the pie chart.**")
else:
    st.subheader("EBITDA Margin Breakdown")
    fig, ax = plt.subplots(figsize=(6,6))
    labels = ["Total Operating Expenses", "EBITDA"]
    values = [total_expenses, ebitda]
    colors = ['#4C72B0', '#55A868']

    ax.pie(values, labels=labels, autopct='%1.1f%%', colors=colors, startangle=140)
    ax.set_title("EBITDA Margin Breakdown")
    st.pyplot(fig)
