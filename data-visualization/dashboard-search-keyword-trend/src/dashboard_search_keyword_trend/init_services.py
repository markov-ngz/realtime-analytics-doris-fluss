import pymysql
import streamlit as st

from dashboard_search_keyword_trend import config
from dashboard_search_keyword_trend.infra import DorisConnection
from dashboard_search_keyword_trend.service import SearchKeywordTrendService


def init_services():
    try:
        doris_connection = DorisConnection(
            host=config.DORIS_HOST,
            port=config.DORIS_PORT,
            user=config.DORIS_USER,
            password=config.DORIS_PASSWORD,
            catalog=config.CATALOG_NAME,
            database=config.DATABASE_NAME,
        ).connect()
        st.session_state.doris_connection = doris_connection
        st.session_state.keyword_service = SearchKeywordTrendService(doris_connection)
        st.session_state.connection_error = None
    except pymysql.Error as e:
        st.session_state.connection_error = str(e)
