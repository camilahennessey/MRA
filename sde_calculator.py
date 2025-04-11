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

# --- PAGE SETUP ---
st.set_page_config(layout="wide")

# --- EMAIL SETUP ---
SENDGRID_API_KEY = st.secrets["SENDGRID_API_KEY"]
SENDGRID_SENDER = st.secrets["SENDGRID_SENDER"]

# --- GOOGLE SHEETS SETUP ---
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

# --- UI LAYOUT ---
st.image("images/MRA logo 9.2015-colorLG.jpg", width=400)
st.title("MRA Seller Discretionary Earnings Valuation Calculator")

col1, col2 = st.columns(2)
with col1:
    name = st.text_input("Name")
with col2:
    email = st.text_input("Email")

st.header("Financial Information")
income = st.number_input("Food & Beverage Income ($)", min_value=0, help="Total food & beverage revenue.")
purchases = st.number_input("F&B Purchases ($)", min_value=0, help="Cost of food & beverage inventory purchased.")
labor = st.number_input("Salaries, Wages, Taxes & Benefits ($)", min_value=0, help="Total employee salaries, taxes, and benefits.")
operating_expenses = st.number_input("Operating Expenses ($)", min_value=0, help="Other operating costs like rent, utilities, supplies.")

# --- SDE Calculation ---
total_expenses = purchases + labor + operating_expenses
sde = income - total_expenses
sde_margin = (sde / income) * 100 if income else 0

st.write(f"### Total Expenses: **${total_expenses:,.0f}**")
st.write(f"### Seller’s Discretionary Earnings (SDE): **${sde:,.0f}**")
st.write(f"### Earnings Margin: **{sde_margin:.0f}%**")

# --- DONUT CHART ---
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

# --- ADJUSTMENTS ---
st.header("Adjustments to Seller Discretionary Earnings")
owners_comp = st.number_input("Owner's Compensation", min_value=0, help="Owner's annual compensation from the business.")
health_insurance = st.number_input("Health Insurance", min_value=0, help="Owner's health insurance premiums.")
auto_expense = st.number_input("Auto Expense", min_value=0, help="Vehicle expenses reimbursed or paid by business.")
cell_expense = st.number_input("Cell Phone Expense", min_value=0, help="Owner's cell phone expenses paid by business.")
other_personal = st.number_input("Other Personal Expense", min_value=0, help="Other personal expenses paid by business.")
extraordinary_expense = st.number_input("Extraordinary Nonrecurring Expense", min_value=0, help="Unusual one-time expenses.")
receipts_owner_purchases = st.number_input("Receipts for Owner Purchases", min_value=0, help="Business-paid personal purchases.")
depreciation_amortization = st.number_input("Depreciation and Amortization", min_value=0, help="Non-cash expenses: depreciation and amortization.")
interest_loans = st.number_input("Interest on Loan Payments", min_value=0, help="Interest paid on loans.")
travel_entertainment = st.number_input("Travel and Entertainment", min_value=0, help="Travel, meals, entertainment for business purposes.")
donations = st.number_input("Donations", min_value=0, help="Charitable donations made by business.")
family_salaries = st.number_input("Family Salaries", min_value=0, help="Salaries paid to family members not critical to business.")
occupancy_adjustment = st.number_input("Occupancy Cost Adjustments", min_value=0, help="Adjustment if rent is above/below market.")
other1 = st.number_input("Other", min_value=0, help="Other non-operating adjustments.")
other2 = st.number_input("Other (Additional)", min_value=0, help="Additional adjustments not listed above.")

# --- FINAL CALCULATIONS ---
total_adjustments = (owners_comp + health_insurance + auto_expense + cell_expense + other_personal +
    extraordinary_expense + receipts_owner_purchases + depreciation_amortization + interest_loans +
    travel_entertainment + donations + family_salaries + occupancy_adjustment + other1 + other2)

net_profit_loss = sde + total_adjustments
valuation_1_5x = net_profit_loss * 1.5
valuation_2_0x = net_profit_loss * 2.0
valuation_2_5x = net_profit_loss * 2.5

st.header("Valuation Multiples")
st.write(f"#### Low Multiple Valuation (1.5x): **${valuation_1_5x:,.0f}**")
st.write(f"#### Median Multiple Valuation (2.0x): **${valuation_2_0x:,.0f}**")
st.write(f"#### High Multiple Valuation (2.5x): **${valuation_2_5x:,.0f}**")

# --- PDF Export ---
pdf_buffer = BytesIO()
pdf = canvas.Canvas(pdf_buffer, pagesize=letter)
pdf.setFont("Helvetica-Bold", 16)
pdf.drawString(100, 750, "MRA SDE Valuation Report")
y = 720
pdf.setFont("Helvetica", 12)
for line in [
    f"Name: {name}",
    f"Email: {email}",
    f"Total Expenses: ${total_expenses:,.2f}",
    f"SDE: ${sde:,.2f}",
    f"Earnings Margin: {sde_margin:.2f}%",
    f"Total Owner Benefit: ${total_adjustments:,.2f}",
    f"Net Profit/Loss: ${net_profit_loss:,.2f}",
    f"Low Valuation (1.5x): ${valuation_1_5x:,.2f}",
    f"Median Valuation (2.0x): ${valuation_2_0x:,.2f}",
    f"High Valuation (2.5x): ${valuation_2_5x:,.2f}",
]:
    pdf.drawString(80, y, line)
    y -= 20
pdf.save()
pdf_buffer.seek(0)

# --- Buttons ---
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
