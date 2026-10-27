# 🌦️ Progetto Meteo

<p align="center">
  <a href="https://progetto-meteo-gvm3zvz4cadns7gxmvm9hc.streamlit.app/">
    <img src="https://img.shields.io/badge/☀️%20PROVA%20LA%20WEB%20APP-1687F8?style=for-the-badge&logo=streamlit&logoColor=white" alt="Prova Progetto Meteo online">
  </a>
</p>

<p align="center">
  <b>Le informazioni meteorologiche, in una dashboard semplice e intuitiva.</b>
</p>

---

## 📌 Descrizione

**Progetto Meteo** è un'applicazione web realizzata in Python che permette di consultare informazioni meteorologiche attraverso una dashboard interattiva.

L'interfaccia è progettata per rendere la consultazione dei dati semplice e immediata, con una presentazione visiva pensata per facilitare la lettura delle informazioni.

L'applicazione è sviluppata con **Streamlit** e utilizza il servizio **Open-Meteo** per recuperare i dati meteorologici.

## ✨ Caratteristiche

- 🌍 Consultazione dei dati meteorologici per una località selezionata.
- 📊 Visualizzazione dei dati attraverso grafici e componenti interattivi.
- 🖥️ Dashboard accessibile direttamente dal browser.
- 🐍 Sviluppo in Python.
- ☁️ Pubblicazione online tramite Streamlit Community Cloud.

## 🚀 Prova l'applicazione

Non è necessario installare Python o configurare un ambiente di sviluppo per provare la versione online.

👉 **[Apri Progetto Meteo](https://progetto-meteo-gvm3zvz4cadns7gxmvm9hc.streamlit.app/)**

## 🛠️ Tecnologie utilizzate

| Tecnologia | Utilizzo |
|---|---|
| Python | Linguaggio di programmazione |
| Streamlit | Interfaccia web e dashboard |
| Open-Meteo | Servizio per i dati meteorologici |
| Requests | Richieste HTTP verso i servizi esterni |
| Pandas | Gestione e organizzazione dei dati |
| Plotly | Visualizzazione interattiva dei dati |
| GitHub | Versionamento e gestione del codice |
| Streamlit Community Cloud | Pubblicazione dell'applicazione online |

## 💻 Avvio in locale

Per eseguire il progetto sul proprio computer è necessario avere Python installato.

### 1. Clonare il repository

```bash
git clone https://github.com/alexred20759/Progetto-meteo.git
```

### 2. Entrare nella cartella

```bash
cd Progetto-meteo
```

### 3. Creare un ambiente virtuale

```bash
python -m venv .venv
```

### 4. Attivare l'ambiente virtuale

**Windows — PowerShell**

```powershell
.\.venv\Scripts\Activate.ps1
```

### 5. Installare le dipendenze

```bash
python -m pip install -r requirements.txt
```

### 6. Avviare la dashboard

```bash
python -m streamlit run dashboard.py
```

Al termine dell'avvio, Streamlit mostrerà nel terminale l'indirizzo locale da aprire nel browser.

## 📁 Struttura del progetto

```text
Progetto-meteo/
│
├── app.py
├── dashboard.py
├── mereo_forecasting.py
├── requirements.txt
└── README.md
```

- `app.py` — launcher del progetto.
- `dashboard.py` — dashboard meteorologica Streamlit.
- `mereo_forecasting.py` — programma originale di previsione e visualizzazione.
- `requirements.txt` — dipendenze Python del progetto.
- `README.md` — documentazione del repository.

## 🌱 Obiettivo del progetto

Il progetto nasce con l'obiettivo di realizzare uno strumento meteorologico accessibile via web, sperimentando Python, la visualizzazione dei dati e lo sviluppo di applicazioni interattive.

## 📄 Licenza

Al momento non è specificata una licenza nel presente README. Le condizioni di utilizzo e redistribuzione del codice dipendono dalla licenza eventualmente associata al repository.

---

<p align="center">
  🌦️ <b>Progetto Meteo</b>
  <br>
  <i>Python · Streamlit · Open-Meteo</i>
</p>
