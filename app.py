import streamlit as st
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import time

# Configurazione della pagina Streamlit
st.set_page_config(page_title="Inviato automatico Email", page_icon="✉️", layout="centered")

st.title("✉️ Invio Email Massivo (Singolo)")
st.write("Questo strumento invia la stessa email a più destinatari singolarmente, proteggendo la privacy.")

# Layout a due colonne per le credenziali
col1, col2 = st.columns(2)
with col1:
    mittente = st.text_input("Il tuo indirizzo Gmail", placeholder="esempio@gmail.com")
with col2:
    password = st.text_input("La tua 'Password per le app'", type="password", help="Inserisci la password di 16 caratteri generata nel tuo account Google.")

# Campi per la composizione dell'email
oggetto = st.text_input("Oggetto dell'email", value="Proposta editoriale - [Tuo Nome]")
corpo_testo = st.text_area("Corpo dell'email", height=200, placeholder="Gentile redazione,\n\nVi contatto per...")

# Campo per i destinatari
destinatari_raw = st.text_area(
    "Lista Destinatari (inserisci un indirizzo per riga o separati da virgola)",
    placeholder="editore1@esempio.it\neditore2@esempio.com"
)

# Sliders per personalizzare il ritardo
ritardo = st.slider("Ritardo tra un invio e l'altro (in secondi)", min_value=1, max_value=15, value=3, 
                    help="Un ritardo maggiore riduce il rischio che Gmail scambi i tuoi invii per spam.")

# Pulsante di invio
if st.button("🚀 Avvia Invio Email", type="primary"):
    
    # Validazione rapida dei campi
    if not mittente or not password:
        st.error("Per favore, inserisci le tue credenziali Gmail.")
    elif not oggetto or not corpo_testo:
        st.error("L'oggetto o il corpo dell'email non possono essere vuoti.")
    elif not destinatari_raw.strip():
        st.error("Inserisci almeno un destinatario.")
    else:
        # Pulizia della lista dei destinatari
        destinatari = [d.strip() for d in destinatari_raw.replace(",", "\n").split("\n") if d.strip()]
        
        st.info(f"Preparazione all'invio di {len(destinatari)} email...")
        
        # Elementi grafici dinamici
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        # CORREZIONE: Creiamo un segnaposto fisso per i log
        log_placeholder = st.empty()
        logs = ""
        
        # Mostriamo il box iniziale vuoto
        log_placeholder.text_area("Log delle operazioni:", value=logs, height=150)

        try:
            # Connessione al server SMTP
            status_text.text("Connessione al server Gmail in corso...")
            server = smtplib.SMTP("smtp.gmail.com", 587)
            server.starttls()
            server.login(mittente, password)
            
            logs += "✅ Connessione stabilita con successo.\n"
            log_placeholder.text_area("Log delle operazioni:", value=logs, height=150)

            # Ciclo di invio
            for index, destinatario in enumerate(destinatari):
                status_text.text(f"Inviando a: {destinatario}...")
                
                try:
                    # Costruzione messaggio
                    msg = MIMEMultipart()
                    msg['From'] = mittente
                    msg['To'] = destinatario
                    msg['Subject'] = oggetto
                    msg.attach(MIMEText(corpo_testo, 'plain', 'utf-8'))
                    
                    # Invio effettivo
                    server.sendmail(mittente, destinatario, msg.as_string())
                    logs += f"[{index + 1}/{len(destinatari)}] Inviata a {destinatario}\n"
                    
                except Exception as e_single:
                    logs += f"❌ Errore con {destinatario}: {str(e_single)}\n"
                
                # Aggiorniamo il segnaposto senza sovrascriverlo
                log_placeholder.text_area("Log delle operazioni:", value=logs, height=150)
                
                # Aggiornamento barra progresso
                percentuale = int(((index + 1) / len(destinatari)) * 100)
                progress_bar.progress(percentuale)
                
                # Pausa anti-spam
                if index < len(destinatari) - 1:
                    time.sleep(ritardo)
            
            server.quit()
            status_text.text("Operazione completata!")
            st.success(f"Fatto! Processo terminato. {len(destinatari)} email elaborate.")

        except Exception as e:
            st.error(f"Errore di connessione generale: {e}")
            st.warning("Verifica che la tua 'Password per le app' sia corretta e che la verifica in due passaggi sia attiva.")
            
