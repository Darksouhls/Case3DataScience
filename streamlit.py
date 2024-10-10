import streamlit as st

from tab1 import load_tab1
from tab2 import load_tab2
from tab3 import load_tab3

st.set_page_config(
    page_title='Vluchten Informatie',
    page_icon="✈️",
)

tab1, tab2, tab3 = st.tabs(["Top 5", "Vertraging analyse", "Beste route"])

with tab1:
    load1 = load_tab1()
with tab2:
    load2 = load_tab2()
with tab3:
    load3 = load_tab3()