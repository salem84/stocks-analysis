import datetime
import numpy as np
import pandas as pd
import yfinance as yf
import streamlit as st
import plotly.graph_objects as go
import streamlit.components.v1 as components
import os

# Scarica i dati dell'ultimo anno per un dato ticker
@st.cache_data(ttl=3600)
def get_stock_data(ticker, start_date, end_date):
    try:
        azione = yf.Ticker(ticker)
        data = azione.history(start=start_date, end=end_date)
        if data.empty:
            return None, None
        
        nome_completo = azione.info.get('longName', 'Nome non disponibile')
        return nome_completo, data
    except:
        return None, None
    
def check_ticker_is_valid(ticker):
    try:
        data = yf.download(ticker, period="5d")
        if data.empty:
            return None
        return data
    except:
        return None

# Funzione principale per elaborare e visualizzare i dati per più stock
def plot_stocks(tickers, start_date, end_date):
    
    # Creare il DataFrame vuoto
    df = pd.DataFrame()

    for ticker in tickers:
        # Scarica i dati
        nome_completo, data = get_stock_data(ticker, start_date, end_date)
        if data is None:
            st.write(f"Ticker '{ticker}' non valido o senza dati disponibili.")
            continue
        
        # Estrai i valori minimi, massimi e attuali
        min_val = data['Low'].min()
        max_val = data['High'].max()
        current_val = data['Close'][-1]

        # Trova i giorni corrispondenti al minimo e massimo
        min_day = data['Low'].idxmin()  # Giorno del valore minimo
        max_day = data['High'].idxmax()  # Giorno del valore massimo

        percentuale_da_max = 1 - (current_val / max_val)
        percentuale_da_min = (min_val / current_val) - 1
        differenza = abs(percentuale_da_min - percentuale_da_max)

        nuova_riga = pd.DataFrame([{
            'Ticker': ticker,
            'Nome Completo': nome_completo,
            'YF': 'https://finance.yahoo.com/quote/{0}'.format(ticker),
            'Valore Minimo': min_val,
            'Giorno Minimo': min_day,
            'Valore Attuale': current_val,
            'Valore Massimo': max_val,
            'Giorno Massimo': max_day,
            'Perc. da Min': percentuale_da_min*100,
            'Perc. da Max': percentuale_da_max*100,
            'Differenza': differenza,
            'FormattedMin': f"{min_val:.2f} ({min_day.strftime('%d/%m/%Y')})",
            'FormattedMax': f"{max_val:.2f} ({max_day.strftime('%d/%m/%Y')})"
        }])

        df = pd.concat([df, nuova_riga], ignore_index=True)

    # Preparo dataframe
    df.set_index('Ticker', inplace=True)
    df = df.sort_values(by='Differenza', ascending=False)
    st.dataframe(df, 
                 column_order=[
                     'Nome Completo', 
                     'YF', 
                     'FormattedMin',
                     'Valore Attuale',
                     'FormattedMax',
                     ],
                 column_config={
                    'YF': st.column_config.LinkColumn("YF", display_text="🌍"),
                    'Valore Attuale': st.column_config.NumberColumn(format="%.2f"),
                    'FormattedMin': st.column_config.TextColumn("Minimo"),
                    'FormattedMax': st.column_config.TextColumn("Massimo"),
                    'Differenza': None
                })

    # Creare il grafico a barre orizzontali con Plotly
    fig = go.Figure()

    # Barre per la salita
    fig.add_trace(go.Bar(
        y=df.index,
        x=df['Perc. da Min'],
        orientation='h',
        name='Perc. da Min',
        marker=dict(color='green')
    ))

    # Barre per la discesa
    fig.add_trace(go.Bar(
        y=df.index,
        x=df['Perc. da Max'],
        orientation='h',
        name='Perc. da Max',
        marker=dict(color='red')
    ))

    # Aggiornare il layout del grafico
    fig.update_layout(
        #title='Salita e discesa delle azioni rispetto al valore attuale ordinate per ampiezza',
        xaxis_title='Percentuale',
        yaxis_title='',
        barmode='overlay',  # Se vuoi le barre sovrapposte (puoi cambiare in 'group')
        #legend=dict(orientation="h", yanchor="bottom", y=1, xanchor="right", x=1),
        showlegend=False,
        height=200+30*len(df)
    )

    # Mostrare il grafico interattivo con Streamlit
    st.plotly_chart(fig)


