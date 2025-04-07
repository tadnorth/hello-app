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
st.title("Distance vs Date")

try:
    df = load_data(SHEET_URL)

    if not df.empty:
        numericize_date("Timestamp")
        # Create new column with weight based on actvity type
        df["Weight"] = df["Run or Cycle?"].apply(lambda x: 0.33333 if x == "CYCLE" else 1)
        
        # Create new column with the sum of the product of Distance and Weight
        # df["Weighted Distance"] = df["Distance (km)"] * df["Weight"]
        df["Actual (km)"] = (df["Distance (km)"] * df["Weight"]).cumsum()

        # Create a new column showing the fraction of the way through the year times the 1000km goal
        df["Target (km)"] = (df["Number Date"].dt.dayofyear / 365) * 1000

        # st.write("### Data Preview:")
        # st.dataframe(df)

        # Select Columns

        x_col = numericize_date("Timestamp")
        y_col = "Actual (km)"
        target_col = "Target (km)"
        # x_col = st.selectbox("Select X-Axis Column:", df.columns)
        # y_col = st.selectbox("Select Y-Axis Column:", df.columns)

        # Plot Graph
        if x_col and y_col:
            # st.write(f"### Distance vs Date")
            
            # graph the target distance and the accumulated weighted distance both against the date
            st.line_chart(df.set_index(x_col)[[target_col, y_col]])
            #st.line_chart(df.set_index(x_col)[y_col])

            # Use Altair for more customization!!! EXPERIMENTAL
            import altair as alt

            # Melt the DataFrame if you have multiple Y-series (not needed if just one column)
            chart_df = df[[x_col, y_col]].copy()

            # Create Altair chart
            chart = alt.Chart(chart_df).mark_line().encode(
                x=alt.X(x_col, title="Date"),
                y=alt.Y(y_col, title=y_col),
                color=alt.value("#1f77b4")  # Set your desired hex color here
            ).properties(
                width=700,
                height=400
            )

            st.altair_chart(chart, use_container_width=True)

    else:
        st.error("No data found in the Google Sheet.")
except Exception as e:
    st.error(f"Error loading data: {e}")
