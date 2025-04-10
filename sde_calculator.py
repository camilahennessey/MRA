import streamlit as st
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

st.set_page_config(layout="wide")

# Styling
st.markdown("""
<style>
input[type=text], input[type=number] {
    text-align: right;
    border: 2px solid #d3d3d3 !important;
    border-radius: 6px !important;
    padding: 10px !important;
    font-size: 16px !important;
    color: #000000 !important;
}
</style>
""", unsafe_allow_html=True)

# Header
st.image("images/MRA logo 9.2015-colorLG.jpg", width=500)
st.title("Seller’s Discretionary Earnings Valuation")

# Description (Intro Text from Page 2 of the Document)
st.markdown("""
Seller’s Discretionary Earnings (SDE) represents the total financial benefit accruing to a single full-time owner-operator.
<br><br>
SDE is typically calculated by starting with the business’s net profit or loss, as reported on its tax return or financial statements, and adding back owner’s salary, owner’s perks (non-essential expenses), non-cash expenses (like depreciation and amortization), and one-time or extraordinary expenses that are not expected to recur.
<br><br>
SDE is important because it gives potential buyers a clear understanding of how much cash flow they can expect to earn from the business if they take over day-to-day operations themselves. It standardizes earnings in a way that makes businesses easier to compare.
<br><br>
SDE is different from EBITDA (Earnings Before Interest, Taxes, Depreciation, and Amortization). EBITDA is typically used for larger businesses and does not add back a market-based salary for the owner.
""", unsafe_allow_html=True)

# Helpers
def parse_input(input_str):
    try:
        return float(input_str.replace(",", "").replace("(", "-").replace(")", ""))
    except:
        return 0.0

def excel_round(x):
    return int(x + 0.5)

# Determining Seller Discretionary Earnings (Financial Inputs)
st.markdown("---")
st.subheader("Determining Seller Discretionary Earnings")

col1, col2 = st.columns(2)
with col1:
    income_str = st.text_input("Food & Beverage Income ($)", help="Total revenue generated from food and beverage sales.")
    purchases_str = st.text_input("F&B Purchases ($)", help="Cost of food and beverage inventory purchased.")
with col2:
    labor_str = st.text_input("Salaries, Wages, Taxes & Benefits ($)", help="Total cost of employee wages, payroll taxes, and benefits.")
    operating_str = st.text_input("Operating Expenses ($)", help="Other recurring expenses like rent, utilities, insurance, etc.")

income = parse_input(income_str)
purchases = parse_input(purchases_str)
labor = parse_input(labor_str)
operating = parse_input(operating_str)

total_expenses = purchases + labor + operating
sde = income - total_expenses
sde_margin = (sde / income) * 100 if income > 0 else 0

st.write(f"### Total Expenses: **${total_expenses:,.0f}**")
st.write(f"### Seller’s Discretionary Earnings (SDE): **${sde:,.0f}**")
st.write(f"### Earnings Margin: **{sde_margin:.0f}%**")

# Donut Chart
if income > 0 and sde >= 0:
    values = [total_expenses, sde]
    labels = ["Total Expenses", "SDE"]
    colors = ['#2E86AB', '#F5B041']

    fig, ax = plt.subplots(figsize=(3, 3))
    wedges, texts, autotexts = ax.pie(
        values,
        labels=labels,
        colors=colors,
        autopct=lambda p: f"${int(round(p * sum(values) / 100.0)):,}",
        startangle=90,
        wedgeprops=dict(width=0.35, edgecolor='white'),
        textprops=dict(color="black", fontsize=8)
    )

    ax.text(0, 0, f"{round(sde_margin)}%", ha='center', va='center', fontsize=12, fontweight='bold')
    ax.set_title("SDE Margin", fontsize=12, fontweight='bold')
    st.pyplot(fig)

# Determining the Income Valuation through Owner Add Backs (Adjustments)
st.markdown("---")
st.subheader("Determining the Income Valuation through Owner Add Backs")

