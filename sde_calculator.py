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

# --- PAGE SETUP ---
st.set_page_config(layout="wide")

# --- 1. EMAIL SETUP ---
SENDGRID_API_KEY = st.secrets["SENDGRID_API_KEY"]
SENDGRID_SENDER = st.secrets["SENDGRID_SENDER"]

# --- 2. GOOGLE SHEETS SETUP ---
GCP_SHEET_ID = st.secrets["GCP_SHEET_ID"]
SCOPE = ["https://www.googleapis.com/auth/spreadsheets"]
creds = Credentials.from_service_account_info(st.secrets["gcp_service_account"], scopes=SCOPE)
service = build('sheets', 'v4', credentials=creds)
sheet = service.spreadsheets()

# --- FUNCTIONS ---
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

# --- UI ---
st.image("images/MRA logo 9.2015-colorLG.jpg", width=400)
st.title("MRA Seller Discretionary Earnings Valuation Calculator")

col1, col2 = st.columns(2)
with col1:
    name = st.text_input("Name")
with col2:
    email = st.text_input("Email")

st.header("Financial Information")
revenue = st.number_input("Revenue", min_value=0)
expenses = st.number_input("Operating Expenses", min_value=0)

st.subheader("Addbacks")
owner_salary = st.number_input("Owner's Salary", min_value=0)
payroll_taxes = st.number_input("Payroll Taxes", min_value=0)
depreciation = st.number_input("Depreciation", min_value=0)
interest = st.number_input("Interest", min_value=0)
one_time_expenses = st.number_input("One-Time Expenses", min_value=0)

# --- CALCULATIONS ---
net_profit = revenue - expenses
addbacks = owner_salary + payroll_taxes + depreciation + interest + one_time_expenses
sde = net_profit + addbacks
sde_margin = (sde / revenue) * 100 if revenue > 0 else 0

valuation_15x = sde * 1.5
valuation_20x = sde * 2.0
valuation_25x = sde * 2.5

# --- EXPORT PDF ---
pdf_buffer = BytesIO()
pdf = canvas.Canvas(pdf_buffer, pagesize=letter)
pdf.drawString(100, 750, f"MRA SDE Valuation Report for {name}")
pdf.drawString(100, 730, f"Revenue: ${revenue:,.2f}")
pdf.drawString(100, 710, f"Expenses: ${expenses:,.2f}")
pdf.drawString(100, 690, f"Net Profit: ${net_profit:,.2f}")
pdf.drawString(100, 670, f"Total Addbacks: ${addbacks:,.2f}")
pdf.drawString(100, 650, f"Seller’s Discretionary Earnings (SDE): ${sde:,.2f}")
pdf.drawString(100, 630, f"SDE Margin: {sde_margin:.2f}%")
pdf.drawString(100, 610, f"Valuation @1.5x: ${valuation_15x:,.2f}")
pdf.drawString(100, 590, f"Valuation @2.0x: ${valuation_20x:,.2f}")
pdf.drawString(100, 570, f"Valuation @2.5x: ${valuation_25x:,.2f}")
pdf.save()
pdf_buffer.seek(0)

# --- DOWNLOAD OR SEND ---
st.download_button(
    label="Download Results as PDF",
    data=pdf_buffer,
    file_name="sde_valuation_report.pdf",
    mime="application/pdf"
)

if st.button("Send Results to Your Email"):
    if name and email:
        send_email(email, pdf_buffer)
        save_to_google_sheets(name, email)
    else:
        st.error("❌ Please fill out both Name and Email before sending.")
