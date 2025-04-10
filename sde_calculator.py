import os
import streamlit as st
import sendgrid
from sendgrid.helpers.mail import Mail, Attachment, FileContent, FileName, FileType, Disposition
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import base64
import pandas as pd
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

# Simple inputs for demonstration
revenue = st.number_input("Enter Revenue", min_value=0)
expenses = st.number_input("Enter Expenses", min_value=0)

# Calculate SDE
sde = revenue - expenses

# Export PDF
pdf_buffer = BytesIO()
pdf = canvas.Canvas(pdf_buffer, pagesize=letter)
pdf.drawString(100, 750, f"MRA SDE Valuation Report for {name}")
pdf.drawString(100, 720, f"Revenue: ${revenue:,.2f}")
pdf.drawString(100, 700, f"Expenses: ${expenses:,.2f}")
pdf.drawString(100, 680, f"Seller’s Discretionary Earnings (SDE): ${sde:,.2f}")
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
