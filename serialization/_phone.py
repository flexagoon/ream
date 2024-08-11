def __format_phone(phone: str) -> str:
    phone = phone.replace(" ", "")
    if phone[0] == "+":
        phone = phone[1:]

    pattern = None
    code = ""
    for code_len in range(4, 0, -1):
        current_code = phone[:code_len]
        if current_code in __formats:
            code = current_code
            pattern = __formats[current_code]
            phone = phone[code_len:]
            break

    if pattern is None:
        return f"+{code} {phone}"

    formatted_phone = ""
    for i in range(len(pattern)):
        if pattern[i] == "X":
            formatted_phone += phone[0]
            phone = phone[1:]
        else:
            formatted_phone += pattern[i]

    return f"+{code} {formatted_phone}"


__formats = {
    "376": "XX XX XX",  # Andorra
    "971": "XX XXX XXXX",  # United Arab Emirates
    "93": "XXX XXX XXX",  # Afghanistan
    "1268": "XXX XXXX",  # Antigua & Barbuda
    "1264": "XXX XXXX",  # Anguilla
    "355": "XX XXX XXXX",  # Albania
    "374": "XX XXX XXX",  # Armenia
    "244": "XXX XXX XXX",  # Angola
    "54": None,  # Argentina
    "1684": "XXX XXXX",  # American Samoa
    "43": "X XXXXXXXX",  # Austria
    "61": "X XXXX XXXX",  # Australia
    "297": "XXX XXXX",  # Aruba
    "994": "XX XXX XXXX",  # Azerbaijan
    "387": "XX XXX XXX",  # Bosnia & Herzegovina
    "1246": "XXX XXXX",  # Barbados
    "880": "XX XXX XXX",  # Bangladesh
    "32": "XXX XX XX XX",  # Belgium
    "226": "XX XX XX XX",  # Burkina Faso
    "359": None,  # Bulgaria
    "973": "XXXX XXXX",  # Bahrain
    "257": "XX XX XXXX",  # Burundi
    "229": "XX XXX XXX",  # Benin
    "1441": "XXX XXXX",  # Bermuda
    "673": "XXX XXXX",  # Brunei Darussalam
    "591": "X XXX XXXX",  # Bolivia
    "599": None,  # Bonaire, Curaçao, Sint Eustatius & Saba
    "55": "XX XXXXX XXXX",  # Brazil
    "1242": "XXX XXXX",  # Bahamas
    "975": "XX XXX XXX",  # Bhutan
    "267": "XX XXX XXX",  # Botswana
    "375": "XX XXX XXXX",  # Belarus
    "501": None,  # Belize
    "243": "XX XXX XXXX",  # Congo (Dem. Rep.)
    "236": "XX XX XX XX",  # Central African Rep.
    "242": "XX XXX XXXX",  # Congo (Rep.)
    "41": "XX XXX XXXX",  # Switzerland
    "225": "XX XX XX XXXX",  # Côte d'Ivoire
    "682": None,  # Cook Islands
    "56": "X XXXX XXXX",  # Chile
    "237": "XXXX XXXX",  # Cameroon
    "86": "XXX XXXX XXXX",  # China
    "57": "XXX XXX XXXX",  # Colombia
    "506": "XXXX XXXX",  # Costa Rica
    "53": "X XXX XXXX",  # Cuba
    "238": "XXX XXXX",  # Cape Verde
    "357": "XXXX XXXX",  # Cyprus
    "420": "XXX XXX XXX",  # Czech Republic
    "49": "XXXX XXXXXXX",  # Germany
    "253": "XX XX XX XX",  # Djibouti
    "45": "XXXX XXXX",  # Denmark
    "1767": "XXX XXXX",  # Dominica
    "1809": "XXX XXXX",  # Dominican Rep.
    "213": "XXX XX XX XX",  # Algeria
    "593": "XX XXX XXXX",  # Ecuador
    "372": "XXXX XXXX",  # Estonia
    "20": "XX XXXX XXXX",  # Egypt
    "291": "X XXX XXX",  # Eritrea
    "34": "XXX XXX XXX",  # Spain
    "251": "XX XXX XXXX",  # Ethiopia
    "358": None,  # Finland
    "679": "XXX XXXX",  # Fiji
    "500": None,  # Falkland Islands
    "691": None,  # Micronesia
    "298": "XXX XXX",  # Faroe Islands
    "33": "X XX XX XX XX",  # France
    "241": "X XX XX XX",  # Gabon
    "44": "XXXX XXXXXX",  # United Kingdom
    "1473": "XXX XXXX",  # Grenada
    "995": "XXX XXX XXX",  # Georgia
    "594": None,  # French Guiana
    "233": "XX XXX XXXX",  # Ghana
    "350": "XXXX XXXX",  # Gibraltar
    "299": "XXX XXX",  # Greenland
    "220": "XXX XXXX",  # Gambia
    "224": "XXX XXX XXX",  # Guinea
    "590": "XXX XX XX XX",  # Guadeloupe
    "240": "XXX XXX XXX",  # Equatorial Guinea
    "30": "XXX XXX XXXX",  # Greece
    "502": "X XXX XXXX",  # Guatemala
    "1671": "XXX XXXX",  # Guam
    "245": "XXX XXXX",  # Guinea-Bissau
    "592": None,  # Guyana
    "852": "X XXX XXXX",  # Hong Kong
    "504": "XXXX XXXX",  # Honduras
    "385": "XX XXX XXX",  # Croatia
    "509": "XXXX XXXX",  # Haiti
    "36": "XXX XXX XXX",  # Hungary
    "62": "XXX XXXXXX",  # Indonesia
    "353": "XX XXX XXXX",  # Ireland
    "972": "XX XXX XXXX",  # Israel
    "91": "XXXXX XXXXX",  # India
    "246": "XXX XXXX",  # Diego Garcia
    "964": "XXX XXX XXXX",  # Iraq
    "98": "XXX XXX XXXX",  # Iran
    "354": "XXX XXXX",  # Iceland
    "39": "XXX XXX XXX",  # Italy
    "1876": "XXX XXXX",  # Jamaica
    "962": "X XXXX XXXX",  # Jordan
    "81": "XX XXXX XXXX",  # Japan
    "254": "XXX XXX XXX",  # Kenya
    "996": "XXX XXXXXX",  # Kyrgyzstan
    "855": "XX XXX XXX",  # Cambodia
    "686": "XXXX XXXX",  # Kiribati
    "269": "XXX XXXX",  # Comoros
    "1869": "XXX XXXX",  # Saint Kitts & Nevis
    "850": None,  # North Korea
    "82": "XX XXXX XXX",  # South Korea
    "965": "XXXX XXXX",  # Kuwait
    "1345": "XXX XXXX",  # Cayman Islands
    "856": "XX XX XXX XXX",  # Laos
    "961": "XX XXX XXX",  # Lebanon
    "1758": "XXX XXXX",  # Saint Lucia
    "423": "XXX XXXX",  # Liechtenstein
    "94": "XX XXX XXXX",  # Sri Lanka
    "231": "XX XXX XXXX",  # Liberia
    "266": "XX XXX XXX",  # Lesotho
    "370": "XXX XXXXX",  # Lithuania
    "352": "XXX XXX XXX",  # Luxembourg
    "371": "XXX XXXXX",  # Latvia
    "218": "XX XXX XXXX",  # Libya
    "212": "XX XXX XXXX",  # Morocco
    "377": "XXXX XXXX",  # Monaco
    "373": "XX XXX XXX",  # Moldova
    "382": None,  # Montenegro
    "261": "XX XX XXX XX",  # Madagascar
    "692": None,  # Marshall Islands
    "389": "XX XXX XXX",  # North Macedonia
    "223": "XXXX XXXX",  # Mali
    "95": None,  # Myanmar
    "976": "XX XX XXXX",  # Mongolia
    "853": "XXXX XXXX",  # Macau
    "1670": "XXX XXXX",  # Northern Mariana Islands
    "596": None,  # Martinique
    "222": "XXXX XXXX",  # Mauritania
    "1664": "XXX XXXX",  # Montserrat
    "356": "XX XX XX XX",  # Malta
    "230": "XXXX XXXX",  # Mauritius
    "960": "XXX XXXX",  # Maldives
    "265": "XX XXX XXXX",  # Malawi
    "52": None,  # Mexico
    "60": "XX XXXX XXXX",  # Malaysia
    "258": "XX XXX XXXX",  # Mozambique
    "264": "XX XXX XXXX",  # Namibia
    "687": None,  # New Caledonia
    "227": "XX XX XX XX",  # Niger
    "672": None,  # Norfolk Island
    "234": "XX XXXX XXXX",  # Nigeria
    "505": "XXXX XXXX",  # Nicaragua
    "31": "X XX XX XX XX",  # Netherlands
    "47": "XXXX XXXX",  # Norway
    "977": "XX XXXX XXXX",  # Nepal
    "674": None,  # Nauru
    "683": None,  # Niue
    "64": "XXXX XXXX",  # New Zealand
    "968": "XXXX XXXX",  # Oman
    "507": "XXXX XXXX",  # Panama
    "51": "XXX XXX XXX",  # Peru
    "689": None,  # French Polynesia
    "675": None,  # Papua New Guinea
    "63": "XXX XXX XXXX",  # Philippines
    "92": "XXX XXX XXXX",  # Pakistan
    "48": "XXX XXX XXX",  # Poland
    "508": None,  # Saint Pierre & Miquelon
    "1787": "XXX XXXX",  # Puerto Rico
    "970": "XXX XX XXXX",  # Palestine
    "351": "XXX XXX XXX",  # Portugal
    "680": None,  # Palau
    "595": "XXX XXX XXX",  # Paraguay
    "974": "XX XXX XXX",  # Qatar
    "262": "XXX XXX XXX",  # Réunion
    "40": "XXX XXX XXX",  # Romania
    "381": "XX XXX XXXX",  # Serbia
    "7": "XXX XXX XXXX",  # Russian Federation
    "250": "XXX XXX XXX",  # Rwanda
    "966": "XX XXX XXXX",  # Saudi Arabia
    "677": None,  # Solomon Islands
    "248": "X XX XX XX",  # Seychelles
    "249": "XX XXX XXXX",  # Sudan
    "46": "XX XXX XXXX",  # Sweden
    "65": "XXXX XXXX",  # Singapore
    "247": None,  # Saint Helena
    "386": "XX XXX XXX",  # Slovenia
    "421": "XXX XXX XXX",  # Slovakia
    "232": "XX XXX XXX",  # Sierra Leone
    "378": "XXX XXX XXXX",  # San Marino
    "221": "XX XXX XXXX",  # Senegal
    "252": "XX XXX XXX",  # Somalia
    "597": "XXX XXXX",  # Suriname
    "211": "XX XXX XXXX",  # South Sudan
    "239": "XX XXXXX",  # São Tomé & Príncipe
    "503": "XXXX XXXX",  # El Salvador
    "1721": "XXX XXXX",  # Sint Maarten
    "963": "XXX XXX XXX",  # Syria
    "268": "XXXX XXXX",  # Eswatini
    "1649": "XXX XXXX",  # Turks & Caicos Islands
    "235": "XX XX XX XX",  # Chad
    "228": "XX XXX XXX",  # Togo
    "66": "X XXXX XXXX",  # Thailand
    "992": "XX XXX XXXX",  # Tajikistan
    "690": None,  # Tokelau
    "670": None,  # Timor-Leste
    "993": "XX XXXXXX",  # Turkmenistan
    "216": "XX XXX XXX",  # Tunisia
    "676": None,  # Tonga
    "90": "XXX XXX XXXX",  # Turkey
    "1868": "XXX XXXX",  # Trinidad & Tobago
    "688": None,  # Tuvalu
    "886": "XXX XXX XXX",  # Taiwan
    "255": "XX XXX XXXX",  # Tanzania
    "380": "XX XXX XX XX",  # Ukraine
    "256": "XX XXX XXXX",  # Uganda
    "1": "XXX XXX XXXX",  # USA / Canada
    "598": "X XXX XXXX",  # Uruguay
    "998": "XX XXX XX XX",  # Uzbekistan
    "1784": "XXX XXXX",  # Saint Vincent & the Grenadines
    "58": "XXX XXX XXXX",  # Venezuela
    "1284": "XXX XXXX",  # British Virgin Islands
    "1340": "XXX XXXX",  # US Virgin Islands
    "84": None,  # Vietnam
    "678": None,  # Vanuatu
    "681": None,  # Wallis & Futuna
    "685": None,  # Samoa
    "383": "XXXX XXXX",  # Kosovo
    "967": "XXX XXX XXX",  # Yemen
    "27": "XX XXX XXXX",  # South Africa
    "260": "XX XXX XXXX",  # Zambia
    "263": "XX XXX XXXX",  # Zimbabwe
}
