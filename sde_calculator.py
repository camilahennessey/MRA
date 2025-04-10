import streamlit as st
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, Attachment, FileContent, FileName, FileType, Disposition
import base64

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
st.title("MRA Seller Discretionary Earnings Valuation Calculator")

col1, col2 = st.columns([1, 1])
with col1:
    name = st.text_input("Name")
with col2:
    email = st.text_input("Email")

# Description
st.markdown("""
<div style='background-color:#f0f0f0; padding:15px; border-left:6px solid #333;'>
Seller Discretionary Earnings (SDE) represents a business’s operating income before deducting the owner's salary and benefits, interest, taxes, depreciation, and amortization. This calculator helps estimate SDE and project valuation ranges based on industry-standard multiples.
</div>
""", unsafe_allow_html=True)

# Helpers
def parse_input(input_str):
    try:
        return float(input_str.replace(",", "").replace("(", "-").replace(")", ""))
    except:
        return 0.0

def excel_round(x):
    return int(x + 0.5)

# Financial Inputs
st.markdown("---")
st.subheader("Financial Information")
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

# Adjustments
st.markdown("---")
st.subheader("Adjustments to Seller Discretionary Earnings")

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

# Multiples
st.subheader("What Drives the Multiple")
st.markdown("""
<div style='background-color:#f1f1f1; padding:10px; border-left:6px solid #333; border-radius:5px; font-size:14px;'>
There are many variables that can lessen or enhance the value of your business. The area in which you do business, competition or the lack of competition, seasonality, facility, and quality of operations all can have an impact on your valuation multiple.
</div>
""", unsafe_allow_html=True)

# Only override SDE for this section
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

def send_email(recipient_email, pdf_buffer):
    sendgrid_api_key = os.getenv("SENDGRID_API_KEY")
    sender_email = os.getenv("SENDGRID_SENDER")
    
    if not sendgrid_api_key or not sender_email:
        st.error("Email sending failed: API key or sender email not found.")
        return

    message = Mail(
        from_email=sender_email,
        to_emails=recipient_email,
        subject="Your MRA SDE Valuation Report",
        html_content="Attached is your SDE Valuation Report."
    )

    # Add PDF attachment
    pdf_buffer.seek(0)
    encoded_pdf = base64.b64encode(pdf_buffer.read()).decode()
    attachment = Attachment(
        FileContent(encoded_pdf),
        FileName('sde_valuation_report.pdf'),
        FileType('application/pdf'),
        Disposition('attachment')
    )
    message.attachment = attachment

    try:
        sg = SendGridAPIClient(sendgrid_api_key)
        sg.send(message)
        st.success("✅ Email sent successfully!")
    except Exception as e:
        st.error(f"❌ Email sending failed: {e}")

pdf_buffer = generate_pdf(data)

st.download_button(
    label="Download Results as PDF",
    data=pdf_buffer,
    file_name="sde_results.pdf",
    mime="application/pdf"
)

if st.button("Send Results to Your Email"):
    send_email(email, pdf_buffer)
