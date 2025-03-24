import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches 
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

# Streamlit styling
st.markdown("""
<style>
.centered-image {
    display: flex;
    justify-content: center;
}
input[type=number], input[type=text] {
    text-align: right;
}
</style>
""", unsafe_allow_html=True)

# Logo
st.markdown('<div class="centered-image">', unsafe_allow_html=True)
st.image("images/MRA logo 9.2015-colorLG.jpg", width=500)
st.markdown('</div>', unsafe_allow_html=True)

# Title and inputs
st.title("MRA EBITDA Valuation Calculator")
name = st.text_input("Enter Your Name")
email = st.text_input("Enter Your Email")

st.markdown("""
### What is EBITDA?  
EBITDA (Earnings Before Interest, Taxes, Depreciation, and Amortization) is a key financial metric used to analyze a restaurant's operational performance.  
It provides a holistic view of business profitability before accounting for non-operating expenses.

### Why is EBITDA Important?  
- Helps compare operational profitability across businesses.  
- Excludes tax and financing decisions to show core earnings.  
- Useful for investors evaluating a restaurant’s financial health.
""")

# Helper for comma input parsing
def parse_input(input_str):
    try:
        return float(input_str.replace(",", ""))
    except:
        return 0.0

# Helper function for autopct formatting
def make_autopct(values):
    def autopct(pct):
        total = sum(values)
        val = int(round(pct * total / 100.0))
        return f"${val:,}"
    return autopct

# Financial inputs
st.subheader("Enter Financial Information")
net_sales_str = st.text_input("Net Sales ($)", value="0")
cogs_str = st.text_input("Cost of Goods Sold (COGS) ($)", value="0")
employee_cost_str = st.text_input("Employee Cost ($)", value="0")
other_operating_cost_str = st.text_input("Other Operating Cost ($)", value="0")

net_sales = parse_input(net_sales_str)
cogs = parse_input(cogs_str)
employee_cost = parse_input(employee_cost_str)
other_operating_cost = parse_input(other_operating_cost_str)

# EBITDA Calculation
if net_sales > 0:
    total_expenses = cogs + employee_cost + other_operating_cost
    ebitda = net_sales - total_expenses
    ebitda_margin = (ebitda / net_sales) * 100
else:
    total_expenses, ebitda, ebitda_margin = 0, 0, 0

st.write(f"### Total Operating Expenses: **${total_expenses:,.0f}**")
st.write(f"### EBITDA: **${ebitda:,.0f}**")
st.write(f"### EBITDA Margin: **{ebitda_margin:.0f}%**")

# Donut Chart Visualization
if total_expenses == 0 and ebitda == 0:
    st.write("⚠️ **Enter values above to generate the pie chart.**")
elif ebitda < 0:
    st.error("⚠️ **EBITDA is negative. A pie chart cannot be generated.**")
else:
    st.subheader("EBITDA Margin Breakdown")

    # Data for chart
    values = [total_expenses, ebitda]
    labels = ["Total Operating Expense", "EBITDA"]
    colors = ['#2E86AB', '#F5B041']

    # Create the figure
    fig, ax = plt.subplots(figsize=(6, 6))

    wedges, texts, autotexts = ax.pie(
        values,
        labels=labels,
        colors=colors,
        autopct=make_autopct(values),  # FIXED AUTOPCT FUNCTION
        startangle=90,
        wedgeprops=dict(width=0.4, edgecolor='white'),
        textprops=dict(color="black", fontsize=10),
    )

    ax.text(0, 0, f"{ebitda_margin:.0f}%", ha='center', va='center',
            fontsize=24, fontweight='bold', color='black')

    ax.set_title("EBITDA Margin", fontsize=18, fontweight='bold', pad=20)

    legend_labels = [f"{labels[i]}: ${values[i]:,}" for i in range(len(labels))]
    patches = [mpatches.Patch(color=colors[i], label=legend_labels[i]) for i in range(len(labels))]
    ax.legend(handles=patches, loc='lower center', bbox_to_anchor=(0.5, -0.2),
              ncol=1, frameon=False, fontsize=11)

    ax.axis('equal')
    plt.tight_layout()
    st.pyplot(fig)

# Owner Benefit inputs
st.subheader("Owner Benefit Calculation")
categories = {
    "Owner’s Compensation": st.text_input("Owner’s Compensation ($)", value="0"),
    "Health Insurance": st.text_input("Health Insurance ($)", value="0"),
    "Auto Expense": st.text_input("Auto Expense ($)", value="0"),
    "Cellphone Expense": st.text_input("Cellphone Expense ($)", value="0"),
    "Other Personal Expense": st.text_input("Other Personal Expense ($)", value="0"),
    "Extraordinary Nonrecurring Expense": st.text_input("Extraordinary Nonrecurring Expense ($)", value="0"),
    "Receipts for Owner Purchases": st.text_input("Receipts for Owner Purchases ($)", value="0"),
    "Depreciation and Amortization": st.text_input("Depreciation and Amortization ($)", value="0"),
    "Interest on Loan Payments": st.text_input("Interest on Loan Payments ($)", value="0"),
    "Travel and Entertainment": st.text_input("Travel and Entertainment ($)", value="0"),
    "Donations": st.text_input("Donations ($)", value="0"),
    "Other 1": st.text_input("Other 1 ($)", value="0"),
    "Other 2": st.text_input("Other 2 ($)", value="0"),
    "Other 3": st.text_input("Other 3 ($)", value="0"),
}

total_owner_benefit = sum(parse_input(val) for val in categories.values())
st.write(f"### Total Owner Benefit: **${total_owner_benefit:,.0f}**")

# Valuation Base: EBITDA + Owner Benefit
valuation_base = ebitda + total_owner_benefit
st.write(f"### Valuation Base (EBITDA + Owner Benefit): **${valuation_base:,.0f}**")

# Multiples Section
st.subheader("Determining the Multiple")
st.markdown("""
### How Multiples Work  
Multiples help determine the estimated business valuation. Most common multiples in the restaurant industry range from **1.25x to 2.0x** of the EBITDA + Owner Benefit.
""")

low_multiple = valuation_base * 1.25
median_multiple = valuation_base * 1.5
high_multiple = valuation_base * 2.0

if valuation_base > 0:
    st.write(f"#### Low Multiple (1.25x): **${low_multiple:,.0f}**")
    st.write(f"#### Median Multiple (1.5x): **${median_multiple:,.0f}**")
    st.write(f"#### High Multiple (2.0x): **${high_multiple:,.0f}**")
else:
    st.warning("⚠️ **Enter values above to calculate multiple valuations.**")

# PDF Export
st.subheader("Export Results")
data = {
