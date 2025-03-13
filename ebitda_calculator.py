import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# Centering image using st.image() with CSS styling
st.markdown(
    """
    <style>
    .centered-image {
        display: flex;
        justify-content: center;
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.markdown('<div class="centered-image">', unsafe_allow_html=True)
st.image("images/MRA logo 9.2015-colorLG.jpg", width=500)
st.markdown('</div>', unsafe_allow_html=True)


# Section 1: Title & Explanation
st.title("MRA EBITDA Valuation Calculator")

st.markdown("""
### What is EBITDA?  
EBITDA (Earnings Before Interest, Taxes, Depreciation, and Amortization) is a key financial metric used to analyze a restaurant's operational performance.  
It provides a holistic view of business profitability before accounting for non-operating expenses.

### Why is EBITDA Important?  
- Helps compare operational profitability across businesses.  
- Excludes tax and financing decisions to show core earnings.  
- Useful for investors evaluating a restaurant’s financial health.
""")

# Section 2: EBITDA Calculator Inputs
st.subheader("Enter Financial Information")
net_sales = st.number_input("Net Sales ($)", min_value=0.00, format="%.2f")
cogs = st.number_input("Cost of Goods Sold (COGS) ($)", min_value=0.00, format="%.2f")
employee_cost = st.number_input("Employee Cost ($)", min_value=0.00, format="%.2f")
other_operating_cost = st.number_input("Other Operating Cost ($)", min_value=0.00, format="%.2f")

# Prevent NaN errors by ensuring calculations only happen if net_sales > 0
if net_sales > 0:
    total_expenses = cogs + employee_cost + other_operating_cost
    ebitda = net_sales - total_expenses
    ebitda_margin = (ebitda / net_sales) * 100
else:
    total_expenses, ebitda, ebitda_margin = 0, 0, 0

# Display results
st.write(f"### Total Operating Expenses: **${total_expenses:,.2f}**")
st.write(f"### EBITDA: **${ebitda:,.2f}**")
st.write(f"### EBITDA Margin: **{ebitda_margin:.2f}%**")

# Preventing Pie Chart NaN issues & Handling Negative EBITDA
if total_expenses == 0 and ebitda == 0:
    st.write("⚠️ **Enter values above to generate the pie chart.**")
elif ebitda < 0:
    st.error("⚠️ **EBITDA is negative. A pie chart cannot be generated.**")
else:
    st.subheader("EBITDA Margin Breakdown")
    fig, ax = plt.subplots(figsize=(6,6))
    labels = ["Total Operating Expenses", "EBITDA"]
    values = [total_expenses, ebitda]
    colors = ['#4C72B0', '#55A868']

    ax.pie(values, labels=labels, autopct='%1.1f%%', colors=colors, startangle=140)
    ax.set_title("EBITDA Margin Breakdown")
    st.pyplot(fig)

# Section 3: Owner Benefit Calculation
st.subheader("Owner Benefit Calculation")

# Inputs for owner benefit
owner_salary = st.number_input("Owner Salary ($)", min_value=0.00, format="%.2f")
other_benefits = st.number_input("Other Benefits ($)", min_value=0.00, format="%.2f")
add_backs = st.number_input("Add-Backs (Discretionary Expenses) ($)", min_value=0.00, format="%.2f")

# Ensure ebitda exists before using it
total_owner_benefit = 0  # Default to prevent errors
if "ebitda" in locals():
    total_owner_benefit = ebitda + owner_salary + other_benefits + add_backs

# Display results
st.write(f"### Total Owner Benefit: **${total_owner_benefit:,.2f}**")

# Section 4: Determining the Multiple
st.subheader("Determining the Multiple")

# Explanation of multiples
st.markdown("""
### How Multiples Work
Multiples help determine the estimated business valuation. 
The most common multiples for small businesses in the restaurant industry range from **1.25x to 2.0x** of owner benefit.
""")

# Ensure multiple calculations only happen when total_owner_benefit > 0
low_multiple, median_multiple, high_multiple = 0, 0, 0  # Default values to avoid errors
if total_owner_benefit > 0:
    low_multiple = total_owner_benefit * 1.25
    median_multiple = total_owner_benefit * 1.5
    high_multiple = total_owner_benefit * 2.0

    # Display multiple valuations
    st.write(f"#### Low Multiple (1.25x): **${low_multiple:,.2f}**")
    st.write(f"#### Median Multiple (1.5x): **${median_multiple:,.2f}**")
    st.write(f"#### High Multiple (2.0x): **${high_multiple:,.2f}**")
else:
    st.warning("⚠️ **Enter values above to calculate multiple valuations.**")

# Section 5: Export Results
st.subheader("Export Results")

# Convert results into a DataFrame for exporting
data = {
    "Metric": ["Total Operating Expenses", "EBITDA", "EBITDA Margin", "Total Owner Benefit", 
               "Low Multiple (1.25x)", "Median Multiple (1.5x)", "High Multiple (2.0x)"],
    "Value": [
        total_expenses, ebitda, f"{ebitda_margin:.2f}%", total_owner_benefit, 
        low_multiple, median_multiple, high_multiple
    ]
}

df = pd.DataFrame(data)

# Export button
st.download_button(label="Download Results as CSV", data=df.to_csv(index=False), file_name="ebitda_results.csv", mime="text/csv")
