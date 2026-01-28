# Pubsub
Aggiungi `google-cloud-pubsub` a requirements.txt

## Setup
### Crea progetto e credenziali
Vedi firestore.  
Dovrai usare le credenziali in ogni applicazione che faccia uso di PubSub!

### Crea un topic
```sh
export TOPIC=topic
gcloud pubsub topics create ${TOPIC}
```
### Crea una subscription a un topic
```sh
export SUBSCRIPTION_NAME=subscription_name
gcloud pubsub subscriptions create ${SUBSCRIPTION_NAME} --topic ${TOPIC}
```

## Python publisher
### Definisci il publisher
```python
from google.cloud import pubsub

publisher = pubsub.PublisherClient()
topic = 'topic'
project_id = 'project-id'
topic_path = publisher.topic_path(project_id, topic)
# puoi ottenere questo percorso anche dalla dashboard Google
```

### Pubblica un messaggio
```python
publisher.publish(topic_path, 'message'.encode('utf-8'))
# puoi usare json.dumps per inviare oggetti
```

## Python subscriber
### Definisci il subscriber
```python
from google.cloud import pubsub

subscriber = pubsub.SubscriberClient()
project_id = 'project-id'
subscription_name = 'subscription-name'
subscription_path = subscriber.subscription_path(project_id, subscription_name)
# puoi ottenere questo percorso anche dalla dashboard Google
```
### Sottoscrivi un topic
```python
pull = subscriber.subscribe(subscription_path, callback=callback)
```

### Pulla messaggi
```python
try:
    pull.result(timeout=30)
except:
    pull.cancel()
```

### Definisci un callback che sarà invocato ad ogni ricezione di messaggio
```python
def callback(message):
    message.ack()
    message_content = message.data.decode('utf-8')
```
