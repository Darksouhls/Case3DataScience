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

    merge['FLT'] = merge['FLT'].str.replace(r'\d+', '', regex=True)
    totaal_vluchten_per_luchthaven = merge.groupby('ICAO')['Airport ID'].value_counts()

    # Bereken het aantal vertraagde vluchten per maatschappij
    delayed_vluchten = merge[merge['ATA_ATD_ltc'] > merge['STA_STD_ltc']]
    delayed_vluchten_per_luchthaven = delayed_vluchten.groupby('ICAO')['Airport ID'].value_counts()

    # Maak een DataFrame voor de vertragingsratio
    ratio_per_luchthaven = pd.DataFrame({
        'Totale vluchten': totaal_vluchten_per_luchthaven,
        'Vertraagde vluchten': delayed_vluchten_per_luchthaven
    }).fillna(0)  # Vul lege waarden op met 0 voor maatschappijen zonder vertragingen

    # Bereken de vertragingsratio
    ratio_per_luchthaven['Ratio'] = ratio_per_luchthaven['Vertraagde vluchten'] / ratio_per_luchthaven['Totale vluchten']
    ratio_per_luchthaven['Ratio (%)'] = (ratio_per_luchthaven['Ratio'] * 100).round(2)

    unique_icao_orgdes_ratio = unique_icao_orgdes.merge(ratio_per_luchthaven, on = 'ICAO', how = 'left')

    # kleur gedefinieerd op basis van ratio
    def get_delay_color(count):
        if count == 100:
            return 'darkred'
        elif count > 60:
            return 'red'
        elif count > 20:
            return 'orange'
        elif count > 0:
            return 'darkgreen'
        else:
            return 'green'

    #----------------------------------
    # Legenda code vanuit VA opdracht 3  
    #----------------------------------

    def add_categorical_legend(folium_map, title, colors, labels):
        if len(colors) != len(labels):
            raise ValueError("colors and labels must have the same length.")

        color_by_label = dict(zip(labels, colors))
        
        legend_categories = ""     
        for label, color in color_by_label.items():
            legend_categories += f"<li><span style='background:{color}'></span>{label}</li>"
            
        legend_html = f"""
        <div id='maplegend' class='maplegend'>
        <div class='legend-title'>{title}</div>
        <div class='legend-scale'>
            <ul class='legend-labels'>
            {legend_categories}
            </ul>
        </div>
        </div>
        """
        script = f"""
            <script type="text/javascript">
            var oneTimeExecution = (function() {{
                        var executed = false;
                        return function() {{
                            if (!executed) {{
                                var checkExist = setInterval(function() {{
                                        if ((document.getElementsByClassName('leaflet-top leaflet-right').length) || (!executed)) {{
                                            document.getElementsByClassName('leaflet-top leaflet-right')[0].style.display = "flex"
                                            document.getElementsByClassName('leaflet-top leaflet-right')[0].style.flexDirection = "column"
                                            document.getElementsByClassName('leaflet-top leaflet-right')[0].innerHTML += `{legend_html}`;
                                            clearInterval(checkExist);
                                            executed = true;
                                        }}
                                        }}, 100);
                            }}
                        }};
                    }})();
            oneTimeExecution()
            </script>
        """
    

        css = """

        <style type='text/css'>
        .maplegend {
            z-index:9999;
            float:right;
            background-color: rgba(255, 255, 255, 1);
            border-radius: 5px;
            border: 2px solid #bbb;
            padding: 10px;
            font-size:12px;
            positon: relative;
        }
        .maplegend .legend-title {
            text-align: left;
            margin-bottom: 5px;
            font-weight: bold;
            font-size: 90%;
            }
        .maplegend .legend-scale ul {
            margin: 0;
            margin-bottom: 5px;
            padding: 0;
            float: left;
            list-style: none;
            }
        .maplegend .legend-scale ul li {
            font-size: 80%;
            list-style: none;
            margin-left: 0;
            line-height: 18px;
            margin-bottom: 2px;
            }
        .maplegend ul.legend-labels li span {
            display: block;
            float: left;
            height: 16px;
            width: 30px;
            margin-right: 5px;
            margin-left: 0;
            border: 0px solid #ccc;
            }
        .maplegend .legend-source {
            font-size: 80%;
            color: #777;
            clear: both;
            }
        .maplegend a {
            color: #777;
            }
        </style>
        """

        folium_map.get_root().header.add_child(folium.Element(script + css))

        return folium_map

    #----------------------------------
    # Plot 1
    #-----------------------------------

    # Definieer de functie om markers te laden en de kaart te maken
    @st.cache_data
    def load_markers(data):
        # Maak een nieuwe kaart aan
        m = folium.Map(location=[20, 0], zoom_start=2)

        # Voeg markers toe aan de kaart
        for idx, row in data.iterrows():
            folium.Marker(
                location=[row['Latitude'], row['Longitude']],
                popup=(f"Airport: {row['ICAO']} "
                        f"Ratio: {row['Ratio (%)']}"),
                icon=folium.Icon(icon='plane', prefix='fa', color=get_delay_color(row['Ratio (%)']))
            ).add_to(m)
        
        m = add_categorical_legend(m, 'Ratio vertraging per vliegveld',
                             colors = ['darkred', 'red', 'orange', 'darkgreen', 'green'],
                           labels = ['100%', '> 60%', '> 20%', '> 0%', '0%'])
        return m

    # Roep de functie aan met de DataFrame als argument
    map_markers = load_markers(unique_icao_orgdes_ratio)

    # laat zien in streamlit
    st.title("Vliegvelden Kaart")
    st_data = st_folium(map_markers, width=1000)

    st.markdown('---')
    return load_tab3