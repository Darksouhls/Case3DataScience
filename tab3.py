import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path
import plotly.express as px
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import datetime
import folium
from streamlit_folium import st_folium
import matplotlib.pyplot as plt
import matplotlib.colors

def load_tab3():

    #-----------------------------------------------
    # Inladen en bewerken van datasets
    #------------------------------------------------

    @st.cache_data
    def load_data(bestandsnaam, scheidingsteken): 
        try:
            schedule = pd.read_csv(bestandsnaam, sep=scheidingsteken)  # Lees het CSV-bestand
            return schedule  # Retourneer de DataFrame
        except FileNotFoundError:
            st.error(f'Bestand {bestandsnaam} niet gevonden.') 
            return None
        except Exception as e:
            st.error(f'Fout bij het lezen van {bestandsnaam}: {e}')
            return None  # Retourneer None als er een fout is

    @st.cache_data
    def load_excel(bestandsnaam):
        try:
            df = pd.read_excel(bestandsnaam)
            return df  # Retourneer de DataFrame
        except FileNotFoundError:
            print(f'Bestand {bestandsnaam} niet gevonden.') 
        except Exception as e:
            print(f'Fout bij het lezen van {bestandsnaam}: {e}')
        return None  # Retourneer None als er een fout is

    # functie om data te cleane
    @st.cache_data
    def clean_data(df):
        return df.dropna(subset=['Time (secs)', '[3d Altitude M]'])

    # laad de data
    df_airports = load_data('airports-extended-clean.csv', ';')
    dfschema = load_data('schedule_airport.csv', ',')

    # clean de data
    df_airports['ICAO'].dropna(inplace=True)
    dfschema['Org/Des'].dropna(inplace=True)

    # Merge de data's
    merge = pd.merge(df_airports, dfschema, left_on='ICAO', right_on='Org/Des', how='inner')

    # verwijder NaN
    merge.dropna(inplace=True)

    # voeg data toe met dubbele waardes verwijderd
    unique_icao_orgdes = merge[['ICAO', 'Org/Des', 'Longitude', 'Latitude']].drop_duplicates()

    # vervang de punten met commas 
    unique_icao_orgdes['Latitude'] = unique_icao_orgdes['Latitude'].str.replace(',', '.').astype(float)
    unique_icao_orgdes['Longitude'] = unique_icao_orgdes['Longitude'].str.replace(',', '.').astype(float)

    #----------------------------------
    # Plot 1
    #-----------------------------------

    # Creer de map met begin punt
    m = folium.Map(location=[20, 0], zoom_start=2)

    # voeg de locaties toe in de map
    for idx, row in unique_icao_orgdes.iterrows():
        folium.Marker(
            location=[row['Latitude'], row['Longitude']],  # Location of the airport
            popup=f"Airport: {row['ICAO']}",  # Pop-up with ICAO code
            icon=folium.Icon(icon='plane', prefix='fa', color='blue')  # Correct Font Awesome plane icon
        ).add_to(m)


    # laat zien in streamlit
    st.title("Vliegvelden Kaart")
    st_data = st_folium(m, width=725, height=500)

    st.markdown('---')
    return load_tab3