#----Esercizio 1----
'''
import os
import json
from google.cloud import firestore
from google.cloud import pubsub_v1
import time

publisher = pubsub_v1.PublisherClient()
topic_path = publisher.topic_path(os.environ['PROJECT_ID'], os.environ['TOPIC_NAME']) 


for i in range(1,11):
    data={'id': i, 'status': 'processing'}
    future = publisher.publish(topic_path, json.dumps(data).encode('utf-8'))
    time.sleep(0.5)
    try:
        message_id = future.result()
        print(f"✅ Messaggio inviato con ID: {message_id}")
    except Exception as e:
        print(f"❌ Errore durante l'invio: {e}")
'''
#----------------

#----Esercizio 2----
'''
import os
import json
from google.cloud import firestore
from google.cloud import pubsub_v1
import time
import random

publisher = pubsub_v1.PublisherClient()
topic_path = publisher.topic_path(os.environ['PROJECT_ID'], os.environ['TOPIC_NAME']) 

for i in range(1,11):
    data={'temperatura': random.uniform(0,100)}
    future = publisher.publish(topic_path, json.dumps(data).encode('utf-8'))
    time.sleep(0.5)
    try:
        message_id = future.result()
        print(f"✅ Messaggio inviato con ID: {message_id}")
    except Exception as e:
        print(f"❌ Errore durante l'invio: {e}")
'''
#----------------


#-----Esercizio 3-------
'''
import os
from google.cloud import pubsub_v1
import sys

# Argomenti da riga di comando (es: python3 worker.py nome_topic)
if len(sys.argv) < 3:
    print("Errore: specifica il topic da ascoltare.")
    sys.exit(1)

topic_name = sys.argv[1]
mesaggio = sys.argv[2]

# Configurazione Globale
PROJECT_ID = os.environ.get('PROJECT_ID')
publisher = pubsub_v1.PublisherClient()

def publish_message(topic_name, message_string):
    """
    1. Crea il topic se non esiste.
    2. Invia il messaggio.
    """
    # Costruzione percorso completo: projects/{id}/topics/{nome}
    topic_path = publisher.topic_path(PROJECT_ID, topic_name)
    
    # 2. Logica "Get or Create" (Idempotenza)
    try:
        publisher.get_topic(request={"topic": topic_path})
        print("Topic trovato")
    except Exception:
        print("Topic creato")
        publisher.create_topic(name=topic_path)

    # 3. Pubblicazione (Importante: encode in bytes!)
    future = publisher.publish(topic_path, data=message_string.encode("utf-8"))
    
    return future.result() # Restituisce l'ID del messaggio pubblicato

# --- ESEMPIO DI UTILIZZO ---
publish_message(topic_name=topic_name, message_string=str(mesaggio))
'''
#-----------------