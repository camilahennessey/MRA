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
    try:
        sheet.values().append(
            spreadsheetId=GCP_SHEET_ID,
            range="MRA Valuation Tool Users!A:B",
            valueInputOption="RAW",
            body=body
        ).execute()
        st.success("✅ Thanks for using our tool!")
    except Exception as e:
        st.error(f"❌: {e}")

# --- UI LAYOUT ---
st.image("images/MRA logo 9.2015-colorLG.jpg", width=400)

st.title("MRA Seller’s Discretionary Earnings Valuation Calculator")

st.markdown("""
*This is merely a broadbrush modeling tool to assist you in an understanding of what your restaurant business worth may be. 
For definitive financial understanding of the valuation of your business, the assessment should be done by a Financial Professional certified and specializing in business valuations. 
The financial information you provide in this modeling tool is not captured and is for your eyes only.*
""")

col1, col2 = st.columns(2)
with col1:
    name = st.text_input("Name")
with col2:
    email = st.text_input("Email")

st.header("Determining Seller Discretionary Earnings")
st.markdown("Financial Information")

def number_input_comma(label, **kwargs):
    val = st.text_input(label, **kwargs)
    try:
        return int(val.replace(',', ''))
    except:
        return 0

income = number_input_comma("Food & Beverage Income ($)", placeholder="Enter value")
purchases = number_input_comma("F&B Purchases ($)", placeholder="Enter value")
labor = number_input_comma("Salaries, Wages, Taxes & Benefits ($)", placeholder="Enter value")
operating_expenses = number_input_comma("Operating Expenses ($)", placeholder="Enter value")

# --- SDE Calculation ---
total_expenses = purchases + labor + operating_expenses
sde = income - total_expenses
sde_margin = (sde / income) * 100 if income else 0

if income:
    st.write(f"### Total Expenses: **${total_expenses:,}**")
    st.write(f"### Seller’s Discretionary Earnings (SDE): **${sde:,}**")
    st.write(f"### Earnings Margin: **{sde_margin:.0f}%**")

# --- Donut Chart ---
if income and sde >= 0:
    values = [total_expenses, sde]
    labels = ["Total Expenses", "SDE"]
    colors = ['#2E86AB', '#F5B041']

    fig, ax = plt.subplots(figsize=(1, 1))
    ax.pie(
        values,
        labels=labels,
        colors=colors,
        autopct=lambda p: f"${int(round(p * sum(values) / 100.0)):,}",
        startangle=90,
        wedgeprops=dict(width=0.35, edgecolor='white'),
        textprops=dict(color="black", fontsize=6)
    )
    ax.text(0, 0, f"{round(sde_margin)}%", ha='center', va='center', fontsize=8, fontweight='bold')
    ax.set_title("SDE Margin", fontsize=8, fontweight='bold')
    st.pyplot(fig)

st.header("Determining the Income Valuation through Owner Add Backs")
st.markdown("Adjustments to Seller Discretionary Earnings")

owners_comp = number_input_comma("Owner's Compensation", placeholder="Enter value")
health_insurance = number_input_comma("Health Insurance", placeholder="Enter value")
auto_expense = number_input_comma("Auto Expense", placeholder="Enter value")
cell_expense = number_input_comma("Cell Phone Expense", placeholder="Enter value")
other_personal = number_input_comma("Other Personal Expense", placeholder="Enter value")
extraordinary_expense = number_input_comma("Extraordinary Nonrecurring Expense", placeholder="Enter value")
receipts_owner_purchases = number_input_comma("Receipts for Owner Purchases", placeholder="Enter value")
depreciation_amortization = number_input_comma("Depreciation and Amortization", placeholder="Enter value")
interest_loans = number_input_comma("Interest on Loan Payments", placeholder="Enter value")
travel_entertainment = number_input_comma("Travel and Entertainment", placeholder="Enter value")
donations = number_input_comma("Donations", placeholder="Enter value")
family_salaries = number_input_comma("Family Salaries", placeholder="Enter value")
occupancy_adjustment = number_input_comma("Occupancy Cost Adjustments", placeholder="Enter value")
other1 = number_input_comma("Other", placeholder="Enter value")
other2 = number_input_comma("Other (Additional)", placeholder="Enter value")

# --- Final Calculations ---
total_owner_benefit = sum([
    owners_comp, health_insurance, auto_expense, cell_expense, other_personal,
    extraordinary_expense, receipts_owner_purchases, depreciation_amortization,
    interest_loans, travel_entertainment, donations, family_salaries,
    occupancy_adjustment, other1, other2
])

net_profit_loss = income - total_expenses
total_income_valuation = net_profit_loss + total_owner_benefit
valuation_1_5x = total_income_valuation * 1.5
valuation_2_0x = total_income_valuation * 2.0
valuation_2_5x = total_income_valuation * 2.5

st.markdown(f"**Total Owner Benefit:** ${total_owner_benefit:,}")
st.markdown(f"**Net Profit/Loss:** ${net_profit_loss:,}")
st.markdown(f"**Total Income Valuation:** ${total_income_valuation:,}")

st.header("Valuation Multiples")
st.markdown("""
**The Low, Median and High Valuation Multiple**  
Once SDE is calculated, a multiplier is used to arrive at a business valuation, with the multiplier varying based on industry, growth outlook, an example would be if a liquor license is considered an asset of the business, also seasonality and competition.
""")

st.write(f"#### Low Multiple Valuation (1.5x): **${valuation_1_5x:,.0f}**")
st.write(f"#### Median Multiple Valuation (2.0x): **${valuation_2_0x:,.0f}**")
st.write(f"#### High Multiple Valuation (2.5x): **${valuation_2_5x:,.0f}**")

st.markdown("""
A copy of this report will be emailed to you.  
We hope this Restaurant Business Modeling tool has been a good exercise for you in understanding how valuations work and a model of a range in which your business may land in.  
If you have questions as to this methodology or would like advice or assistance in the valuation of your restaurant business, please reach out to Kerry Miller at [kmiller@themassrest.org](mailto:kmiller@themassrest.org).  
Based on your questions or needs, he will connect you with the correct subject matter expert.
""")

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
    f"Total Expenses: ${total_expenses:,}",
    f"SDE: ${sde:,}",
    f"Earnings Margin: {sde_margin:.0f}%",
    f"Total Owner Benefit: ${total_owner_benefit:,}",
    f"Net Profit/Loss: ${net_profit_loss:,}",
    f"Total Income Valuation: ${total_income_valuation:,}",
    f"Low Valuation (1.5x): ${valuation_1_5x:,.0f}",
    f"Median Valuation (2.0x): ${valuation_2_0x:,.0f}",
    f"High Valuation (2.5x): ${valuation_2_5x:,.0f}",
]:
    pdf.drawString(80, y, line)
    y -= 20

pdf.save()
pdf_buffer.seek(0)

# --- Buttons ---
if name and email:
    st.download_button(
        label="Download Results as PDF",
        data=pdf_buffer,
        file_name="sde_results.pdf",
        mime="application/pdf"
    )
else:
    st.warning("⚠️ Please fill out both Name and Email to download your results.")

if st.button("Send Results to Your Email"):
    if name and email:
        send_email(email, pdf_buffer)
        save_to_google_sheets(name, email)
    else:
        st.error("❌ Please fill out both Name and Email before sending.")
