
# ============================================================
# PROGETTO METEO
# File: dashboard.py
#
# Dashboard meteorologica realizzata con Streamlit e Plotly.
#
# Funzionalità:
# - Ricerca della città tramite Open-Meteo.
# - Meteo attuale.
# - Storico degli ultimi sette giorni.
# - Previsioni orarie e giornaliere.
# - Grafici organizzati in griglie responsive.
# - Analisi agricole: precipitazioni, ET0 e condizioni del suolo.
# - Tabella riepilogativa.
#
# Grafica:
# - Tema blu notte e azzurro.
# - Schede informative.
# - Grafici interattivi separati per categoria.
#
# IMPORTANTE:
# - Non modificare app.py.
# - Non modificare mereo_forecasting.py.
# - Il CSS esterno si trova in assets/css/style.css.
# ============================================================


# ============================================================
# IMPORTAZIONE DELLE LIBRERIE
# ============================================================

import base64
from pathlib import Path

import pandas as pd
import plotly.graph_objects as go
import requests
import streamlit as st


# ============================================================
# PERCORSI DEL PROGETTO
# ============================================================

CARTELLA_PROGETTO = Path(__file__).resolve().parent

# Percorso dell'immagine di sfondo della dashboard.
PERCORSO_SFONDO = (
    CARTELLA_PROGETTO
    / "assets"
    / "immagini"
    / "sfondo_terra.png"
)

# Percorso del foglio di stile CSS.
PERCORSO_CSS = (
    CARTELLA_PROGETTO
    / "assets"
    / "css"
    / "style.css"
)


# ============================================================
# CONFIGURAZIONE OPEN-METEO
# ============================================================

FORECAST_URL = "https://api.open-meteo.com/v1/forecast"

GEOCODING_URL = (
    "https://geocoding-api.open-meteo.com/v1/search"
)

# Giorni di storico e previsione.
PAST_DAYS = 7
FORECAST_DAYS = 16

TIMEOUT = 30


# ============================================================
# PALETTE DEI COLORI
# ============================================================

BLU_NOTTE = "#10243A"
BLU_PANNELLO = "#183650"
BLU_AZZURRO = "#38BDF8"
AZZURRO_CHIARO = "#7DD3FC"

BIANCO = "#F1F5F9"
TESTO_SECONDARIO = "#B8C9D9"

COLORE_TEMPERATURA = "#FB7185"
COLORE_MASSIMA = "#FB7185"
COLORE_MINIMA = "#60A5FA"

COLORE_PIOGGIA = "#38BDF8"
COLORE_VENTO = "#A78BFA"
COLORE_ET0 = "#FBBF24"
COLORE_SUOLO = "#34D399"
COLORE_UMIDITA = "#22D3EE"
COLORE_RADIAZIONE = "#F59E0B"


# ============================================================
# CARICAMENTO DELLO SFONDO
# ============================================================

# Converte l'immagine della Terra in Base64 per il CSS.
if PERCORSO_SFONDO.is_file():

    with open(PERCORSO_SFONDO, "rb") as file:
        SFONDO_BASE64 = base64.b64encode(
            file.read()
        ).decode("utf-8")

    SFONDO_CSS = (
        "background: "
        "linear-gradient("
        "rgba(10, 27, 45, 0.70), "
        "rgba(10, 27, 45, 0.82)"
        "), "
        f'url("data:image/png;base64,{SFONDO_BASE64}") '
        "center / cover fixed no-repeat;"
    )

else:

    SFONDO_CSS = (
        "background: linear-gradient("
        "135deg, #10243A 0%, #142D46 55%, #10243A 100%"
        ");"
    )


# ============================================================
# CONFIGURAZIONE DELLA PAGINA
# ============================================================

