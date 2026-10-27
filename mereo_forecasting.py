
# ============================================================
# PROGETTO METEO
# File: dashboard.py
#
# Dashboard meteorologica realizzata con Streamlit.
# Grafica moderna blu notte e azzurro.
#
# API utilizzate:
# - Open-Meteo Forecast
# - Open-Meteo Geocoding
# ============================================================

import requests
import pandas as pd
import plotly.graph_objects as go
import streamlit as st


# ============================================================
# CONFIGURAZIONE
# ============================================================

FORECAST_URL = "https://api.open-meteo.com/v1/forecast"
GEOCODING_URL = "https://geocoding-api.open-meteo.com/v1/search"

FORECAST_DAYS = 7
TIMEOUT = 20

# Configura la pagina prima di visualizzare gli elementi.
st.set_page_config(
    page_title="Progetto Meteo",
    page_icon="🌦️",
    layout="wide",
)


# ============================================================
# GRAFICA DELLA DASHBOARD
# ============================================================

# Colori principali del tema.
BLU_NOTTE = "#0B1224"
BLU_SCHEDA = "#14213B"
AZZURRO = "#47C8FF"
AZZURRO_VERDE = "#69E0CE"
VIOLA = "#A5A9FF"
TESTO = "#E5F3FF"
TESTO_SECONDARIO = "#9AB4D7"

# CSS personalizzato per lo sfondo, i riquadri e i testi.
st.markdown(
    f"""
    <style>
        .stApp {{
            background-color: {BLU_NOTTE};
            color: {TESTO};
        }}

        [data-testid="stHeader"] {{
            background-color: rgba(11, 18, 36, 0.95);
        }}

        [data-testid="stSidebar"] {{
            background-color: {BLU_SCHEDA};
        }}

        h1, h2, h3 {{
            color: {TESTO} !important;
        }}

        p, label, .stMarkdown {{
            color: {TESTO};
        }}

        [data-testid="stMetric"] {{
            background-color: {BLU_SCHEDA};
            border: 1px solid #263957;
            border-radius: 14px;
            padding: 18px;
        }}

        [data-testid="stMetricLabel"] {{
            color: {TESTO_SECONDARIO} !important;
        }}

        [data-testid="stMetricValue"] {{
            color: {AZZURRO} !important;
        }}

        div.stButton > button {{
            background-color: {AZZURRO};
            color: {BLU_NOTTE};
            border: none;
            border-radius: 10px;
            font-weight: bold;
            min-height: 42px;
        }}

        div.stButton > button:hover {{
            background-color: {AZZURRO_VERDE};
            color: {BLU_NOTTE};
            border: none;
        }}

        div[data-baseweb="input"] {{
            background-color: {BLU_SCHEDA};
            border-radius: 10px;
        }}

        [data-testid="stDataFrame"] {{
            border: 1px solid #263957;
            border-radius: 12px;
            overflow: hidden;
        }}

        hr {{
            border-color: #263957;
        }}

        .intestazione-meteo {{
            background: linear-gradient(120deg, #14213B, #173A5E);
            padding: 24px;
            border-radius: 18px;
            border: 1px solid #263957;
            margin-bottom: 20px;
        }}

        .sottotitolo-meteo {{
            color: {TESTO_SECONDARIO};
            font-size: 16px;
        }}

        .etichetta-sezione {{
            color: {AZZURRO};
            font-size: 13px;
            font-weight: bold;
            letter-spacing: 2px;
            text-transform: uppercase;
        }}
    </style>
    """,
    unsafe_allow_html=True,
)

