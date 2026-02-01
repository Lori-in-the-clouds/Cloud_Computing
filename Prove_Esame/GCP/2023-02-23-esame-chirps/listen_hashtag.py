from google.cloud import pubsub_v1
import os
import sys
import uuid
from file_firestone import *

db_firestone = FirestoreManager()
hashtag = sys.argv[1]
project_id = os.environ['PROJECT_ID']
hashtag_cleaned = hashtag.split("#")[1]

sub_name = f"sub_{uuid.uuid4()}"

subscriber = pubsub_v1.SubscriberClient()
sub_path = subscriber.subscription_path(project_id, sub_name)
topic_path = subscriber.topic_path(project_id, hashtag_cleaned)
print(topic_path)
subscriber.create_subscription(request={"name": sub_path, "topic": topic_path})


def callback(message):
    # Il contenuto del messaggio (l'ID del Chirp) è in message.data
    chirp_id = message.data.decode("utf-8")
    print(f"📩 Ricevuto ID messaggio: {chirp_id}")
    
    # Qui andrà la logica per cercare il testo su Firestore...
    elem = db_firestone.get_element("messages",chirp_id)
    # Fondamentale: confermiamo la ricezione del messaggio
    message_d = elem["message"]
    print(f"Messaggio:{message_d}")
    message.ack()

streaming_pull_future = subscriber.subscribe(sub_path, callback=callback)
print(f"In ascolto per l'hashtag {hashtag}... premi Ctrl+C per fermarti.")

with subscriber:
    try:
        # Questo mantiene lo script in esecuzione finché non lo interrompi
        streaming_pull_future.result()
    except KeyboardInterrupt:
        # Quando premi Ctrl+C, fermiamo l'ascolto
        streaming_pull_future.cancel()
        print("\nChiusura in corso...")
    finally:
        # 🧹 Cancelliamo la sottoscrizione temporanea dal cloud
        subscriber.delete_subscription(request={"subscription": sub_path})
        print("Sottoscrizione eliminata. Ciao!")


        projects/chrips-esame/topics/cartolina