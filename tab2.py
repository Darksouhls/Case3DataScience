import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import plotly.express as px
from sklearn.linear_model import LinearRegression

def load_tab2():
    @st.cache_data
    def load_data(bestandsnaam, scheidingsteken):
        try:
            schedule = pd.read_csv(bestandsnaam, sep=scheidingsteken)  # Lees het CSV-bestand
            return schedule  # Retourneer de DataFrame
        except FileNotFoundError:
            print(f'Bestand {bestandsnaam} niet gevonden.')
        except Exception as e:
            print(f'Fout bij het lezen van {bestandsnaam}: {e}')
        return None  # Retourneer None als er een fout is

    df = load_data('schedule_airport.csv', ',')  # Leest het CSV-bestand
    check = load_data('schedule_airport.csv', ',')  # Leest het CSV-bestand

    df['STA_STD_ltc'] = pd.to_datetime(df['STA_STD_ltc'], format = '%H:%M:%S' , errors = 'coerce')
    df['ATA_ATD_ltc'] = pd.to_datetime(df['ATA_ATD_ltc'], format = '%H:%M:%S' , errors = 'coerce')

    df['Delay_Minutes'] = (df['ATA_ATD_ltc'] - df['STA_STD_ltc']).dt.total_seconds() / 60
    df_cleaned = df.dropna(subset = ['Delay_Minutes'])

    df_cleaned['STD'] = pd.to_datetime(df_cleaned['STD'], format = '%d/%m/%Y', errors = 'coerce')
    daily_delay = df_cleaned.groupby(df_cleaned['STD'].dt.date)['Delay_Minutes'].mean()

    #-------------------------------------------------
    #  plot 1
    #-------------------------------------------------
    st.header('Voorspelling vluchten vertraging')
    # Bereid de data voor
    X = np.array(pd.to_datetime(daily_delay.index).astype('int64').values.reshape(-1, 1))  # Wijziging hier
    y = daily_delay.values

    # Maak een model voor de regressie
    model = LinearRegression()
    model.fit(X, y)

    # Voorspel de vertragingen van 2021
    future_dates = pd.date_range(start='2019-01-01', end='2021-12-31')
    X_future = np.array(future_dates.astype('int64').values.reshape(-1, 1))  # Wijziging hier
    predictions = model.predict(X_future)

    # Zet de voorspellingen om naar een DataFrame voor Plotly
    predictions_df = pd.DataFrame({
        'Datum': future_dates,
        'Voorspelling': predictions
    })

    # Maak een DataFrame voor de daadwerkelijke data
    actual_data_df = pd.DataFrame({
        'Datum': daily_delay.index,
        'Gemiddelde Vertraging': daily_delay.values
    })

    # Maak de Plotly Express plot
    fig = px.line(actual_data_df, x='Datum', y='Gemiddelde Vertraging', 
                title='Gemiddelde dagelijkse vluchtvertraging in de tijd met voorspelling voor 2021', 
                markers=True, labels={'Gemiddelde Vertraging': 'Gemiddelde Vertraging (Minuten)'})

    # Voeg de voorspelling toe aan de plot
    fig.add_scatter(x=predictions_df['Datum'], y=predictions_df['Voorspelling'], mode='lines', 
                    name='Voorspelling 2021', line=dict(color='red', dash='dash'))

    # Pas de layout aan
    fig.update_layout(xaxis_title='Datum', yaxis_title='Gemiddelde Vertraging (Minuten)', 
                    xaxis_tickangle=-45)
    fig.update_layout(width = 1000, height = 700)
    # Laat de plot zien in Streamlit
    st.plotly_chart(fig)

    st.markdown('---')
    #-------------------------------------------------------
    #   Data inladen nieuwe soort plotjes
    #-------------------------------------------------------    

    df2 = df_cleaned
    df2['month'] = df2['STD'].dt.to_period('M')
    monthly_data = df2.groupby('month').agg({
        'Delay_Minutes': 'mean',
        'FLT': 'count',
    })

    monthly_data['inbound_vluchten'] = (monthly_data['FLT'] * 0.4).astype(int)
    monthly_data['uitgaande_vluchten'] = monthly_data['FLT'] - monthly_data['inbound_vluchten']

    X = monthly_data['uitgaande_vluchten'].values.reshape(-1, 1)
    y = monthly_data['Delay_Minutes'].values
    model = LinearRegression()
    model.fit(X, y)

    toekomstige_maanden = pd.date_range(start='2021-01-01', end='2021-12-31', freq='M')
    toekomstige_vluchten = np.linspace(monthly_data['uitgaande_vluchten'].min(), monthly_data['uitgaande_vluchten'].max(), len(toekomstige_maanden))
    voorspellingen = model.predict(toekomstige_vluchten.reshape(-1, 1))
    voorspellingen = np.clip(voorspellingen, 0, None)

    #----------------------------------------------------------
    # Plot 2
    #---------------------------------------------------------

    # Maak een lijn grafiek vanuit de maandelijkse data
    fig1 = px.line(
        monthly_data, 
        x=monthly_data.index.astype(str), 
        y='Delay_Minutes', 
        title='Grafiek 1: Werkelijke Vertragingen voor Uitgaande Vluchten (2019-2020)',
        labels={'Delay_Minutes': 'Gemiddelde Vertraging (Minuten)', 'index': 'Maand'},
        markers=True
    )

    # Pas layout aan zodat het overzichtelijk is
    fig1.update_layout(
        xaxis_title='Maand',
        yaxis_title='Gemiddelde Vertraging (Minuten)',
        xaxis_tickangle=-45,
        template='plotly_white',
        title_font=dict(size=16),
        xaxis=dict(tickfont=dict(size=10)),
        yaxis=dict(tickfont=dict(size=12)),
        showlegend=False
    )

    # Voeg een grid toe
    fig1.update_xaxes(showgrid=True, gridwidth=0.5, gridcolor='lightgray')
    fig1.update_yaxes(showgrid=True, gridwidth=0.5, gridcolor='lightgray')

    st.plotly_chart(fig1)

    #------------------------------------------------------
    # Plot 3
    #------------------------------------------------------

    # Maak een DataFrame voor de voorspelde data
    voorspelling_df = pd.DataFrame({
        'Maand': toekomstige_maanden,
        'Voorspelde Vertragingen': voorspellingen
    })

    # Maak een lijn grafiek vanuit de voorspelde data
    fig2 = px.line(
        voorspelling_df, 
        x='Maand', 
        y='Voorspelde Vertragingen', 
        title='Grafiek 2: Voorspelde Vertragingen voor Uitgaande Vluchten (2021)',
        labels={'Voorspelde Vertragingen': 'Gemiddelde Vertraging (Minuten)', 'Maand': 'Maand'},
        markers=True
    )

    # Pas de layout aan
    fig2.update_traces(line=dict(color='tomato', dash='dash'))  # Zet de lijnstijl en kleur
    fig2.update_layout(
        xaxis_title='Maand',
        yaxis_title='Gemiddelde Vertraging (Minuten)',
        xaxis_tickangle=-45,
        template='plotly_white',
        title_font=dict(size=16),
        xaxis=dict(tickfont=dict(size=10)),
        yaxis=dict(tickfont=dict(size=12)),
        showlegend=True
    )

    # Voeg een grid toe
    fig2.update_xaxes(showgrid=True, gridwidth=0.5, gridcolor='lightgray')
    fig2.update_yaxes(showgrid=True, gridwidth=0.5, gridcolor='lightgray')

    # Voeg een legende toe
    fig2.update_layout(legend_title_text='Legende')

    st.plotly_chart(fig2)

    #----------------------------------------------------------
    # Plot 4
    #----------------------------------------------------------
    
    df2['departure_hour'] = df2['STA_STD_ltc'].dt.hour
    hourly_flights = df2.groupby('departure_hour')['FLT'].count()

    # Maak een DataFrame voor de uurlijkse vluchten
    hourly_flights_df = pd.DataFrame({
        'Uur van de Dag': hourly_flights.index,
        'Aantal Uitgaande Vluchten': hourly_flights.values
    })

    # Maak de Plotly Express plot
    fig3 = px.line(
        hourly_flights_df, 
        x='Uur van de Dag', 
        y='Aantal Uitgaande Vluchten', 
        title='Grafiek 3: Drukte per Uur (Uitgaande Vluchten)',
        labels={'Aantal Uitgaande Vluchten': 'Aantal Uitgaande Vluchten', 'Uur van de Dag': 'Uur van de Dag'},
        markers=True
    )

    # Pas de layout aan (zoals in je Matplotlib-code)
    fig3.update_traces(line=dict(color='green'))  # Zet de lijnkleur naar groen
    fig3.update_layout(
        xaxis_title='Uur van de Dag',
        yaxis_title='Aantal Uitgaande Vluchten',
        xaxis_tickangle=-45,
        template='plotly_white',
        title_font=dict(size=16),
        xaxis=dict(tickfont=dict(size=10)),
        yaxis=dict(tickfont=dict(size=12)),
        showlegend=False
    )

    # Voeg een grid toe
    fig3.update_xaxes(showgrid=True, gridwidth=0.5, gridcolor='lightgray')
    fig3.update_yaxes(showgrid=True, gridwidth=0.5, gridcolor='lightgray')

    st.plotly_chart(fig3)

    #-----------------------------------------------
    # Plot 5
    #-----------------------------------------------

    # Selecteer de top 3 maanden met de meeste uitgaande vluchten
    top_3_maanden = monthly_data['uitgaande_vluchten'].nlargest(3)

    # Maak een DataFrame voor de top 3 maanden
    top_3_df = pd.DataFrame({
        'Maand': top_3_maanden.index.astype(str),
        'Aantal Uitgaande Vluchten': top_3_maanden.values
    })

    # Maak de Plotly Express bar plot
    fig4 = px.bar(
        top_3_df, 
        x='Maand', 
        y='Aantal Uitgaande Vluchten', 
        title='Grafiek 4: Top 3 Drukste Maanden voor Uitgaande Vluchten (2019-2020)',
        labels={'Aantal Uitgaande Vluchten': 'Aantal Uitgaande Vluchten', 'Maand': 'Maand'},
        color_discrete_sequence=['orange']  # Zet de kleur naar oranje
    )

    # Pas de layout aan
    fig4.update_layout(
        xaxis_title='Maand',
        yaxis_title='Aantal Uitgaande Vluchten',
        xaxis_tickangle=-45,
        template='plotly_white',
        title_font=dict(size=16),
        xaxis=dict(tickfont=dict(size=10)),
        yaxis=dict(tickfont=dict(size=12))
    )

    fig4.update_xaxes(categoryorder='total descending')

    st.plotly_chart(fig4)

    #-------------------------------------------------------
    # Plot 6
    #-------------------------------------------------------

    # Functie om het seizoen te bepalen
    def get_season(date):
        month = date.month
        if month in [3, 4, 5]:
            return 'Lente'
        elif month in [6, 7, 8]:
            return 'Zomer'
        elif month in [9, 10, 11]:
            return 'Herfst'
        else:
            return 'Winter'

    # Voeg de kolom 'season' toe aan de DataFrame
    df2['season'] = df2['STD'].apply(get_season)

    # Groepeer de data op seizoen en tel het aantal vluchten per seizoen
    seasonal_flights = df2.groupby('season')['FLT'].count().reset_index()

    # Maak een Plotly Express bar plot
    fig5 = px.bar(
        seasonal_flights, 
        x='season', 
        y='FLT', 
        title='Grafiek 5: Seizoensgebonden Drukte',
        labels={'season': 'Seizoen', 'FLT': 'Aantal Vluchten'},
        color_discrete_sequence=['orange']
    )

    # Pas de layout aan
    fig5.update_layout(
        xaxis_title='Seizoen',
        yaxis_title='Aantal Vluchten',
        xaxis_tickangle=-45,
        template='plotly_white',
        title_font=dict(size=16),
        xaxis=dict(tickfont=dict(size=12)),
        yaxis=dict(tickfont=dict(size=12)),
        showlegend=False
    )

    # Plot de grafiek in Streamlit
    st.plotly_chart(fig5)

    #-----------------------------------------------
    # Plot 7
    #-----------------------------------------------

    # Voeg de kolom 'day_of_week' toe aan de DataFrame
    df2['day_of_week'] = df2['STD'].dt.day_name()

    # Groepeer de data op dag van de week en tel het aantal vluchten per dag
    weekly_flights = df2.groupby('day_of_week')['FLT'].count().reset_index()

    # Sorteer de dagen in de juiste volgorde
    days_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    weekly_flights['day_of_week'] = pd.Categorical(weekly_flights['day_of_week'], categories=days_order, ordered=True)
    weekly_flights = weekly_flights.sort_values('day_of_week')

    # Maak een Plotly Express bar plot
    fig6 = px.bar(
        weekly_flights, 
        x='day_of_week', 
        y='FLT', 
        title='Grafiek 6: Drukte per Dag van de Week (2019-2020)',
        labels={'day_of_week': 'Dag', 'FLT': 'Aantal Vluchten'},
        color_discrete_sequence=['lightgreen']
    )

    # Pas de layout aan
    fig6.update_layout(
        xaxis_title='Dag van de Week',
        yaxis_title='Aantal Vluchten',
        xaxis_tickangle=-45,
        template='plotly_white',
        title_font=dict(size=16),
        xaxis=dict(tickfont=dict(size=12)),
        yaxis=dict(tickfont=dict(size=12)),
        showlegend=False
    )

    # Plot de grafiek in Streamlit
    st.plotly_chart(fig6)



    return load_tab2