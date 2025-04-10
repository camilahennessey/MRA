import streamlit as st
import matplotlib.pyplot as plt
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import base64
import sendgrid
from sendgrid.helpers.mail import Mail, Attachment, FileContent, FileName, FileType, Disposition
import gspread
from google.oauth2.service_account import Credentials

# === Streamlit Settings ===
st.set_page_config(layout="wide")

# === Secrets ===
SENDGRID_API_KEY = st.secrets["SENDGRID_API_KEY"]
SENDGRID_SENDER = st.secrets["SENDGRID_SENDER"]

# Google Sheets Setup
SCOPE = ["https://www.googleapis.com/auth/spreadsheets"]
creds = Credentials.from_service_account_info(st.secrets, scopes=SCOPE)
client = gspread.authorize(creds)
sheet = client.open_by_key(st.secrets["GCP_SHEET_ID"]).sheet1

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

# === Donut Chart ===
if income > 0 and sde >= 0:
    values = [total_expenses, sde]
    labels = ["Total Expenses", "SDE"]
    colors = ['#2E86AB', '#F5B041']
    fig, ax = plt.subplots(figsize=(3, 3))
    ax.pie(values, labels=labels, colors=colors,
           autopct=lambda p: f"${int(round(p * sum(values) / 100.0)):,}",
           startangle=90, wedgeprops=dict(width=0.35, edgecolor='white'),
           textprops=dict(color="black", fontsize=8))
    ax.text(0, 0, f"{round(sde_margin)}%", ha='center', va='center', fontsize=12, fontweight='bold')
    ax.set_title("SDE Margin", fontsize=12, fontweight='bold')
    st.pyplot(fig)

# === PDF Generator ===
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
    "Name": name, "Email": email,
    "F&B Income": f"${income:,.0f}", "Purchases": f"${purchases:,.0f}",
    "Labor": f"${labor:,.0f}", "Operating Expenses": f"${operating:,.0f}",
    "Total Expenses": f"${total_expenses:,.0f}",
    "SDE": f"${sde:,.0f}", "SDE Margin": f"{sde_margin:.0f}%"
}

pdf_buffer = generate_pdf(data)

# === Send Email ===
def send_email(recipient_email, pdf_buffer):
    if not recipient_email or "@" not in recipient_email:
        st.error("Invalid email address.")
        return

    pdf_encoded = base64.b64encode(pdf_buffer.getvalue()).decode()

    sg = sendgrid.SendGridAPIClient(api_key=SENDGRID_API_KEY)

    attachment = Attachment(
        FileContent(pdf_encoded),
        FileName("sde_results.pdf"),
        FileType("application/pdf"),
        Disposition("attachment")
    )

    message = Mail(
        from_email=SENDGRID_SENDER,
        to_emails=recipient_email,
        subject="Your MRA SDE Valuation Report",
        plain_text_content="Attached is your personalized valuation report."
    )
    message.attachment = attachment

    try:
        sg.send(message)
        st.success("✅ Email sent successfully!")
    except Exception as e:
        st.error(f"❌ Email sending failed: {str(e)}")

# === Save to Google Sheets ===
def save_to_google_sheets(name, email):
    try:
        sheet.append_row([name, email])
        st.success("✅ Data saved to Google Sheets successfully!")
    except Exception as e:
        st.error(f"❌ Failed to save to Google Sheets: {str(e)}")

# === Buttons ===
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
        st.error("❌ Please fill in your Name and Email before sending.")

