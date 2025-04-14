import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime
import pytz

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
        st.dataframe(df)

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

        # attempt with altair
        import altair as alt

        # Clean up and validate columns
        df.columns = df.columns.str.strip()

        # Convert to datetime and sort
        df["Date"] = pd.to_datetime(df["Number Date"], errors="coerce")
        df = df.sort_values("Date")

        # Convert Y-axis columns to numeric
        df["Actual (km)"] = pd.to_numeric(df["Actual (km)"], errors="coerce")
        df["Target (km)"] = pd.to_numeric(df["Target (km)"], errors="coerce")

        # Drop rows with missing values in any critical column
        df = df.dropna(subset=["Date", "Actual (km)", "Target (km)"])
        
        # add a column to check if "Date" and "Number Date" are exactly the same
        df["Date Check"] = df["Date"].dt.strftime("%d/%m/%Y %H:%M:%S") == df["Number Date"].dt.strftime("%d/%m/%Y %H:%M:%S")

        # preview dataframe
        st.dataframe(df)

        # Melt to long format
        melted_df = df.melt(
            id_vars=["Number Date"],
            value_vars=["Actual (km)", "Target (km)"],
            var_name="Series",
            value_name="Distance"
        )

        # Set custom color scale
        color_scale = alt.Scale(
            domain=["Actual (km)", "Target (km)"],
            range=["#1f77b4", "#d62728"]
        )

        # Build Altair chart
        chart = alt.Chart(melted_df).mark_line().encode(
            x=alt.X("Number Date:T", title="Number Date"),
            y=alt.Y("Distance:Q", title="Distance (km)"),
            color=alt.Color("Series:N", scale=color_scale, title="Legend")
        ).properties(
            width=700,
            height=400,
            title="Actual vs Target Distance Over Time"
        )

        st.altair_chart(chart, use_container_width=True)



    else:
        st.error("No data found in the Google Sheet.")
except Exception as e:
    st.error(f"Error loading data: {e}")
