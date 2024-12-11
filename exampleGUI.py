import tkinter as tk
from tkinter import ttk
import time

def start_loading():
    # Reset della barra di progresso
    progress_bar['value'] = 0
    status_label['text'] = "Caricamento in corso..."
    app.update()  # Aggiorna la GUI

    # Simula il caricamento in 10 passi
    total_steps = 10
    for step in range(1, total_steps + 1):
        time.sleep(0.5)  # Simula il tempo di caricamento
        progress_bar['value'] = (step / total_steps) * 100  # Aggiorna la barra
        percent_label['text'] = f"{int((step / total_steps) * 100)}%"  # Aggiorna la percentuale
        app.update()  # Aggiorna la GUI

    # Aggiorna lo stato finale
    status_label['text'] = "Caricamento completato!"

# Creazione della finestra principale
app = tk.Tk()
app.title("Barra di Caricamento")
app.geometry("300x150")

# Etichetta di stato
status_label = tk.Label(app, text="Premi 'Avvia' per iniziare", font=("Arial", 12))
status_label.pack(pady=10)

# Barra di progresso
progress_bar = ttk.Progressbar(app, orient="horizontal", length=250, mode="determinate")
progress_bar.pack(pady=10)

# Etichetta per la percentuale
percent_label = tk.Label(app, text="0%", font=("Arial", 10))
percent_label.pack()

# Bottone per avviare il caricamento
start_button = tk.Button(app, text="Avvia", command=start_loading)
start_button.pack(pady=10)

# Avvia la finestra principale
app.mainloop()
