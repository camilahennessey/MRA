import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
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

# Helper for comma input parsing
def parse_input(input_str):
    try:
        return float(input_str.replace(",", ""))
    except:
        return 0.0

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

# Donut chart
# Pie Chart (Smaller Size)
if total_expenses == 0 and ebitda == 0:
    st.write("⚠️ **Enter values above to generate the pie chart.**")
elif ebitda < 0:
    st.error("⚠️ **EBITDA is negative. A pie chart cannot be generated.**")
else:
    st.subheader("EBITDA Margin Breakdown")

    values = [total_expenses, ebitda]
    labels = ["Total Operating Expense ($)", "EBITDA ($)"]
    colors = ['#4C72B0', '#F28E2B']

    fig, ax = plt.subplots(figsize=(3.5, 3.5))  # Smaller chart
    wedges, _, _ = ax.pie(
        values,
        colors=colors,
        startangle=90,
        wedgeprops=dict(width=0.4)
    )

    # Draw percentage inside donut
    ax.text(0, 0, f"{int(ebitda_margin)}%", ha='center', va='center', fontsize=16, fontweight='bold')

    # Title
    ax.set_title("EBITDA Margin", fontsize=14, fontweight='bold')

    # Legend below the chart
    ax.legend(wedges, labels, loc='lower center', bbox_to_anchor=(0.5, -0.2),
              ncol=2, frameon=False, fontsize=9)

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

# Multiple Valuations
st.subheader("Determining the Multiple")
st.markdown("""
### How Multiples Work  
Multiples help determine the estimated business valuation. Most common multiples in the restaurant industry range from **1.25x to 2.0x** of owner benefit.
""")

low_multiple = total_owner_benefit * 1.25
median_multiple = total_owner_benefit * 1.5
high_multiple = total_owner_benefit * 2.0

if total_owner_benefit > 0:
    st.write(f"#### Low Multiple (1.25x): **${low_multiple:,.0f}**")
    st.write(f"#### Median Multiple (1.5x): **${median_multiple:,.0f}**")
    st.write(f"#### High Multiple (2.0x): **${high_multiple:,.0f}**")
else:
    st.warning("⚠️ **Enter values above to calculate multiple valuations.**")

# Export PDF
st.subheader("Export Results")
data = {
    "Metric": ["Name", "Email", "Total Operating Expenses", "EBITDA", "EBITDA Margin", "Total Owner Benefit",
               "Low Multiple (1.25x)", "Median Multiple (1.5x)", "High Multiple (2.0x)"],
    "Value": [name, email, f"${total_expenses:,.0f}", f"${ebitda:,.0f}", f"{ebitda_margin:.0f}%", f"${total_owner_benefit:,.0f}",
              f"${low_multiple:,.0f}", f"${median_multiple:,.0f}", f"${high_multiple:,.0f}"]
}

def generate_pdf(data):
    buffer = BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter
    pdf.setFont("Helvetica", 12)
    pdf.drawString(100, height - 50, "MRA EBITDA Valuation Report")
    y_position = height - 100
    for metric, value in zip(data["Metric"], data["Value"]):
        pdf.drawString(100, y_position, f"{metric}: {value}")
        y_position -= 20
    pdf.save()
    buffer.seek(0)
    return buffer

pdf_buffer = generate_pdf(data)
st.download_button(label="Download Results as PDF", data=pdf_buffer, file_name="ebitda_results.pdf", mime="application/pdf")
