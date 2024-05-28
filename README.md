# Trading-agent
Creazione di trading agent per lo sviluppo di trading automatico. Utilizzo della piattaforma MetaTrader5 con la libreria mt5 dell'API di python. 


Si lavora sotto Linux con il layer di compatibilità Wine.

Creeremo 3 agenti:

1) Agent 1 incaricato del download dei dati su DB PostgreSQL.

2) Agent 2: buy at random and sells when TP (Take Profit) >= 1%

3) Agent 3, da progettare con gli algoritmi di Reinforcement Learning.

## Algoritmo.

1. Installare Metatrader. [[Introduzione tool-strumenti Tesi.]]

2. Creare broker account demo TickMil con un conto di 1000 USDollars. Si lavora solo su azioni NASDAQ.

3. Account TickMill va connesso a Metatrader . 
   A Metatrader si possono connettere diversi broker, noi utilizziamo questo perché ha delle features interessanti.

4. Viene fatto il download dei dati delle azioni e si inserisce in un DB postgreSQL. In questo modo viene creato uno storico sul quale poi fare il learning.

5. Agente che funge da reference , compra azioni a random e le rivende quando guadagna l'1%. 
   Questo è il nemico da battere, cioè facciamo un trading agents che vuole battere questo.
   
6. Terzo agente: si sceglierà una strategia. Quando si sceglie la strategia si possono fare esperimenti offline. 

Gli algoritmi di reinforcement learning devono fare tante simulazioni , devono provare tante strategie, non possiamo aspettare il tempo vero, dobbiamo simulare tanti mesi in pochi minuti, per elaborare diverse strategie rapidamente.



