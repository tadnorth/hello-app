# remember to streamlit run .\test1.py using a terminal
# ref this page for the basics: https://docs.streamlit.io/get-started/fundamentals/main-concepts

import streamlit as st

st.title("TESTING THE THINGS!")
st.write("Hello stream world!")
st.write("Here's a \"second\" line of tezt")

'yeah hi' " ok down to business"

import numpy as np
import pandas as pd


exp_dataframesplots = st.expander(label="Dataframe & Plotting Examples")
with exp_dataframesplots:

    df = pd.DataFrame({
        'first column': [1, 2, 3, 4],
        'second column': [10, 20, 30, 40]
    })

    st.write(pd.DataFrame({
        'first column': [1, 2, 3, 4],
        'second column': [10, 20, 30, 40]
    }))

    st.dataframe(df)
    [1,2,3,4]
    st.write('[1,2,3,4]')

    # dataframe = pd.DataFrame(np.random.randn(10,20))
    # dataframe

    dataframe = pd.DataFrame(
        np.random.randn(10,20),
        columns=('col %d' % i for i in range(20)))

    st.dataframe(dataframe.style.highlight_max(axis=0))

    # st.table(dataframe)

    chart_data = pd.DataFrame(
        np.random.randn(20,3),
        columns=['a','b','c']
    )

    st.line_chart(chart_data)

    map_data = pd.DataFrame(
        np.random.randn(1000,2) / [70,50] + [49.2, -122.9],
        columns=['lat','lon']
    )
    st.map(map_data)

if st.sidebar.checkbox("Slider Example"):
    x = st.slider('x')
    st.write(x, 'squared is', x*x)

if st.sidebar.checkbox("Text Input & Session State"):
    st.text_input("your name", key="name")
    st.session_state.name

### UNIT CONVERTER SECTION ###
exp_unitconverter = st.sidebar.expander(label="Unit Converter & Session State")
with exp_unitconverter:
    st.title("Convert Weight Units")
    col1, col2 = st.columns(2)

    def kg_to_lbs():
        st.session_state.lbs = st.session_state.kg*2.205

    def lbs_to_kg():
        st.session_state.kg = st.session_state.lbs/2.205

    with col1:
        kilograms = st.number_input("Kilograms:", key="kg",
        on_change = kg_to_lbs)

    with col2:
        pounds = st.number_input("Pounds:", key="lbs",
        on_change = lbs_to_kg)

if st.sidebar.checkbox('Selection Example'):
    df = pd.DataFrame({
    'first column': [1, 2, 3, 4],
    'second column': [10, 20, 30, 40]
    })

    option = st.sidebar.selectbox(
        'Which number do you like best?',
        df['second column']
    )

    st.sidebar.write('You selected: ', option)
