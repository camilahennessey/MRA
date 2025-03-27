import streamlit as st
import pandas as pd
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

# Logo
st.markdown('<div class="centered-image">', unsafe_allow_html=True)
st.image("images/MRA logo 9.2015-colorLG.jpg", width=500)
st.markdown('</div>', unsafe_allow_html=True)

# Title and Info
st.title("MRA Seller Discretionary Earnings Valuation Calculator")
st.markdown("### Your Info")
col1, col2 = st.columns([1, 1])
with col1:
    st.markdown('<p style="font-size: 16px; font-weight: bold;">Name</p>', unsafe_allow_html=True)
    name = st.text_input("Name", label_visibility="collapsed")
with col2:
    st.markdown('<p style="font-size: 16px; font-weight: bold;">Email</p>', unsafe_allow_html=True)
    email = st.text_input("Email", label_visibility="collapsed")

# Description
st.markdown("""
<div style='background-color:#f0f0f0; padding:15px; border-left:6px solid #333;'>
Seller Discretionary Earnings is a financial metric used to analyze the company’s operational performance in a given year/quarter. It provides a holistic idea of the company’s business at an operational level to every investor. It is also used as a level playing field to compare companies at an operational level and ascertain their operational profitability.<br><br>
It is the operating income (earnings) after subtracting it from the operational expenses. Operating income is the company’s revenues from business operations like sale of products/services. Operating expenses is the sum of the cost of goods sold, employee expenses, and, other expenses such as admin, marketing, and sales expenses. This tells you the total earnings of a company at the operating level.<br><br>
Earnings margin, is an indicative feature of the company’s overall health. However, to get the Earnings margin of a company—you need to know its net/profit/loss first. Based on the Seller Discretionary Earnings margin of a company, One can decide whether it is a worthy an investment.
</div>
""", unsafe_allow_html=True)

# Helpers
def parse_input(input_str):
    try:
        return float(input_str.replace(",", "").replace("(", "-").replace(")", ""))
    except:
        return 0.0

def make_autopct(values):
    def autopct(pct):
        total = sum(values)
        val = int(round(pct * total / 100.0))
        return f"${val:,}"
    return autopct

# Financial Inputs
st.markdown("---")
st.subheader("Financial Information")

col1, col2 = st.columns(2)
with col1:
    st.markdown('<p style="font-size: 16px; font-weight: bold;">Food & Beverage Income ($)</p>', unsafe_allow_html=True)
    income_str = st.text_input("Income", value="", label_visibility="collapsed")
    st.markdown('<p style="font-size: 16px; font-weight: bold;">F&B Purchases ($)</p>', unsafe_allow_html=True)
    purchases_str = st.text_input("Purchases", value="", label_visibility="collapsed")
with col2:
    st.markdown('<p style="font-size: 16px; font-weight: bold;">Salaries, Wages, Taxes & Benefits ($)</p>', unsafe_allow_html=True)
    labor_str = st.text_input("Labor", value="", label_visibility="collapsed")
    st.markdown('<p style="font-size: 16px; font-weight: bold;">Operating Expenses ($)</p>', unsafe_allow_html=True)
    operating_str = st.text_input("Operating", value="", label_visibility="collapsed")

income = parse_input(income_str)
purchases = parse_input(purchases_str)
labor = parse_input(labor_str)
operating = parse_input(operating_str)

total_expenses = purchases + labor + operating
sde = income - total_expenses
sde_margin = (sde / income) * 100 if income > 0 else 0

st.write(f"### Total Expenses: **${total_expenses:,.0f}**")
st.write(f"### Seller’s Discretionary Earnings (SDE): **${sde:,.0f}**")
st.markdown(f"**Earnings Margin:** {sde_margin:.0f}%")

# Donut Chart
if income == 0:
    st.warning("⚠️ Enter values above to generate the pie chart.")
elif sde < 0:
    st.error("⚠️ SDE is negative. A pie chart cannot be generated.")
else:
    st.subheader("SDE Breakdown")

    values = [total_expenses, sde]
    labels = ["Total Expenses", "SDE"]
    colors = ['#2E86AB', '#F5B041']

    fig, ax = plt.subplots(figsize=(2.8, 2.8))
    wedges, texts, autotexts = ax.pie(
        values,
        labels=labels,
        colors=colors,
        autopct=make_autopct(values),
        startangle=90,
        wedgeprops=dict(width=0.35, edgecolor='white'),
        textprops=dict(color="black", fontsize=8)
    )

    ax.text(0, 0, f"{round(sde_margin)}%", ha='center', va='center', fontsize=12, fontweight='bold', color='black')
    ax.set_title("SDE Margin", fontsize=12, fontweight='bold', pad=10)
    legend_labels = [f"{labels[i]}: ${values[i]:,}" for i in range(len(labels))]
    patches = [mpatches.Patch(color=colors[i], label=legend_labels[i]) for i in range(len(labels))]
    ax.legend(handles=patches, loc='lower center', bbox_to_anchor=(0.5, -0.35), ncol=1, frameon=False, fontsize=9)

    ax.axis('equal')
    plt.tight_layout()
    st.pyplot(fig)

# PDF Export
st.subheader("Export Results")

data = {
    "Metric": [
        "Name", "Email", "F&B Income", "Purchases", "Labor", "Operating Expenses",
        "Total Expenses", "SDE", "SDE Margin"
    ],
    "Value": [
        name, email, f"${income:,.0f}", f"${purchases:,.0f}", f"${labor:,.0f}", f"${operating:,.0f}",
        f"${total_expenses:,.0f}", f"${sde:,.0f}", f"{sde_margin:.0f}%"
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
        if "Adjusted SDE" in metric:
            y_position -= 10

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
