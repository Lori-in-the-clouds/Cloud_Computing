import os, json, sys, uuid
from google.cloud import pubsub_v1
import time

project_id = os.environ['PROJECT_ID']
topic_richiesta = os.environ['TOPIC_NAME'] # secretsanta
sub_risposta = os.environ['SUBSCRIPTION_RISPOSTE'] # Una sub dedicata alle risposte

def richiedi_santa(email):
    publisher = pubsub_v1.PublisherClient()
    subscriber = pubsub_v1.SubscriberClient()
    
    # Creiamo un ID unico per questa specifica richiesta
    request_id = str(uuid.uuid4())
    
    topic_path = publisher.topic_path(project_id, topic_richiesta)
    data = {'email': email, 'request_id': request_id}
    
    print(f"Inviando richiesta per {email} (ID: {request_id})...")
    publisher.publish(topic_path, json.dumps(data).encode('utf-8'))

    # Ora il publisher diventa temporaneamente un "ascoltatore" per ricevere la risposta
    sub_path = subscriber.subscription_path(project_id, sub_risposta)
    
    def callback(message):
        dati_risposta = json.loads(message.data.decode('utf-8'))
        # FILTRO DI CONCORRENZA: Verifichiamo se l'ID corrisponde alla nostra richiesta
        if dati_risposta.get('request_id') == request_id:
            print("\n RISPOSTA RICEVUTA:")
            print(json.dumps(dati_risposta))
            message.ack()
            os._exit(0) # Chiudiamo il programma una volta ricevuta la risposta
        else:
            # Non è per noi, lasciamo che altri client la leggano (nack)
            message.nack()

    subscriber.subscribe(sub_path, callback=callback)
    print("In attesa della notifica dal sistema...")
    while True: time.sleep(1)

if __name__ == '__main__':
    email_input = sys.argv[1]
    richiedi_santa(email_input)