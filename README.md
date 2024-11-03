# 📈 Applicazione per la Visualizzazione della Volatilità delle Azioni

Consente di visualizzare il grafico con il posizionamento percentuale dei prezzi delle azioni nel range di movimento del titolo.
Nel punto 0 viene visualizzato il dato odierno.
Le azioni sono ordinate dall'alto verso il basso in ordine di spostamento tra minimo e massimo. Quelle che si sono mosse di meno vengono visualizzate in alto nel grafico.
Per l'analisi vengono utilizzati i dati di Yahoo Finance.

## Come eseguire l'applicazione sul tuo computer

1. Installa i requisiti:
   ```sh
   pip install -r requirements.txt
   ```

2. Esegui l'applicazione
   ``` sh
   streamlit run streamlit_app.py
   ```

## Funzionalità

- **Aggiungi Ticker:** Puoi aggiungere ticker specifici compatibili con Yahoo Finance.
- **Mostra Grafico:** Mostra la tabella e il grafico con le informazioni sulle azioni selezionate. 
- **Condividi:** Condividi la pagina con un link generato automaticamente.