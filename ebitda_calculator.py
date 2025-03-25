import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

# Set page layout
st.set_page_config(layout="wide")

# Custom CSS for input fields
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

# Title and inputs
st.title("MRA EBITDA Valuation Calculator")
st.markdown("### Your Info")
col1, col2 = st.columns([1, 1])
with col1:
    st.markdown('<p style="font-size: 16px; font-weight: bold;">Name</p>', unsafe_allow_html=True)
    name = st.text_input("Name", label_visibility="collapsed")
with col2:
    st.markdown('<p style="font-size: 16px; font-weight: bold;">Email</p>', unsafe_allow_html=True)
    email = st.text_input("Email", label_visibility="collapsed")

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
st.markdown("---")
st.subheader("Financial Information")
col1, col2 = st.columns([1, 1])
with col1:
    st.markdown('<p style="font-size: 16px; font-weight: bold;">Net Sales ($)</p>', unsafe_allow_html=True)
    net_sales_str = st.text_input("Net Sales ($)", value="", label_visibility="collapsed")
    st.markdown('<p style="font-size: 16px; font-weight: bold;">COGS ($)</p>', unsafe_allow_html=True)
    cogs_str = st.text_input("COGS ($)", value="", label_visibility="collapsed")
with col2:
    st.markdown('<p style="font-size: 16px; font-weight: bold;">Employee Cost ($)</p>', unsafe_allow_html=True)
    employee_cost_str = st.text_input("Employee Cost ($)", value="", label_visibility="collapsed")
    st.markdown('<p style="font-size: 16px; font-weight: bold;">Other Operating Cost ($)</p>', unsafe_allow_html=True)
    other_operating_cost_str = st.text_input("Other Operating Cost ($)", value="", label_visibility="collapsed")

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
    st.write("\u26a0\ufe0f **Enter values above to generate the pie chart.**")
elif ebitda < 0:
    st.error("\u26a0\ufe0f **EBITDA is negative. A pie chart cannot be generated.**")
else:
    st.subheader("EBITDA Margin Breakdown")

    values = [total_expenses, ebitda]
    labels = ["Total Operating Expense", "EBITDA"]
    colors = ['#2E86AB', '#F5B041']

    fig, ax = plt.subplots(figsize=(3, 3))
    wedges, texts, autotexts = ax.pie(
        values,
        labels=labels,
        colors=colors,
        autopct=make_autopct(values),
        startangle=90,
        wedgeprops=dict(width=0.4, edgecolor='white'),
        textprops=dict(color="black", fontsize=12),
    )

    ax.text(0, 0, f"{ebitda_margin:.0f}%", ha='center', va='center', fontsize=28, fontweight='bold', color='black')
    ax.set_title("EBITDA Margin", fontsize=20, fontweight='bold', pad=20)

    legend_labels = [f"{labels[i]}: ${values[i]:,}" for i in range(len(labels))]
    patches = [mpatches.Patch(color=colors[i], label=legend_labels[i]) for i in range(len(labels))]
    ax.legend(handles=patches, loc='lower center', bbox_to_anchor=(0.5, -0.2), ncol=1, frameon=False, fontsize=12)

    ax.axis('equal')
    plt.tight_layout()
    st.pyplot(fig)

# Owner Benefit inputs
st.subheader("Owner Benefit Calculation")
owner_inputs = {
    "Owner's Compensation": "",
    "Health Insurance": "",
    "Auto Expense": "",
    "Cellphone Expense": "",
    "Other Personal Expense": "",
    "Extraordinary Nonrecurring Expense": "",
    "Receipts for Owner Purchases": "",
    "Depreciation and Amortization": "",
    "Interest on Loan Payments": "",
    "Travel and Entertainment": "",
    "Donations": "",
    "Other 1": "",
    "Other 2": "",
    "Other 3": ""
}

cols = st.columns(2)
categories = {}
for i, (label, default) in enumerate(owner_inputs.items()):
    with cols[i % 2]:
        st.markdown(f'<p style="font-size: 16px; font-weight: bold;">{label} ($)</p>', unsafe_allow_html=True)
        categories[label] = st.text_input(f"{label} ($)", value=default, label_visibility="collapsed")

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
    st.warning("\u26a0\ufe0f **Enter values above to calculate multiple valuations.**")

# PDF Export
st.subheader("Export Results")

# Define data dictionary for PDF generation
data = {
    "Metric": [
        "Name",
        "Email",
        "Total Operating Expenses",
        "EBITDA",
        "EBITDA Margin",
        "Total Owner Benefit",
        "Valuation Base (EBITDA + Owner Benefit)",
        "Low Multiple (1.25x)",
        "Median Multiple (1.5x)",
        "High Multiple (2.0x)"
    ],
    "Value": [
        name,
        email,
        f"${total_expenses:,.0f}",
        f"${ebitda:,.0f}",
        f"{ebitda_margin:.0f}%",
        f"${total_owner_benefit:,.0f}",
        f"${valuation_base:,.0f}",
        f"${low_multiple:,.0f}",
        f"${median_multiple:,.0f}",
        f"${high_multiple:,.0f}"
    ]
}

def generate_pdf(data):
    buffer = BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter

    # Title
    pdf.setFont("Helvetica-Bold", 16)
    pdf.drawString(100, height - 50, "MRA EBITDA Valuation Report")

    y_position = height - 90

    # Draw each line
    for metric, value in zip(data["Metric"], data["Value"]):
        # Section headers in bold
        if "Name" in metric or "Owner" in metric or "Valuation Base" in metric:
            pdf.setFont("Helvetica-Bold", 12)
        else:
            pdf.setFont("Helvetica", 12)

        pdf.drawString(80, y_position, f"{metric}: {value}")
        y_position -= 20

        # Add extra spacing after major sections
        if "Margin" in metric or "Total Owner Benefit" in metric or "High Multiple" in metric:
            y_position -= 10

    pdf.save()
    buffer.seek(0)
    return buffer

# Generate PDF and provide download button
pdf_buffer = generate_pdf(data)
st.download_button(
    label="Download Results as PDF",
    data=pdf_buffer,
    file_name="ebitda_results.pdf",
    mime="application/pdf"
)
