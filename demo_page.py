import streamlit as st
from companies_house_connection import CompaniesHouseConnection

import requests
import pandas as pd
import socket

st.set_page_config(
    page_title="Companies House Connection Demo",
    page_icon="🌎",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://github.com/LordLean/Companies-House-Explorer/',
        'Report a bug': "https://github.com/LordLean/Companies-House-Explorer/issues",
        'About': "Companies House Connection Demo"
    }
)

def get_lat_lng(postcode):
    '''
    Function to get latitude and longitude from a given postcode using the 'postcodes.io' API
    '''
    # build url for api call
    base_url = f"http://api.postcodes.io/postcodes/{postcode}"
    response = requests.get(base_url)
    data = response.json()
    if data['status'] == 200:
        # extract lat and long
        latitude = data['result']['latitude']
        longitude = data['result']['longitude']
        return pd.Series([latitude, longitude])
    else:
        return pd.Series([None, None])

def get_public_ip():
    '''
    Function to get the public IP address of the system using the 'httpbin.org' API
    '''
    try:
        response = requests.get("https://httpbin.org/ip")
        data = response.json()
        return data["origin"]
    except requests.RequestException:
        return None

with st.sidebar:
    # input field for api key if not in .streamlit/secrets.toml
    api_key = st.text_input("Companies House API Key")
    public_ip = get_public_ip()
    if public_ip:
        # display public ip to simplify companies house account set-up
        st.markdown(f"Public IP address: `{public_ip}`")
# if api key not stored in .streamlit/secrets.toml
api_key = api_key if api_key else st.secrets["api_key"]


with st.form("submit_form"):
    input_company = st.text_input("Enter UK Companies House Search Query")
    with st.expander("Help"):
        st.markdown("""
       # Companies-House-Explorer
        Web application to demo Streamlit connections, leveraging the UK's Companies House's free API service.

        Submitted in part for consideration in the [Streamlit Hackathon](https://discuss.streamlit.io/t/connections-hackathon/47574)

        Guide to use:
        1. Create a free developer account at [Companies House](https://developer.company-information.service.gov.uk/)
        2. Create an application (select live)
        3. Select REST API
        4. Insert public IP (seen in sidebar) into restricted IPs
        5. Copy API key into sidebar input
        6. Start querying! Why not try Facebook or Dominos?

        ## Experimental Connection:
        """)
        with open("companies_house_connection.py", "r") as file:
            content = file.read()
        st.code(content)
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