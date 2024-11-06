import streamlit as st

from tab1 import load_tab1
from tab2 import load_tab2
from tab3 import load_tab3
from veranderingen import load_verandering

st.set_page_config(
    page_title='Vluchten Informatie',
    page_icon="✈️",
    layout = "wide",
    initial_sidebar_state = "auto"
)
st.write('Source Kaggle en Dlo')
# Sidebar for Mode Selection
mode = st.sidebar.radio("Wat wil je zien", options=["Veranderingen van de app", "Nieuwe app"], index=1)

if mode == 'Veranderingen van de app':
    load = load_verandering()

else:
    st.header("Vertraging Analyses")
    tab1, tab2, tab3 = st.tabs(["Land", "Luchtvaatmaatschappij", "Kaart"])

    with tab1:
        load1 = load_tab1()
    with tab2:
        load2 = load_tab2()
    with tab3:
        load3 = load_tab3()