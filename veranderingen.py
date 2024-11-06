# veranderingen tot nu toe (moet mooi laten zien worden met tekst en video's en foto's. eventueel code aanpassingen laten zien waarnodig)
# - Layout van de totale streamlit app
# - Tab namen veranderd en van positie veranderd
# - Blad 1 plots aangepast zodat de juiste data te zien is (uitgaand ook echt uitgaand, vertraging per uur ook echt per uur per land)
# - Blad 2 periode keuze toegevoegd inplaats van per dag
# - blad 2 verhoudingstabel toegevoegd om een beter beeld te krijgen van de vertragingskans per land aan de hand van 
# het aantal vluchten in de periode
# - Blad 3 (eerdere laadtijd van 36,95 seconde)

import streamlit as st
import pandas as pd
from PIL import Image

def load_verandering():
    st.header("Aanpassingen tenopzichte van versie 1:")
     # Toggle voor inbound of outbound selecteren
    veranderingen = st.radio("Selecteer welk tabblad je wilt zien", options=["Layout", "Land v2", "Luchtvaartmaatschappij v2", "Kaart v2"])

    if veranderingen == "Land v2":
        st.header("Land-tabblad aanpassingen")
        st.markdown('---')
        land = Image.open('./images/land.png')
        top = Image.open('./images/top.png')

        st.subheader("Grote veranderingen")
        st.image(land)
        st.image(top, caption='Veranderingen van de eerste 4 grafieken. Blauw is de layout aanpassingen, Rood is de oude data, \
                    groen is de nieuwe data')

        st.write("In bovenstaande afbeeldingen zijn veel aanpassingen geweest. Als eerste is de layout veranderd (in blauw). Eerst \
        waren de grafieken onder elkaar geplaatst. Door de layout aanpassing die eerder is besproken onder knop 'layout' konden \
        de grafieken doormiddel van kolommen naast en onder elkaar geplaatst worden zodat alles er overzichtelijker uit zal zien. \
        Bijna alle data is in één keer te zien per land. Daarnaast klopte heel erg veel data in de grafieken niet. Dit is aangegeven \
        in rood. Bij de 3e grafiek over drukte per uur van een bepaald land werd de data ingeladen van de drukte per uur over alle \
        landen dit was na het juist filteren weer rechtgezet. Nu geeft de grafiek hoeveel vluchten er per uur vertrekken van een \
        geselecteerd land. Hiermee kan een betere conclusie gemaakt worden over de drukte van een bepaald land per uur. Dit zelfde \
        probleem was er ook met grafiek 5 en grafiek 6 over de seizoensgebonden drukte en drukte per dag. Dit was ook over alle \
        landen samen genomen.")

        st.markdown("---")

        st.subheader("Nieuwe functie")
        nieuw = Image.open('./images/Screenshot_66.png')

        st.image(nieuw, caption='Nieuwe functie voor alle grafieken. Filteren op in- of uitgaande vluchten')
        st.write("Er is naast het juist filteren van de data ook een nieuwe functie toe. Er kan met één knop makkelijk gefilterd worden \
        op in- of uitgaande vluchten. Hierdoor kan er een beter beeld gevormt worden over de drukte van een bepaald land en waardoor \
        het eventueel veroorzaakt wordt.")
        st.markdown("---")

    elif veranderingen == "Luchtvaartmaatschappij v2":
        st.header("Luchtvaartmaatschappij-tabblad aanpassingen")
        st.markdown('---')

        verwijderd1 = Image.open('./images/Screenshot_49.png')
        verwijderd2 = Image.open('./images/Screenshot_50.png')
        luchtvaart = Image.open('./images/luchtvaartmaatschapij.png')
        kalender = Image.open('./images/kalender.png')

        code_kalender = '''@st.cache_data
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
beschikbare_landen = beschikbare_landen(formatted_start_date, formatted_end_date)'''

        st.subheader("Verwijderingen")
        col1, col2 = st.columns([1,2])
        with col1:
            st.image(verwijderd1, width=400, caption='Verwijderde grafieken')
        with col2:
            st.image(verwijderd2, width=400, caption='Verwijderde grafieken')

        st.write("Voorheen was op de tabblad 'Top 5' hier de twee bovenstaande grafieken te zien. De data die hierin is geplaatst \
        en de manier waarop het gefilterd wordt is goed gedaan, alleen voegt het niet veel toe aan het verhaal die de dashboard nu \
        wilt vertellen. Hierdoor is er gekozen om deze data uit de dashboard te halen om uiteindelijk een beter verhaal te kunnen \
        vertellen.")
        st.markdown("---")


        st.subheader("Kalender upgrade")
        st.image(kalender, width=700, caption='Verandering in kalender van per dag bekijken, naar periode. Rood is het oude, \
                groen is het nieuwe.')
        st.write("In versie 1 kon de data alleen gefilterd worden per dag. Dit is veranderd naar kalender functie waarin de periode \
        aangegeven kan worden. Dit is gedaan met onderstaande code. Wat opvalt is dat er gefilterd wordt met twee data binnen \
        beschikbare_landen(), 'start_datum' en 'eind_datum'. Deze filtering zorgt voor de periode aanduiding van de bijbehorende \
        grafiek.")
        st.code(code_kalender, language="python")


        st.markdown("---")
        st.subheader("Data toevoeging")

        st.image(luchtvaart, width=1000, caption='Verandering naar het luchtvaart gedeelte. Rood is het oude, groen \
                            het nieuwe. Daarnaast is een toevoeging gedaan van een verhoudingstabel')
        st.write("Hierin is heel erg veel veranderd. Ten eerste is er een knop toegevoegd om te filteren op ingaande of uitgaande \
        vluchten. Hierdoor kan er een betere conclusie getrokken worden over welke luchtvaartmaatschappij er gekozen kan worden \
        als men op vakantie gaat of terug gaat naar huis. Daarnaast is de grafiek waarin 'LX' ookwel 'Swiss Airline' in staat \
        samengevoegd met de andere grafiek. Dit komt omdat er naast de grafiek een verhoudingstabel geplaatst is waarin te zien \
        is hoeveel vluchten een bepaalde luchtvaartmaatschappij heeft en hoeveel hiervan vertraagd zijn. Hierdoor is de grafiek \
        een visualisatie van de tabel.") 

        st.markdown('---')    

        st.subheader("Toevoeging")
        Luchthaven = Image.open('./images/Screenshot_70.png')
        st.image(Luchthaven, caption='Ratio vertraagde vliegtuigen per land per luchthaven')
        st.write("Deze plot is toegevoegd om de ratio van de vertraging per luchthaven in het land te laten zien. Deze toevoeging \
        is erbij gezet om de rode draad in het verhaal te verbeteren. Op deze manier kan de gebruiker een betere beslissing maken \
        over het onderwerp")

    elif veranderingen == "Kaart v2":
        st.header("Kaart-tabblad aanpassingen")
        st.markdown('---')
        st.subheader("Verwijderingen")

        kaarten = Image.open('./images/Screenshot_57.png')
        col1, col2 = st.columns(2)

        with col1:
            st.image(kaarten, caption='Verwijderde grafieken')
        with col2:
            st.write("In bovenstaande foto is te zien dat er vanuit voorheen genoemde tabblad 'Beste route' nu een paar grafieken zijn \
            verwijderd. Deze zijn verwijderd omdat deze grafieken los staan qua data dan de andere datasets. Hierdoor kan er niet mooi \
            één verhaal verteld worden. Werd er bij de andere datasets alleen naar de data gekeken van Nederland naar Barcelona dan \
            had deze dataset meer kunnen vertellen. Helaas is het onderwerp veranderd en is er dan ook gekozen om deze grafieken niet \
            in het dashboard te laten.")

        st.markdown("---")
        st.subheader("Kaart aanpassingen")
        kaart = Image.open('./images/kaart.png')
        code_ratio = '''totaal_vluchten_per_luchthaven = merge.groupby('ICAO')['Airport ID'].value_counts()

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
    ratio_per_luchthaven['Ratio (%)'] = (ratio_per_luchthaven['Ratio'] * 100).round(2)'''

        st.image(kaart, caption = 'Aanpassing van de markers van de kaart')
        st.write("De kaart is aangepast om de vliegvelden te laten zien met een kleur aanduiding over de ratio vertraagde vliegtuigen. \
        Deze ratio is gebasseerd over het totaal aantal vluchten dat in de dataset naar één bepaald vliegveld is gegaan, ongeacht \
        ingaand of uitgaand, en dan te kijken naar hoeveel vluchten er vertraagd zijn. Daarnaast is de kaart ook vergroot, zodat de \
        kaart beter leesbaar is in de huidige layout. De manier om deze ratio te berekenen is met onderstaande code gedaan. Hier is te \
        zien dat er een dataframe is genaamd merge. Hier zitten alle gegevens in over alle vluchten per land per luchthaven. De \
        luchthavenafkortingen staan in kolom 'ICAO'. Hierbij worden daarna alle 'Airport ID's' geteld om zo het aantal vluchten te \
        berekenen. Dit is op deze manier gedaan omdat na veel onderzoek het duidelijk was dat er altijd een vlucht in het dataframe \
        staat. Hierdoor was dit een makkelijke maatstaaf om het totaal aantal vluchten te tellen. Daarna is de dataframe gefilterd \
        op alleen de vluchten die later dan gepland zijn aangekomen. Dit is ongeacht ingaand of uitgaande vluchten. Dit wordt dan \
        gedeeltdoor elkaar gedaan om zo op het ratio vertraagde vluchten vergeleken met alle vluchten te berekenen.")

        st.code(code_ratio, language="python")
        st.markdown("---")
    else: 
        st.header("Overige aanpassingen")
        st.markdown("---")
        st.subheader("Layout aanpassingen")
        # Plaats grafiek en tabel naast elkaar
        col1, col2 = st.columns([1,2])

        layout = Image.open('./images/layout.png')
        code_layout = '''st.set_page_config( page_title='Vluchten Informatie',
                        page_icon="✈️",
                        layout = "wide",
                        initial_sidebar_state = "auto"
                    )'''

        st.image(layout, caption='Layout verandering. Rood is de oude layout, Groen de nieuwe')

        st.write("Vanuit het oude dashboard was er ook een layout verandering. Er is gekozen voor een brede layout zodat de plotten \
        die gemaakt zijn beter tot hun recht komen. Hierdoor is de het een stuk overzichtelijker geworden en beter leesbaar. Bij \
        bijvoorbeeld het tabblad van 'Land' konden alle 6 de plotten over de vertraging in en uitgaand beter naast elkaar gezet \
        worden om sneller te vergelijken. Bij het tabblad van 'Luchtvaartmaatschappij' werd dit gebruikt om een verhoudingstabel naast \
        één van de plotten te plaatsen. Deze aanpassing is met onderstaande code gemaakt. Hierbij is te zien dat bij de layout is \
        gekozen voor 'wide'. Hierbij is ook gekozen om de side_bar_state op 'auto' te zetten. Hierdoor zal sidebar meteen zichtbaar \
        zijn op de computer, maar niet meteen op de telefoon wanneer deze app op de telefoon bekeken wordt.")

        st.code(code_layout, language="python")
        
        st.markdown("---")
        st.subheader("Sidebar toevoeging")

        # Plaats grafiek en tabel naast elkaar
        col1, col2 = st.columns([1,2])

        with col1:
            sidebar = Image.open('./images/Screenshot_58.png')
            st.image(sidebar, caption='Sidebar toevoeging')
        with col2:
            st.write('Er is een Sidebar toegevoegd om makkelijk tussen deze pagina en de app te wisselen. Hierdoor is er duidelijk wat \
            er veranderd is zodra er op de "Veranderingen van de app" knop gedrukt wordt en kan de nieuwe app gezien worden wanneer er \
            op "Nieuwe app" gedrukt wordt.')

        st.markdown("---")
        st.subheader("Titel en onderwerp verandering")

        # Plaats grafiek en tabel naast elkaar
        col1, col2 = st.columns([1,2])

        with col1:
            sidebar = Image.open('./images/titel.png')
            st.image(sidebar, caption='Verandering van de namen van de tabs en titel toevoeging. Rood is het oude, groen is het nieuwe')
        with col2:
            st.write('Tijdens de eerste presentatie van dit dashboard werd er als feedback terug gegeven dat er geen rode draad in het \
            verhaal zat. Dit klopte omdat er meer gekeken werd naar wat er met de data gedaan kon worden. Na overleg is er voor het \
            onderwerp "Vertraging analyse" gekozen. Grotendeels van de data verwerking die was gedaan kon hiervoor gebruikt worden om \
            zo een beter verhaal neer te zetten. Het tabblad "Top 5" is veranderd naar "Luchtvaartmaatschappij", "vertraging analyse" \
            is veranderd naar "Land" en "Beste route" is veranderd naar "Kaart". Alle data die te zien was in die tabbladen zijn in \
            basis hetzelfde. Dit dashboard heeft dan nu ook als doel om een betere vakantie bestemming te kiezen op basis van de \
            vertragingen per land. Daarnaast kan er ook een besluit genomen worden om welke tijd om welke tijd van de dag er het beste \
            vertrokken kan worden. Zodra het land is uitgekozen kan er besloten worden welk luchtvaartmaatschappij het beste past bij \
            het land en de periode waarop vertrokken wordt.')

        st.markdown("---")

        st.subheader("Eventuele veranderingen voor de toekomst")
        st.write("Een grote verandering die gemaakt moet worden voor de gebruiker is tekst bij elke plot om aan te geven \
        wat elke plot betekent. Dit zorgt ervoor dat het duidelijker voor de gebruiker is wat de app inhoudt en wat de gebruiker \
        per plot kan doen met de informatie die erin zit.")
    return load_verandering