## Passo 2. 
Creazione broker con account con conto demo su servizio TickMill.
[[https://www.tickmill.eu]]

##### Dati account.
![[Pasted image 20240523000505.png]]


## Passo 3.
Per la connessione di TickMill a MetaTrader5 dobbiamo scrivere codice con Python grazie alla libreria mt5. 

I vari esempi si trovano al seguente link:
[[https://github.com/fede1401/Trading-agent/tree/main/Example]]

Prima di ogni cosa bisogna inizializzare la connessione a MetaTrader 5 con `mt5.initialize()`.
Questo consente l'apertura della piattaforma.

Per effettuare il login dobbiamo passare al metodo mt5.login i campi del numero del conto + password presenti nell'immagine sopra del broker TickMill e server: 'TickmillEU-Demo'.
```
############ variabili programma ###################
path = 'C:\\Program Files\\MetaTrader 5\\terminal64.exe'
login = 
password = ''
server = 'TickmillEU-Demo'
#############################################
```

Inoltre sono presenti dei metodi per ritornare informazioni relative all'account.


## Passo 4.
Importante creare il DB postgreSQL per il salvataggio, la comprensione e l'apprendimento dei dati.

Anche se utilizziamo Windows tramite Wine per eseguire il programma, è sufficiente installare postgreSQL su Linux.
Recarsi su :  https://www.postgresql.org/download/linux/ubuntu/ per installare postgreSQL.

Utilizzare la cartella db-scripts su GitHub per:
- **Definizione nome DB e utente;**
- **Creazione utente postgreSQL;**
- **Creazione schema con varie tabelle;**
- **Definizione privilegi;**
- **Script per l'esecuzione dei compiti precedenti;**

Perciò, posizioniamoci nella cartella db-scripts nel path della cartella relativa al progetto ed eseguire da Linux:
``` sh create.sh```

Per connettersi da terminale al DB e verificare l'esistenza a questo punto eseguire:
``` psql -U federico -h localhost -d nasdaq```

Se troviamo errori e vogliamo eliminare il DB e l'utente, questi sono i passaggi:
```sudo -i -u postgres ```

```DROP DATABASE nome_database; ```
```DROP USER nome_utente; ```

****
Per la connessione al db e l'inserimento di dati vengono utilizzate funzioni in Python:
```
def connectDB():
    try:
        # Configura i parametri di connessione
        conn = psycopg2.connect(
            dbname="nasdaq",
            user="federico",
            password="47002",
            host="localhost",  # oppure l'IP del server PostgreSQL
            port="5432"  # porta predefinita per PostgreSQL
        )
        
        # Crea un cursore
        cur = conn.cursor()

    except (Exception, psycopg2.Error) as error:
        print("Errore durante la connessione al database PostgreSQL", error)

    return cur, conn



# Funzione per convertire numpy types in Python types
def convert_numpy_to_python(value):
    if isinstance(value, np.generic):
        return value.item()  # Usa .item() per ottenere un valore scalare
    return value



def insert_data(symbol, time_frame, rates, cur):
    for rate in rates:
        print(rate)
        try:
            cur.execute(
                "INSERT INTO nasdaq_actions (symbol, time_frame, time_value, open_price, high_price, low_price, close_price, tick_volume, spread, real_volume) "
                "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s) "
                "ON CONFLICT (symbol, time_value, time_frame) DO NOTHING",
                (
                    symbol,
                    time_frame,
                    datetime.fromtimestamp(rate['time']),
                    convert_numpy_to_python(rate['open']),
                    convert_numpy_to_python(rate['high']),
                    convert_numpy_to_python(rate['low']),
                    convert_numpy_to_python(rate['close']),
                    convert_numpy_to_python(rate['tick_volume']),
                    convert_numpy_to_python(rate['spread']),
                    convert_numpy_to_python(rate['real_volume'])
                )
            )
        except Exception as e:
            print("Errore durante l'inserimento dei dati: ", e)


def downloadInsertDB_data(symbol, timeframe, start_date, end_date):
    # Ottenere i dati storici
    rates = mt5.copy_rates_range(symbol, timeframe, start_date, end_date)

    # Controllare se abbiamo ottenuto i dati
    if rates is None:
        print("No data retrieved")
    else:
        # Connettersi al database
        cur, conn = connectDB()
        if cur is not None and conn is not None:
            print("\nConnessione al database nasdaq_actions avvenuta con successo.\n\n\n")
            insert_data(symbol, timeframe, rates, cur)
            conn.commit()
            
            print("Dati salvati nel db.\n\n\n")
            cur.close()
            conn.close()

    return True

```

Per ottenere i dati da inserire nel DB utilizzare il metodo ```copy_rates_range``` della libreria mt5.
Cosa contengono i dati ottenuti dal metodo  ```copy_rates_range``` ?
Contengono i dati storici delle quotazioni di un simbolo (ad esempio EURUSD) in un determinato intervallo di tempo.

Il metodo prende in input:
- **symbol**: il nome del simbolo finanziario (azione come "AAPL" che indica le azioni della APPLE)
- **timeframe**: indica l'intervallo con cui prendere i dati. Ad esempio ci sono:

| **TIMEFRAME_M1/2/3/4/5/6/10/12/15/20/30** | 1/2/3/4/5/6/10/12/15/20/30 minutes |
| ----------------------------------------- | ---------------------------------- |
| **TIMEFRAME_H1/2/3/4/6/8/12**             | **1/2/3/4/5/6/10/12 hours**        |
| **TIMEFRAME_D1**                          | **1 day**                          |
| **TIMEFRAME_W1**                          | **1 week**                         |
| **TIMEFRAME_MN1**                         | **1 month**                        |
Ad esempio se si utilizza: 
- **TIMEFRAME_D1** e si prendono i dati dal 10 maggio al 15 maggio , i dati verrano presi 5 volte ogni giorno;
- **TIMEFRAME_H12** e si prendono i dati dal 10 maggio al 15 maggio, i dati veranno presi 10 volte ogni 12 ore;

- **date_from**: data di partenza da cui prendere i dati
- **date_to**: data di arrivo 

Questo metodo ritorna:
- **data**: indica il periodo di tempo per cui sono validi i dati (ad esempio, "2020-01-08 12:00:00" significa che i dati coprono il periodo dal 2020-01-08 12:00:00 al 2020-01-08 16:00:00).
- **open**: Il prezzo di apertura dell'azione all'inizio del periodo. È il primo prezzo al quale è stata effettuata una transazione all'inizio dell'intervallo.
- **high**: Il prezzo massimo raggiunto dall'azione durante il periodo. È il prezzo più alto al quale è stata effettuata una transazione durante l'intervallo.
- **low**:  Il prezzo minimo raggiunto dall'azione durante il periodo. È il prezzo più basso al quale è stata effettuata una transazione durante l'intervallo.
- **close**: Il prezzo di chiusura dell'azione alla fine del periodo. È l'ultimo prezzo al quale è stata effettuata una transazione alla fine dell'intervallo.
- **tick_volume**: Il numero di tick (transazioni) durante il periodo.  Questo non rappresenta il volume reale ma il numero di cambiamenti di prezzo. Indica il numero di cambiamenti di prezzo durante questo periodo.
- **spread**:  La differenza tra il prezzo di acquisto (bid) e il prezzo di vendita (ask) dell'azione.
- **real_volume**: Il volume reale di scambi (può essere 0 se non disponibile o non applicabile). Rappresenta il numero di unità di strumento finanziario scambiate durante l'intervallo.


![[Pasted image 20240527155553.png]]

Questo è un esempio di ritorno dei dati del metodo.

Ma cosa indica quel prezzo?
I prezzi rappresentano il valore dell'azione in dollari statunitensi (USD). 
Ad esempio, un valore `109.513` in `high` per `AAPL` indica che l'azione Apple ha raggiunto un massimo di `109.513` dollari statunitensi durante l'intervallo di tempo specificato.

Cioè in quel periodo di tempo specificato ci sono state diverse transazioni di acquisto e vendita.

Il prezzo `high` di 109.15 dollari indica che la transazione (acquisto o vendita dell'azione) effettuata al prezzo più alto durante quel giorno è stata eseguita a 109.15 dollari per azione.

****

Per la creazione dello schema del DB ho utilizzato questa semplice tabella:
```
CREATE TABLE IF NOT EXISTS nasdaq_actions (
    symbol VARCHAR (50) NOT NULL,
    time_frame VARCHAR (50) NOT NULL,
    time_value TIMESTAMP NOT NULL,		      -- time of reading YYYY-MM-DD hh-mm-ss
    open_price DOUBLE PRECISION,
    high_price DOUBLE PRECISION,
    low_price DOUBLE PRECISION,
    close_price DOUBLE PRECISION,
    tick_volume BIGINT,
    spread INTEGER, 
    real_volume BIGINT,
    PRIMARY KEY(symbol, time_value, time_frame)
);
```

In questo caso utilizzo una singola tabella dove inserisco i dati delle varie azioni nei diversi periodi e con diversi time_frame.

In questo caso con delle query posso selezionare un'azione o un time-frame specifico per l'analisi.

Rendendo chiave "symbol, time_value, time_frame" faccio sì che non ci saranno mai due righe con stesso simbolo stessa data e stesso time_frame.


## Passo 5.
Per questo passo dobbiamo creare un agente che:
- compra azioni a random e le rivende quando  ha un TP (Take Profit) >= 1%

Come comprare queste azioni a random?

Innanzitutto consideriamo di avere 1000 USD:

Supponiamo di utilizzare 100 USD, compriamo 10 azioni da 10 USD.

Per poter comprare delle azioni è necessario utilizzare il metodo `order_send` della libreria mt5.

###### Analisi metodo `order_send`.
Il metodo prende come parametro d'input una struttura contenente dei campi utili al fine dell'ordine:

| Campo        | Descrizione                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                             |
| ------------ | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| action       | Tipo di operazione di trading. Il valore che ci servirà a noi è:<br>- *TRADE_ACTION_DEAL*: effettua un ordine per un affare istantaneo con i parametri specificati (imposta un ordine di mercato)<br><br>- *TRADE_ACTION_PENDING*: Effettua un ordine per l'esecuzione di un'affare a condizioni specifiche (ordine in sospeso)<br><br>- *TRADE_ACTION_SLTP*: Cambia posizione aperta Stop Loss e Take Profit<br>...                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                    |
| magic        | ID univoco relativo alla richiesta di trading                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                           |
| order        | Ordina il biglietto. Necessario per modificare gli ordini in sospeso. Poco utile per noi poiché utilizziamo ordini istantanei.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                          |
| symbol       | Il nome dello strumento di negoziazione per il quale viene effettuato l'ordine. (azione come "AAPL" per Apple, ...)                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                     |
| volume       | Indica il numero di azioni da acquistare.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                               |
| price        | Prezzo al quale un ordine deve essere eseguito. Il prezzo non è fissato in caso di ordini di mercato per strumenti del tipo "Market Execution" (SYMBOL_TRADE_EXECUTION_MARKET) aventi il tipo TRADE_ACTION_DEAL                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                         |
| stoplimit    | Un prezzo a cui un ordine limite in sospeso è fissato quando il prezzo raggiunge il valore del "prezzo" (questa condizione è obbligatoria). L'ordine in sospeso non viene passato al sistema di negoziazione fino a quel momento.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                       |
| sl           | Un prezzo a cui un ordine Stop Loss viene attivato quando il prezzo si muove in una direzione sfavorevole                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                               |
| tp           | Un prezzo a cui un ordine Take Profit viene attivato quando il prezzo si muove in una direzione favorevole                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                              |
| deviation    | Indica il margine di tolleranza del prezzo entro il quale un ordine di mercato può essere eseguito.<br>Questa tolleranza è espressa in punti (pip) e viene utilizzata per gestire lo **slippage**, che è la differenza tra il prezzo previsto per l'esecuzione dell'ordine e il prezzo effettivo al quale l'ordine viene eseguito.<br><br>Quando invii un ordine di mercato, specialmente in condizioni di alta volatilità, il prezzo può cambiare rapidamente. Se il prezzo cambia nel breve intervallo di tempo tra l'invio dell'ordine e la sua esecuzione, il broker potrebbe eseguire l'ordine a un prezzo diverso da quello previsto. La deviazione permette di specificare quanto sei disposto a tollerare questa differenza di prezzo.<br><br>Supponiamo di voler inviare un ordine di mercato per acquistare un'azione al prezzo corrente, ma siamo disposti a tollerare una variazione di prezzo fino a un certo limite (deviazione). Se la deviazione è impostata a 20 punti e il prezzo corrente è 150.00 USD, l'ordine verrà eseguito solo se il prezzo rimane entro 150.00 ± 0.20 USD (cioè tra 149.80 e 150.20 USD).<br> |
| type         | Order type. The value can be one of the values of the enumeration:<br>- ORDER_TYPE_BUY: Market buy order<br>- ORDER_TYPE_SELL: Market sell order<br>                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                    |
| type_filling | Campo che specifica il metodo di esecuzione dell'ordine:<br>**ORDER_FILLING_FOK (Fill or Kill)**: ordine deve essere eseguito immediatamente e completamente al prezzo specificato o essere cancellato. Non sono ammesse esecuzioni parziali.<br><br>**ORDER_FILLING_IOC (Immediate or Cancel)**: ordine deve essere eseguito immediatamente al prezzo specificato. Se non può essere eseguito completamente, la parte non eseguita verrà cancellata.<br><br>**ORDER_FILLING_RETURN**: Per gli ordini limite. Se l'ordine non può essere eseguito immediatamente, la parte non eseguita viene lasciata come un ordine pendente.<br>                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                     |
| type_time    | Campo che specifica la durata di validità dell'ordine:<br><br>**ORDER_TIME_GTC (Good Till Cancelled)**: l'ordine rimane valido fino a quando non viene cancellato manualmente.<br><br>**ORDER_TIME_DAY**: l'ordine è valido solo per la giornata di trading corrente e viene cancellato automaticamente alla fine della giornata se non eseguito.<br><br>**ORDER_TIME_SPECIFIED**: l'ordine è valido fino a una data e ora specificata.<br><br>**ORDER_TIME_SPECIFIED_DAY**: l'ordine è valido fino alla fine della giornata specificata.<br>                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                           |
| expiration   | Campo utilizzato quando `type_time` è impostato su `ORDER_TIME_SPECIFIED` o `ORDER_TIME_SPECIFIED_DAY`. <br>Specifica la data e l'ora di scadenza dell'ordine.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                          |
| comment      |                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                         |
| position     | Campo che specifica l'ID della posizione aperta che vuoi modificare o chiudere. <br><br>Questo è utile in operazioni come impostazione di Stop Loss/Take Profit (`TRADE_ACTION_SLTP`) o modifica di un ordine (`TRADE_ACTION_MODIFY`).                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                  |
| position_by  | Campo che specifica l'ID della posizione opposta quando vuoi chiudere una posizione utilizzando la funzione `TRADE_ACTION_CLOSE_BY`. <br>Questo permette di chiudere una posizione con un'altra posizione opposta dello stesso simbolo.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                 |

Considerazione importante:

> [!warning]
> Se il prezzo di un azione è di 150.90 USD **non posso** effettuare un ordine di acquisto immediato dell'azione di 50 USD. Se voglio effettuare un ordine di acquisto immediato posso comprare al prezzo dell'azione attuale, cioè di 150.90 USD.
> Se volessi effettuare un ordine di acquisto di 50 USD il mio ordine è pendente e l'ordine viene effettuato nel momento in cui l'azione scende a quel prezzo.

Se desideri acquistare un'azione a un prezzo inferiore rispetto al prezzo di mercato corrente, dovrai utilizzare un **ordine limite**. 
Questo consente di specificare il prezzo massimo che si è disposti a pagare per l'azione. Tuttavia, l'ordine verrà eseguito solo se il prezzo di mercato scende al livello del tuo prezzo limite o al di sotto di esso.


##### Ordine di Mercato (Market Order)
- **Prezzo Attuale**: 150.90 USD
- **Descrizione**: Se invii un ordine di mercato per acquistare, l'ordine verrà eseguito al prezzo di mercato corrente (150.90 USD).

##### Ordine Limite (Limit Order)
- **Prezzo Attuale**: 150.90 USD
- **Prezzo Limite**: 50.00 USD
- **Descrizione**: Se invii un ordine limite per acquistare a 50.00 USD, l'ordine verrà eseguito solo se il prezzo di mercato scende a 50.00 USD o al di sotto di esso. Fino a quel momento, l'ordine rimarrà pendente.


### Tipi di operazione di trading (ordine) :
##### **TRADE_ACTION_DEAL**
 - **Descrizione**: Effettua un ordine istantaneo (ordine di mercato) con i parametri specificati.
 - **Utilizzo**: Quando si desidera entrare o uscire dal mercato immediatamente al miglior prezzo disponibile.
 - **Esempio**: Acquistare 10 azioni di Apple al prezzo di mercato corrente.
```
import MetaTrader5 as mt5
mt5.initialize()

symbol = "AAPL"
volume = 10 # quantità di azioni

order_request = {
    "action": mt5.TRADE_ACTION_DEAL,
    "symbol": symbol,
    "volume": volume,
    "type": mt5.ORDER_TYPE_BUY,
    "price": mt5.symbol_info_tick(symbol).ask,  # Prezzo di mercato corrente
    "deviation": 20,
    "magic": 234000,
    "comment": "Acquisto di mercato",
    "type_time": mt5.ORDER_TIME_GTC,
    "type_filling": mt5.ORDER_FILLING_IOC,
}

result = mt5.order_send(order_request)

if result.retcode != mt5.TRADE_RETCODE_DONE:
    print(f"Errore nell'invio dell'ordine: {result.retcode}")
else:
    print(f"Ordine di mercato inviato con successo: {result}")

mt5.shutdown()
```
Perciò il prezzo di ordine di acquisto dell'azione è dato da:
- `mt5.symbol_info_tick(symbol).ask`  # Prezzo di mercato corrente


##### **TRADE_ACTION_PENDING**
- **Descrizione**: Effettua un ordine pendente che verrà eseguito solo se vengono soddisfatte determinate condizioni.
- **Utilizzo**: Quando si desidera piazzare un ordine che verrà eseguito solo se il mercato raggiunge un certo prezzo.
- **Esempio**: Acquistare 10 azioni di Apple a 150.00 USD (ordine limite).
```
import MetaTrader5 as mt5

mt5.initialize()

symbol = "AAPL"
price = 150.00
volume = 10

order_request = {
    "action": mt5.TRADE_ACTION_PENDING,
    "symbol": symbol,
    "volume": volume,
    "type": mt5.ORDER_TYPE_BUY_LIMIT,
    "price": price,
    "deviation": 20,
    "magic": 234000,
    "comment": "Ordine limite di acquisto",
    "type_time": mt5.ORDER_TIME_GTC,
    "type_filling": mt5.ORDER_FILLING_RETURN,
}

result = mt5.order_send(order_request)

if result.retcode != mt5.TRADE_RETCODE_DONE:
    print(f"Errore nell'invio dell'ordine: {result.retcode}")
else:
    print(f"Ordine pendente inviato con successo: {result}")

mt5.shutdown()
```


##### **TRADE_ACTION_SLTP**
- **Descrizione**: Modifica i livelli di Stop Loss e Take Profit di una posizione aperta.
- **Utilizzo**: Quando si desidera impostare o aggiornare i livelli di Stop Loss e Take Profit per gestire il rischio e i profitti.
- **Esempio**: Impostare Stop Loss e Take Profit su una posizione aperta.
```
import MetaTrader5 as mt5

mt5.initialize()

position_id = 12345678  # ID della posizione aperta
stop_loss = 145.00
take_profit = 155.00

order_request = {
    "action": mt5.TRADE_ACTION_SLTP,
    "position": position_id,
    "sl": stop_loss,
    "tp": take_profit,
    "magic": 234000,
    "comment": "Impostazione SL e TP",
}

result = mt5.order_send(order_request)

if result.retcode != mt5.TRADE_RETCODE_DONE:
    print(f"Errore nell'impostazione di SL/TP: {result.retcode}")
else:
    print(f"Stop Loss e Take Profit impostati con successo: {result}")

mt5.shutdown()
```
In questo caso settando:
- lo **stop_loss** a 145.00 USD si va a chiudere automaticamente la posizione aperta se il prezzo dell'azione scende fino a un certo livello. In questo caso, 145.00 USD.
  Ad esempio se si acquista un'azione a 150.00 USD e il prezzo scende a 145.00 USD, la posizione sarà chiusa automaticamente per evitare una perdita maggiore.

- il **take_profit** a 155.00 USD si va a chiudere automaticamente la tua posizione aperta se il prezzo dell'azione sale fino a un certo livello. In questo caso, 155.00 USD.
  Ad esempio se si acquista un'azione a 150.00 USD e il prezzo sale a 155.00 USD, la tua posizione sarà chiusa automaticamente per assicurare un profitto di 5.00 USD per azione.


##### **TRADE_ACTION_MODIFY**
- **Descrizione**: Modifica i parametri di un ordine di trading precedentemente piazzato.
- **Utilizzo**: Quando si desidera cambiare i dettagli di un ordine pendente non ancora eseguito.
- **Esempio**: Modificare il prezzo limite di un ordine limite pendente.
```
import MetaTrader5 as mt5

mt5.initialize()

order_id = 12345678  # ID dell'ordine pendente
new_price = 149.00

order_request = {
    "action": mt5.TRADE_ACTION_MODIFY,
    "order": order_id,
    "price": new_price,
    "magic": 234000,
    "comment": "Modifica del prezzo limite",
}

result = mt5.order_send(order_request)

if result.retcode != mt5.TRADE_RETCODE_DONE:
    print(f"Errore nella modifica dell'ordine: {result.retcode}")
else:
    print(f"Ordine modificato con successo: {result}")

mt5.shutdown()
```



 ##### **TRADE_ACTION_REMOVE**
- **Descrizione**: Rimuove un ordine pendente precedentemente piazzato.
- **Utilizzo**: Quando si desidera cancellare un ordine pendente che non si desidera più mantenere.
- **Esempio**: Rimuovere un ordine limite pendente.
```
import MetaTrader5 as mt5

mt5.initialize()

order_id = 12345678  # ID dell'ordine pendente

order_request = {
    "action": mt5.TRADE_ACTION_REMOVE,
    "order": order_id,
    "magic": 234000,
    "comment": "Rimozione dell'ordine pendente",
}

result = mt5.order_send(order_request)

if result.retcode != mt5.TRADE_RETCODE_DONE:
    print(f"Errore nella rimozione dell'ordine: {result.retcode}")
else:
    print(f"Ordine rimosso con successo: {result}")

mt5.shutdown()
```


##### **TRADE_ACTION_CLOSE_BY**
**Descrizione**: Chiude una posizione utilizzando una posizione opposta.
**Utilizzo**: Quando si desidera chiudere una posizione aperta con una posizione opposta dello stesso strumento finanziario.
**Esempio**: Chiudere una posizione di acquisto utilizzando una posizione di vendita.
```
import MetaTrader5 as mt5

mt5.initialize()

buy_position_id = 12345678  # ID della posizione di acquisto
sell_position_id = 87654321  # ID della posizione di vendita opposta

order_request = {
    "action": mt5.TRADE_ACTION_CLOSE_BY,
    "position": buy_position_id,
    "position_by": sell_position_id,
    "magic": 234000,
    "comment": "Chiusura della posizione per opposto",
}

result = mt5.order_send(order_request)

if result.retcode != mt5.TRADE_RETCODE_DONE:
    print(f"Errore nella chiusura della posizione: {result.retcode}")
else:
    print(f"Posizione chiusa con successo: {result}")

mt5.shutdown()
```
