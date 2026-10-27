
# ============================================================
# PROGETTO METEO
# File: dashboard.py
#
# Dashboard meteorologica realizzata con Streamlit e Plotly.
#
# Funzionalità:
# - Ricerca della città.
# - Temperatura e vento attuali.
# - Previsioni orarie della temperatura.
# - Previsioni orarie del vento.
# - Temperature massime e minime giornaliere.
# - Precipitazioni giornaliere.
# - Tabella riepilogativa delle previsioni.
#
# Grafica:
# - Tema blu notte e azzurro.
# - Schede informative.
# - Grafici coordinati e interattivi.
#
# Il file app.py e il file originale mereo_forecasting.py
# non devono essere modificati.
# ============================================================


# ============================================================
# IMPORTAZIONE DELLE LIBRERIE
# ============================================================

import requests
import pandas as pd
import plotly.graph_objects as go
import streamlit as st


# ============================================================
# CONFIGURAZIONE DEL PROGRAMMA
# ============================================================

# Indirizzo dell'API Open-Meteo per le previsioni.
FORECAST_URL = "https://api.open-meteo.com/v1/forecast"

# Indirizzo dell'API Open-Meteo per cercare le città.
GEOCODING_URL = "https://geocoding-api.open-meteo.com/v1/search"

# Numero di giorni di previsione.
FORECAST_DAYS = 7

# Tempo massimo di attesa delle richieste HTTP.
TIMEOUT = 20


# ============================================================
# PALETTE DEI COLORI
# ============================================================

# Colori principali della dashboard.
BLU_NOTTE = "#10243A"
BLU_PANNELLO = "#183650"
BLU_AZZURRO = "#38BDF8"
AZZURRO_CHIARO = "#7DD3FC"
BIANCO = "#F1F5F9"
TESTO_SECONDARIO = "#B8C9D9"

# Colori utilizzati nei grafici.
COLORE_TEMPERATURA = "#FB7185"
COLORE_VENTO = "#38BDF8"
COLORE_MASSIMA = "#FB7185"
COLORE_MINIMA = "#60A5FA"
COLORE_PIOGGIA = "#38BDF8"


# ============================================================
# CONFIGURAZIONE DELLA PAGINA
# ============================================================

st.set_page_config(
    page_title="Progetto Meteo",
    page_icon="🌦️",
    layout="wide",
    initial_sidebar_state="collapsed",
)


# ============================================================
# STILE CSS DELLA DASHBOARD
# ============================================================

# Personalizza l'aspetto degli elementi Streamlit.
# I selettori riguardano soltanto la presentazione grafica.

