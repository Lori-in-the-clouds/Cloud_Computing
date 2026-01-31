from flask import Flask, request
from flask_restful import Resource, Api
from file_firestone import *
from time_utils import *
from flask_cors import CORS
import re
from google.cloud import pubsub_v1
import json
import os

app = Flask(__name__)
CORS(app)
api=Api(app)
base_path='/api/v1'

db_firestone = FirestoreManager()
# Inizializzazione Publisher (fuori dalle rotte)
publisher = pubsub_v1.PublisherClient()
topic_path = publisher.topic_path(os.environ['PROJECT_ID'], os.environ['TOPIC_NAME']) 

class FirstResource(Resource):
    
    # Per ottenere una risorsa
    def get(self, idumarell): 
        uma = db_firestone.get_element("dumarell", idumarell)
        if uma is None:
            return None, 404
        return {
            "nome": uma["nome"],
            "cognome": uma["cognome"],
            "cap": uma["cap"]
        },200
        
    # Crea una nuova risorsa
    def post(self, idumarell): 
        request_info = request.json
        #id = request_info.get("id")
        nome = request_info.get("nome")
        cognome = request_info.get("cognome")
        cap = request_info.get("cap")
        """or id is None"""

        if len(str(cap)) != 5 or nome is None or cognome is None or int(idumarell) < 0:
            return None, 400
        
        if db_firestone.get_element("dumarell", idumarell) is not None:
            return None, 409
        
        db_firestone.add_element("dumarell", idumarell, {
            "nome": nome,
            "cognome": cognome,
            "cap": cap})
        
        return {
            "cap": cap, 
            "cognome": cognome,
            "nome": nome
        },201
    
api.add_resource(FirstResource, f'{base_path}/umarell/<string:idumarell>')

class SecondResource(Resource):
    
    # Per ottenere una risorsa
    def get(self, idcantiere): 
        cantiere = db_firestone.get_element("cantiere", idcantiere)
        if cantiere is None:
            return None, 404
        return {
            "indirizzo": cantiere["indirizzo"],
            "cap": cantiere["cap"]
        },200
        
    # Crea una nuova risorsa
    def post(self, idcantiere): 
        request_info = request.json
        #id = request_info.get("id")
        indirizzo = request_info.get("indirizzo")
        cap = request_info.get("cap")
        """or id is None"""

        if len(str(cap)) != 5 or indirizzo is None or int(idcantiere) < 0:
            return None, 400
        
        if db_firestone.get_element("cantiere", idcantiere) is not None:
            return None, 409
        
        db_firestone.add_element("cantiere", idcantiere, {
            "indirizzo": indirizzo,
            "cap": cap})
        
        #inserisco i valori su pub/sub
        data = json.dumps({
            "indirizzo": indirizzo,
            "cap": cap}).encode("utf-8")
        publisher.publish(topic_path, data)

        return {
           'cap': cap, 
           "indirizzo": indirizzo
        },201
        
api.add_resource(SecondResource, f'{base_path}/cantiere/<string:idcantiere>')


class ThirdResource(Resource):
    def get(self): 
        db_firestone.clean_db()
        return None, 200

api.add_resource(ThirdResource, f'{base_path}/clean')



#Ecco un esempio in cui il path possiede solamente un metodo e non è presente alcun parametro:
"""
class SecondResource(Resource):
    def get(self):
        return colors_dao.get_colors(), 200
        
api.add_resource(ColorList, f'{base_path}/colors')
"""

#Per fare debug in locale

if __name__=='__main__':
    app.run(host="localhost", port=8080, debug=True)