# Funzione per aggiungere ticker predefiniti alla lista dei ticker selezionati
def add_predefined_tickers(tickers):
    for ticker in tickers:
        if ticker not in st.session_state.available_tickers:
            st.session_state.available_tickers.append(ticker)
            st.session_state.selezioni.append(ticker)


def svuota_tickers():
    st.session_state.available_tickers = []
    st.session_state.selezioni = []

def add_ticker():
    user_input = st.session_state.text_input_ticker.strip()

    tickers = [ticker.strip().upper() for ticker in user_input.split(';') if ticker.strip()]

    for ticker in tickers:
        # Controlla se il ticker è valido
        data = check_ticker_is_valid(ticker)
        if data is not None:
            if ticker not in st.session_state.available_tickers:
                st.session_state.available_tickers.append(ticker)
            
            if ticker not in st.session_state.selezioni:
                st.session_state.selezioni.append(ticker)
            # else:
            #     st.write('non aggiungo')   

            st.session_state.text_input_ticker = ""
        else:
            st.error(f"Ticker '{user_input}' non valido o dati non disponibili.")


def add_share_button():
    stocks_comma =  ';'.join(selected_stocks)
    html = f'''
         <a class="share-button" onclick="sharePage(event)">
            <span class="icon">🔗Condividi</span> 
        </a>
        '''
    css = '''
        <style>
            .share-button {
                display: inline-flex;
                align-items: center;
                padding: 0.25rem 0.75rem;
                font-size: 16px;
                color: rgb(49, 51, 63);
                background-color: white;
                border: 1px solid rgba(49, 51, 63, 0.2);
                border-radius: 0.5rem;
                cursor: pointer;
                font-family: "Source Sans Pro", sans-serif;
                font-size: 16px;
                # transition: background-color 0.3s;
                text-decoration: none;
            }

            .share-button .icon {
                margin-right: 8px;
                font-size: 18px;
            }

            .share-button:hover {
                border-color: rgb(255, 75, 75);
                color: rgb(255, 75, 75);
            }
        </style>
        '''
    
    js = f'''
        <script>
            function sharePage(evt) {{
                evt.preventDefault();

                if (navigator.share) {{
                    navigator.share({{
                        title: document.title,
                        text: "Guarda questa pagina!",
                        url: "?isin={stocks_comma}"
                    }}).then(() => {{
                        console.log("Pagina condivisa con successo");
                    }}).catch((error) => {{
                        console.error("Errore nella condivisione:", error);
                    }});
                }}
                else {{
                    navigator.clipboard.writeText(evt.target.getAttribute("href")).then(() => {{
                        alert("Link copiato negli appunti"); 
                    }}, 
                    () => {{
                        alert("Errore nella copia del link");
                    }});
                }}
            }}
        </script>
    '''

    components.html(css + js + html)

####################################################################################################

if 'available_tickers' not in st.session_state:
    st.session_state.available_tickers = []

if 'selezioni' not in st.session_state:
    st.session_state.selezioni = []

show_plot = False

# Gestione dei parametri presenti in query string
if 'isin' in st.query_params:
    query_tickers = st.query_params.isin
    query_tickers_list = query_tickers.split(';')
    add_predefined_tickers(query_tickers_list)
    #show_plot = True

# Titolo dell'applicazione
st.title('Posizionamento delle azioni')

