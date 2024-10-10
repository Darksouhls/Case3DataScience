import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path
import plotly.express as px
import numpy as np
#import folium
import plotly.graph_objects as go
from plotly.subplots import make_subplots

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
    st.header("Data needs to be included")
    load3 = load_tab3()