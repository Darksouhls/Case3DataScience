import streamlit as st
import pandas as pd
from pathlib import Path
import plotly.express as px
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import datetime

def load_tab2():

    #-------------------------------
    # Inladen en bewerken Datasets
    #-------------------------------

    @st.cache_data
    #functie om bestanden in te laden met bijbehorende scheidingsteken
    def load_data(bestandsnaam, scheidingsteken): 
        try:
            schedule = pd.read_csv(bestandsnaam, sep=scheidingsteken)  # Lees het CSV-bestand
            return schedule  # Retourneer de DataFrame
        except FileNotFoundError:
            print(f'Bestand {bestandsnaam} niet gevonden.') 
        except Exception as e:
            print(f'Fout bij het lezen van {bestandsnaam}: {e}')
            return None  # Retourneer None als er een fout is

    schedule_df = load_data('schedule_airport.csv', ',') 
    df_airports = load_data('airports-extended-clean.csv', ';')
    wereld_df = load_data('Countries by continents.csv', ',')

    df_airports['ICAO'].dropna()
    schedule_df['LSV'] = schedule_df['LSV'].replace({'L': 'Inbound', 'S': 'Outbound'}).dropna()

    @st.cache_data
    # functie om bestanden samen te voegen
    def merging(dataset1, dataset2, left, right, how):
        merge = pd.merge(dataset1, dataset2, left_on=left, right_on=right, how=how)
        return merge

    merge_df = merging(df_airports, schedule_df, 'ICAO', 'Org/Des', 'inner')

    # Verschillende DataFrames aanmaken op basis van een bestaande DataFrame
    vertraagd = schedule_df[schedule_df['ATA_ATD_ltc'] > schedule_df['STA_STD_ltc']]
    optijd = schedule_df[schedule_df['ATA_ATD_ltc'] <= schedule_df['STA_STD_ltc']]
    precies = schedule_df[schedule_df['ATA_ATD_ltc'] == schedule_df['STA_STD_ltc']]
    eerder = schedule_df[schedule_df['ATA_ATD_ltc'] < schedule_df['STA_STD_ltc']]
    NogateChange = schedule_df[schedule_df['GAT'] == schedule_df['TAR']]
    gateChange = schedule_df[schedule_df['GAT'] != schedule_df['TAR']]

    # Een top 5 lijst maken van een bepaalde DataFrame
    top_5_landen_vertraagd = vertraagd['Org/Des'].value_counts().nlargest(5).index
    top_5_landen_optijd = optijd['Org/Des'].value_counts().nlargest(5).index
    top_5_landen_precies = precies['Org/Des'].value_counts().nlargest(5).index
    top_5_landen_eerder = precies['Org/Des'].value_counts().nlargest(5).index

    
    #-------------------------------------------------------
    #   Plot 1
    #-------------------------------------------------------
    st.header('Vakantie planner')
    st.markdown('---')

    # Kleuren selectie voor 'optijd', 'eerder' en 'vertraagd
    color_optijd = '#00ff00'
    color_eerder = '#0000ff'
    color_vertraagd = '#ff0000'

    @st.cache_data
    def beschikbare_landen(start_datum, eind_datum):
        # Filter continenten op basis van de geselecteerde periode
        landen_met_data = merge_df[(merge_df['STD'] >= start_datum) & (merge_df['STD'] <= eind_datum)]['Country'].unique()
        return landen_met_data

    @st.cache_data
    def df_change(continenten, start_datum, eind_datum):
        # Haal de gegevens op voor de geselecteerde continenten en periode
        change = merge_df[(merge_df['Country'].isin(continenten)) & 
                          (merge_df['STD'] >= start_datum) & 
                          (merge_df['STD'] <= eind_datum)]
        return change

    # Knop om een periode te selecteren
    start_date, end_date = st.date_input(
        'Selecteer periode waarop je wilt kijken', 
        [datetime.date(2019, 1, 1), datetime.date(2020, 12, 31)], 
        min_value=datetime.date(2019, 1, 1), 
        max_value=datetime.date(2020, 12, 31), 
        format='DD/MM/YYYY'
    )
    formatted_start_date = start_date.strftime('%d/%m/%Y')
    formatted_end_date = end_date.strftime('%d/%m/%Y')

    # Haal continenten met data op voor de geselecteerde periode
    beschikbare_landen = beschikbare_landen(formatted_start_date, formatted_end_date)
    continenten = wereld_df[wereld_df['Country'].isin(beschikbare_landen)]['Continent'].unique()


    # Multibox om een bepaalde continent te selecteren
    geselecteerde_continenten = st.multiselect(
        'Selecteer Continent(en)', 
        continenten,
        default=continenten[:3]
    )

    # Haal de gegevens op voor de geselecteerde periode en continenten
    continent_df = df_change(wereld_df[wereld_df['Continent'].isin(geselecteerde_continenten)]['Country'], formatted_start_date, formatted_end_date)

    # Zet data om naar maatschappij op basis van vluchtnummer
    maatschappij_df = continent_df
    maatschappij_df['FLT'] = maatschappij_df['FLT'].str.replace(r'\d+', '', regex=True)
    maatschappij_df = maatschappij_df[maatschappij_df['FLT'] != 'LX'] # LX wordt hier eruit gefilterd, omdat het een grote maatschappij is
    filtered_df = continent_df
    filtered_df['FLT'] = filtered_df['FLT'].str.replace(r'\d+', '', regex=True) 
    filtered_df = filtered_df[filtered_df['FLT'] == 'LX'] # DataFrame voor alleen LX (grote maatschappij), krijgt eigen plot

    fig1 = make_subplots(rows=1, cols=2, subplot_titles=("Data voor Swiss Int. Air Lines",  "Overige Maatschappijen"))

    # Maakt plot voor LX data
    fig1.add_trace(go.Histogram(
        x=filtered_df[filtered_df['STA_STD_ltc'] > filtered_df['ATA_ATD_ltc']]['FLT'], 
        name='Eerder dan gepland',
        marker_color= color_eerder,
        legendgroup='Eerder',
        showlegend = True
    ), row = 1, col = 1)
    fig1.add_trace(go.Histogram(
        x=filtered_df[filtered_df['STA_STD_ltc'] == filtered_df['ATA_ATD_ltc']]['FLT'], 
        name='Precies optijd',
        marker_color = color_optijd,
        legendgroup='Optijd',
        showlegend = True
    ), row = 1, col = 1)
    fig1.add_trace(go.Histogram(
        x=filtered_df[filtered_df['STA_STD_ltc'] < filtered_df['ATA_ATD_ltc']]['FLT'], 
        name='Vertraagd',
        marker_color= color_vertraagd,
        legendgroup='Vertraagd',
        showlegend = True
    ), row = 1, col = 1)

    # Maakt plot voor overige maatschappijen
    fig1.add_trace(go.Histogram(
        x=maatschappij_df[maatschappij_df['STA_STD_ltc'] > maatschappij_df['ATA_ATD_ltc']]['FLT'], 
        name='Eerder dan gepland',
        marker_color = color_eerder,
        legendgroup='Eerder',
        showlegend = True
    ), row = 1, col = 2)
    fig1.add_trace(go.Histogram(
        x=maatschappij_df[maatschappij_df['STA_STD_ltc'] == maatschappij_df['ATA_ATD_ltc']]['FLT'], 
        name='Precies optijd',
        marker_color= color_optijd,
        legendgroup='Optijd',
        showlegend = True
    ), row = 1, col = 2)
    fig1.add_trace(go.Histogram(
        x=maatschappij_df[maatschappij_df['STA_STD_ltc'] < maatschappij_df['ATA_ATD_ltc']]['FLT'], 
        name='Vertraagd',
        marker_color=color_vertraagd,
        legendgroup='Vertraagd',
        showlegend = True
    ), row = 1, col = 2)
    fig1.update_xaxes(categoryorder='total descending')
    fig1.update_layout(barmode='stack', title_text="Geplande gegevens per luchtvaartmaatschappij voor geselecteerde continent(en)")

    st.plotly_chart(fig1)

    #--------------------------------------
    #   Plot 2
    #--------------------------------------

    # Kijkt naar bovenstaande geselecteerde continent en laad de mogelijke landen in
    beschikbaar_land = continent_df[continent_df['Country'].isin(beschikbare_landen)]['Country'].unique()
    geselecteerde_landen = st.multiselect(
        'Selecteer Continent(en)', 
        beschikbaar_land,
        default = beschikbaar_land[:3]
    )

    # Haal de gegevens op voor de geselecteerde periode en continenten
    country_df = df_change(geselecteerde_landen, formatted_start_date, formatted_end_date)

     # Toggle voor inbound of outbound selecteren
    flight_direction = st.radio("Selecteer vluchtrichting", options=["Inbound", "Outbound"])

    # Filter de dataframe op basis van de geselecteerde richting
    if flight_direction == "Inbound":
        country_df = country_df[country_df['LSV'] == 'Inbound']  # Zorg ervoor dat de kolomnaam correct is
    else:
        country_df = country_df[country_df['LSV'] == 'Outbound']  # Zorg ervoor dat de kolomnaam correct is
        
    # Zet data om naar maatschappij op basis van vluchtnummer
    maatschappij_country_df = country_df
    maatschappij_country_df['FLT'] = maatschappij_country_df['FLT'].str.replace(r'\d+', '', regex=True)

    fig2 = go.Figure()

    # Maakt plot voor overige maatschappijen
    fig2.add_trace(go.Histogram(
        x=maatschappij_country_df[maatschappij_country_df['STA_STD_ltc'] > maatschappij_country_df['ATA_ATD_ltc']]['FLT'], 
        name='Eerder dan gepland',
        marker_color = color_eerder,
        legendgroup='Eerder',
        showlegend = True
    ))
    fig2.add_trace(go.Histogram(
        x=maatschappij_country_df[maatschappij_country_df['STA_STD_ltc'] == maatschappij_country_df['ATA_ATD_ltc']]['FLT'], 
        name='Precies optijd',
        marker_color= color_optijd,
        legendgroup='Optijd',
        showlegend = True
    ))
    fig2.add_trace(go.Histogram(
        x=maatschappij_country_df[maatschappij_country_df['STA_STD_ltc'] < maatschappij_country_df['ATA_ATD_ltc']]['FLT'], 
        name='Vertraagd',
        marker_color=color_vertraagd,
        legendgroup='Vertraagd',
        showlegend = True
    ))
    fig2.update_xaxes(categoryorder='total descending')
    fig2.update_layout(barmode='stack', title_text="Geplande gegevens per luchtvaartmaatschappij voor geselecteerde land(en)")


    # Plaats grafiek en tabel naast elkaar
    col1, col2 = st.columns(2)

    with col1:
        # Toon de grafiek in de eerste kolom
        st.plotly_chart(fig2, use_container_width=True)

    #------------------------------------------------------
    #  Tabel 1
    #------------------------------------------------------

    with col2:
        # Bereken de totaalwaarde
        totaal_vluchten_per_maatschappij = maatschappij_country_df['FLT'].value_counts()

        # Bereken het aantal vertraagde vluchten per maatschappij
        delayed_flights = maatschappij_country_df[maatschappij_country_df['ATA_ATD_ltc'] > maatschappij_country_df['STA_STD_ltc']]
        delayed_flights_per_maatschappij = delayed_flights['FLT'].value_counts()

        # Maak een DataFrame voor de vertragingsratio
        ratio_per_maatschappij = pd.DataFrame({
            'Totale vluchten': totaal_vluchten_per_maatschappij,
            'Vertraagde vluchten': delayed_flights_per_maatschappij
        }).fillna(0)  # Vul lege waarden op met 0 voor maatschappijen zonder vertragingen

        # Bereken de vertragingsratio
        ratio_per_maatschappij['Ratio'] = ratio_per_maatschappij['Vertraagde vluchten'] / ratio_per_maatschappij['Totale vluchten']
        ratio_per_maatschappij['Ratio (%)'] = (ratio_per_maatschappij['Ratio'] * 100).round(2)

        # Toon de verhoudingstabel in Streamlit
        st.write("Verhoudingstabel van Vertraagde Vluchten per Maatschappij")
        st.dataframe(ratio_per_maatschappij[['Totale vluchten', 'Vertraagde vluchten', 'Ratio (%)']])

    return load_tab2