import streamlit as st
from streamlit.connections import ExperimentalBaseConnection
import requests
import pandas as pd

class CompaniesHouseConnection(ExperimentalBaseConnection[requests.Response]):
    """
    st.experimental_connection implementation for Companies House API
    https://developer.company-information.service.gov.uk/
    """

    def _connect(self, **kwargs):
        if 'api_key' in kwargs:
            self.api_key = kwargs.pop('api_key')
        else:
            self.api_key = self._secrets['api_key']
        self.auth = (self.api_key, '')

    def search_companies(self, query: str, ttl: int = 3600, items_per_page=300, **kwargs) -> pd.DataFrame:
        @st.cache_data(ttl=ttl)
        def _query(query: str, items_per_page=300, **kwargs):
            headers = {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36',
                'Accept': 'application/json',
                'Content-Type': 'application/json',   
            }
            base_url = "https://api.company-information.service.gov.uk/search/companies"
            params = {
                "q" : query,
                "items_per_page" : items_per_page
            }
            try:
                response = requests.get(base_url, auth=self.auth, params=params, headers=headers)
                if not response:
                    print(response.status_code)
                    print(response.text)
                data = response.json()
                return pd.json_normalize(data['items'])
            except requests.exceptions.RequestException as e:
                print(f"Request failed: {e}")
                return pd.DataFrame() 
        return _query(query, items_per_page, **kwargs)