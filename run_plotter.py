import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials

# Load credentials from Streamlit secrets
creds_dict = st.secrets["gcp_service_account"]
scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
creds = Credentials.from_service_account_info(dict(creds_dict), scopes=scope)

# Authorize with Google Sheets
client = gspread.authorize(creds)

# Google Sheet URL
SHEET_URL = "https://docs.google.com/spreadsheets/d/1-ArplpDGmj7NDo8WanNy5Py76uijZfnMeQhZx0axiqA/edit?gid=129851035#gid=129851035"

def load_data(sheet_url):
    sheet = client.open_by_url(sheet_url).sheet1
    data = sheet.get_all_records()
    return pd.DataFrame(data)

st.title("Google Sheets Data Graphing")

try:
    df = load_data(SHEET_URL)

    if not df.empty:
        st.write("### Data Preview:")
        st.dataframe(df)

        # Select Columns
        x_col = st.selectbox("Select X-Axis Column:", df.columns)
        y_col = st.selectbox("Select Y-Axis Column:", df.columns)

        # Plot Graph
        if x_col and y_col:
            st.write(f"### Graph of {y_col} vs {x_col}")
            st.line_chart(df.set_index(x_col)[y_col])
    else:
        st.error("No data found in the Google Sheet.")
except Exception as e:
    st.error(f"Error loading data: {e}")
