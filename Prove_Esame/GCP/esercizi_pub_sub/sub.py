#---Esercizio 1---

'''
import os
import sys
import json
from google.cloud import pubsub_v1
from google.cloud import firestore

project_id = os.environ['PROJECT_ID']
sub_name = os.environ['SUBSCRIPTION_NAME']

subscriber = pubsub_v1.SubscriberClient()
sub_path = subscriber.subscription_path(project_id, sub_name)

#Funzione che scatta automaticamente quando arriva un mesaggio
def callback(message):

    dati = json.loads(message.data.decode('utf-8'))
    value1 = dati.get('id')
    

    #if not cap_interessati or str(cap_messaggio) in cap_interessati:
    print(f"Ricevuto pacchetto numero {value1}")

if __name__ == '__main__':
    print("Tentativo di avvio del Subscriber...")
    pull = subscriber.subscribe(sub_path, callback=callback)
    try:
        print(f"In ascolto su {sub_path}...")
        pull.result()
    except Exception as e:
        # Se c'è un errore (es. permessi, nomi sbagliati), ora lo vedrai scritto!
        print(f"❌ Il subscriber si è fermato per un errore: {e}")
        pull.cancel()
    except KeyboardInterrupt:
        # Questo serve per quando premi Ctrl+C
        pull.cancel()
        print("\n🛑 Subscriber fermato manualmente.")
'''
#----------------

#----Esercizio 2----
'''
import os
import sys
import json
from google.cloud import pubsub_v1
from google.cloud import firestore

project_id = os.environ['PROJECT_ID']
sub_name = os.environ['SUBSCRIPTION_NAME']

subscriber = pubsub_v1.SubscriberClient()
sub_path = subscriber.subscription_path(project_id, sub_name)

# Se vuoi legger qualcosa passata per linea di comando
cap_interessati = sys.argv[1:] 

#Funzione che scatta automaticamente quando arriva un mesaggio
def callback(message):

    dati = json.loads(message.data.decode('utf-8'))
    temp = dati.get('temperatura')

    if temp is not None and int(temp) > 50:
        print("Allarme")
    elif temp is not None and int(temp) < 50:
        print("Ghiacciato")

    message.ack()
        

if __name__ == '__main__':
    print("Tentativo di avvio del Subscriber...")
    pull = subscriber.subscribe(sub_path, callback=callback)
    try:
        print(f"In ascolto su {sub_path}...")
        pull.result()
    except Exception as e:
        # Se c'è un errore (es. permessi, nomi sbagliati), ora lo vedrai scritto!
        print(f"❌ Il subscriber si è fermato per un errore: {e}")
        pull.cancel()
    except KeyboardInterrupt:
        # Questo serve per quando premi Ctrl+C
        pull.cancel()
        print("\n🛑 Subscriber fermato manualmente.")
'''
#----------------

#-----Esercizio 3-------
'''
import os
import sys
import uuid
from google.cloud import pubsub_v1

# --- CONFIGURAZIONE ---
PROJECT_ID = os.environ.get('PROJECT_ID')

# Argomenti da riga di comando (es: python3 worker.py nome_topic)
if len(sys.argv) < 2:
    print("Errore: specifica il topic da ascoltare.")
    sys.exit(1)

topic_name = sys.argv[1]

# 1. Setup Percorsi
topic_path = f"projects/{PROJECT_ID}/topics/{topic_name}"

# Generiamo un nome sottoscrizione casuale (es. sub-cartolina-xf32s)
sub_name = f"sub-{topic_name}-{str(uuid.uuid4())[:8]}"
subscription_path = f"projects/{PROJECT_ID}/subscriptions/{sub_name}"

# 2. Inizializzazione Client
subscriber = pubsub_v1.SubscriberClient()

# Creazione Sottoscrizione Effimera
print(f"Creazione sottoscrizione: {sub_name} su topic: {topic_path}")
try:
    subscriber.create_subscription(request={"name": subscription_path, "topic": topic_path})
except Exception as e:
    print(f"Errore creazione subscription (forse il topic non esiste?): {e}")
    sys.exit(1)

# 3. La Callback (Cosa fare quando arriva un messaggio)
def callback(message_obj):
    # IMPORTANTE: Decodifica i dati
    content = message_obj.data.decode("utf-8")
    print(f"📩 Ricevuto: {content}")
    
    # --- SPAZIO PER LA TUA LOGICA ---
    # Esempio: db.get_element("collection", content)
    # --------------------------------
    
    # Conferma ricezione (altrimenti PubSub lo rimanda all'infinito)
    message_obj.ack()

# 4. Loop di Ascolto e Pulizia
streaming_pull_future = subscriber.subscribe(subscription_path, callback=callback)
print(f"In ascolto... (Ctrl+C per chiudere)")

with subscriber:
    try:
        # Mantiene lo script vivo
        streaming_pull_future.result()
    except KeyboardInterrupt:
        print("\nChiusura richiesta dall'utente...")
        streaming_pull_future.cancel()
    finally:
        # PULIZIA FINALE: Cancella la sottoscrizione
        print("Eliminazione sottoscrizione temporanea...")
        subscriber.delete_subscription(request={"subscription": subscription_path})
        print("Fatto. Ciao!")
'''
#----------------

