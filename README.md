# Gnome Device Manager

**Gnome Device Manager** è un'applicazione per Linux ispirata al *Device Manager* di Windows, sviluppata in **Python** con **GTK**.  
Permette di visualizzare e gestire in modo grafico tutti i dispositivi collegati al sistema, come schede di rete, monitor, dispositivi di input e periferiche USB.

---

### 🚀 Caratteristiche principali

- Rilevamento automatico dei dispositivi hardware collegati.  
- Visualizzazione organizzata per categorie (Input, Display, Rete, Audio, ecc.).  
- Aggiornamento dinamico della lista dei dispositivi.  
- Interfaccia grafica moderna e coerente con lo stile GNOME.  
- Possibilità di **abilitare**, **disabilitare** o **disconnettere** i dispositivi (con permessi `sudo` o `pkexec`).  

---

### 🧠 Tecnologie utilizzate

- **Python 3**
- **GTK 4 / PyGObject**
- **udev** per la gestione dei dispositivi hardware
- **gettext** per le traduzioni
- **pkexec** per l’esecuzione di comandi con privilegi elevati

---

### 🖥️ Screenshot
<img width="694" height="538" alt="Schermata del 2025-10-14 22-46-11" src="https://github.com/user-attachments/assets/cc3340d9-7790-4d02-b22d-abef80f22840" />

## ⚙️ Installazione
Da sorgente

Clona il repository ed esegui lo script principale:

```bash
git clone https://github.com/<tuo-username>/gnome-device-manager.git
cd gnome-device-manager
python3 main.py
```

## Requisiti

<ol>
  <li>Python >= 3.8</li>
  <li>PyGObject (python3-gi)</li>
  <li>GTK >= 4</li>
  <li>librerie udev</li>
  <li>permessi per eseguire comandi con pkexec</li>
</ol>

per installarli 
```bash
pip3 install -r requirements.txt
```

## Permessi e sicurezza

Alcune azioni (come disabilitare o scollegare un dispositivo) richiedono l’autenticazione tramite pkexec.
L’applicazione mostra una finestra grafica di richiesta password con titolo personalizzato per un’integrazione perfetta con GNOME.

## Contribuire

Contributi, segnalazioni di bug e nuove idee sono sempre benvenuti!

 - Fai un fork del progetto
 - Crea un branch per la tua feature (git checkout -b feature/nuova-funzione)
 - Invia una Pull Request




