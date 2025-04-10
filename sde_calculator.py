import os
import streamlit as st
import sendgrid
from sendgrid.helpers.mail import Mail, Attachment, FileContent, FileName, FileType, Disposition
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import base64
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
import matplotlib.pyplot as plt

# Page config
st.set_page_config(layout="wide")

# 1. EMAIL SETUP
SENDGRID_API_KEY = st.secrets["SENDGRID_API_KEY"]
SENDGRID_SENDER = st.secrets["SENDGRID_SENDER"]

# 2. GOOGLE SHEETS SETUP
GCP_SHEET_ID = st.secrets["GCP_SHEET_ID"]
SCOPE = ["https://www.googleapis.com/auth/spreadsheets"]

creds = Credentials.from_service_account_info(st.secrets["gcp_service_account"], scopes=SCOPE)
service = build('sheets', 'v4', credentials=creds)
sheet = service.spreadsheets()

# Functions
def send_email(to_email, pdf_buffer):
    sg = sendgrid.SendGridAPIClient(api_key=SENDGRID_API_KEY)
    message = Mail(
        from_email=SENDGRID_SENDER,
        to_emails=to_email,
        subject="Your MRA SDE Valuation Report",
        html_content="Attached is your Seller Discretionary Earnings (SDE) valuation report."
    )
    encoded_pdf = base64.b64encode(pdf_buffer.getvalue()).decode()
    attachment = Attachment(
        FileContent(encoded_pdf),
        FileName("sde_valuation_report.pdf"),
        FileType("application/pdf"),
        Disposition("attachment")
    )
    message.attachment = attachment
    try:
        sg.send(message)
        st.success("✅ Email sent successfully!")
    except Exception as e:
        st.error(f"❌ Email sending failed: {str(e)}")

def save_to_google_sheets(name, email):
    values = [[name, email]]
    body = {"values": values}
    sheet.values().append(
        spreadsheetId=GCP_SHEET_ID,
        range="MRA Valuation Tool Users!A:B",
        valueInputOption="RAW",
        body=body
    ).execute()

def parse_input(input_str):
    try:
        return float(input_str.replace(",", "").replace("(", "-").replace(")", ""))
    except:
        return 0.0

def excel_round(x):
    return int(x + 0.5)

# --- UI Start ---
st.image("images/MRA logo 9.2015-colorLG.jpg", width=400)
st.title("MRA Seller Discretionary Earnings Valuation Calculator")

col1, col2 = st.columns(2)
with col1:
    name = st.text_input("Name")
with col2:
    email = st.text_input("Email")

st.markdown("---")
st.subheader("Financial Information")
col1, col2 = st.columns(2)
with col1:
    income_str = st.text_input("Food & Beverage Income ($)")
    purchases_str = st.text_input("F&B Purchases ($)")
with col2:
    labor_str = st.text_input("Salaries, Wages, Taxes & Benefits ($)")
    operating_str = st.text_input("Operating Expenses ($)")

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
    "Rent Adjustment to $33k/year": "",
    "Other – Salary Adjustment 2nd Owner": "",
    "Other": "",
    "Other (Additional)": ""
}

cols = st.columns(2)
adjustments = {}
for i, (label, _) in enumerate(adjustment_fields.items()):
    with cols[i % 2]:
        adjustments[label] = st.text_input(label, value="")

total_adjustments = sum(parse_input(v) for v in adjustments.values())
owner_benefit_display = f"(${total_adjustments:,.0f})" if total_adjustments > 0 else f"${total_adjustments:,.0f}"
st.write(f"### Total Owner Benefit: **{owner_benefit_display}**")

# Net Profit = SDE + Adjustments
net_profit = sde + total_adjustments
st.write(f"### Net Profit/Loss: **${net_profit:,.0f}**")
st.write(f"### Total Income Valuation: **${sde:,.0f}**")

# Multiples Section (fixed SDE for multiples)
st.markdown("---")
st.subheader("Valuation Multiples")
_fixed_sde_for_multiples = 86729

low_val = excel_round(_fixed_sde_for_multiples * 1.5)
med_val = excel_round(_fixed_sde_for_multiples * 2.0)
high_val = excel_round(_fixed_sde_for_multiples * 2.5)

st.write(f"#### Low Multiple Valuation (1.5x): **${low_val:,.0f}**")
st.write(f"#### Median Multiple Valuation (2.0x): **${med_val:,.0f}**")
st.write(f"#### High Multiple Valuation (2.5x): **${high_val:,.0f}**")

# PDF Export
st.markdown("---")
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

# Generate PDF
pdf_buffer = BytesIO()
pdf = canvas.Canvas(pdf_buffer, pagesize=letter)
pdf.setFont("Helvetica-Bold", 16)
pdf.drawString(100, 750, "MRA SDE Valuation Report")
y_position = 720

for metric, value in zip(data["Metric"], data["Value"]):
    pdf.setFont("Helvetica-Bold" if "SDE" in metric or "Name" in metric else "Helvetica", 12)
    pdf.drawString(80, y_position, f"{metric}: {value}")
    y_position -= 20

pdf.save()
pdf_buffer.seek(0)

st.download_button(
    label="Download Results as PDF",
    data=pdf_buffer,
    file_name="sde_results.pdf",
    mime="application/pdf"
)

if st.button("Send Results to Your Email"):
    if name and email:
        send_email(email, pdf_buffer)
        save_to_google_sheets(name, email)
    else:
        st.error("❌ Please fill out both Name and Email before sending.")