st.markdown(
    f"""
    <style>
        /* Sfondo generale della pagina */
        .stApp {{
            background: linear-gradient(
                135deg,
                {BLU_NOTTE} 0%,
                #142D46 55%,
                #10243A 100%
            );
            color: {BIANCO};
        }}

        /* Larghezza e spaziatura del contenuto principale */
        .block-container {{
            max-width: 1450px;
            padding-top: 2rem;
            padding-bottom: 3rem;
        }}

        /* Titoli principali */
        h1, h2, h3 {{
            color: {BIANCO} !important;
            letter-spacing: -0.4px;
        }}

        /* Testo generale */
        p, label, .stMarkdown {{
            color: {BIANCO};
        }}

        /* Testo secondario */
        .testo-secondario {{
            color: {TESTO_SECONDARIO};
            font-size: 0.95rem;
        }}

        /* Intestazione della dashboard */
        .intestazione {{
            background: linear-gradient(
                120deg,
                #183650,
                #1B4965
            );
            border: 1px solid #315875;
            border-radius: 20px;
            padding: 26px 30px;
            margin-bottom: 24px;
        }}

        .titolo-dashboard {{
            color: {BIANCO};
            font-size: 2.2rem;
            font-weight: 750;
            margin-bottom: 6px;
        }}

        .sottotitolo-dashboard {{
            color: {TESTO_SECONDARIO};
            font-size: 1rem;
        }}

        /* Schede informative */
        .scheda-meteo {{
            background: linear-gradient(
                145deg,
                #1B3A54,
                #183047
            );
            border: 1px solid #315875;
            border-radius: 16px;
            padding: 20px;
            min-height: 135px;
            margin-bottom: 12px;
        }}

        .scheda-etichetta {{
            color: {TESTO_SECONDARIO};
            font-size: 0.92rem;
            margin-bottom: 10px;
        }}

        .scheda-valore {{
            color: {BIANCO};
            font-size: 2rem;
            font-weight: 750;
            line-height: 1.2;
        }}

        .scheda-dettaglio {{
            color: {AZZURRO_CHIARO};
            font-size: 0.88rem;
            margin-top: 8px;
        }}

        /* Contenitori dei grafici */
        div[data-testid="stPlotlyChart"] {{
            background: rgba(24, 54, 80, 0.45);
            border: 1px solid #294861;
            border-radius: 14px;
            padding: 8px;
            margin-bottom: 18px;
        }}

        /* Campi di inserimento */
        div[data-testid="stTextInput"] input {{
            background-color: #183650;
            color: {BIANCO};
            border: 1px solid #416581;
            border-radius: 10px;
        }}

        /* Pulsanti */
        div.stButton > button,
        div.stFormSubmitButton > button {{
            background: {BLU_AZZURRO};
            color: #10243A;
            border: none;
            border-radius: 10px;
            font-weight: 700;
            padding: 0.55rem 1.2rem;
            transition: 0.2s ease;
        }}

        div.stButton > button:hover,
        div.stFormSubmitButton > button:hover {{
            background: {AZZURRO_CHIARO};
            color: #10243A;
            border: none;
        }}

        /* Separatore */
        hr {{
            border-color: #31506A;
            margin-top: 1.4rem;
            margin-bottom: 1.4rem;
        }}

        /* Tabelle */
        div[data-testid="stDataFrame"] {{
            border: 1px solid #315875;
            border-radius: 12px;
            overflow: hidden;
        }}

        /* Messaggi e didascalie */
        div[data-testid="stCaptionContainer"] {{
            color: {TESTO_SECONDARIO};
        }}

        /* Adattamento agli schermi piccoli */
        @media (max-width: 768px) {{
            .titolo-dashboard {{
                font-size: 1.7rem;
            }}

            .intestazione {{
                padding: 20px;
            }}

            .scheda-valore {{
                font-size: 1.6rem;
            }}

            .block-container {{
                padding-top: 1rem;
                padding-left: 1rem;
                padding-right: 1rem;
            }}
        }}
    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# RICERCA DELLA CITTÀ
# ============================================================

def cerca_citta(nome_citta):
    """
    Cerca una città tramite il servizio di geocodifica
    di Open-Meteo.

    Restituisce le informazioni della prima città trovata.
    Se non ci sono risultati, restituisce None.
    """

    parametri = {
        "name": nome_citta,
        "count": 1,
        "language": "it",
        "format": "json",
    }

    risposta = requests.get(
        GEOCODING_URL,
        params=parametri,
        timeout=TIMEOUT,
    )

    # Verifica che la richiesta HTTP sia riuscita.
    risposta.raise_for_status()

    dati = risposta.json()

    # Controlla se è stata trovata almeno una città.
    risultati = dati.get("results", [])

    if not risultati:
        return None

    return risultati[0]


# ============================================================
# RECUPERO DELLE PREVISIONI METEO
# ============================================================

def recupera_previsioni(latitudine, longitudine):
    """
    Recupera le previsioni orarie e giornaliere
    fornite dal servizio Open-Meteo.
    """

    parametri = {
        "latitude": latitudine,
        "longitude": longitudine,
        "forecast_days": FORECAST_DAYS,
        "timezone": "auto",
        "temperature_unit": "celsius",
        "wind_speed_unit": "kmh",
        "precipitation_unit": "mm",
        "current": (
            "temperature_2m,"
            "wind_speed_10m"
        ),
        "hourly": (
            "temperature_2m,"
            "wind_speed_10m"
        ),
        "daily": (
            "temperature_2m_max,"
            "temperature_2m_min,"
            "precipitation_sum"
        ),
    }

    risposta = requests.get(
        FORECAST_URL,
        params=parametri,
        timeout=TIMEOUT,
    )

    # Verifica che la richiesta sia riuscita.
    risposta.raise_for_status()

    return risposta.json()


# ============================================================
# FUNZIONE DI SUPPORTO PER I GRAFICI
# ============================================================

def configura_grafico(grafico, titolo, titolo_asse_x, titolo_asse_y):
    """
    Applica lo stile blu notte a un grafico Plotly.

    In questo modo tutti i grafici condividono
    gli stessi colori e le stesse impostazioni.
    """

    grafico.update_layout(
        title={
            "text": titolo,
            "font": {
                "size": 20,
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
        margin={
            "l": 20,
            "r": 20,
            "t": 65,
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

    # Personalizza gli assi e la griglia.
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
# GRAFICO DELLE PREVISIONI ORARIE
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
    Crea un grafico a linee interattivo.
    """

    grafico = go.Figure()

    grafico.add_trace(
        go.Scatter(
            x=date,
            y=valori,
            mode="lines+markers",
            name=nome_serie,
            line={
                "color": colore,
                "width": 3,
                "shape": "spline",
            },
            marker={
                "size": 5,
                "color": colore,
                "line": {
                    "color": BIANCO,
                    "width": 1,
                },
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
# GRAFICO DELLE TEMPERATURE GIORNALIERE
# ============================================================

def crea_grafico_temperature_giornaliere(
    date,
    temperature_massime,
    temperature_minime,
):
    """
    Confronta le temperature massime e minime
    previste per ciascun giorno.
    """

    grafico = go.Figure()

    # Linea delle temperature massime.
    grafico.add_trace(
        go.Scatter(
            x=date,
            y=temperature_massime,
            mode="lines+markers",
            name="Temperatura massima",
            line={
                "color": COLORE_MASSIMA,
                "width": 3,
                "shape": "spline",
            },
            marker={
                "size": 8,
            },
            hovertemplate=(
                "%{x|%d/%m}<br>"
                "Massima: %{y:.1f} °C"
                "<extra></extra>"
            ),
        )
    )

    # Linea delle temperature minime.
    grafico.add_trace(
        go.Scatter(
            x=date,
            y=temperature_minime,
            mode="lines+markers",
            name="Temperatura minima",
            line={
                "color": COLORE_MINIMA,
                "width": 3,
                "shape": "spline",
            },
            marker={
                "size": 8,
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
# GRAFICO DELLE PRECIPITAZIONI
# ============================================================

def crea_grafico_precipitazioni(date, precipitazioni):
    """
    Crea un grafico a barre delle precipitazioni
    giornaliere previste.
    """

    grafico = go.Figure()

    grafico.add_trace(
        go.Bar(
            x=date,
            y=precipitazioni,
            name="Precipitazioni",
            marker={
                "color": COLORE_PIOGGIA,
                "line": {
                    "color": AZZURRO_CHIARO,
                    "width": 1,
                },
            },
            hovertemplate=(
                "Giorno: %{x|%d/%m}<br>"
                "Precipitazioni: %{y:.1f} mm"
                "<extra></extra>"
            ),
        )
    )

    return configura_grafico(
        grafico,
        "Precipitazioni giornaliere",
        "Giorno",
        "Precipitazioni (mm)",
    )


# ============================================================
# FUNZIONE PER MOSTRARE LE SCHEDE INFORMATIVE
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
# INTESTAZIONE DELLA DASHBOARD
# ============================================================

st.markdown(
    """
    <div class="intestazione">
        <div class="titolo-dashboard">
            🌦️ Meteo Dashboard
        </div>
        <div class="sottotitolo-dashboard">
            Condizioni attuali e previsioni meteorologiche
            dei prossimi sette giorni.
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# MODULO DI RICERCA
# ============================================================

with st.form("form_ricerca_citta"):

    colonna_ricerca, colonna_pulsante = st.columns(
        [4, 1],
        vertical_alignment="bottom",
    )

    with colonna_ricerca:
        nome_citta = st.text_input(
            "📍 Cerca una città",
            placeholder="Esempio: Taranto, Roma, Milano...",
        )

    with colonna_pulsante:
        cerca = st.form_submit_button(
            "Cerca meteo",
            type="primary",
            use_container_width=True,
        )


# ============================================================
# ELABORAZIONE DELLA RICERCA
# ============================================================

if cerca:

    # Verifica che sia stato inserito un nome.
    if not nome_citta.strip():

        st.warning("Inserisci il nome di una città.")

    else:

        try:

            # Cerca la città e recupera le sue coordinate.
            with st.spinner("🔎 Ricerca della città..."):
                citta = cerca_citta(nome_citta.strip())

            if citta is None:

                st.error(
                    "Nessuna città trovata. "
                    "Controlla il nome e riprova."
                )

            else:

                latitudine = citta["latitude"]
                longitudine = citta["longitude"]

                nome_visualizzato = citta["name"]
                paese = citta.get("country", "")

                # Recupera i dati meteorologici.
                with st.spinner("🌦️ Recupero delle previsioni..."):
                    dati = recupera_previsioni(
                        latitudine,
                        longitudine,
                    )

                # Controlla la presenza dei dati necessari.
                if (
                    not dati.get("current")
                    or not dati.get("hourly")
                    or not dati.get("daily")
                ):

                    st.error(
                        "Il servizio meteo non ha restituito "
                        "tutti i dati necessari."
                    )

                else:

                    # Mostra il nome della località.
                    st.subheader(
                        f"📍 {nome_visualizzato}, {paese}"
                    )

                    st.caption(
                        f"Coordinate geografiche: "
                        f"{latitudine}, {longitudine}"
                    )

                    # Recupera i dati meteorologici attuali.
                    dati_attuali = dati["current"]

                    temperatura_attuale = dati_attuali.get(
                        "temperature_2m"
                    )

                    vento_attuale = dati_attuali.get(
                        "wind_speed_10m"
                    )

                    # Recupera le previsioni giornaliere.
                    dati_giornalieri = dati["daily"]

                    temperature_massime = (
                        dati_giornalieri["temperature_2m_max"]
                    )

                    temperature_minime = (
                        dati_giornalieri["temperature_2m_min"]
                    )

                    precipitazioni = (
                        dati_giornalieri["precipitation_sum"]
                    )

                    # Ricava il massimo e il minimo del primo giorno.
                    massima_oggi = (
                        temperature_massime[0]
                        if temperature_massime
                        else None
                    )

                    minima_oggi = (
                        temperature_minime[0]
                        if temperature_minime
                        else None
                    )

                    pioggia_oggi = (
                        precipitazioni[0]
                        if precipitazioni
                        else None
                    )

                    st.divider()

                    # ====================================================
                    # SCHEDE DELLE CONDIZIONI METEO
                    # ====================================================

                    st.subheader("📊 Situazione meteorologica")

                    col1, col2, col3, col4 = st.columns(4)

                    with col1:
                        mostra_scheda(
                            "Temperatura attuale",
                            (
                                f"{temperatura_attuale:.1f} °C"
                                if temperatura_attuale is not None
                                else "N/D"
                            ),
                            "Temperatura dell'aria",
                            "🌡️",
                        )

                    with col2:
                        mostra_scheda(
                            "Vento attuale",
                            (
                                f"{vento_attuale:.1f} km/h"
                                if vento_attuale is not None
                                else "N/D"
                            ),
                            "Velocità del vento",
                            "💨",
                        )

                    with col3:
                        mostra_scheda(
                            "Massima prevista",
                            (
                                f"{massima_oggi:.1f} °C"
                                if massima_oggi is not None
                                else "N/D"
                            ),
                            "Massima del primo giorno",
                            "☀️",
                        )

                    with col4:
                        mostra_scheda(
                            "Minima prevista",
                            (
                                f"{minima_oggi:.1f} °C"
                                if minima_oggi is not None
                                else "N/D"
                            ),
                            "Minima del primo giorno",
                            "🌙",
                        )

                    # Mostra le precipitazioni previste per il giorno.
                    if pioggia_oggi is not None:
                        st.caption(
                            "🌧️ Precipitazioni previste per il primo "
                            f"giorno: {pioggia_oggi:.1f} mm."
                        )

                    st.divider()

                    # ====================================================
                    # PREVISIONI ORARIE
                    # ====================================================

                    dati_orari = dati["hourly"]

                    tabella_oraria = pd.DataFrame({
                        "Data e ora": pd.to_datetime(
                            dati_orari["time"]
                        ),
                        "Temperatura (°C)": (
                            dati_orari["temperature_2m"]
                        ),
                        "Vento (km/h)": (
                            dati_orari["wind_speed_10m"]
                        ),
                    })

                    # Grafico della temperatura oraria.
                    st.subheader("🌡️ Andamento della temperatura")

                    grafico_temperatura = crea_grafico_linea(
                        date=tabella_oraria["Data e ora"],
                        valori=tabella_oraria[
                            "Temperatura (°C)"
                        ],
                        titolo="Previsioni orarie della temperatura",
                        nome_serie="Temperatura",
                        colore=COLORE_TEMPERATURA,
                        nome_asse_y="Temperatura (°C)",
                    )

                    st.plotly_chart(
                        grafico_temperatura,
                        use_container_width=True,
                        key="grafico_temperatura",
                    )

                    # Grafico del vento orario.
                    st.subheader("💨 Andamento del vento")

                    grafico_vento = crea_grafico_linea(
                        date=tabella_oraria["Data e ora"],
                        valori=tabella_oraria["Vento (km/h)"],
                        titolo="Previsioni orarie del vento",
                        nome_serie="Velocità del vento",
                        colore=COLORE_VENTO,
                        nome_asse_y="Velocità (km/h)",
                    )

                    st.plotly_chart(
                        grafico_vento,
                        use_container_width=True,
                        key="grafico_vento",
                    )

                    st.divider()

                    # ====================================================
                    # PREVISIONI GIORNALIERE
                    # ====================================================

                    tabella_giornaliera = pd.DataFrame({
                        "Data": pd.to_datetime(
                            dati_giornalieri["time"]
                        ).date,
                        "Temperatura massima (°C)": (
                            temperature_massime
                        ),
                        "Temperatura minima (°C)": (
                            temperature_minime
                        ),
                        "Precipitazioni (mm)": precipitazioni,
                    })

                    # Grafico delle temperature giornaliere.
                    st.subheader(
                        "📅 Temperature massime e minime giornaliere"
                    )

                    grafico_temperature = (
                        crea_grafico_temperature_giornaliere(
                            date=tabella_giornaliera["Data"],
                            temperature_massime=(
                                tabella_giornaliera[
                                    "Temperatura massima (°C)"
                                ]
                            ),
                            temperature_minime=(
                                tabella_giornaliera[
                                    "Temperatura minima (°C)"
                                ]
                            ),
                        )
                    )

                    st.plotly_chart(
                        grafico_temperature,
                        use_container_width=True,
                        key="grafico_temperature_giornaliere",
                    )

                    # Grafico delle precipitazioni giornaliere.
                    st.subheader("🌧️ Precipitazioni giornaliere")

                    grafico_pioggia = crea_grafico_precipitazioni(
                        date=tabella_giornaliera["Data"],
                        precipitazioni=(
                            tabella_giornaliera[
                                "Precipitazioni (mm)"
                            ]
                        ),
                    )

                    st.plotly_chart(
                        grafico_pioggia,
                        use_container_width=True,
                        key="grafico_precipitazioni",
                    )

                    # ====================================================
                    # TABELLA RIEPILOGATIVA
                    # ====================================================

                    st.subheader("📋 Riepilogo dei sette giorni")

                    st.dataframe(
                        tabella_giornaliera,
                        use_container_width=True,
                        hide_index=True,
                    )

                    # Informazioni sul servizio utilizzato.
                    st.divider()

                    st.caption(
                        "🌐 Dati meteorologici forniti da Open-Meteo. "
                        "Le previsioni possono essere aggiornate "
                        "dal servizio nel corso della giornata."
                    )

        # ============================================================
        # GESTIONE DEGLI ERRORI
        # ============================================================

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

        except (KeyError, TypeError, ValueError, IndexError) as errore:

            st.error(
                "Si è verificato un problema durante "
                "l'elaborazione delle previsioni."
            )

            st.caption(f"Dettaglio tecnico: {errore}")
