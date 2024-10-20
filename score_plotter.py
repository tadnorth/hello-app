# score_plotter

import streamlit as st
import pandas as pd
#import matplotlib.pyplot as plt

# Function to load data from the notes file
def load_data(file):
    data = pd.read_csv(file)
    return data

# Streamlit app
st.title("iOS Notes Data Plotter")