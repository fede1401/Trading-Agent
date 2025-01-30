from datetime import datetime
import psycopg2  # https://www.youtube.com/watch?v=miEFm1CyjfM


# Funzione per connettersi al database PostgreSQL 'nasdaq'.
def connect_nasdaq():
    try:
        # Configura i parametri di connessione per PostgreSQL
        conn = psycopg2.connect(
            dbname="nasdaq3",  # Nome del database
            user="federico",  # Nome utente
            password="fede",  # Password utente
            host="localhost",  # Indirizzo IP o nome host del server PostgreSQL
            port="5433"  # Porta di default per PostgreSQL
        )

        # Crea un oggetto cursore per eseguire le query
        cur = conn.cursor()

    except (Exception, psycopg2.Error) as error:
        # Gestisce gli errori durante la connessione
        print("Errore durante la connessione al database PostgreSQL", error)

    # Ritorna il cursore e l'oggetto di connessione al database
    return cur, conn


# psql -U federico14 -h localhost -d nasdaq
# psql -U federico -h localhost -d nasdaq3 -p 5433

# Funzione di esempio per connettersi al database 'nasdaq' e eseguire una query di esempio.
def connectDB_example():
    try:
        # Configura i parametri di connessione
        conn = psycopg2.connect(
            dbname="nasdaq",  # Nome del database
            user="federico",  # Nome utente
            password="47002",  # Password utente
            host="localhost",  # Indirizzo IP o nome host del server PostgreSQL
            port="5432"  # Porta di default per PostgreSQL
        )

        # Crea un oggetto cursore per eseguire le query
        cur = conn.cursor()

        # Esegui una query di esempio per ottenere la versione del database PostgreSQL
        cur.execute("SELECT version();")

        # Recupera il primo record restituito dalla query
        record = cur.fetchone()

        # Stampa la versione del database PostgreSQL a cui si è connessi
        print("\nConnesso a - \n", record)

        # Chiudi il cursore e la connessione
        cur.close()
        conn.close()

    except (Exception, psycopg2.Error) as error:
        # Gestisce gli errori durante la connessione e l'esecuzione della query
        print("Errore durante la connessione al database PostgreSQL", error)

    # Ritorna il cursore e l'oggetto di connessione al database
    return cur, conn


if __name__ == "__main__":
    # connectDB_example()
    connect_nasdaq()
