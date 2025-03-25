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

    fig, ax = plt.subplots(figsize=(6, 6))
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
}

cols = st.columns(2)
categories = {}
for i, (label, default) in enumerate(owner_inputs.items()):

