import streamlit as st
import matplotlib.pyplot as plt
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import os
import base64
import sendgrid
from sendgrid.helpers.mail import Mail, Attachment, FileContent, FileName, FileType, Disposition
import gspread
from google.oauth2.service_account import Credentials

# === Streamlit Page Settings ===
st.set_page_config(layout="wide")

# === Load Secrets ===
SENDGRID_API_KEY = os.getenv("SENDGRID_API_KEY")
SENDGRID_SENDER = os.getenv("SENDGRID_SENDER")

# Load Google Service Account
service_account_info = {
    "type": os.getenv("GCP_TYPE"),
    "project_id": os.getenv("GCP_PROJECT_ID"),
    "private_key_id": os.getenv("GCP_PRIVATE_KEY_ID"),
    "private_key": os.getenv("GCP_PRIVATE_KEY").replace('\\n', '\n'),
    "client_email": os.getenv("GCP_CLIENT_EMAIL"),
    "client_id": os.getenv("GCP_CLIENT_ID"),
    "auth_uri": os.getenv("GCP_AUTH_URI"),
    "token_uri": os.getenv("GCP_TOKEN_URI"),
    "auth_provider_x509_cert_url": os.getenv("GCP_AUTH_PROVIDER_CERT_URL"),
    "client_x509_cert_url": os.getenv("GCP_CLIENT_CERT_URL"),
}

# Google Sheets Setup
SCOPE = ["https://www.googleapis.com/auth/spreadsheets"]
credentials = Credentials.from_service_account_info(service_account_info, scopes=SCOPE)
client = gspread.authorize(credentials)

# === Styling ===
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

# === Header ===
st.image("images/MRA logo 9.2015-colorLG.jpg", width=500)
st.title("MRA Seller Discretionary Earnings Valuation Calculator")

# === User Info ===
col1, col2 = st.columns([1, 1])
with col1:
    name = st.text_input("Name")
with col2:
    email = st.text_input("Email")

# === Description ===
st.markdown("""
<div style='background-color:#f0f0f0; padding:15px; border-left:6px solid #333;'>
Seller Discretionary Earnings (SDE) represents a business’s operating income before deducting the owner's salary and benefits, interest, taxes, depreciation, and amortization. This calculator helps estimate SDE and project valuation ranges based on industry-standard multiples.
</div>
""", unsafe_allow_html=True)

# === Helpers ===
def parse_input(input_str):
    try:
        return float(input_str.replace(",", "").replace("(", "-").replace(")", ""))
    except:
        return 0.0

def excel_round(x):
    return int(x + 0.5)

# === Financial Inputs ===
st.markdown("---")
st.subheader("Financial Information")

col1, col2 = st.columns(2)
with col1:
    income_str = st.text_input("Food & Beverage Income ($)", help="Total revenue from food and beverage sales.")
    purchases_str = st.text_input("F&B Purchases ($)", help="Cost of inventory purchased.")
with col2:
    labor_str = st.text_input("Salaries, Wages, Taxes & Benefits ($)", help="Employee wages, taxes, and benefits.")
    operating_str = st.text_input("Operating Expenses ($)", help="Rent, utilities, insurance, etc.")

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

# === Donut Chart ===
if income > 0 and sde >= 0:
    values = [total_expenses, sde]
    labels = ["Total Expenses", "SDE"]
    colors = ['#2E86AB', '#F5B041']
    fig, ax = plt.subplots(figsize=(3, 3))
    ax.pie(values, labels=labels, colors=colors, autopct=lambda p: f"${int(round(p * sum(values) / 100.0)):,}",
           startangle=90, wedgeprops=dict(width=0.35, edgecolor='white'), textprops=dict(color="black", fontsize=8))
    ax.text(0, 0, f"{round(sde_margin)}%", ha='center', va='center', fontsize=12, fontweight='bold')
    ax.set_title("SDE Margin", fontsize=12, fontweight='bold')
    st.pyplot(fig)

# === Adjustments ===
st.markdown("---")
st.subheader("Adjustments to Seller Discretionary Earnings")