st.set_page_config(
    page_title="Progetto Meteo",
    page_icon="🌦️",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ============================================================
# CARICAMENTO DEL CSS ESTERNO
# ============================================================

try:

    with open(PERCORSO_CSS, "r", encoding="utf-8") as file:
        STILE_CSS = file.read()

except OSError as errore:

    st.error(
        "Impossibile caricare il foglio di stile CSS. "
        "Controlla che assets/css/style.css esista."
    )

    st.caption(f"Dettaglio tecnico: {errore}")
    st.stop()


# ============================================================
# APPLICAZIONE DELLO STILE
# ============================================================

st.markdown(
    f"""
    <style>
        {STILE_CSS}

        .stApp {{
            {SFONDO_CSS}
            color: {BIANCO};
        }}
    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# RICERCA DELLE CITTÀ
# ============================================================

@st.cache_data(ttl=3600)
def cerca_citta(nome_citta):
    """
    Cerca le località tramite Open-Meteo.

    I risultati vengono conservati in cache per un'ora.
    """

    parametri = {
        "name": nome_citta,
        "count": 5,
        "language": "it",
        "format": "json",
    }

    risposta = requests.get(
        GEOCODING_URL,
        params=parametri,
        timeout=TIMEOUT,
    )

    risposta.raise_for_status()

    return risposta.json().get("results", [])


# ============================================================
# DESCRIZIONE DELLE LOCALITÀ
# ============================================================

def descrivi_citta(citta):
    """
    Crea una descrizione leggibile della località.
    """

    nome = citta.get("name", "Località sconosciuta")
    area = citta.get("admin1") or citta.get("admin2") or ""
    paese = citta.get("country", "")

    parti = [nome]

    if area and area.lower() != nome.lower():
        parti.append(area)

    if paese:
        parti.append(paese)

    return " — ".join(parti)


# ============================================================
# RECUPERO DEL METEO
# ============================================================

@st.cache_data(ttl=900)
def recupera_previsioni(latitudine, longitudine):
    """
    Recupera meteo attuale, dati orari e dati giornalieri.

    La cache dura 15 minuti per evitare richieste ripetute
    quando Streamlit aggiorna la pagina.
    """

    parametri = {
        "latitude": latitudine,
        "longitude": longitudine,
        "timezone": "auto",
        "temperature_unit": "celsius",
        "wind_speed_unit": "kmh",
        "precipitation_unit": "mm",
        "past_days": PAST_DAYS,
        "forecast_days": FORECAST_DAYS,

        # Condizioni meteorologiche attuali.
        "current": (
            "temperature_2m,"
            "relative_humidity_2m,"
            "is_day,"
            "weather_code,"
            "precipitation,"
            "rain,"
            "wind_speed_10m,"
            "wind_direction_10m,"
            "wind_gusts_10m,"
            "cloud_cover"
        ),

        # Variabili orarie utili per il meteo e l'agricoltura.
        "hourly": (
            "temperature_2m,"
            "relative_humidity_2m,"
            "dew_point_2m,"
            "apparent_temperature,"
            "precipitation_probability,"
            "precipitation,"
            "rain,"
            "showers,"
            "snowfall,"
            "evapotranspiration,"
            "et0_fao_evapotranspiration,"
            "vapour_pressure_deficit,"
            "wind_speed_10m,"
            "wind_direction_10m,"
            "wind_gusts_10m,"
            "soil_temperature_0cm,"
            "soil_temperature_6cm,"
            "soil_temperature_18cm,"
            "soil_moisture_0_to_1cm,"
            "soil_moisture_1_to_3cm,"
            "soil_moisture_3_to_9cm,"
            "soil_moisture_9_to_27cm,"
            "soil_moisture_27_to_81cm"
        ),

        # Variabili giornaliere.
        "daily": (
            "weather_code,"
            "temperature_2m_max,"
            "temperature_2m_min,"
            "sunrise,"
            "sunset,"
            "daylight_duration,"
            "sunshine_duration,"
            "rain_sum,"
            "precipitation_sum,"
            "precipitation_hours,"
            "precipitation_probability_max,"
            "shortwave_radiation_sum,"
            "et0_fao_evapotranspiration"
        ),
    }

    risposta = requests.get(
        FORECAST_URL,
        params=parametri,
        timeout=TIMEOUT,
    )

    risposta.raise_for_status()

    return risposta.json()


# ============================================================
# CONVERSIONE DEI DATI IN DATAFRAME
# ============================================================

def crea_dataframe_orario(dati_orari):
    """
    Trasforma le variabili orarie in una tabella Pandas.
    """

    tabella = pd.DataFrame(dati_orari)

    # Converte le date in oggetti datetime.
    tabella["time"] = pd.to_datetime(tabella["time"])

    return tabella


def crea_dataframe_giornaliero(dati_giornalieri):
    """
    Trasforma le variabili giornaliere in una tabella Pandas.
    """

    tabella = pd.DataFrame(dati_giornalieri)

    tabella["time"] = pd.to_datetime(tabella["time"])

    return tabella


# ============================================================
# STILE COMUNE DEI GRAFICI
# ============================================================

def configura_grafico(
    grafico,
    titolo,
    titolo_asse_x,
    titolo_asse_y,
):
    """
    Applica uno stile uniforme ai grafici Plotly.
    """

    grafico.update_layout(
        title={
            "text": titolo,
            "font": {
                "size": 18,
                "color": BIANCO,
            },
        },
        xaxis_title=titolo_asse_x,
        yaxis_title=titolo_asse_y,
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font={
            "family": "Arial, sans-serif",
            "color": TESTO_SECONDARIO,
            "size": 12,
        },
        hovermode="x unified",
        autosize=True,
        margin={
            "l": 15,
            "r": 15,
            "t": 60,
            "b": 35,
        },
        legend={
            "orientation": "h",
            "yanchor": "bottom",
            "y": 1.02,
            "xanchor": "left",
            "x": 0,
        },
    )

    grafico.update_xaxes(
        showgrid=False,
        zeroline=False,
        linecolor="#31506A",
    )

    grafico.update_yaxes(
        showgrid=True,
        gridcolor="rgba(125, 211, 252, 0.12)",
        zeroline=False,
        linecolor="#31506A",
    )

    return grafico


# ============================================================
# GRAFICO A LINEE
# ============================================================

def crea_grafico_linea(
    date,
    valori,
    titolo,
    nome_serie,
    colore,
    nome_asse_y,
):
    """
    Crea un grafico a linee per una singola variabile.
    """

    grafico = go.Figure()

    grafico.add_trace(
        go.Scatter(
            x=date,
            y=valori,
            mode="lines",
            name=nome_serie,
            connectgaps=False,
            line={
                "color": colore,
                "width": 2.5,
            },
            hovertemplate=(
                "%{x|%d/%m %H:%M}<br>"
                "%{y:.1f}<extra></extra>"
            ),
        )
    )

    return configura_grafico(
        grafico,
        titolo,
        "Data e ora",
        nome_asse_y,
    )


# ============================================================
# GRAFICO A BARRE
# ============================================================

def crea_grafico_barre(
    date,
    valori,
    titolo,
    nome_serie,
    colore,
    nome_asse_y,
):
    """
    Crea un grafico a barre per dati giornalieri.
    """

    grafico = go.Figure()

    grafico.add_trace(
        go.Bar(
            x=date,
            y=valori,
            name=nome_serie,
            marker_color=colore,
            hovertemplate=(
                "Data: %{x|%d/%m}<br>"
                "%{y:.1f}<extra></extra>"
            ),
        )
    )

    return configura_grafico(
        grafico,
        titolo,
        "Giorno",
        nome_asse_y,
    )


# ============================================================
# GRAFICO DELLE TEMPERATURE GIORNALIERE
# ============================================================

def crea_grafico_temperature_giornaliere(tabella):
    """
    Confronta le temperature massime e minime giornaliere.
    """

    grafico = go.Figure()

    grafico.add_trace(
        go.Scatter(
            x=tabella["time"],
            y=tabella["temperature_2m_max"],
            mode="lines+markers",
            name="Massima",
            line={
                "color": COLORE_MASSIMA,
                "width": 2.5,
            },
            hovertemplate=(
                "%{x|%d/%m}<br>"
                "Massima: %{y:.1f} °C"
                "<extra></extra>"
            ),
        )
    )

    grafico.add_trace(
        go.Scatter(
            x=tabella["time"],
            y=tabella["temperature_2m_min"],
            mode="lines+markers",
            name="Minima",
            line={
                "color": COLORE_MINIMA,
                "width": 2.5,
            },
            hovertemplate=(
                "%{x|%d/%m}<br>"
                "Minima: %{y:.1f} °C"
                "<extra></extra>"
            ),
        )
    )

    return configura_grafico(
        grafico,
        "Temperature massime e minime",
        "Giorno",
        "Temperatura (°C)",
    )


# ============================================================
# GRAFICO DELLE PRECIPITAZIONI E DELL'ET0
# ============================================================

def crea_grafico_bilancio_idrico(tabella):
    """
    Confronta le precipitazioni e l'evapotraspirazione ET0.

    ET0 rappresenta l'evapotraspirazione di riferimento:
    non equivale automaticamente al fabbisogno della coltura.
    """

    grafico = go.Figure()

    grafico.add_trace(
        go.Bar(
            x=tabella["time"],
            y=tabella["precipitation_sum"],
            name="Precipitazioni",
            marker_color=COLORE_PIOGGIA,
            hovertemplate=(
                "Data: %{x|%d/%m}<br>"
                "Precipitazioni: %{y:.1f} mm"
                "<extra></extra>"
            ),
        )
    )

    grafico.add_trace(
        go.Scatter(
            x=tabella["time"],
            y=tabella["et0_fao_evapotranspiration"],
            mode="lines+markers",
            name="ET₀",
            line={
                "color": COLORE_ET0,
                "width": 2.5,
            },
            hovertemplate=(
                "Data: %{x|%d/%m}<br>"
                "ET₀: %{y:.1f} mm"
                "<extra></extra>"
            ),
        )
    )

    return configura_grafico(
        grafico,
        "Precipitazioni ed ET₀",
        "Giorno",
        "Millimetri (mm)",
    )


# ============================================================
# SCHEDE INFORMATIVE
# ============================================================

def mostra_scheda(etichetta, valore, dettaglio, icona):
    """
    Visualizza una scheda con etichetta, valore e dettaglio.
    """

    st.markdown(
        f"""
        <div class="scheda-meteo">
            <div class="scheda-etichetta">
                {icona} {etichetta}
            </div>
            <div class="scheda-valore">
                {valore}
            </div>
            <div class="scheda-dettaglio">
                {dettaglio}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ============================================================
# CONVERSIONE DEL CODICE METEOROLOGICO
# ============================================================

def descrivi_meteo(codice):
    """
    Converte i codici WMO più comuni in descrizioni italiane.
    """

    descrizioni = {
        0: "Cielo sereno",
        1: "Prevalentemente sereno",
        2: "Parzialmente nuvoloso",
        3: "Coperto",
        45: "Nebbia",
        48: "Nebbia con brina",
        51: "Pioviggine debole",
        53: "Pioviggine moderata",
        55: "Pioviggine intensa",
        61: "Pioggia debole",
        63: "Pioggia moderata",
        65: "Pioggia intensa",
        71: "Neve debole",
        73: "Neve moderata",
        75: "Neve intensa",
        80: "Rovesci deboli",
        81: "Rovesci moderati",
        82: "Rovesci intensi",
        95: "Temporale",
        96: "Temporale con grandine debole",
        99: "Temporale con grandine intensa",
    }

    if codice is None:
        return "Dato non disponibile"

    try:
        codice = int(codice)
    except (ValueError, TypeError):
        return "Dato non disponibile"

    return descrizioni.get(codice, "Condizione meteorologica variabile")


# ============================================================
# STATO DELLA RICERCA
# ============================================================

if "risultati_citta" not in st.session_state:
    st.session_state["risultati_citta"] = []

if "citta_selezionata" not in st.session_state:
    st.session_state["citta_selezionata"] = None

if "carica_meteo" not in st.session_state:
    st.session_state["carica_meteo"] = False


# ============================================================
# MENU LATERALE
# ============================================================

with st.sidebar:

    st.markdown("## 🌍 Cerca una località")

    st.markdown(
        '<p class="testo-secondario">'
        "Scrivi il nome e seleziona il risultato corretto."
        "</p>",
        unsafe_allow_html=True,
    )

    nome_citta = st.text_input(
        "Nome della città",
        placeholder="Es. Taranto, Roma, Milano...",
        key="campo_nome_citta",
    )

    if st.button(
        "🔎 Cerca località",
        type="primary",
        width="stretch",
    ):

        if not nome_citta.strip():

            st.warning("Inserisci il nome di una città.")

            st.session_state["risultati_citta"] = []

        else:

            try:

                with st.spinner("Ricerca delle località..."):

                    st.session_state["risultati_citta"] = cerca_citta(
                        nome_citta.strip()
                    )

                if not st.session_state["risultati_citta"]:
                    st.warning("Nessuna località trovata.")

            except requests.exceptions.RequestException:

                st.error(
                    "Non è stato possibile contattare "
                    "il servizio di geocodifica."
                )

    risultati_citta = st.session_state["risultati_citta"]

    if risultati_citta:

        opzioni_citta = [
            descrivi_citta(citta)
            for citta in risultati_citta
        ]

        indice_corrente = 0

        citta_precedente = st.session_state.get(
            "citta_selezionata"
        )

        if citta_precedente:

            descrizione_precedente = descrivi_citta(
                citta_precedente
            )

            if descrizione_precedente in opzioni_citta:

                indice_corrente = opzioni_citta.index(
                    descrizione_precedente
                )

        indice_scelto = st.selectbox(
            "Seleziona la località",
            options=range(len(risultati_citta)),
            index=indice_corrente,
            format_func=lambda indice: opzioni_citta[indice],
            key="selettore_localita",
        )

        if st.button(
            "🌦️ Mostra previsioni",
            width="stretch",
        ):

            st.session_state["citta_selezionata"] = (
                risultati_citta[indice_scelto]
            )

            st.session_state["carica_meteo"] = True

    st.divider()

    st.caption(
        "Dati meteorologici forniti da Open-Meteo."
    )


# ============================================================
# INTESTAZIONE DELLA DASHBOARD
# ============================================================

st.markdown(
    """
    <div class="intestazione">
        <div class="titolo-dashboard">🌦️ Meteo Dashboard</div>
        <div class="sottotitolo-dashboard">
            Meteo, previsioni e analisi per l'agricoltura.
            Cerca una località dal menu laterale.
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# SCHERMATA INIZIALE
# ============================================================

if not st.session_state["carica_meteo"]:

    col1, col2, col3 = st.columns(3)

    with col1:
        mostra_scheda(
            "Meteo attuale",
            "Temperatura",
            "Consulta le condizioni della località scelta.",
            "🌡️",
        )

    with col2:
        mostra_scheda(
            "Previsioni",
            "16 giorni",
            "Esplora i dati meteorologici giornalieri.",
            "📈",
        )

    with col3:
        mostra_scheda(
            "Agro Analisi",
            "ET₀ e pioggia",
            "Confronta precipitazioni ed evapotraspirazione.",
            "🌱",
        )

    st.info(
        "Per iniziare, cerca una città nel menu laterale, "
        "seleziona la località corretta e premi "
        "«Mostra previsioni»."
    )


# ============================================================
# ELABORAZIONE DEL METEO
# ============================================================

if st.session_state["carica_meteo"]:

    # Evita richieste ripetute durante i successivi aggiornamenti.
    st.session_state["carica_meteo"] = False

    citta = st.session_state["citta_selezionata"]

    if citta is None:

        st.warning("Cerca e seleziona prima una località.")

    else:

        try:

            latitudine = citta["latitude"]
            longitudine = citta["longitude"]

            localita_completa = descrivi_citta(citta)

            # Recupera tutti i dati necessari.
            with st.spinner("🌦️ Recupero dei dati meteorologici..."):

                dati = recupera_previsioni(
                    latitudine,
                    longitudine,
                )

            dati_attuali = dati.get("current", {})
            dati_orari = dati.get("hourly", {})
            dati_giornalieri = dati.get("daily", {})

            if not dati_attuali or not dati_orari or not dati_giornalieri:

                st.error(
                    "Open-Meteo non ha restituito tutti "
                    "i dati necessari."
                )

                st.stop()

            # Trasforma i dati in tabelle Pandas.
            tabella_oraria = crea_dataframe_orario(
                dati_orari
            )

            tabella_giornaliera = crea_dataframe_giornaliero(
                dati_giornalieri
            )

            # Intestazione della località.
            st.subheader(f"📍 {localita_completa}")

            st.caption(
                f"Coordinate: {latitudine}, {longitudine}"
            )

            # ====================================================
            # GRIGLIA 1: SITUAZIONE ATTUALE
            # ====================================================

            st.divider()

            st.subheader("🌤️ Situazione meteorologica attuale")

            temperatura = dati_attuali.get("temperature_2m")
            umidita = dati_attuali.get("relative_humidity_2m")
            vento = dati_attuali.get("wind_speed_10m")
            raffiche = dati_attuali.get("wind_gusts_10m")
            pioggia = dati_attuali.get("precipitation")
            codice = dati_attuali.get("weather_code")

            descrizione = descrivi_meteo(codice)

            col1, col2, col3, col4 = st.columns(4)

            with col1:

                mostra_scheda(
                    "Temperatura",
                    (
                        f"{temperatura:.1f} °C"
                        if temperatura is not None
                        else "N/D"
                    ),
                    descrizione,
                    "🌡️",
                )

            with col2:

                mostra_scheda(
                    "Umidità relativa",
                    (
                        f"{umidita:.0f}%"
                        if umidita is not None
                        else "N/D"
                    ),
                    "Umidità atmosferica",
                    "💧",
                )

            with col3:

                mostra_scheda(
                    "Vento",
                    (
                        f"{vento:.1f} km/h"
                        if vento is not None
                        else "N/D"
                    ),
                    (
                        f"Raffiche: {raffiche:.1f} km/h"
                        if raffiche is not None
                        else "Raffiche non disponibili"
                    ),
                    "💨",
                )

            with col4:

                mostra_scheda(
                    "Precipitazioni",
                    (
                        f"{pioggia:.1f} mm"
                        if pioggia is not None
                        else "N/D"
                    ),
                    "Valore meteorologico attuale",
                    "🌧️",
                )

            # ====================================================
            # GRIGLIA 2: TEMPERATURE
            # ====================================================

            st.divider()

            st.subheader("🌡️ Temperature")

            # La colonna sinistra mostra l'andamento orario.
            # La colonna destra mostra minime e massime giornaliere.
            col1, col2 = st.columns(2)

            with col1:

                grafico = crea_grafico_linea(
                    tabella_oraria["time"],
                    tabella_oraria["temperature_2m"],
                    "Temperatura oraria",
                    "Temperatura",
                    COLORE_TEMPERATURA,
                    "Temperatura (°C)",
                )

                st.plotly_chart(
                    grafico,
                    width="stretch",
                    key="grafico_temperatura_oraria",
                )

            with col2:

                grafico = crea_grafico_temperature_giornaliere(
                    tabella_giornaliera
                )

                st.plotly_chart(
                    grafico,
                    width="stretch",
                    key="grafico_temperature_giornaliere",
                )

            # ====================================================
            # GRIGLIA 3: PRECIPITAZIONI
            # ====================================================

            st.divider()

            st.subheader("🌧️ Precipitazioni")

            col1, col2 = st.columns(2)

            with col1:

                grafico = crea_grafico_barre(
                    tabella_giornaliera["time"],
                    tabella_giornaliera["precipitation_sum"],
                    "Precipitazioni giornaliere",
                    "Precipitazioni",
                    COLORE_PIOGGIA,
                    "Precipitazioni (mm)",
                )

                st.plotly_chart(
                    grafico,
                    width="stretch",
                    key="grafico_precipitazioni",
                )

            with col2:

                grafico = crea_grafico_barre(
                    tabella_giornaliera["time"],
                    tabella_giornaliera[
                        "precipitation_probability_max"
                    ],
                    "Probabilità massima di pioggia",
                    "Probabilità",
                    AZZURRO_CHIARO,
                    "Probabilità (%)",
                )

                st.plotly_chart(
                    grafico,
                    width="stretch",
                    key="grafico_probabilita_pioggia",
                )

            # ====================================================
            # GRIGLIA 4: VENTO
            # ====================================================

            st.divider()

            st.subheader("💨 Vento")

            col1, col2 = st.columns(2)

            with col1:

                grafico = crea_grafico_linea(
                    tabella_oraria["time"],
                    tabella_oraria["wind_speed_10m"],
                    "Velocità oraria del vento",
                    "Velocità",
                    COLORE_VENTO,
                    "Velocità (km/h)",
                )

                st.plotly_chart(
                    grafico,
                    width="stretch",
                    key="grafico_vento_orario",
                )

            with col2:

                grafico = crea_grafico_linea(
                    tabella_oraria["time"],
                    tabella_oraria["wind_gusts_10m"],
                    "Raffiche orarie",
                    "Raffiche",
                    COLORE_ET0,
                    "Raffiche (km/h)",
                )

                st.plotly_chart(
                    grafico,
                    width="stretch",
                    key="grafico_raffiche",
                )

            # ====================================================
            # GRIGLIA 5: BILANCIO IDRICO AGRICOLO
            # ====================================================

            st.divider()

            st.subheader("🌱 Agro Analisi")

            st.caption(
                "ET₀ è un valore di riferimento: per stimare "
                "l'irrigazione effettiva servono anche coltura, "
                "fase di crescita e caratteristiche del terreno."
            )

            col1, col2 = st.columns(2)

            with col1:

                grafico = crea_grafico_bilancio_idrico(
                    tabella_giornaliera
                )

                st.plotly_chart(
                    grafico,
                    width="stretch",
                    key="grafico_bilancio_idrico",
                )

            with col2:

                grafico = crea_grafico_linea(
                    tabella_oraria["time"],
                    tabella_oraria["et0_fao_evapotranspiration"],
                    "Evapotraspirazione di riferimento oraria",
                    "ET₀",
                    COLORE_ET0,
                    "ET₀ (mm)",
                )

                st.plotly_chart(
                    grafico,
                    width="stretch",
                    key="grafico_et0_orario",
                )

            # ====================================================
            # GRIGLIA 6: TERRENO
            # ====================================================

            st.divider()

            st.subheader("🌿 Condizioni del terreno")

            col1, col2 = st.columns(2)

            with col1:

                grafico = crea_grafico_linea(
                    tabella_oraria["time"],
                    tabella_oraria["soil_temperature_6cm"],
                    "Temperatura del suolo a 6 cm",
                    "Temperatura del suolo",
                    COLORE_SUOLO,
                    "Temperatura (°C)",
                )

                st.plotly_chart(
                    grafico,
                    width="stretch",
                    key="grafico_temperatura_suolo",
                )

            with col2:

                grafico = crea_grafico_linea(
                    tabella_oraria["time"],
                    tabella_oraria["soil_moisture_0_to_1cm"],
                    "Umidità del suolo a 0–1 cm",
                    "Umidità del suolo",
                    COLORE_UMIDITA,
                    "Contenuto volumetrico",
                )

                st.plotly_chart(
                    grafico,
                    width="stretch",
                    key="grafico_umidita_suolo",
                )

            # ====================================================
            # GRIGLIA 7: UMIDITÀ E RADIAZIONE
            # ====================================================

            st.divider()

            st.subheader("☀️ Atmosfera e radiazione solare")

            col1, col2 = st.columns(2)

            with col1:

                grafico = crea_grafico_linea(
                    tabella_oraria["time"],
                    tabella_oraria["relative_humidity_2m"],
                    "Umidità relativa oraria",
                    "Umidità",
                    COLORE_UMIDITA,
                    "Umidità (%)",
                )

                st.plotly_chart(
                    grafico,
                    width="stretch",
                    key="grafico_umidita_oraria",
                )

            with col2:

                grafico = crea_grafico_barre(
                    tabella_giornaliera["time"],
                    tabella_giornaliera["shortwave_radiation_sum"],
                    "Radiazione solare giornaliera",
                    "Radiazione",
                    COLORE_RADIAZIONE,
                    "Energia (MJ/m²)",
                )

                st.plotly_chart(
                    grafico,
                    width="stretch",
                    key="grafico_radiazione",
                )

            # ====================================================
            # TABELLA RIEPILOGATIVA GIORNALIERA
            # ====================================================

            st.divider()

            st.subheader("📋 Riepilogo giornaliero")

            # Seleziona le colonne più utili per una lettura rapida.
            colonne_tabella = [
                "time",
                "temperature_2m_max",
                "temperature_2m_min",
                "precipitation_sum",
                "precipitation_probability_max",
                "et0_fao_evapotranspiration",
                "sunshine_duration",
            ]

            # Mantiene soltanto le colonne presenti nella risposta API.
            colonne_disponibili = [
                colonna
                for colonna in colonne_tabella
                if colonna in tabella_giornaliera.columns
            ]

            tabella_riepilogo = tabella_giornaliera[
                colonne_disponibili
            ].copy()

            tabella_riepilogo = tabella_riepilogo.rename(
                columns={
                    "time": "Data",
                    "temperature_2m_max": "Massima (°C)",
                    "temperature_2m_min": "Minima (°C)",
                    "precipitation_sum": "Precipitazioni (mm)",
                    "precipitation_probability_max": (
                        "Probabilità pioggia (%)"
                    ),
                    "et0_fao_evapotranspiration": "ET₀ (mm)",
                    "sunshine_duration": "Sole (secondi)",
                }
            )

            st.dataframe(
                tabella_riepilogo,
                width="stretch",
                hide_index=True,
            )

            # ====================================================
            # TABELLA ORARIA DETTAGLIATA
            # ====================================================

            with st.expander("🔎 Mostra dati orari dettagliati"):

                st.dataframe(
                    tabella_oraria,
                    width="stretch",
                    hide_index=True,
                )

            # ====================================================
            # INFORMAZIONI FINALI
            # ====================================================

            st.divider()

            st.caption(
                "🌐 Dati forniti da Open-Meteo. "
                "Le previsioni sono stime modellistiche e possono "
                "essere aggiornate nel corso della giornata."
            )

        # ========================================================
        # GESTIONE DEGLI ERRORI
        # ========================================================

        except requests.exceptions.Timeout:

            st.error(
                "La richiesta al servizio meteo è scaduta. "
                "Riprova tra qualche istante."
            )

        except requests.exceptions.RequestException as errore:

            st.error(
                "Errore durante il collegamento al servizio meteo."
            )

            st.caption(f"Dettaglio tecnico: {errore}")

        except (
            KeyError,
            TypeError,
            ValueError,
            IndexError,
        ) as errore:

            st.error(
                "Si è verificato un problema durante "
                "l'elaborazione delle previsioni."
            )

            st.caption(f"Dettaglio tecnico: {errore}")
