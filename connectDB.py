import MetaTrader5 as mt5
from datetime import datetime
import psycopg2 # https://www.youtube.com/watch?v=miEFm1CyjfM


def connect_nasdaq():
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



# psql -U federico14 -h localhost -d nasdaq
def connectDB_example ():
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
        
        # Esegui una query di esempio
        cur.execute("SELECT version();")
        
        # Recupera e stampa i risultati
        record = cur.fetchone()
        print("\nConnesso a - \n", record)
        
        # Chiudi il cursore e la connessione
        cur.close()
        conn.close()

    except (Exception, psycopg2.Error) as error:
        print("Errore durante la connessione al database PostgreSQL", error)

    return cur, conn