adjustment_fields = {
    "Owner's Compensation": "Salary or personal compensation paid to the owner.",
    "Health Insurance": "Health insurance premiums.",
    "Auto Expense": "Auto-related expenses.",
    "Cellphone Expense": "Cellphone expenses.",
    "Other Personal Expense": "Other non-business expenses.",
    "Extraordinary Nonrecurring Expense": "One-time unusual expenses.",
    "Receipts for Owner Purchases": "Personal purchases through the business.",
    "Depreciation and Amortization": "Non-cash depreciation expenses.",
    "Interest on Loan Payments": "Loan interest payments.",
    "Travel and Entertainment": "Travel & entertainment expenses.",
    "Donations": "Charitable contributions.",
    "Rent Adjustment to $33k/year": "Fair market rent adjustment.",
    "Other – Salary Adjustment 2nd Owner": "Second owner's salary adjustment.",
    "Other": "Other owner adjustments.",
    "Other (Additional)": "Additional adjustments."
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

# === Multiples Section ===
st.subheader("What Drives the Multiple")
st.markdown("""
<div style='background-color:#f1f1f1; padding:10px; border-left:6px solid #333; border-radius:5px; font-size:14px;'>
There are many variables that can lessen or enhance the value of your business.
</div>
""", unsafe_allow_html=True)

_fixed_sde_for_multiples = 86729
low_val = excel_round(_fixed_sde_for_multiples * 1.5)
med_val = excel_round(_fixed_sde_for_multiples * 2.0)
high_val = excel_round(_fixed_sde_for_multiples * 2.5)

st.write(f"#### Low Multiple Valuation (1.5x): **${low_val:,.0f}**")
st.write(f"#### Median Multiple Valuation (2.0x): **${med_val:,.0f}**")
st.write(f"#### High Multiple Valuation (2.5x): **${high_val:,.0f}**")

# === PDF Export ===
st.subheader("Export Results")

def generate_pdf(data):
    buffer = BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter
    pdf.setFont("Helvetica-Bold", 16)
    pdf.drawString(100, height - 50, "MRA SDE Valuation Report")
    y_position = height - 90
    for metric, value in data.items():
        pdf.setFont("Helvetica-Bold" if "SDE" in metric or "Name" in metric else "Helvetica", 12)
        pdf.drawString(80, y_position, f"{metric}: {value}")
        y_position -= 20
    pdf.save()
    buffer.seek(0)
    return buffer

data = {
    "Name": name, "Email": email, "F&B Income": f"${income:,.0f}", "Purchases": f"${purchases:,.0f}",
    "Labor": f"${labor:,.0f}", "Operating Expenses": f"${operating:,.0f}", "Total Expenses": f"${total_expenses:,.0f}",
    "SDE": f"${sde:,.0f}", "SDE Margin": f"{sde_margin:.0f}%", "Total Owner Benefit": owner_benefit_display,
    "Net Profit/Loss": f"${net_profit:,.0f}", "Total Income Valuation": f"${sde:,.0f}",
    "Low Multiple Valuation (1.5x)": f"${low_val:,.0f}", "Median Multiple Valuation (2.0x)": f"${med_val:,.0f}",
    "High Multiple Valuation (2.5x)": f"${high_val:,.0f}"
}

pdf_buffer = generate_pdf(data)

st.download_button(
    label="Download Results as PDF",
    data=pdf_buffer,
    file_name="sde_results.pdf",
    mime="application/pdf"
)

# === Send Email ===
def send_email(recipient, pdf_buffer):
    try:
        if not recipient:
            st.error("Please enter a valid email.")
            return

        pdf_base64 = base64.b64encode(pdf_buffer.getvalue()).decode()
        sg = sendgrid.SendGridAPIClient(api_key=SENDGRID_API_KEY)

        attachment = Attachment(
            FileContent(pdf_base64),
            FileName("sde_results.pdf"),
            FileType("application/pdf"),
            Disposition("attachment")
        )

        email = Mail(
            from_email=SENDGRID_SENDER,
            to_emails=recipient,
            subject="Your MRA SDE Valuation Report",
            plain_text_content="Attached is your valuation report."
        )

        email.attachment = attachment
        sg.send(email)
        st.success("Email sent successfully!")

    except Exception as e:
        st.error(f"Email sending failed: {e}")

if st.button("Send Results to Your Email"):
    send_email(email, pdf_buffer)

# === Save to Google Sheets ===
if name and email:
    sheet = client.open("YOUR_SHEET_NAME_HERE").sheet1
    sheet.append_row([name, email, income, purchases, labor, operating, total_expenses, sde, sde_margin, total_adjustments, net_profit, sde])

