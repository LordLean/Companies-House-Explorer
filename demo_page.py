import streamlit as st
from companies_house_connection import CompaniesHouseConnection

import requests
import pandas as pd

st.set_page_config(
    page_title="Companies House Connection Demo",
    page_icon="🌎",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://www.extremelycoolapp.com/help',
        'Report a bug': "https://www.extremelycoolapp.com/bug",
        'About': "Companies House PythonAPI Demo"
    }
)

def get_lat_lng(postcode):
    base_url = f"http://api.postcodes.io/postcodes/{postcode}"
    response = requests.get(base_url)
    data = response.json()
    if data['status'] == 200:
        latitude = data['result']['latitude']
        longitude = data['result']['longitude']
        return pd.Series([latitude, longitude])
    else:
        return pd.Series([None, None])

api_key = st.secrets["api_key"]

with st.form("submit_form"):
    input_company = st.text_input("Enter UK Companies House Search Query")
    with st.expander("Help"):
        st.write("Why not try Facebook, or Dominos?")
    submitted = st.form_submit_button("Submit")

# build connection
conn = st.experimental_connection('companieshouse', type=CompaniesHouseConnection, api_key=api_key)

if submitted and input_company:
    # search on specified input
    company_data = conn.search_companies(input_company)

    # get coordinates from UK postcodes
    company_data[['latitude', 'longitude']] = company_data['address.postal_code'].apply(get_lat_lng)
    # copy coords to df 
    coords = company_data[["latitude", "longitude"]]
    # remove Nones
    coords.dropna(inplace=True)
    # visualize df and map
    st.dataframe(company_data, use_container_width=True)
    st.map(coords)

elif submitted and not input_company:
    st.warning("Enter a company, corporate entity, owner, or individual")