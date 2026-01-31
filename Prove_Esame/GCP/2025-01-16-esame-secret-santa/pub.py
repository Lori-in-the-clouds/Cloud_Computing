import os
import json
from google.cloud import firestore
from google.cloud import pubsub_v1
from file_firestone import *

db_firestone = FirestoreManager()

def discover_secret_santa(email):
    l = db_firestone.get_all_elements("lista_partecipanti")

    l_sorted = sorted(l,key=lambda d: from_string_to_date_full(d["timestamp"]),reverse=False)
    res = {}
    from_t = {}
    if l_sorted[-1]["id"] == email:
        res = l_sorted[0]
        elem =  [elem for elem in l_sorted if elem["id"] == email]
        from_t = {
            "id": elem[0]["id"],
            "firstname": elem[0]["firstname"],
            "lastname": elem[0]["lastname"]
        }
    
    else:
        for i in range(len(l_sorted)):
            if l_sorted[i]["id"] == email:
                res = l_sorted[i+1]
                from_t = l_sorted[i]
    
    return {
        "fromEmail": email,
        "fromFirstName": from_t["firstname"],
        "fromLastName": from_t["lastname"],
        "toEmail": res["id"],
        "toFirstName": res["firstname"],
        "toLastName": res["lastname"]
    }

project_id = os.environ['PROJECT_ID']
sub_name = os.environ['SUBSCRIPTION_NAME']
subscriber = pubsub_v1.SubscriberClient()
sub_path = subscriber.subscription_path(project_id, sub_name)

#Funzione che scatta automaticamente quando arriva un mesaggio
def callback(message):
    message.ack() #Conferma la ricezione
    dati = json.loads(message.data.decode('utf-8'))
    email = dati.get('email')
    request_id = dati.get("request_id")
    res = discover_secret_santa(email)

    publisher = pubsub_v1.PublisherClient()
    t_path = publisher.topic_path(project_id, "risposte-santa")

    payload_risposta = {
        'request_id': request_id,
        'risultato': res
    }
    publisher.publish(t_path, json.dumps(payload_risposta).encode('utf-8'))
    print(f"Risposta inviata al topic risposte-santa")


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