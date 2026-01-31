from flask import Flask, request
from flask_restful import Resource, Api
from file_firestone import *
from time_utils import *
from flask_cors import CORS
import re

app = Flask(__name__)
CORS(app)
api=Api(app)
base_path='/api/v1'

db_firestone = FirestoreManager()

def update_daily_summary(self, data):
    
    l = db_firestone.get_all_elements("prenotazioni")
    tot_pasti = 0

    for elem in l:
        if elem['id'].split('_')[0] == data:
            tot_pasti += elem['bimbi']

    l_filtered = [elem for elem in l if elem['id'].split('_')[0] == data]
    l_asili = [
        {
        "nome_asilo":item["id"].split("_", 1)[1],
        "numero_bimbi":item["bimbi"]
        } 
        for item in l_filtered]

    db_firestone.add_element("riepiloghi", f"{data}", 
                             {
                                "totale_pasti": tot_pasti,
                                "lista_asili": l_asili
                             })

class FirstResource(Resource):
       
    # Crea una nuova risorsa
    def post(self, data): 
        request_info = request.json
        asilo = request_info.get("asilo")
        bambini = request_info.get("bambini")

        if bambini < 1 or from_string_to_date(data) is None:
            return None, 400
        
        l = db_firestone.get_all_elements("prenotazioni")
        print(db_firestone.get_all_elements("prenotazioni"))

        for elem in l:
            if f"{data}_{asilo}" == elem['id']:
                return None, 409
        
        db_firestone.add_element("prenotazioni", f"{data}_{asilo}", {"bimbi": bambini})
        update_daily_summary(self, data)
        return None, 201
    
    # Crea una nuova risorsa
    def put(self, data): 
        request_info = request.json
        asilo = request_info.get("asilo")
        bambini = request_info.get("bambini")

        if bambini < 1 or from_string_to_date(data) is None:
            return None, 400
        
        l = db_firestone.get_all_elements("prenotazioni")
        print(db_firestone.get_all_elements("prenotazioni"))

        for elem in l:
            if f"{data}_{asilo}" == elem['id']:
                db_firestone.add_element("prenotazioni", f"{data}_{asilo}", {"bimbi": bambini})
                return None, 200
        return None, 404
    
    # Per ottenere una risorsa
    def get(self, data): 

        if from_string_to_date(data) is None:
            return None, 400

        l = db_firestone.get_all_elements("prenotazioni")
        l_filtered = [elem for elem in l if elem['id'].split('_')[0] == data]
        if len(l_filtered) != 0:
            l_ordini = [
                {
                    "asilo": item["id"].split("_", 1)[1], 
                    "bambini": item["bimbi"]
                } 
                for item in l_filtered 
            ]

            return {
                "data": data,
                "totale": sum(elem['bimbi'] for elem in l_filtered),
                "ordini": l_ordini
            }, 200
        else:
            return None, 404
            
#Per ciascuna classe eseguiamo il collegamento con il path corretto all'esterno della classe indicando il nome del parametro (se presente nel path).
api.add_resource(FirstResource, f'{base_path}/mensa/<string:data>')

class SecondResource(Resource):
    def post(self):
        db_firestone.clean_collection("prenotazioni")
        return None, 200

api.add_resource(SecondResource, f'{base_path}/clean')


#Per fare debug in locale

if __name__=='__main__':
    app.run(host="localhost", port=8080, debug=True)

