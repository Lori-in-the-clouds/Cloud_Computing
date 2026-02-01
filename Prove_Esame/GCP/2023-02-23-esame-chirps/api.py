from flask import Flask, request
from flask_restful import Resource, Api
from file_firestone import *
from time_utils import *
from flask_cors import CORS
import re
import uuid
from google.cloud import pubsub_v1
import os

# Genera un UUID casuale (versione 4)
#nuovo_id = uuid.uuid4()

def is_valid_uuid(uuid_to_test, version=4):
    """
    Verifica se una stringa è un UUID valido.
    """
    try:
        # Tenta di creare un oggetto UUID; se fallisce, solleva ValueError
        uuid_obj = uuid.UUID(uuid_to_test, version=version)
    except ValueError:
        return False
    return str(uuid_obj) == uuid_to_test

app = Flask(__name__)
CORS(app)
api=Api(app)
base_path='/api/v1'

db_firestone = FirestoreManager()

def validate_payload(data, required_fields):
    """
    Controlla se i campi richiesti esistono, se i tipi sono corretti
    e se i valori sono validi.
    """
    for field, expected_type in required_fields.items():
        val = data.get(field)
        
        # 1. Controllo esistenza
        if val is None:
            return False, f"Campo {field} mancante"
        # 2. Controllo tipo (es. int, str, bool)
        if not isinstance(val, expected_type):
            return False, f"Campo {field} deve essere di tipo {expected_type.__name__}"
        # 3. Controlli logici specifici (opzionale)
        if expected_type == int and val < 0:
            return False, f"Campo {field} non può essere negativo"
        # 4. Controllo Email
        if field == "email":
            if not re.match(r"[^@]+@[^@]+\.[^@]+", val):
                return False, "Email non valida" 
        # 5. Controllo Data
        if field == "date":
            try:
                datetime.strptime(val, "%d-%m-%Y")
            except ValueError:
                return False, "Data non valida, formato richiesto gg-mm-YYYY"
                        
                return True, None   
        # 6. Stringhe non vuote
        if expected_type == str and val.strip() == "":
            return False, f"Campo {field} non può essere vuoto"
        

project_id = os.environ['PROJECT_ID']
publisher = pubsub_v1.PublisherClient()

def get_or_create_topic(hashtag):
    
    topic_path = publisher.topic_path(project_id, hashtag.split("#")[1])
    try:
        # Proviamo a vedere se esiste già
        publisher.get_topic(request={"topic": topic_path})
    except Exception:
        # Se non esiste, lo creiamo
        publisher.create_topic(name=topic_path)
    
    return topic_path

class FirstResource(Resource):

    # Crea una nuova risorsa
    def post(self): 
        try:
        # force=True serve se il client non manda l'header corretto
            message = request.get_json(force=True)
        except:
        # Se il client manda testo puro senza virgolette (non JSON valido)
            message = request.data.decode('utf-8').strip().strip('"')
        print("Messaggio")
        print(message)
        if message is None or len(message) < 1 or len(message) > 100: 
            return None, 400
        
        id = str(uuid.uuid4())

        db_firestone.add_element("messages",id,{
            "message": message,
            "hashtags": get_hashtags(message),
            "timestamp": from_date_full_to_string(datetime.now())
        })

        for hash in get_hashtags(message):
            if db_firestone.get_element("hashtags",hash) is not None:
                    elem = db_firestone.get_element("hashtags",hash)
                    l = elem["list_messages"]
                    l.append(f"{id}: {from_date_full_to_string(datetime.now())}")
                    elem = db_firestone.add_element("hashtags",hash,elem)
            else:
                db_firestone.add_element("hashtags",hash,{
                    "list_messages" : [f"{id}: {from_date_full_to_string(datetime.now())}"]
                })

        #Publisher-------------
        
        for hash in get_hashtags(message):
            topic_path = get_or_create_topic(hash)
            # Pubblichiamo l'ID del messaggio (convertito in bytes)
            print("Pubblichiamo ID del messaggio")
            publisher.publish(topic_path, data=id.encode("utf-8"))
        #-----------------

    
        return {
            "id": id,
            "message": message,
            "timestamp": from_date_full_to_string(datetime.now())
        }, 201
              
api.add_resource(FirstResource, f'{base_path}/chirps/')


class SecondResource(Resource):
    def post(self):
        db_firestone.clean_collection("messages")
        return None,200
    
api.add_resource(SecondResource, f'{base_path}/clean')


class ThirdResource(Resource):
    def get(self,id):
        if not is_valid_uuid(id):
            return None,404
        
        elem = db_firestone.get_element("messages",id)
        print("elemento")
        print(elem)
        if elem is None:
            return None,404
        
        return {
            "id": id,
            "message": elem["message"],
            "timestamp": elem["timestamp"]
        },200
    
api.add_resource(ThirdResource, f'{base_path}/chirps/<string:id>')



class FourthResource(Resource):
    def get(self,topic):
        l = db_firestone.get_all_elements("messages")
        l_filtered = [elem for elem in l if topic in elem["hashtags"]]
        
        if len(l_filtered) == 0:
            return None,404
        
        return [
            elem["message"]
            for elem in l_filtered
        ], 200
    
api.add_resource(FourthResource, f'{base_path}/topics/<string:topic>')


#Per fare debug in locale

if __name__=='__main__':
    app.run(host="localhost", port=8080, debug=True)

    