import pandas as pd

def landen():
    # Maak een dictionary met alle landen en continenten
    continenten_data = {
        'Continent': [
            'Afrika', 'Afrika', 'Afrika', 'Afrika', 'Afrika', 'Afrika', 'Afrika', 'Afrika', 'Afrika', 'Afrika', 'Afrika', 'Afrika', 'Afrika', 'Afrika', 'Afrika', 'Afrika', 'Afrika', 'Afrika', 'Afrika', 'Afrika', 
            'Afrika', 'Afrika', 'Afrika', 'Afrika', 'Afrika', 'Afrika', 'Afrika', 'Afrika', 'Afrika', 'Afrika', 'Afrika', 'Afrika', 'Afrika', 'Afrika', 'Afrika', 'Afrika', 'Afrika', 'Afrika', 'Afrika', 'Afrika',
            'Azië', 'Azië', 'Azië', 'Azië', 'Azië', 'Azië', 'Azië', 'Azië', 'Azië', 'Azië', 'Azië', 'Azië', 'Azië', 'Azië', 'Azië', 'Azië', 'Azië', 'Azië', 'Azië', 'Azië',
            'Azië', 'Azië', 'Azië', 'Azië', 'Azië', 'Azië', 'Azië', 'Azië', 'Azië', 'Azië', 'Azië', 'Azië', 'Azië', 'Azië', 'Azië', 
            'Europa', 'Europa', 'Europa', 'Europa', 'Europa', 'Europa', 'Europa', 'Europa', 'Europa', 'Europa', 'Europa', 'Europa', 'Europa', 'Europa', 'Europa', 'Europa', 'Europa', 'Europa', 'Europa', 'Europa',
            'Europa', 'Europa', 'Europa', 'Europa', 'Europa', 'Europa', 'Europa', 'Europa', 'Europa', 'Europa', 'Europa', 'Europa',
            'Noord-Amerika', 'Noord-Amerika', 'Noord-Amerika', 'Noord-Amerika', 'Noord-Amerika', 'Noord-Amerika', 'Noord-Amerika', 'Noord-Amerika', 'Noord-Amerika', 'Noord-Amerika', 'Noord-Amerika', 
            'Zuid-Amerika', 'Zuid-Amerika', 'Zuid-Amerika', 'Zuid-Amerika', 'Zuid-Amerika', 'Zuid-Amerika', 'Zuid-Amerika', 'Zuid-Amerika', 'Zuid-Amerika', 'Zuid-Amerika', 'Zuid-Amerika', 
            'Oceanië', 'Oceanië', 'Oceanië', 'Oceanië', 'Oceanië', 'Oceanië', 'Oceanië', 'Oceanië', 'Oceanië', 'Oceanië'
        ],
        'Land': [
            'Algerije', 'Angola', 'Benin', 'Botswana', 'Burkina Faso', 'Burundi', 'Kaapverdië', 'Kameroen', 'Centraal-Afrikaanse Republiek', 'Tsjaad', 'Comoren', 'Congo-Brazzaville', 'Congo-Kinshasa', 'Djibouti', 'Egypte', 'Equatoriaal-Guinea', 
            'Eritrea', 'Eswatini', 'Ethiopië', 'Gabon', 'Gambia', 'Ghana', 'Guinee', 'Guinee-Bissau', 'Ivoorkust', 'Kenia', 'Lesotho', 'Liberia', 'Libië', 'Madagaskar', 'Malawi', 'Mali', 'Mauritanië', 'Mauritius', 'Marokko', 'Mozambique', 
            'Namibië', 'Niger', 'Nigeria', 'Rwanda', 'Sao Tomé en Principe', 'Senegal', 'Seychellen', 'Sierra Leone', 'Somalië', 'Zuid-Afrika', 'Zuid-Soedan', 'Soedan', 'Tanzania', 'Togo', 'Tunesië', 'Oeganda', 'Zambia', 'Zimbabwe',
            'Afghanistan', 'Armenië', 'Azerbeidzjan', 'Bahrein', 'Bangladesh', 'Bhutan', 'Brunei', 'Cambodja', 'China', 'Cyprus', 'Georgië', 'India', 'Indonesië', 'Iran', 'Irak', 'Israël', 'Japan', 'Jordanië', 'Kazachstan', 'Koeweit', 
            'Kirgizië', 'Laos', 'Libanon', 'Maleisië', 'Maldiven', 'Mongolië', 'Myanmar', 'Nepal', 'Noord-Korea', 'Oman', 'Pakistan', 'Palestina', 'Filipijnen', 'Qatar', 'Rusland', 'Saoedi-Arabië', 'Singapore', 'Zuid-Korea', 'Sri Lanka', 'Syrië',
            'Tadzjikistan', 'Thailand', 'Oost-Timor', 'Turkmenistan', 'Verenigde Arabische Emiraten', 'Oezbekistan', 'Vietnam', 'Jemen',
            'Albanië', 'Andorra', 'Armenië', 'Oostenrijk', 'Azerbeidzjan', 'Wit-Rusland', 'België', 'Bosnië en Herzegovina', 'Bulgarije', 'Kroatië', 'Cyprus', 'Tsjechië', 'Denemarken', 'Estland', 'Finland', 'Frankrijk', 'Georgië', 
            'Duitsland', 'Griekenland', 'Hongarije', 'IJsland', 'Ierland', 'Italië', 'Kazachstan', 'Kosovo', 'Letland', 'Liechtenstein', 'Litouwen', 'Luxemburg', 'Malta', 'Moldavië', 'Monaco', 'Montenegro', 'Nederland', 'Noord-Macedonië', 
            'Noorwegen', 'Polen', 'Portugal', 'Roemenië', 'Rusland', 'San Marino', 'Servië', 'Slowakije', 'Slovenië', 'Spanje', 'Zweden', 'Zwitserland', 'Turkije', 'Oekraïne', 'Verenigd Koninkrijk', 'Vaticaanstad',
            'Antigua en Barbuda', 'Bahama\'s', 'Barbados', 'Belize', 'Canada', 'Costa Rica', 'Cuba', 'Dominica', 'Dominicaanse Republiek', 'El Salvador', 'Grenada', 'Guatemala', 'Haïti', 'Honduras', 'Jamaica', 'Mexico', 'Nicaragua', 
            'Panama', 'Saint Kitts en Nevis', 'Saint Lucia', 'Saint Vincent en de Grenadines', 'Trinidad en Tobago', 'Verenigde Staten',
            'Argentinië', 'Bolivia', 'Brazilië', 'Chili', 'Colombia', 'Ecuador', 'Guyana', 'Paraguay', 'Peru', 'Suriname', 'Uruguay', 'Venezuela',
            'Australië', 'Fiji', 'Kiribati', 'Marshall Eilanden', 'Micronesië', 'Nauru', 'Nieuw-Zeeland', 'Palau', 'Papoea-Nieuw-Guinea', 'Samoa', 'Salomonseilanden', 'Tonga', 'Tuvalu', 'Vanuatu'
        ]
    }    

    return continenten_data
