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

# Function to send email
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
        response = sg.send(message)
        st.success("✅ Email sent successfully!")
    except Exception as e:
        st.error(f"❌ Email sending failed: {str(e)}")

# Function to save user info to Google Sheets
def save_to_google_sheets(name, email):
    values = [[name, email]]
    body = {"values": values}
    sheet.values().append(
        spreadsheetId=GCP_SHEET_ID,
        range="MRA Valuation Tool Users!A:B",
        valueInputOption="RAW",
        body=body
    ).execute()

# UI
st.image("images/MRA logo 9.2015-colorLG.jpg", width=400)
st.title("MRA Seller Discretionary Earnings Valuation Calculator")

col1, col2 = st.columns(2)
with col1:
    name = st.text_input("Name")
with col2:
    email = st.text_input("Email")

st.header("Financial Information")

revenue = st.number_input("Revenue", min_value=0)
operating_expenses = st.number_input("Operating Expenses", min_value=0)
owner_salary = st.number_input("Owner's Salary", min_value=0)
payroll_taxes = st.number_input("Payroll Taxes", min_value=0)
owner_health_insurance = st.number_input("Owner's Health Insurance", min_value=0)
owner_retirement = st.number_input("Owner's Retirement Contributions", min_value=0)
owner_personal_expenses = st.number_input("Owner's Personal Expenses", min_value=0)
owner_family_payroll = st.number_input("Owner's Family on Payroll", min_value=0)
rent_adjustment = st.number_input("Rent Adjustment", min_value=0)
other_addbacks = st.number_input("Other Addbacks", min_value=0)

# Calculations
net_profit = revenue - operating_expenses
total_addbacks = (owner_salary + payroll_taxes + owner_health_insurance +
                  owner_retirement + owner_personal_expenses + owner_family_payroll +
                  rent_adjustment + other_addbacks)
sde = net_profit + total_addbacks
sde_margin = (sde / revenue * 100) if revenue != 0 else 0
valuation_1_5x = sde * 1.5
valuation_2_0x = sde * 2.0
valuation_2_5x = sde * 2.5

# Export PDF
pdf_buffer = BytesIO()
pdf = canvas.Canvas(pdf_buffer, pagesize=letter)
pdf.drawString(100, 750, f"MRA SDE Valuation Report for {name}")
pdf.drawString(100, 720, f"Revenue: ${revenue:,.2f}")
pdf.drawString(100, 700, f"Operating Expenses: ${operating_expenses:,.2f}")
pdf.drawString(100, 680, f"Owner's Salary: ${owner_salary:,.2f}")
pdf.drawString(100, 660, f"Payroll Taxes: ${payroll_taxes:,.2f}")
pdf.drawString(100, 640, f"Owner's Health Insurance: ${owner_health_insurance:,.2f}")
pdf.drawString(100, 620, f"Owner's Retirement Contributions: ${owner_retirement:,.2f}")
pdf.drawString(100, 600, f"Owner's Personal Expenses: ${owner_personal_expenses:,.2f}")
pdf.drawString(100, 580, f"Owner's Family on Payroll: ${owner_family_payroll:,.2f}")
pdf.drawString(100, 560, f"Rent Adjustment: ${rent_adjustment:,.2f}")
pdf.drawString(100, 540, f"Other Addbacks: ${other_addbacks:,.2f}")
pdf.drawString(100, 500, f"Net Profit: ${net_profit:,.2f}")
pdf.drawString(100, 480, f"Total Addbacks: ${total_addbacks:,.2f}")
pdf.drawString(100, 460, f"Seller's Discretionary Earnings (SDE): ${sde:,.2f}")
pdf.drawString(100, 440, f"SDE Margin: {sde_margin:.2f}%")
pdf.drawString(100, 400, f"Valuation (1.5x SDE): ${valuation_1_5x:,.2f}")
pdf.drawString(100, 380, f"Valuation (2.0x SDE): ${valuation_2_0x:,.2f}")
pdf.drawString(100, 360, f"Valuation (2.5x SDE): ${valuation_2_5x:,.2f}")
pdf.save()
pdf_buffer.seek(0)

# Download button
st.download_button(
    label="Download Results as PDF",
    data=pdf_buffer,
    file_name="sde_valuation_report.pdf",
    mime="application/pdf"
)

# Send email button
if st.button("Send Results to Your Email"):
    if name and email:
        send_email(email, pdf_buffer)
        save_to_google_sheets(name, email)
    else:
        st.error("❌ Please fill out both Name and Email before sending.")
