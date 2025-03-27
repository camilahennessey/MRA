import streamlit as st
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

# Page setup
st.set_page_config(layout="wide")

# Custom styles
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

# Title and explanation
st.title("MRA Seller Discretionary Earnings Valuation Calculator")

with st.container():
    st.markdown("""
    <div style='background-color:#f0f0f0; padding:15px; border-radius:5px; border: 1px solid gray; font-size:16px;'>
    Seller Discretionary Earnings is a financial metric used to analyze the company’s operational performance in a given year/quarter. It provides a holistic idea of the company’s business at an operational level to every investor. It is also used as a level playing field to compare companies at an operational level and ascertain their operational profitability.
    <br><br>
    It is the operating income (earnings) after subtracting it from the operational expenses. Operating income is the company’s revenues from business operations like sale of products/services. Operating expenses is the sum of the cost of goods sold, employee expenses, and other expenses such as admin, marketing, and sales expenses. This tells you the total earnings of a company at the operating level.
    <br><br>
    Earnings margin is an indicative feature of the company’s overall health. However, to get the Earnings margin of a company—you need to know its net profit/loss first. Based on the Seller Discretionary Earnings margin of a company, one can decide whether it is a worthy an investment.
    </div>
    """, unsafe_allow_html=True)

# Operating Expense Note
st.markdown("""
<div style='background-color:#e8f4fc; padding:10px; border-left:6px solid #3498db; border-radius:5px; font-size:16px;'>
<strong>ℹ️ Operating Expense on your P+L should include:</strong><br>
Advertising, Auto Allowance, Bank Fees, Condo Fees, Credit Card Fees, Depreciation, Dues & Subscriptions, Insurance, Interest, Legal & Professional Fees, Licenses, Office Expense and Postage, Outside Services, Owner Compensation, Printing, Rents, Repairs and Maintenance, Restaurant Supplies, Telephone, Utilities.
</div>
""", unsafe_allow_html=True)

# Inputs
st.subheader("Adjustments to Seller Discretionary Earnings")

adjustment_fields = {
    "Owner's Compensation": "",
    "Health Insurance": "",
    "Auto Expense": "",
    "Cellphone Expense": "",
    "Other Personal Expense": "",
    "Extraordinary Nonrecurring Exp": "",
    "Receipts for Owner Purchases": "",
    "Depreciation and Amortization": "",
    "Interest on Loan Payments": "",
    "Travel and Entertainment": "",
    "Donations": "",
    "Rent Adjustment to $33k/year": "",
    "Other – Salary Adjustment 2nd Owner": "",
    "Other": ""
}

cols = st.columns(2)
values = {}

for i, (label, default) in enumerate(adjustment_fields.items()):
    with cols[i % 2]:
        st.markdown(f"<p style='font-size: 16px; font-weight: bold;'>{label}</p>", unsafe_allow_html=True)
        val = st.text_input(label, value=default, label_visibility="collapsed")
        val = val.replace("(", "-").replace(")", "")  # Handle parentheses as negative
        try:
            values[label] = float(val.replace(",", ""))
        except:
            values[label] = 0.0

total_sde = sum(values.values())
st.write(f"### Total SDE Adjustments: **${total_sde:,.0f}**")

# PDF Export
st.subheader("Export Results")

pdf_data = {
    "Metric": list(values.keys()) + ["Total Seller Discretionary Earnings"],
    "Value": [f"${v:,.0f}" for v in values.values()] + [f"${total_sde:,.0f}"]
}

def generate_pdf(data):
    buffer = BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter
    pdf.setFont("Helvetica-Bold", 16)
    pdf.drawString(100, height - 50, "MRA SDE Valuation Report")

    y = height - 90
    pdf.setFont("Helvetica", 12)
    for metric, value in zip(data["Metric"], data["Value"]):
        pdf.drawString(80, y, f"{metric}: {value}")
        y -= 20
        if "Total" in metric:
            y -= 10
    pdf.save()
    buffer.seek(0)
    return buffer

pdf_buffer = generate_pdf(pdf_data)

st.download_button(
    label="Download SDE Report as PDF",
    data=pdf_buffer,
    file_name="sde_valuation_report.pdf",
    mime="application/pdf"
)