# Imposta il tema scuro e il colore azzurro dei grafici.
st.markdown(
    """
    <style>
        .block-container {
            padding-top: 2rem;
            padding-bottom: 3rem;
        }
    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# FUNZIONI PER RECUPERARE I DATI
# ============================================================

def cerca_citta(nome_citta):
    """
    Cerca una città italiana e restituisce le coordinate
    geografiche necessarie per richiedere le previsioni.
    """

    params_geo = {
        "name": nome_citta,
        "count": 5,
        "countryCode": "IT",
        "language": "it",
        "format": "json",
    }

    # Invia la richiesta al servizio di geocodifica.
    response_geo = requests.get(
        GEOCODING_URL,
        params=params_geo,
        timeout=TIMEOUT,
    )

    # Segnala eventuali errori della richiesta HTTP.
    response_geo.raise_for_status()

    data_geo = response_geo.json()

    # Controlla se sono state trovate città.
    risultati = data_geo.get("results", [])

    if not risultati:
        return None

    # Restituisce il primo risultato trovato.
    return risultati[0]


def recupera_previsioni(latitudine, longitudine):
    """
    Recupera le condizioni attuali, i dati orari
    e le previsioni giornaliere.
    """

    params_forecast = {
        "latitude": latitudine,
        "longitude": longitudine,
        "forecast_days": FORECAST_DAYS,
        "timezone": "auto",
        "temperature_unit": "celsius",
        "wind_speed_unit": "kmh",
        "precipitation_unit": "mm",
        "current": "temperature_2m,wind_speed_10m",
        "hourly": "temperature_2m,wind_speed_10m",
        "daily": (
            "temperature_2m_max,"
            "temperature_2m_min,"
            "precipitation_sum"
        ),
    }

    # Invia la richiesta al servizio meteo.
    response_forecast = requests.get(
        FORECAST_URL,
        params=params_forecast,
        timeout=TIMEOUT,
    )

    response_forecast.raise_for_status()

    return response_forecast.json()


# ============================================================
# FUNZIONI PER CREARE I GRAFICI
# ============================================================

def configura_grafico(fig, altezza=350):
    """
    Applica a un grafico Plotly il tema blu notte
    utilizzato dalla dashboard.
    """

    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor=BLU_SCHEDA,
        plot_bgcolor=BLU_SCHEDA,
        font=dict(
            family="Arial",
            color=TESTO,
            size=12,
        ),
        title=dict(
            font=dict(
                color=TESTO,
                size=17,
            ),
            x=0.02,
        ),
        height=altezza,
        margin=dict(l=20, r=20, t=65, b=25),
        hovermode="x unified",
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
        ),
        xaxis=dict(
            showgrid=True,
            gridcolor="#263957",
            zerolinecolor="#263957",
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor="#263957",
            zerolinecolor="#263957",
        ),
    )

    return fig


def crea_grafico_linea(
    tempi,
    valori,
    titolo,
    nome_serie,
    colore,
    unita,
):
    """
    Crea un grafico a linee con sfondo blu notte.
    """

    fig = go.Figure()

    # Disegna la linea della serie meteorologica.
    fig.add_trace(
        go.Scatter(
            x=tempi,
            y=valori,
            mode="lines",
            name=nome_serie,
            line=dict(
                color=colore,
                width=3,
                shape="spline",
            ),
            hovertemplate=(
                "%{x|%d/%m/%Y %H:%M}"
                "<br>%{y:.1f} "
                + unita
                + "<extra></extra>"
            ),
        )
    )

    # Applica il tema comune al grafico.
    configura_grafico(fig, altezza=350)

    fig.update_layout(
        title=titolo,
        xaxis_title="Data e ora",
        yaxis_title=unita,
    )

    return fig


def crea_grafico_temperature_giornaliere(df_daily):
    """
    Confronta le temperature massime e minime
    previste per ciascun giorno.
    """

    fig = go.Figure()

    # Linea delle temperature massime.
    fig.add_trace(
        go.Scatter(
            x=df_daily["time"],
            y=df_daily["temperature_2m_max"],
            mode="lines+markers",
            name="Temperatura massima",
            line=dict(
                color=AZZURRO,
                width=3,
                shape="spline",
            ),
            marker=dict(size=7),
            hovertemplate=(
                "Data: %{x|%d/%m/%Y}"
                "<br>Massima: %{y:.1f} °C"
                "<extra></extra>"
            ),
        )
    )

    # Linea delle temperature minime.
    fig.add_trace(
        go.Scatter(
            x=df_daily["time"],
            y=df_daily["temperature_2m_min"],
            mode="lines+markers",
            name="Temperatura minima",
            line=dict(
                color=VIOLA,
                width=3,
                shape="spline",
            ),
            marker=dict(size=7),
            hovertemplate=(
                "Data: %{x|%d/%m/%Y}"
                "<br>Minima: %{y:.1f} °C"
                "<extra></extra>"
            ),
        )
    )

    configura_grafico(fig, altezza=350)

    fig.update_layout(
        title="Temperature massime e minime",
        xaxis_title="Data",
        yaxis_title="Temperatura (°C)",
    )

    return fig


def crea_grafico_precipitazioni(df_daily):
    """
    Mostra le precipitazioni previste per ogni giorno.
    """

    fig = go.Figure()

    fig.add_trace(
        go.Bar(
            x=df_daily["time"],
            y=df_daily["precipitation_sum"],
            name="Precipitazioni",
            marker=dict(
                color=AZZURRO,
                line=dict(
                    color="#8BE0FF",
                    width=1,
                ),
            ),
            hovertemplate=(
                "Data: %{x|%d/%m/%Y}"
                "<br>Precipitazioni: %{y:.1f} mm"
                "<extra></extra>"
            ),
        )
    )

    configura_grafico(fig, altezza=350)

    fig.update_layout(
        title="Precipitazioni giornaliere",
        xaxis_title="Data",
        yaxis_title="Precipitazioni (mm)",
    )

    return fig


# ============================================================
# INTERFACCIA PRINCIPALE
# ============================================================

st.markdown(
    """
    <div class="intestazione-meteo">
        <div class="etichetta-sezione">METEO · PREVISIONI</div>
        <h1>🌦️ Progetto Meteo</h1>
        <div class="sottotitolo-meteo">
            Le condizioni attuali e le previsioni,
            in una dashboard moderna.
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# Campo di ricerca e pulsante sulla stessa riga.
colonna_ricerca, colonna_pulsante = st.columns([4, 1])

with colonna_ricerca:
    nome_citta = st.text_input(
        "Cerca una città italiana",
        placeholder="Ad esempio: Taranto, Roma, Milano",
    )

with colonna_pulsante:
    st.write("")
    st.write("")
    cerca = st.button(
        "🔎 Cerca meteo",
       width="stretch",
        type="primary",
    )


# ============================================================
# RICERCA E VISUALIZZAZIONE DELLE PREVISIONI
# ============================================================

if cerca:

    # Controlla che sia stato inserito un nome.
    if not nome_citta.strip():

        st.warning("Inserisci il nome di una città.")

    else:

        try:
            # Recupera le informazioni meteorologiche.
            with st.spinner("🌐 Recupero delle previsioni meteo..."):

                citta = cerca_citta(nome_citta.strip())

                if citta is None:
                    st.warning(
                        "Nessuna città italiana trovata. "
                        "Controlla il nome e riprova."
                    )
                    st.stop()

                latitudine = citta["latitude"]
                longitudine = citta["longitude"]

                dati_forecast = recupera_previsioni(
                    latitudine,
                    longitudine,
                )

            # ------------------------------------------------
            # PREPARAZIONE DEI DATAFRAME
            # ------------------------------------------------

            df_hourly = pd.DataFrame(
                dati_forecast["hourly"]
            )

            df_daily = pd.DataFrame(
                dati_forecast["daily"]
            )

            # Converte le date in oggetti data/ora.
            df_hourly["time"] = pd.to_datetime(
                df_hourly["time"]
            )

            df_daily["time"] = pd.to_datetime(
                df_daily["time"]
            )

            # Legge le condizioni meteorologiche attuali.
            dati_attuali = dati_forecast["current"]

            temperatura_attuale = dati_attuali[
                "temperature_2m"
            ]

            vento_attuale = dati_attuali[
                "wind_speed_10m"
            ]

            # ------------------------------------------------
            # INFORMAZIONI SULLA CITTÀ
            # ------------------------------------------------

            nome_risultato = citta.get("name", nome_citta)
            regione = citta.get("admin1", "")

            if regione:
                st.subheader(
                    f"📍 {nome_risultato} — {regione}"
                )
            else:
                st.subheader(f"📍 {nome_risultato}")

            st.caption(
                f"Previsioni per i prossimi {FORECAST_DAYS} giorni"
            )

            # ------------------------------------------------
            # SCHEDE DELLE CONDIZIONI ATTUALI
            # ------------------------------------------------

            # Recupera massima e minima del primo giorno.
            temperatura_massima = df_daily[
                "temperature_2m_max"
            ].iloc[0]

            temperatura_minima = df_daily[
                "temperature_2m_min"
            ].iloc[0]

            col_temp, col_vento, col_max, col_min = st.columns(4)

            with col_temp:
                st.metric(
                    "🌡️ Temperatura attuale",
                    f"{temperatura_attuale:.1f} °C",
                )

            with col_vento:
                st.metric(
                    "💨 Velocità del vento",
                    f"{vento_attuale:.1f} km/h",
                )

            with col_max:
                st.metric(
                    "🔺 Massima di oggi",
                    f"{temperatura_massima:.1f} °C",
                )

            with col_min:
                st.metric(
                    "🔹 Minima di oggi",
                    f"{temperatura_minima:.1f} °C",
                )

            st.divider()

            # ------------------------------------------------
            # I QUATTRO GRAFICI IN DUE RIGHE
            # ------------------------------------------------

            st.markdown(
                '<div class="etichetta-sezione">'
                'ANALISI METEOROLOGICA'
                '</div>',
                unsafe_allow_html=True,
            )

            # Crea i quattro grafici.
            grafico_temperatura = crea_grafico_linea(
                df_hourly["time"],
                df_hourly["temperature_2m"],
                "🌡️ Temperatura oraria",
                "Temperatura",
                AZZURRO,
                "°C",
            )

            grafico_vento = crea_grafico_linea(
                df_hourly["time"],
                df_hourly["wind_speed_10m"],
                "💨 Velocità del vento",
                "Velocità del vento",
                AZZURRO_VERDE,
                "km/h",
            )

            grafico_temperature_giornaliere = (
                crea_grafico_temperature_giornaliere(
                    df_daily
                )
            )

            grafico_precipitazioni = (
                crea_grafico_precipitazioni(
                    df_daily
                )
            )

            # Prima riga: temperatura e vento.
            col_grafico_1, col_grafico_2 = st.columns(2)

            with col_grafico_1:
                st.plotly_chart(
                    grafico_temperatura,
                    use_container_width=True,
                )

            with col_grafico_2:
                st.plotly_chart(
                    grafico_vento,
                    use_container_width=True,
                )

            # Seconda riga: temperature giornaliere e pioggia.
            col_grafico_3, col_grafico_4 = st.columns(2)

            with col_grafico_3:
                st.plotly_chart(
                    grafico_temperature_giornaliere,
                    use_container_width=True,
                )

            with col_grafico_4:
                st.plotly_chart(
                    grafico_precipitazioni,
                    use_container_width=True,
                )

            st.divider()

            # ------------------------------------------------
            # TABELLA DELLE PREVISIONI GIORNALIERE
            # ------------------------------------------------

            st.subheader("📅 Riepilogo delle previsioni")

            # Rinomina le colonne per renderle leggibili.
            tabella = df_daily.rename(
                columns={
                    "time": "Data",
                    "temperature_2m_max": "Temperatura max (°C)",
                    "temperature_2m_min": "Temperatura min (°C)",
                    "precipitation_sum": "Precipitazioni (mm)",
                }
            )

            # Seleziona soltanto le colonne da visualizzare.
            tabella = tabella[
                [
                    "Data",
                    "Temperatura max (°C)",
                    "Temperatura min (°C)",
                    "Precipitazioni (mm)",
                ]
            ].copy()

            # Formatta le date.
            tabella["Data"] = tabella["Data"].dt.strftime(
                "%d/%m/%Y"
            )

            # Visualizza la tabella nella dashboard.
            st.dataframe(
                tabella,
                use_container_width=True,
                hide_index=True,
            )

            st.caption(
                "Dati meteorologici forniti da Open-Meteo."
            )

        except requests.exceptions.Timeout:
            st.error(
                "Il servizio meteo non ha risposto in tempo. "
                "Riprova tra qualche istante."
            )

        except requests.exceptions.RequestException as errore:
            st.error(
                f"Errore durante il collegamento alle API: {errore}"
            )

        except (KeyError, TypeError, ValueError) as errore:
            st.error(
                f"Errore nell'elaborazione dei dati ricevuti: {errore}"
            )

else:
    # Messaggio iniziale prima di effettuare la ricerca.
    st.info(
        "🏙️ Inserisci una città italiana e premi "
        "**Cerca meteo** per visualizzare le previsioni."
    )