import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime
import pytz

# Google Sheets Configuration
SHEET_URL = "https://docs.google.com/spreadsheets/d/1-ArplpDGmj7NDo8WanNy5Py76uijZfnMeQhZx0axiqA/edit?gid=129851035#gid=129851035"

# service account depends on local PC
# SERVICE_ACCOUNT_FILE = "tads-tooling-b9e7328a381e.json" # tbox
SERVICE_ACCOUNT_FILE = "tads-tooling-7880293dcd19.json" # t-laptop

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
        # Add an entry to the dataframe with the timestamp for today, to be used for graphing the target up to today
        pacific_tz = pytz.timezone("US/Pacific")
        today = datetime.now(pacific_tz)
        new_entry = {
            "Timestamp": today.strftime("%d/%m/%Y %H:%M:%S"),
            "Run or Cycle?": "RUN",  # Default activity type
            "Distance (km)": 0,  # Default distance
        }
        df = pd.concat([df, pd.DataFrame([new_entry])], ignore_index=True)
        
        # create a new column with the date in a numeric format
        numericize_date("Timestamp")
        
        # Create new column with weight based on actvity type
        df["Weight"] = df["Run or Cycle?"].apply(lambda x: 0.33333 if x == "CYCLE" else 1)
        
        # Create new column with the sum of the product of Distance and Weight
        # df["Weighted Distance"] = df["Distance (km)"] * df["Weight"]
        df["Actual (km)"] = (df["Distance (km)"] * df["Weight"]).cumsum()

        # Create a new column showing the fraction of the way through the year times the 1000km goal
        df["Target (km)"] = (df["Number Date"].dt.dayofyear / 365) * 1000

        # calculate how much actual exceeds or lags behind the target today
        df["Diff (km)"] = df["Actual (km)"] - df["Target (km)"]

        # show what the value Diff is today
        today_diff = df.iloc[-1]["Diff (km)"]
        # today_diff = -today_diff
        if today_diff < 0:
            st.markdown(f"### Today you are <span style='color:red'>{-today_diff:.2f} km</span> below target", unsafe_allow_html=True)
        else:
            st.markdown(f"### Today you are <span style='color:green'>{today_diff:.2f} km</span> above target", unsafe_allow_html=True)

        # st.write("### Data Preview:")
        # st.dataframe(df)

        # Select Columns

        x_col = "Number Date"
        # numericize_date("Timestamp")
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

    else:
        st.error("No data found in the Google Sheet.")
except Exception as e:
    st.error(f"Error loading data: {e}")
