import streamlit as st
import pandas as pd
from pathlib import Path
import plotly.express as px
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import datetime

def load_tab1():

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

    #-----------------------------------------------------
    # Plot 1
    #-----------------------------------------------------

    st.header('Vergelijking Top 5 Vertraagde en Niet-Vertraagde Landen')

    # Voeg selectievakjes toe voor gate change filters
    toggle = st.radio("Selecteer wat je wilt zien", ('Gate Changes', 'Inbound/Outbound'), index=0)
    show_all = st.toggle("Laat alleen de top 5 zien")

    color_not_changed = '#1f77b4'  # Blauwe kleur voor "Gate has not been changed"
    color_changed = '#ff7f0e'  # Oranje kleur voor "Gate has been changed"

    fig1 = make_subplots(rows=1, cols=2, subplot_titles=("Top 5 vertraagde landen stacked",  "Top 5 optijd landen stacked"))

    # Logica om "Alles" te tonen
    if show_all:
        fig1.add_trace(go.Histogram(x=vertraagd[vertraagd['Org/Des'].isin(top_5_landen_vertraagd)]['Org/Des'], name='Vertraagd'), 
                    row=1, col=1)
        fig1.add_trace(go.Histogram(x=optijd[optijd['Org/Des'].isin(top_5_landen_optijd)]['Org/Des'], name='Optijd'), 
                    row=1, col=2)

    else:
        # Logica om "Gate Changes" te tonen
        if toggle == 'Gate Changes':
            show_gate_not_changed = st.checkbox('Gate has not been changed', value=True)
            show_gate_changed = st.checkbox('Gate has been changed', value=False)

            if show_gate_not_changed:
                fig1.add_trace(go.Histogram(x=vertraagd[(vertraagd['Org/Des'].isin(top_5_landen_vertraagd)) & 
                                                        (vertraagd['GAT'] == vertraagd['TAR'])]['Org/Des'], 
                                            name='Gate has not been changed',
                                            marker_color=color_not_changed,
                                            legendgroup='Gate Status',
                                            showlegend = True),  
                                row=1, col=1)
                fig1.add_trace(go.Histogram(x=optijd[(optijd['Org/Des'].isin(top_5_landen_optijd)) & 
                                                        (optijd['GAT'] == optijd['TAR'])]['Org/Des'],
                                            name='Gate has not been changed',
                                            marker_color=color_not_changed,
                                            legendgroup='Gate Status',
                                            showlegend = False),  
                                row=1, col=2)

            if show_gate_changed:
                fig1.add_trace(go.Histogram(x=vertraagd[(vertraagd['Org/Des'].isin(top_5_landen_vertraagd)) & 
                                                        (vertraagd['GAT'] != vertraagd['TAR'])]['Org/Des'],
                                            name='Gate has been changed',
                                            marker_color=color_changed,
                                            legendgroup='Gate Status',
                                            showlegend = True),  
                                row=1, col=1)
                fig1.add_trace(go.Histogram(x=optijd[(optijd['Org/Des'].isin(top_5_landen_optijd)) & 
                                                        (optijd['GAT'] != optijd['TAR'])]['Org/Des'], 
                                            name='Gate has been changed',
                                            marker_color=color_changed,
                                            legendgroup='Gate Status',
                                            showlegend = False),  
                                row=1, col=2)
                
        # Logica om "Inbound en Outbound" vluchten te tonen
        elif toggle == 'Inbound/Outbound':
            show_inbound = st.checkbox('Inbound flights', value=True)
            show_outbound = st.checkbox('Outbound flights', value=False)

            if show_inbound:
                fig1.add_trace(go.Histogram(x=vertraagd[(vertraagd['Org/Des'].isin(top_5_landen_vertraagd)) & 
                                                        (vertraagd['LSV'] == 'Inbound')]['Org/Des'], 
                                            name='Inbound',
                                            marker_color=color_not_changed,
                                            legendgroup='Inbound',
                                            showlegend = True),  
                                row=1, col=1)
                fig1.add_trace(go.Histogram(x=optijd[(optijd['Org/Des'].isin(top_5_landen_optijd)) & 
                                                        (optijd['LSV'] == 'Inbound')]['Org/Des'], 
                                            name='Inbound',
                                            marker_color=color_not_changed,
                                            legendgroup='Inbound',
                                            showlegend = False),  
                                row=1, col=2)

            if show_outbound:
                fig1.add_trace(go.Histogram(x=vertraagd[(vertraagd['Org/Des'].isin(top_5_landen_vertraagd)) & 
                                                        (vertraagd['LSV'] == 'Outbound')]['Org/Des'], 
                                            name='Outbound',
                                            marker_color=color_changed,
                                            legendgroup='Inbound',
                                            showlegend = True), 
                                row=1, col=1)
                fig1.add_trace(go.Histogram(x=optijd[(optijd['Org/Des'].isin(top_5_landen_optijd)) & 
                                                        (optijd['LSV'] == 'Outbound')]['Org/Des'], 
                                            name='Outbound',
                                            marker_color=color_changed,
                                            legendgroup='Inbound',
                                            showlegend = False),  
                                row=1, col=2)

    fig1.update_yaxes(matches='y')
    fig1.update_xaxes(categoryorder='total descending')
    fig1.update_layout(barmode='stack', title_text="Vergelijking Top 5 vertraagde en optijd landen")

    st.plotly_chart(fig1)

    st.markdown('---')
    #-------------------------------------------------------
    #   Plot 2
    #-------------------------------------------------------

    st.header('Vergelijking Top 5 Niet-Vertraagde Landen')

    # Voeg selectievakjes toe voor gate change filters
    toggle_time = st.radio("Selecteer wat je wilt zien", ('All Gate Changes', 'All Inbound/Outbound'), index=0)
    show_all_time = st.toggle("Laat alles zien")

    fig2 = make_subplots(rows=1, cols=2, subplot_titles=("Top 5 landen 'eerder dan gepland'",  "Top 5 landen 'Precies op tijd'"))

    # Logica om "Alles" te tonen
    if show_all_time:
        fig2.add_trace(go.Histogram(x=eerder[eerder['Org/Des'].isin(top_5_landen_eerder)]['Org/Des'], name='eerder'), 
                    row=1, col=1)
        fig2.add_trace(go.Histogram(x=precies[precies['Org/Des'].isin(top_5_landen_vertraagd)]['Org/Des'], name='precies'), 
                    row=1, col=2)

    else:
        # Logica om "Gate Changes" te tonen
        if toggle_time == 'All Gate Changes':
            show_gate_not_changed_time = st.checkbox('Gate is niet veranderd', value=True)
            show_gate_changed_time = st.checkbox('Gate is veranderd', value=False)

            if show_gate_not_changed_time:
                fig2.add_trace(go.Histogram(x=eerder[(eerder['Org/Des'].isin(top_5_landen_eerder)) & 
                                                        (eerder['GAT'] == eerder['TAR'])]['Org/Des'], 
                                            name='Gate has not been changed',
                                            marker_color=color_not_changed,
                                            legendgroup='Gate Status Time',
                                            showlegend = True),  
                                row=1, col=1)
                fig2.add_trace(go.Histogram(x=precies[(precies['Org/Des'].isin(top_5_landen_precies)) & 
                                                        (precies['GAT'] == precies['TAR'])]['Org/Des'],
                                            name='Gate has not been changed',
                                            marker_color=color_not_changed,
                                            legendgroup='Gate Status Time',
                                            showlegend = False),  
                                row=1, col=2)

            if show_gate_changed_time:
                fig2.add_trace(go.Histogram(x=eerder[(eerder['Org/Des'].isin(top_5_landen_eerder)) & 
                                                        (eerder['GAT'] != eerder['TAR'])]['Org/Des'],
                                            name='Gate has been changed',
                                            marker_color=color_changed,
                                            legendgroup='Gate Status Time',
                                            showlegend = True),  
                                row=1, col=1)
                fig2.add_trace(go.Histogram(x=precies[(precies['Org/Des'].isin(top_5_landen_precies)) & 
                                                        (precies['GAT'] != precies['TAR'])]['Org/Des'], 
                                            name='Gate has been changed',
                                            marker_color=color_changed,
                                            legendgroup='Gate Status Time',
                                            showlegend = False),  
                                row=1, col=2)
                
        # Logica om "Inbound en Outbound" vluchten te tonen
        elif toggle_time == 'All Inbound/Outbound':
            show_inbound_time = st.checkbox('Inkomende vluchten', value=True)
            show_outbound_time = st.checkbox('Uitgaande vluchten', value=False)

            if show_inbound_time:
                fig2.add_trace(go.Histogram(x=eerder[(eerder['Org/Des'].isin(top_5_landen_eerder)) & 
                                                        (eerder['LSV'] == 'Inbound')]['Org/Des'], 
                                            name='Inbound',
                                            marker_color=color_not_changed,
                                            legendgroup='Inbound Time',
                                            showlegend = True),  
                                row=1, col=1)
                fig2.add_trace(go.Histogram(x=precies[(precies['Org/Des'].isin(top_5_landen_precies)) & 
                                                        (precies['LSV'] == 'Inbound')]['Org/Des'], 
                                            name='Inbound',
                                            marker_color=color_not_changed,
                                            legendgroup='Inbound Time',
                                            showlegend = False),  
                                row=1, col=2)

            if show_outbound_time:
                fig2.add_trace(go.Histogram(x=eerder[(eerder['Org/Des'].isin(top_5_landen_eerder)) & 
                                                        (eerder['LSV'] == 'Outbound')]['Org/Des'], 
                                            name='Outbound',
                                            marker_color=color_changed,
                                            legendgroup='Inbound Time',
                                            showlegend = True), 
                                row=1, col=1)
                fig2.add_trace(go.Histogram(x=precies[(precies['Org/Des'].isin(top_5_landen_precies)) & 
                                                        (precies['LSV'] == 'Outbound')]['Org/Des'], 
                                            name='Outbound',
                                            marker_color=color_changed,
                                            legendgroup='Inbound Time',
                                            showlegend = False),  
                                row=1, col=2)

    fig2.update_yaxes(matches='y')
    fig2.update_xaxes(categoryorder='total descending')
    fig2.update_layout(barmode='stack', title_text="Vergelijking Top 5 optijd landen")

    st.plotly_chart(fig2)

    st.markdown('---')
    #-------------------------------------------------------
    #   Plot 3
    #-------------------------------------------------------

    # Kleuren selectie voor 'optijd', 'eerder' en 'vertraagd
    color_optijd = '#00ff00'
    color_eerder = '#0000ff'
    color_vertraagd = '#ff0000'

    @st.cache_data
    def beschikbare_landen(datum):
        # Filter continenten op basis van de datum
        landen_met_data = merge_df[merge_df['STD'] == datum]['Country'].unique()
        return landen_met_data

    @st.cache_data
    def df_change(continenten, datum):
        # Haal de gegevens op voor de geselecteerde continenten en datum
        change = merge_df[(merge_df['Country'].isin(continenten)) & (merge_df['STD'] == datum)]
        return change

    # Knop om een datum te selecteren
    start_date = st.date_input('Selecteer datum waarop je wilt kijken', datetime.date(2019,1,1), 
        min_value = datetime.date(2019, 1, 1), max_value = datetime.date(2020,12,31), format = 'DD/MM/YYYY')
    formatted_start_date = start_date.strftime('%d/%m/%Y')  # Zet de datum om naar de gewenste indeling

    # Haal continenten met data op voor de geselecteerde datum
    beschikbare_landen = beschikbare_landen(formatted_start_date)
    continenten = wereld_df[wereld_df['Country'].isin(beschikbare_landen)]['Continent'].unique()

    # Multibox om een bepaalde continent te selecteren
    geselecteerde_continenten = st.multiselect(
        'Selecteer Continent(en)', 
        continenten,
        default = continenten[:3]
    )

    # Haal de gegevens op voor de geselecteerde periode en continenten
    continent_df = df_change(wereld_df[wereld_df['Continent'].isin(geselecteerde_continenten)]['Country'], formatted_start_date)

    # Zet data om naar maatschappij op basis van vluchtnummer
    maatschappij_df = continent_df
    maatschappij_df['FLT'] = maatschappij_df['FLT'].str.replace(r'\d+', '', regex=True)
    maatschappij_df = maatschappij_df[maatschappij_df['FLT'] != 'LX'] # LX wordt hier eruit gefilterd, omdat het een grote maatschappij is
    filtered_df = continent_df
    filtered_df['FLT'] = filtered_df['FLT'].str.replace(r'\d+', '', regex=True) 
    filtered_df = filtered_df[filtered_df['FLT'] == 'LX'] # DataFrame voor alleen LX (grote maatschappij), krijgt eigen plot

    fig3 = make_subplots(rows=1, cols=2, subplot_titles=("Data voor Swiss Int. Air Lines",  "Overige Maatschappijen"))

    # Maakt plot voor LX data
    fig3.add_trace(go.Histogram(
        x=filtered_df[filtered_df['STA_STD_ltc'] > filtered_df['ATA_ATD_ltc']]['FLT'], 
        name='Eerder dan gepland',
        marker_color= color_eerder,
        legendgroup='Eerder',
        showlegend = True
    ), row = 1, col = 1)
    fig3.add_trace(go.Histogram(
        x=filtered_df[filtered_df['STA_STD_ltc'] == filtered_df['ATA_ATD_ltc']]['FLT'], 
        name='Precies optijd',
        marker_color = color_optijd,
        legendgroup='Optijd',
        showlegend = True
    ), row = 1, col = 1)
    fig3.add_trace(go.Histogram(
        x=filtered_df[filtered_df['STA_STD_ltc'] < filtered_df['ATA_ATD_ltc']]['FLT'], 
        name='Vertraagd',
        marker_color= color_vertraagd,
        legendgroup='Vertraagd',
        showlegend = True
    ), row = 1, col = 1)

    # Maakt plot voor overige maatschappijen
    fig3.add_trace(go.Histogram(
        x=maatschappij_df[maatschappij_df['STA_STD_ltc'] > maatschappij_df['ATA_ATD_ltc']]['FLT'], 
        name='Eerder dan gepland',
        marker_color = color_eerder,
        legendgroup='Eerder',
        showlegend = True
    ), row = 1, col = 2)
    fig3.add_trace(go.Histogram(
        x=maatschappij_df[maatschappij_df['STA_STD_ltc'] == maatschappij_df['ATA_ATD_ltc']]['FLT'], 
        name='Precies optijd',
        marker_color= color_optijd,
        legendgroup='Optijd',
        showlegend = True
    ), row = 1, col = 2)
    fig3.add_trace(go.Histogram(
        x=maatschappij_df[maatschappij_df['STA_STD_ltc'] < maatschappij_df['ATA_ATD_ltc']]['FLT'], 
        name='Vertraagd',
        marker_color=color_vertraagd,
        legendgroup='Vertraagd',
        showlegend = True
    ), row = 1, col = 2)
    fig3.update_xaxes(categoryorder='total descending')
    fig3.update_layout(barmode='stack', title_text="Geplande gegevens per luchtvaartmaatschappij voor geselecteerde continent(en)")

    st.plotly_chart(fig3)

    #--------------------------------------
    #   Plot 4
    #--------------------------------------

    # Kijkt naar bovenstaande geselecteerde continent en laad de mogelijke landen in
    beschikbaar_land = continent_df[continent_df['Country'].isin(beschikbare_landen)]['Country'].unique()
    geselecteerde_landen = st.multiselect(
        'Selecteer Continent(en)', 
        beschikbaar_land,
        default = beschikbaar_land[:3]
    )

    # Haal de gegevens op voor de geselecteerde periode en continenten
    country_df = df_change(geselecteerde_landen, formatted_start_date)

    # Zet data om naar maatschappij op basis van vluchtnummer
    maatschappij_country_df = country_df
    maatschappij_country_df['FLT'] = maatschappij_country_df['FLT'].str.replace(r'\d+', '', regex=True)
    maatschappij_country_df = maatschappij_country_df[maatschappij_country_df['FLT'] != 'LX'] # LX wordt hier eruit gefilterd, omdat het een grote maatschappij is
    filtered_country_df = country_df
    filtered_country_df['FLT'] = filtered_country_df['FLT'].str.replace(r'\d+', '', regex=True) 
    filtered_country_df = filtered_country_df[filtered_country_df['FLT'] == 'LX'] # DataFrame voor alleen LX (grote maatschappij), krijgt eigen plot

    fig4 = make_subplots(rows=1, cols=2, subplot_titles=("Data voor Swiss Int. Air Lines",  "Overige Maatschappijen"))

    # Maakt plot voor LX data
    fig4.add_trace(go.Histogram(
        x=filtered_country_df[filtered_country_df['STA_STD_ltc'] > filtered_country_df['ATA_ATD_ltc']]['FLT'], 
        name='Eerder dan gepland',
        marker_color= color_eerder,
        legendgroup='Eerder',
        showlegend = True
    ), row = 1, col = 1)
    fig4.add_trace(go.Histogram(
        x=filtered_country_df[filtered_country_df['STA_STD_ltc'] == filtered_country_df['ATA_ATD_ltc']]['FLT'], 
        name='Precies optijd',
        marker_color = color_optijd,
        legendgroup='Optijd',
        showlegend = True
    ), row = 1, col = 1)
    fig4.add_trace(go.Histogram(
        x=filtered_country_df[filtered_country_df['STA_STD_ltc'] < filtered_country_df['ATA_ATD_ltc']]['FLT'], 
        name='Vertraagd',
        marker_color= color_vertraagd,
        legendgroup='Vertraagd',
        showlegend = True
    ), row = 1, col = 1)

    # Maakt plot voor overige maatschappijen
    fig4.add_trace(go.Histogram(
        x=maatschappij_country_df[maatschappij_country_df['STA_STD_ltc'] > maatschappij_country_df['ATA_ATD_ltc']]['FLT'], 
        name='Eerder dan gepland',
        marker_color = color_eerder,
        legendgroup='Eerder',
        showlegend = True
    ), row = 1, col = 2)
    fig4.add_trace(go.Histogram(
        x=maatschappij_country_df[maatschappij_country_df['STA_STD_ltc'] == maatschappij_country_df['ATA_ATD_ltc']]['FLT'], 
        name='Precies optijd',
        marker_color= color_optijd,
        legendgroup='Optijd',
        showlegend = True
    ), row = 1, col = 2)
    fig4.add_trace(go.Histogram(
        x=maatschappij_country_df[maatschappij_country_df['STA_STD_ltc'] < maatschappij_country_df['ATA_ATD_ltc']]['FLT'], 
        name='Vertraagd',
        marker_color=color_vertraagd,
        legendgroup='Vertraagd',
        showlegend = True
    ), row = 1, col = 2)
    fig4.update_xaxes(categoryorder='total descending')
    fig4.update_layout(barmode='stack', title_text="Geplande gegevens per luchtvaartmaatschappij voor geselecteerde land(en)")

    st.plotly_chart(fig4)

    return load_tab1