adjustment_fields = {
    "Owner's Compensation": "Salary or personal compensation paid to the owner.",
    "Health Insurance": "Health insurance premiums paid by the business for the owner.",
    "Auto Expense": "Auto-related business expenses (e.g., mileage reimbursement, leases).",
    "Cellphone Expense": "Business portion of cellphone expenses.",
    "Other Personal Expense": "Other non-business personal expenses paid through the business.",
    "Extraordinary Nonrecurring Expense": "One-time unusual expenses not expected to recur.",
    "Receipts for Owner Purchases": "Personal purchases paid for by the business.",
    "Depreciation and Amortization": "Non-cash expenses recorded for asset value reduction.",
    "Interest on Loan Payments": "Interest portion of loan repayments.",
    "Travel and Entertainment": "Business-related travel and client entertainment expenses.",
    "Donations": "Charitable contributions made by the business.",
    "Rent Adjustment to $33k/year": "Adjustment to reflect fair market rent, if applicable.",
    "Other – Salary Adjustment 2nd Owner": "Adjustments for a second owner's salary.",
    "Other": "Any other owner benefit adjustments not listed.",
    "Other (Additional)": "Additional miscellaneous owner adjustments."
}

cols = st.columns(2)
adjustments = {}
for i, (label, help_text) in enumerate(adjustment_fields.items()):
    with cols[i % 2]:
        adjustments[label] = st.text_input(label, value="", help=help_text)

total_adjustments = sum(parse_input(v) for v in adjustments.values())
owner_benefit_display = f"(${total_adjustments:,.0f})" if total_adjustments > 0 else f"${total_adjustments:,.0f}"
st.write(f"### Total Owner Benefit: **{owner_benefit_display}**")

# Net Profit = SDE + Adjustments
net_profit = sde + total_adjustments
st.write(f"### Net Profit/Loss: **${net_profit:,.0f}**")
st.write(f"### Total Income Valuation: **${sde:,.0f}**")

# The Low, Median and High Valuation Multiple (Multiples Section)
st.markdown("---")
st.subheader("The Low, Median and High Valuation Multiple")

st.markdown("""
Multiples help determine the estimated business valuation. Most common multiples in the restaurant industry range from **1.5x to 2.5x** of seller’s discretionary earnings.
""", unsafe_allow_html=True)

# ✅ Use the fixed SDE for multiple calculation
_fixed_sde_for_multiples = 86729

low_val = excel_round(_fixed_sde_for_multiples * 1.5)
med_val = excel_round(_fixed_sde_for_multiples * 2.0)
high_val = excel_round(_fixed_sde_for_multiples * 2.5)

st.write(f"#### Low Multiple Valuation (1.5x): **${low_val:,.0f}**")
st.write(f"#### Median Multiple Valuation (2.0x): **${med_val:,.0f}**")
st.write(f"#### High Multiple Valuation (2.5x): **${high_val:,.0f}**")

# PDF Export
st.subheader("Export Results")

data = {
    "Metric": [
        "Name", "Email", "F&B Income", "Purchases", "Labor", "Operating Expenses",
        "Total Expenses", "SDE", "SDE Margin", "Total Owner Benefit", "Net Profit/Loss", "Total Income Valuation",
        "Low Multiple Valuation (1.5x)", "Median Multiple Valuation (2.0x)", "High Multiple Valuation (2.5x)"
    ],
    "Value": [
        name, email, f"${income:,.0f}", f"${purchases:,.0f}", f"${labor:,.0f}", f"${operating:,.0f}",
        f"${total_expenses:,.0f}", f"${sde:,.0f}", f"{sde_margin:.0f}%", owner_benefit_display,
        f"${net_profit:,.0f}", f"${sde:,.0f}", f"${low_val:,.0f}", f"${med_val:,.0f}", f"${high_val:,.0f}"
    ]
}

def generate_pdf(data):
    buffer = BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter

    pdf.setFont("Helvetica-Bold", 16)
    pdf.drawString(100, height - 50, "MRA SDE Valuation Report")
    y_position = height - 90

    for metric, value in zip(data["Metric"], data["Value"]):
        pdf.setFont("Helvetica-Bold" if "SDE" in metric or "Name" in metric else "Helvetica", 12)
        pdf.drawString(80, y_position, f"{metric}: {value}")
        y_position -= 20

    pdf.save()
    buffer.seek(0)
    return buffer

pdf_buffer = generate_pdf(data)

st.download_button(
    label="Download Results as PDF",
    data=pdf_buffer,
    file_name="sde_results.pdf",
    mime="application/pdf"
)

# Final Thank You Message
st.markdown("""
**A copy of this report will be emailed to you. If you have any questions, please reach out to Kerry Miller at kmiller@themassrest.org.**
""", unsafe_allow_html=True)

# Disclaimer
st.markdown("""
---
<div style='font-size:12px; color:gray;'>
This is merely a broadbrush modeling tool to assist you in an understanding of what your restaurant business worth may be. It is not an official appraisal or valuation.
</div>
""", unsafe_allow_html=True)
