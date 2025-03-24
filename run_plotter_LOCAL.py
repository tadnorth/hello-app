import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials

# Google Sheets Configuration
SHEET_URL = "https://docs.google.com/spreadsheets/d/1-ArplpDGmj7NDo8WanNy5Py76uijZfnMeQhZx0axiqA/edit?gid=129851035#gid=129851035"
SERVICE_ACCOUNT_FILE = "tads-tooling-b9e7328a381e.json"

# Authenticate with Google Sheets
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=scope)
client = gspread.authorize(creds)

# Load Data from Google Sheets
def load_data(sheet_url):
    sheet = client.open_by_url(sheet_url).sheet1
    data = sheet.get_all_records()
    return pd.DataFrame(data)

# numericize the date
def numericize_date(date_col):
    df["Number Date"] = pd.to_datetime(df[date_col], format="%d/%m/%Y %H:%M:%S", errors="coerce")
    return "Number Date"

# Streamlit UI
st.title("Google Sheets Data Graphing")

try:
    df = load_data(SHEET_URL)

    if not df.empty:
        # st.write("### Data Preview:")
        # st.dataframe(df)

        # Select Columns

        x_col = numericize_date("Timestamp")
        y_col = "Distance (km)"
        # x_col = st.selectbox("Select X-Axis Column:", df.columns)
        # y_col = st.selectbox("Select Y-Axis Column:", df.columns)

        # Plot Graph
        if x_col and y_col:
            st.write(f"### Graph of {y_col} vs {x_col}")
            st.line_chart(df.set_index(x_col)[y_col])
    else:
        st.error("No data found in the Google Sheet.")
except Exception as e:
    st.error(f"Error loading data: {e}")
