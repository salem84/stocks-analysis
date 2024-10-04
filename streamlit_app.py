import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import yfinance as yf
import streamlit as st

# Scarica i dati dell'ultimo anno per un dato ticker
def get_stock_data(ticker):
    try:
        azione = yf.Ticker(ticker)
        data = azione.history(period="1y")
        if data.empty:
            return None, None
        
        nome_completo = azione.info.get('longName', 'Nome non disponibile')
        return nome_completo, data
    except:
        return None, None
    
def check_ticker_is_valid(ticker):
    try:
        data = yf.download(ticker, period="1d")
        if data.empty:
            return None
        return data
    except:
        return None

# Funzione principale per elaborare e visualizzare i dati per più stock
def plot_stocks(tickers):
    plt.figure(figsize=(12, 8))
    
    # Liste per conservare i risultati
    labels = []
    salite = []
    discese = []
    dati_ticker = []

    for ticker in tickers:
        # Scarica i dati
        nome_completo, data = get_stock_data(ticker)
        if data is None:
            st.write(f"Ticker '{ticker}' non valido o senza dati disponibili.")
            continue
        
        # Estrai i valori minimi, massimi e attuali
        min_val = data['Low'].min()
        max_val = data['High'].max()
        current_val = data['Close'][-1]

        percentuale_salita = min_val - current_val
        percentuale_discesa = max_val - current_val

        dati_ticker.append({
            'Ticker': ticker,
            'Nome Completo': nome_completo,
            'Valore Minimo': min_val,
            'Valore Attuale': current_val,
            'Valore Massimo': max_val
        })
        
        # Aggiungiamo i risultati alle liste
        labels.append(ticker)
        salite.append(percentuale_salita)
        discese.append(percentuale_discesa)

    df = pd.DataFrame(dati_ticker)
    df.set_index('Ticker', inplace=True)
    st.dataframe(df)

    # Definire la posizione delle barre
    y_pos = np.arange(len(labels))

    # Creare il grafico a barre orizzontali
    fig, ax = plt.subplots(figsize=(8, 6))

    # Barre per la salita (a destra di zero)
    ax.barh(y_pos, salite, align='center', color='green', label="")
    # Barre per la discesa (a sinistra di zero)
    ax.barh(y_pos, discese, align='center', color='red', label="")

    # Etichette
    ax.set_yticks(y_pos)
    ax.set_yticklabels(labels)
    # ax.set_xlabel('Percentuale')
    ax.set_title('Salita e discesa delle azioni rispetto al valore attuale')

    # Aggiungere la linea centrale per l'actual (zero)
    ax.axvline(0, color='black', linewidth=3)

    # Mostrare la leggenda
    ax.legend()

    # Mostrare il grafico
    st.pyplot(plt)

# Funzione per aggiungere ticker predefiniti alla lista dei ticker selezionati
def add_predefined_tickers(tickers):
    for ticker in tickers:
        if ticker not in available_tickers:
            st.session_state.available_tickers.append(ticker)
            st.session_state.selezioni.append(ticker)

    #st.session_state['available_tickers'] = available_tickers
    #st.success(f'Ticker aggiunti: {", ".join(tickers)}')

def svuota_tickers():
    available_tickers.clear()
    st.session_state.available_tickers = available_tickers

def add_ticker():
    user_input = st.session_state.text_input_ticker.strip()

    tickers = [ticker.strip().upper() for ticker in user_input.split(';') if ticker.strip()]

    for ticker in tickers:
        # Controlla se il ticker è valido
        data = check_ticker_is_valid(ticker)
        if data is not None:
            if user_input not in available_tickers:
                available_tickers.append(user_input)
                st.session_state.selezioni.append(user_input)
                st.session_state.available_tickers = available_tickers
                st.session_state.text_input_ticker = ""
        else:
            st.error(f"Ticker '{user_input}' non valido o senza dati disponibili.")

####################################################################################################

if 'available_tickers' not in st.session_state:
    st.session_state.available_tickers = []

if 'selezioni' not in st.session_state:
    st.session_state.selezioni = []

available_tickers = st.session_state.get('available_tickers', [])
selected_tickers = st.session_state.get('selezioni', [])

# Titolo dell'applicazione
st.title('Volatilità delle azioni')

with st.sidebar:
    st.markdown("""
        Puoi aggiungere:
        - un ticker specifico
        - una lista di ticker separata da ;
        - selezionare un insieme di stocks predefinite usando i button sottostanti.
        """)

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

    col1, col2 = st.columns([2,1])

    with col1:
        # Input dell'utente per inserire i ticker
        instr = 'Inserisci un ticker:'
        user_input = st.text_input(instr, placeholder=instr, key='text_input_ticker',  label_visibility='collapsed', on_change=add_ticker)
    
    with col2:
        addBtn = st.button('Aggiungi', on_click=add_ticker)
    
    st.divider()

    if st.button('Aggiungi Global Tech'):
        add_predefined_tickers(global_tech_stocks)

    if st.button('Aggiungi Banche Italiane'):
        add_predefined_tickers(banche_italiane_stocks)

    if st.button('Aggiungi FTSE MIB 40 Stocks'):
        add_predefined_tickers(mib40_tickers)

    if st.button('Svuota tutto'):
        svuota_tickers()


# Select box per mostrare i ticker aggiunti
selected_stock = st.multiselect('Aggiungi un ticker usando il menù laterale:', st.session_state.available_tickers, default=st.session_state.selezioni)

# Mostra i grafici solo se ci sono ticker validi aggiunti
if len(selected_stock) > 0:
    if st.button('Mostra grafico'):
        plot_stocks(selected_stock)
