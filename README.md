# Trading-agent
> [!IMPORTANT]
> Sviluppo di **trading agent** per lo sviluppo di **trading automatico**. (senza intervento umano diretto)

Lo sviluppo di trading agent consiste nella **creazione di software autonomi in grado di eseguire operazioni di trading sui mercati finanziari senza intervento umano diretto**.

Per lo sviluppo di questi abbiamo necessita di alcuni strumenti e tool.
Si utilizzerà:
- **MetaTrader 5 (MT5)**: Una piattaforma potente e versatile per l'analisi di mercato e per effettuare operazioni di trading su diversi strumenti finanziari.
- **Broker TickMill** con account demo: Utilizzato per testare strategie senza rischiare denaro reale.

Per la connessione della piattaforma MetaTrader5 a Python si utilizza la libreria '*mt5*' dell'API di Python.

Si lavora sotto Linux con il layer di compatibilità Wine.

Nel dominio della mia applicazione si effettua trading con i simboli azionari quotati sulla borsa del Nasdaq e messi a disposizione dal broker TickMill.

***

### Algoritmo per lo sviluppo di trading agent.
1. Installare Metatrader.

2. Creare broker account demo TickMil con un conto di 1000 USDollars. 

3. Definizione di funzioni per connessione e login server MetaTrader5.

4. Sviluppo e creazione dell'agent1. (agente incaricato del download dei dati su DB PostgreSQL)

5. Sviluppo e creazione dell'agent2. (agente che funge da reference, e all'infinito compra azioni a random, le rivende quando guadagna l'1% e va in pausa per 15 minuti)

6. Sviluppo e creazione dell'agent3 (agente che utilizza gli algoritmi di Reinforcement Learning).

Lo sviluppo del codice è reso modulare, cioè i file agent1.py e agent2.py utilizzano funzioni da file esterni. 

Non si ha un simulatore, questo verrà creato dallo storico dei dati online, grazie all'agent1.

***