with st.sidebar:

    # Definisci alcune liste predefinite di ticker
    global_tech_stocks = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA']
    banche_italiane_stocks = ['BAMI.MI', 'BMED.MI', 'BMPS.MI', 'BPE.MI', 'FBK.MI', 'ISP.MI', 'MB.MI', 'UCG.MI']
    mib40_tickers = [
        "A2A.MI", "AMP.MI", "AZM.MI",  # A2a (A2A.MI), Amplifon (AMP.MI), Azimut (AZM.MI)
        "BAMI.MI", "BC.MI", "BMED.MI",  # Banco Bpm (BAMI.MI), Brunello Cucinelli (BC.MI), Banca Mediolanum (BMED.MI)
        "BMPS.MI", "BPE.MI", "BPSO.MI",  # Banca Monte Paschi Siena (BMPS.MI), Bper Banca (BPE.MI), Bca Pop Sondrio (BPSO.MI)
        "CPR.MI", "DIA.MI", "ENEL.MI",  # Campari (CPR.MI), Diasorin (DIA.MI), Enel (ENEL.MI)
        "ENI.MI", "ERG.MI", "FBK.MI",  # Eni (ENI.MI), Erg (ERG.MI), Finecobank (FBK.MI)
        "G.MI", "HER.MI", "IG.MI",  # Generali (G.MI), Hera (HER.MI), Italgas (IG.MI)
        "INW.MI", "IP.MI", "ISP.MI",  # Inwit (INW.MI), Interpump Group (IP.MI), Intesa Sanpaolo (ISP.MI)
        "IVG.MI", "LDO.MI", "MB.MI",  # Iveco Group (IVG.MI), Leonardo (LDO.MI), Mediobanca (MB.MI)
        "MONC.MI", "NEXI.MI", "PIRC.MI",  # Moncler (MONC.MI), Nexi (NEXI.MI), Pirelli & C (PIRC.MI)
        "PST.MI", "PRY.MI", "RACE.MI",  # Poste Italiane (PST.MI), Prysmian (PRY.MI), Ferrari (RACE.MI)
        "REC.MI", "SPM.MI", "SRG.MI",  # Recordati Ord (REC.MI), Saipem (SPM.MI), Snam (SRG.MI)
        "STLAM.MI", "STMMI.MI", "TEN.MI",  # Stellantis (STLAM.MI), Stmicroelectronics (STMMI.MI), Tenaris (TEN.MI)
        "TIT.MI", "TRN.MI", "UCG.MI",  # Telecom Italia (TIT.MI), Terna (TRN.MI), Unicredit (UCG.MI)
        "UNI.MI"  # Unipol (UNI.MI)
    ]

    if st.button('Aggiungi Global Tech'):
        add_predefined_tickers(global_tech_stocks)

    if st.button('Aggiungi Banche Italiane'):
        add_predefined_tickers(banche_italiane_stocks)

    if st.button('Aggiungi FTSE MIB 40 Stocks'):
        add_predefined_tickers(mib40_tickers)

    if st.button('Svuota tutto'):
        svuota_tickers()


text = """
Puoi aggiungere:
- un ticker specifico (es. STLAM.MI, AAPL) compatibile con [Yahoo Finance](https://finance.yahoo.com)
- una lista di ticker separata da __;__
- selezionare un insieme di stocks predefinite usando i button nel menu di navigazione laterale

"""

st.info(text, icon="✍️")

col1, col2 = st.columns([2,1])

with col1:
    # Input dell'utente per inserire i ticker
    instr = 'Inserisci un ticker:'
    user_input = st.text_input(instr, placeholder=instr, key='text_input_ticker',  label_visibility='collapsed', on_change=add_ticker)

with col2:
    addBtn = st.button('Aggiungi', on_click=add_ticker)

st.divider()

today = datetime.datetime.now()
year_ago = today - datetime.timedelta(days=365)
selected_date = st.date_input(
    "Seleziona periodo",
    (year_ago, today),
    year_ago,
    today,
    format="DD/MM/YYYY",
)

# Select box per mostrare i ticker aggiunti
selected_stocks = st.multiselect('Ticker da visualizzare nel grafico:', st.session_state.available_tickers, default=st.session_state.selezioni
                                # , on_change=lambda: st.query_params.clear()
                                , key="selezioni"
                                #, on_change=plot_selected_stocks, key="selected_stocks"
                                )

# Mostra i grafici solo se ci sono ticker validi aggiunti
if len(selected_stocks) > 0:
    if st.button('Mostra grafico') or show_plot:
        plot_stocks(selected_stocks, selected_date[0], selected_date[1])
        add_share_button()


# st.write(st.session_state.available_tickers)
# st.write(st.session_state.selezioni) 