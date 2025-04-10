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

# Page setup
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

# --- Functions ---
def send_email(to_email, pdf_buffer):
    sg = sendgrid.SendGridAPIClient(api_key=SENDGRID_API_KEY)
    message = Mail(
        from_email=SENDGRID_SENDER,
        to_emails=to_email,
        subject="Your MRA Seller's Discretionary Earnings (SDE) Valuation Report",
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

# --- UI Layout ---
st.image("images/MRA logo 9.2015-colorLG.jpg", width=400)
st.title("MRA Seller Discretionary Earnings Valuation Calculator")

col1, col2 = st.columns(2)
with col1:
    name = st.text_input("Name")
with col2:
    email = st.text_input("Email")

st.header("Financial Information")
income = st.number_input("Food & Beverage Income ($)", min_value=0)
purchases = st.number_input("F&B Purchases ($)", min_value=0)
labor = st.number_input("Salaries, Wages, Taxes & Benefits ($)", min_value=0)
operating_expenses = st.number_input("Operating Expenses ($)", min_value=0)

total_expenses = purchases + labor + operating_expenses
sde = income - total_expenses
sde_margin = (sde / income) * 100 if income else 0

st.header("Adjustments to Seller Discretionary Earnings")
owners_comp = st.number_input("Owner's Compensation", min_value=0)
health_insurance = st.number_input("Health Insurance", min_value=0)
auto_expense = st.number_input("Auto Expense", min_value=0)
cell_expense = st.number_input("Cell Phone Expense", min_value=0)
other_personal = st.number_input("Other Personal Expense", min_value=0)
extraordinary_expense = st.number_input("Extraordinary Nonrecurring Expense", min_value=0)
receipts_owner_purchases = st.number_input("Receipts for Owner Purchases", min_value=0)
depreciation_amortization = st.number_input("Depreciation and Amortization", min_value=0)
interest_loans = st.number_input("Interest on Loan Payments", min_value=0)
travel_entertainment = st.number_input("Travel and Entertainment", min_value=0)
donations = st.number_input("Donations", min_value=0)
family_salaries = st.number_input("Family Salaries", min_value=0)
occupancy_adjustment = st.number_input("Occupancy Cost Adjustments", min_value=0)
other1 = st.number_input("Other", min_value=0)
other2 = st.number_input("Other (Additional)", min_value=0)

# Total Owner Benefits
total_adjustments = (owners_comp + health_insurance + auto_expense + cell_expense + other_personal + 
    extraordinary_expense + receipts_owner_purchases + depreciation_amortization + interest_loans + 
    travel_entertainment + donations + family_salaries + occupancy_adjustment + other1 + other2)

net_profit_loss = sde + total_adjustments

# Valuation Multiples (Fixed SDE for valuation section)
_fixed_sde_for_multiples = 86729
valuation_1_5x = _fixed_sde_for_multiples * 1.5
valuation_2_0x = _fixed_sde_for_multiples * 2.0
valuation_2_5x = _fixed_sde_for_multiples * 2.5

# --- PDF Generation ---
pdf_buffer = BytesIO()
pdf = canvas.Canvas(pdf_buffer, pagesize=letter)
pdf.setFont("Helvetica-Bold", 16)
pdf.drawString(100, 750, "MRA SDE Valuation Report")
y = 720

def write_line(text):
    global y
    pdf.setFont("Helvetica", 12)
    pdf.drawString(80, y, text)
    y -= 20

write_line(f"Name: {name}")
write_line(f"Email: {email}")
write_line(f"Income: ${income:,.2f}")
write_line(f"Purchases: ${purchases:,.2f}")
write_line(f"Labor: ${labor:,.2f}")
write_line(f"Operating Expenses: ${operating_expenses:,.2f}")
write_line(f"Total Expenses: ${total_expenses:,.2f}")
write_line(f"SDE: ${sde:,.2f}")
write_line(f"SDE Margin: {sde_margin:.2f}%")
write_line(f"Total Owner Benefit: ${total_adjustments:,.2f}")
write_line(f"Net Profit/Loss: ${net_profit_loss:,.2f}")
write_line(f"Total Income Valuation: ${sde:,.2f}")
write_line(f"Valuation 1.5x: ${valuation_1_5x:,.2f}")
write_line(f"Valuation 2.0x: ${valuation_2_0x:,.2f}")
write_line(f"Valuation 2.5x: ${valuation_2_5x:,.2f}")

pdf.save()
pdf_buffer.seek(0)

# --- Download and Send Buttons ---
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
