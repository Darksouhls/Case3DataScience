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

    df1= load_excel('1Flight 1.xlsx')
    df2= load_excel('1Flight 2.xlsx')
    df3= load_excel('1Flight 3.xlsx')
    df4= load_excel('1Flight 4.xlsx')
    df5= load_excel('1Flight 5.xlsx')
    df6= load_excel('1Flight 6.xlsx')
    df7= load_excel('1Flight 7.xlsx')

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

    #-------------------------------------------------
    # Plot 2
    #--------------------------------------------------

    # Schoon de dataset
    df2_clean = df2.dropna(subset=['[3d Latitude]', '[3d Longitude]', 'TRUE AIRSPEED (derived)'])  # Drop rows with missing values
    df2_clean = df2_clean[df2_clean['[3d Latitude]'] < 90]  # Remove unrealistic values (like 3.40e+38)

    # TRUE AIRSPEED numeriek maken 
    df2_clean['TRUE AIRSPEED (derived)'] = pd.to_numeric(df2_clean['TRUE AIRSPEED (derived)'], errors='coerce').fillna(0)

    # Maak een lijst van lat/long coördinaten
    flight_coords = list(zip(df2_clean['[3d Latitude]'], df2_clean['[3d Longitude]']))

    # Maak een lijst van snelheden
    speeds = df2_clean['TRUE AIRSPEED (derived)'].values

    # Normaliseer snelheden voor kleurmapping
    vmin, vmax = speeds.min(), speeds.max()
    norm = plt.Normalize(vmin=vmin, vmax=vmax)
    cmap = plt.get_cmap('coolwarm')  # Kleuren van blauw (langzaam) naar rood (snel)

    # Maak een folium kaart, gecentreerd rond het gemiddelde van de latitudes en longitudes
    map_center = [df2_clean['[3d Latitude]'].mean(), df2_clean['[3d Longitude]'].mean()]
    flight_map = folium.Map(location=map_center, zoom_start=5.3)

    # Voeg een polyline toe aan de kaart om de vliegroute te laten zien, met kleuren gebaseerd op snelheid
    for i in range(1, len(flight_coords)):
        start = flight_coords[i-1]
        end = flight_coords[i]
        speed = speeds[i]
        
        # Haal de kleur voor dit segment op, gebaseerd op snelheid
        color = matplotlib.colors.to_hex(cmap(norm(speed)))
        
        # Voeg het gekleurde segment toe aan de kaart
        folium.PolyLine([start, end], color=color, weight=2.5, opacity=1).add_to(flight_map)

    # Voeg markeringen toe voor de start- en eindpunten
    folium.Marker(flight_coords[0], popup="Start", icon=folium.Icon(color='green')).add_to(flight_map)  # Startpunt
    folium.Marker(flight_coords[-1], popup="End", icon=folium.Icon(color='red')).add_to(flight_map)  # Eindpunt

    # Voeg de kaart toe aan Streamlit
    st.title("Vluchtkaart met snelheden")
    st_data = st_folium(flight_map, width=725, height=500)

    st.markdown('---')
    #--------------------------------------------------
    # Plot 3
    #----------------------------------------------------

    # Data inladen en opschonen, deze stappen worden gecached voor snellere herladen
    df1_clean = clean_data(df1)
    df2_clean = clean_data(df2)
    df3_clean = clean_data(df3)
    df4_clean = clean_data(df4)
    df5_clean = clean_data(df5)
    df6_clean = clean_data(df6)
    df7_clean = clean_data(df7)

    # Maak een dictionary met de vluchtdata
    flight_data = {
        'Flight 1': df1_clean,
        'Flight 2': df2_clean,
        'Flight 3': df3_clean,
        'Flight 4': df4_clean,
        'Flight 5': df5_clean,
        'Flight 6': df6_clean,
        'Flight 7': df7_clean
    }

    # Voeg een dropdown toe om de vlucht te selecteren
    selected_flights = st.multiselect(
        'Selecteer een vluchttype', 
        options=list(flight_data.keys()), 
        default=['Flight 1']  
    )

    # Laad spinner zodat de gebruiker weet dat de data wordt geladen (optioneel)
    with st.spinner('Vluchtdata wordt geladen...'):
        # Maak de plot
        plt.figure(figsize=(12, 6))

        # Definieer kleuren en linestyles
        colors = ['blue', 'red', 'green', 'orange', 'purple', 'black', 'coral']
        linestyles = ['-', '--', '-.', ':', '-', '--', (0, (5, 10))]

        # Plot de geselecteerde vluchten
        for idx, flight in enumerate(selected_flights):
            df_clean = flight_data[flight]
            plt.plot(
                df_clean['Time (secs)'], df_clean['[3d Altitude M]'], 
                color=colors[idx], linestyle=linestyles[idx], 
                label=flight, alpha=0.8
            )

        # Voeg titels en labels toe
        plt.title('Hoogte (M) VS Tijd (sec) Scatter Plot voor Meerdere Vluchten', fontsize=14)
        plt.xlabel('Time (sec)', fontsize=12)
        plt.ylabel('Hoogte (Meters)', fontsize=12)

        # Voeg legenda toe
        plt.legend(loc='center left', bbox_to_anchor=(1, 0.5), fontsize=10)

        # Voeg grid toe voor betere leesbaarheid
        plt.grid(True)

        # Zorg dat de layout goed is
        plt.tight_layout()

        # Toon de plot in Streamlit
        st.pyplot(plt)

    st.markdown('---')

    #---------------------------------------------------------
    # Plot 4
    #--------------------------------------------------------
    # Functie om data te laden en te cachen
    @st.cache_data
    def load_data(file):
        return pd.read_excel(file)

    # Functie om te bekijken waar de vliegtuig stijgt
    def find_ascent_start(df, altitude_column='[3d Altitude M]'):
        return df[df[altitude_column] > 0].iloc[0]['Time (secs)']

    # Functie om de tijd te normaliseren
    def normalize_flight_time(df, start_time):
        return df['Time (secs)'] - start_time

    # Functie om te interpoleren
    def interpolate_altitudes(common_time, time_data, altitude_data):
        return np.interp(common_time, time_data, altitude_data)

    # Laad en verwerk de data (met caching)
    df1_clean = load_excel('1Flight 1.xlsx')
    df2_clean = load_excel('1Flight 2.xlsx')
    df3_clean = load_excel('1Flight 3.xlsx')
    df4_clean = load_excel('1Flight 4.xlsx')
    df5_clean = load_excel('1Flight 5.xlsx')
    df6_clean = load_excel('1Flight 6.xlsx')
    df7_clean = load_excel('1Flight 7.xlsx')

    # Bereken de starttijden van de stijging voor elke vlucht
    start_time_hoogte1 = find_ascent_start(df1_clean)
    start_time_hoogte2 = find_ascent_start(df2_clean)
    start_time_hoogte3 = find_ascent_start(df3_clean)
    start_time_hoogte4 = find_ascent_start(df4_clean)
    start_time_hoogte5 = find_ascent_start(df5_clean)
    start_time_hoogte6 = find_ascent_start(df6_clean)
    start_time_hoogte7 = find_ascent_start(df7_clean)

    # Normaliseer de tijd
    time_hoogte = normalize_flight_time(df1_clean, start_time_hoogte1)
    time_hoogte1 = normalize_flight_time(df2_clean, start_time_hoogte2)
    time_hoogte2 = normalize_flight_time(df3_clean, start_time_hoogte3)
    time_hoogte3 = normalize_flight_time(df4_clean, start_time_hoogte4)
    time_hoogte4 = normalize_flight_time(df5_clean, start_time_hoogte5)
    time_hoogte5 = normalize_flight_time(df6_clean, start_time_hoogte6)
    time_hoogte6 = normalize_flight_time(df7_clean, start_time_hoogte7)

    # Interpoleer om alle vluchten op dezelfde tijdspunten af te stemmen
    common_time = np.linspace(0, min(time_hoogte.max(), time_hoogte1.max(), time_hoogte2.max(),
                                    time_hoogte3.max(), time_hoogte4.max(), time_hoogte5.max(),
                                    time_hoogte6.max()), 500)

    alt1_interp = interpolate_altitudes(common_time, time_hoogte, df1_clean['[3d Altitude M]'])
    alt2_interp = interpolate_altitudes(common_time, time_hoogte1, df2_clean['[3d Altitude M]'])
    alt3_interp = interpolate_altitudes(common_time, time_hoogte2, df3_clean['[3d Altitude M]'])
    alt4_interp = interpolate_altitudes(common_time, time_hoogte3, df4_clean['[3d Altitude M]'])
    alt5_interp = interpolate_altitudes(common_time, time_hoogte4, df5_clean['[3d Altitude M]'])
    alt6_interp = interpolate_altitudes(common_time, time_hoogte5, df6_clean['[3d Altitude M]'])
    alt7_interp = interpolate_altitudes(common_time, time_hoogte6, df7_clean['[3d Altitude M]'])

    # Bereken de gemiddelde hoogte bij elk tijdspunt
    mean_altitude = np.mean([alt1_interp, alt2_interp, alt3_interp, alt4_interp, alt5_interp, alt6_interp, alt7_interp], axis=0)

    # Maak een dictionary met vluchtdata
    flight_data = {
        'Flight 1': (time_hoogte, df1_clean['[3d Altitude M]'], alt1_interp),
        'Flight 2': (time_hoogte1, df2_clean['[3d Altitude M]'], alt2_interp),
        'Flight 3': (time_hoogte2, df3_clean['[3d Altitude M]'], alt3_interp),
        'Flight 4': (time_hoogte3, df4_clean['[3d Altitude M]'], alt4_interp),
        'Flight 5': (time_hoogte4, df5_clean['[3d Altitude M]'], alt5_interp),
        'Flight 6': (time_hoogte5, df6_clean['[3d Altitude M]'], alt6_interp),
        'Flight 7': (time_hoogte6, df7_clean['[3d Altitude M]'], alt7_interp)
    }

    # Voeg een dropdown toe voor het selecteren van vluchten
    selected_flights = st.multiselect(
        'Select flights to display',
        options=list(flight_data.keys()),
        default=list(flight_data.keys())  # Select all flights by default
    )

    # Streamlit UI checkbox voor het gemiddelde
    plot_mean = st.checkbox('Plot Mean Altitude', value=True)

    # Laad spinner zodat de gebruiker weet dat er iets gebeurt (optioneel)
    with st.spinner('Data wordt geladen...'):
        # Creeër de plot
        plt.figure(figsize=(12, 6))

        # Definieer kleuren en linestijlen
        colors = ['blue', 'red', 'green', 'orange', 'purple', 'black', 'coral']
        linestyles = ['-', '--', '-.', ':', '-', '--', (0, (5, 10))]

        # Plot de geselecteerde vluchten
        for idx, flight in enumerate(selected_flights):
            time, altitude, _ = flight_data[flight]
            plt.plot(time, altitude, color=colors[idx], linestyle=linestyles[idx], label=flight, alpha=0.4)

        # Optioneel: plot de gemiddelde hoogte als de checkbox is ingeschakeld
        if plot_mean:
            plt.plot(common_time, mean_altitude, color='cyan', linestyle='-', label='Mean Altitude', linewidth=3)

        # Voeg titels en labels toe
        plt.title('Altitude (Meters) VS Tijd (sec) met Gem. Altitude Lijn', fontsize=14)
        plt.xlabel('Tijd beginnend op 0 (secs)', fontsize=12)
        plt.ylabel('Altitude (Meters)', fontsize=12)

        # Voeg een legenda toe
        plt.legend(loc='center left', bbox_to_anchor=(1, 0.5), fontsize=10)

        # Voeg een grid toe voor betere leesbaarheid
        plt.grid(True)

        # Zorg ervoor dat de layout netjes is
        plt.tight_layout()

        # Toon de plot in Streamlit
        st.pyplot(plt)