#### Broker per trading agent: TickMill
Realizzare un account demo in USD in TickMill con un budget di 1000 USD nel seguente sito:[https://www.tickmill.eu](TickMill).

Impostare come deposit: 1000 USD con una leva di 1:1.

Una volta effettuata la creazione, arriveranno le credenziali per email.

Dato che i campi del numero del conto relativi all'account sono sempre utilizzati per i vari login nel programma possiamo immagazzinarli in un file "variableLocal.py" nel workspace.
In questo caso li avremo sempre da qualche parte.

Nel progetto si lavora solamente con i simboli azionari iscritti alla borsa del Nasdaq.
Il broker non accetta tutti i simboli azionari, perciò nel codice ci sarà un file destinato ad ottenerli.

Utilizzo della piattaforma **Metatrader5** che offre API Python per la realizzazione di trading agents.

### Metatrader 5.
##### Configurazione sistema.
Utilizzare un elaboratore con architettura AMD che sia x_86, ... (poiché problemi con ARM).

Utilizzare distribuzione Linux "Ubuntu".

###### Seguire questi passi:
https://www.mql5.com/en/forum/457940

1. Install Wine with the following command (skip if you already installed)

`sudo apt install wine`

2. Install the MetaTrader 5 platform:
For Ubuntu:
`wget https://download.mql5.com/cdn/web/metaquotes.software.corp/mt5/mt5ubuntu.sh ; chmod +x mt5ubuntu.sh ; ./mt5ubuntu.sh` 

For Debian:   
`wget https://download.mql5.com/cdn/web/metaquotes.software.corp/mt5/mt5debian.sh ; chmod +x mt5debian.sh ; ./mt5debian.sh`

Se l'installazione non va a buon fine, digitare sul terminale `winecfg` e selezionare come versione di Windows 10.

3. Download Python 3.8 to your Downloads folder

`cd ~/Downloads`
`wget https://www.python.org/ftp/python/3.8.0/python-3.8.0-amd64.exe --no-check-certificate
`

4. Install Python 3.8 for the Windows environment in Wine. Assuming you are in the _~/Downloads_ folder

`wine cmd`
`python-3.8.0-amd64.exe``
`

5. A questo punto nuovamente digitare `python-3.8.0-amd64.exe`, dirigersi a Modify e aggiungere la spunta "Add Python to environment variables"


### Wine.
Wine (originariamente un acronimo di "Wine Is Not an Emulator") è un livello di compatibilità  open source che consente di eseguire software/applicazioni **Windows** anche su sistemi operativi compatibili con POSIX, come Linux, macOS e BSD.

I coder di Wine lo definiscono precisamente come un "_non-emulatore_". 

La strategia adottata dagli sviluppatori non prevede infatti una forma di emulazione diretta (come una macchina virtuale o un emulatore o un sistema di containerizzazione) ma procede convertendo le API di Windows in chiamate di sistema **POSIX**(_Portable Operating System Interface for Unix_) eliminando le prestazioni e le penalità di memoria di altri metodi e consentendoti di integrare in modo pulito le applicazioni Windows nel tuo desktop.

#### A cosa è necessario Wine?
Noi dobbiamo lavorare con l'API di python della libreria mt5 di Metatrader5. 
Purtroppo l'installazione di questa libreria avviene soltanto con sistema operativo Windows, perciò con Wine riusciamo a utilizzare questa libreria.


#### Installazione MetaTrader5.
Per la connessione di TickMill a MetaTrader5 dobbiamo scrivere codice con Python grazie alla libreria mt5. 

Per installare Metatrader 5:
- `wine cmd`
- `pip install MetaTrader5`


Quello che faccio è:
- Utilizzare Ubuntu e visual Studio code per programmare;
- Se voglio runnare il programma che utilizza le libreria di Metatrader5 , utilizzo Wine:
	- esegui su terminale Linux il comando "wine cmd" che apre il cmd di Windows
	- A questo punto navigo per arrivare al path dove si trova il file python e lo eseguo da wine cmd con il comando "python nomefile.py"



## Database postgreSQL.
Importante creare il DB postgreSQL per il salvataggio, la comprensione e l'apprendimento dei dati.

Anche se utilizziamo Windows tramite Wine per eseguire il programma, è sufficiente installare postgreSQL su Linux.
Recarsi su :  https://www.postgresql.org/download/linux/ubuntu/ per installare postgreSQL.

Utilizzare la cartella "db-scripts" per:
- **Definizione nome DB e utente;**
- **Creazione utente postgreSQL;**
- **Creazione schema con varie tabelle;**
- **Definizione privilegi;**
- **Script per l'esecuzione dei compiti precedenti;**

Per creare il database, ci posizioniamo nella cartella db-scripts nel path della cartella relativa al progetto ed eseguire da Linux:
``` sh create.sh```

##### Collegamento da terminale al DB.
Per il collegamento al database da terminale si utilizza il comando
``` psql -U nome_utente -h localhost -d nome_db```, in questo caso si utilizza ``` psql -U federico -h localhost -d nasdaq```

verrà chiesta una password che si trova nel file "create-db-user.sql".

Una volta entrati possiamo effettuare diverse query oppure inserimenti ed eliminazioni.

Ad esempio se volessimo:
##### Eliminare tutte le righe di una tabella:
``` DELETE FROM nome_tabella; ```

##### Eliminare una tabella:
``` DROP TABLE nome_tabella; ```

##### Cercare qualcosa in ordine decrescente:
```  SELECT nome_colonna FROM nome_tabella ORDER BY nome_colonna DESC```

##### Tornare il risultato della query con un limite di righe:
``` SELECT nome_colonna FROM nome_tabella WHERE condizioni LIMIT 1```
In questo caso con l'1 dopo il LIMIT torna solo una riga,...

***

##### Eliminare il database: o l'utente
Per effettuare l'eliminazione del database si complica poiché dobbiamo accedere come utente postgres. 
Ecco i seguenti passaggi:
1. ```sudo -i -u postgres ```
2. ``` psql ```
3. ```DROP DATABASE nome_database; ``` OR ```DROP USER nome_utente; ```

****

### Sviluppo Agent1 e Agent2.
> [!IMPORTANT]
> L'agent1 si occupa di:
> - **Raccogliere i dati di mercato dei simboli azionari quotati sulla borsa Nasdaq accettati dal broker TickMill** e
> - **Inserire questi dati all'interno del database postgreSQL**.

Lo scopo di questo è ==creare uno storico su cui basare l'analisi e l'apprendimento dell'agent3==.


> [!IMPORTANT]
> L'Agent 2 svolge le seguenti operazioni:
>
> - **Acquista azioni** in modo casuale da un pool di simboli azionari accettati dal broker TickMill (5% per capitalizzazione decrescente).
> - **Rivende le azioni acquistate** quando il profitto raggiunge un Take Profit (TP) di almeno 1%.


