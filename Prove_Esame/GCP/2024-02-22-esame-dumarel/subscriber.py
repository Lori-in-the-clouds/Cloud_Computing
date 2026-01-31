import os
import sys
import json
from google.cloud import pubsub_v1

# Leggiamo i CAP passati da riga di comando: python client_sub.py 41121 41125
cap_interessati = sys.argv[1:] 

project_id = os.environ['PROJECT_ID']
sub_name = os.environ['SUBSCRIPTION_NAME']

subscriber = pubsub_v1.SubscriberClient()
sub_path = subscriber.subscription_path(project_id, sub_name)

def callback(message):
    message.ack()
    dati = json.loads(message.data.decode('utf-8'))
    print("arrivato messaggio Pub/Sub")
    
    cap_messaggio = dati.get('cap')
    indirizzo = dati.get('indirizzo')

    # LOGICA DI FILTRO:
    # Se non abbiamo specificato CAP, mostriamo tutto.
    # Se abbiamo specificato dei CAP, mostriamo solo quelli corrispondenti.
    if not cap_interessati or str(cap_messaggio) in cap_interessati:
        print(f"NUOVO CANTIERE TROVATO!")
        print(f"Indirizzo: {indirizzo}")
        print(f"CAP: {cap_messaggio}")
        print("-" * 30)

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

