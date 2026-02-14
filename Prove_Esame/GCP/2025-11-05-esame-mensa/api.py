from time_utils import *
from flask import Flask, request
from flask_restful import Resource, Api
from file_firestone import *
from flask_cors import CORS
import re

app = Flask(__name__)
CORS(app)
api=Api(app)
base_path='/api/v1'

db_firestone = FirestoreManager()



def get_trend(data,l):
    days = []
    for i in range(1,8):
        days.append(from_date_to_string(from_string_to_date(data) - timedelta(days=i)))
    #print(days)
    
    l_filtered = [elem for elem in l if elem["id"].split("_")[0] in days]
    print(l_filtered)
    mean = 0
    for elem in l_filtered:
        mean += elem["bambini"]
    
    mean /= 7.0
    if mean != 0:
        trend = ((sum([float(elem["bambini"]) for elem in l if elem["id"].split("_")[0] in data]) - mean) / mean) * 100.00
        return trend
    else: 
        return 0


class FirstResource(Resource):
    
    # Per ottenere una risorsa
    def get(self, data): 
        #color = colors_dao.get_method() #questo intercetta le informazioni dentro il json della richiesta
        if data is None or from_string_to_date(data,pattern="%d-%m-%Y") is None:
             return None, 400
         
        l = db_firestone.get_all_elements("prenotazioni")
        l_filered = [elem for elem in l if elem["id"].split("_")[0] == data]

        totale = 0
        for elem in l_filered:
            totale += elem["bambini"]

        return {
            "data": data,
            "totale": totale,
            "trend": 0,
            "ordini": [
                {
                    "asilo": elem["id"].split("_")[1],
                    "bambini": elem["bambini"]
                } for elem in l_filered ],
            "trend": get_trend(data,l)
        },200
    
        
    # Crea una nuova risorsa
    def post(self, data): 
        request_info = request.json
        asilo = request_info.get("asilo")
        bambini = request_info.get("bambini")

        if data is None or from_string_to_date(data,pattern="%d-%m-%Y") is None or asilo is None or bambini is None or bambini < 1:
            return None,400
        
        l = db_firestone.get_all_elements("prenotazioni")
        l_filered = [elem for elem in l if elem["id"] == f"{data}_{asilo}"]
        if len(l_filered) > 0:
            return None,409
        
        db_firestone.add_element("prenotazioni",f"{data}_{asilo}", {"bambini": bambini})

        return {
            "data": data,
            "asilo": asilo,
            "bambini": bambini
        },201
        
    # Aggiorna una risorsa specifica 
    def put(self, data): 
        request_info =request.json
        asilo = request_info.get("asilo")
        bambini = request_info.get("bambini")

        if data is None or from_string_to_date(data,pattern="%d-%m-%Y") is None or asilo is None or bambini is None or bambini < 1:
            return None,400
        
        l = db_firestone.get_all_elements("prenotazioni")
        l_filered = [elem for elem in l if elem["id"] == f"{data}_{asilo}"]
        
        if len(l_filered) == 0:
            return None,404
        
        db_firestone.add_element("prenotazioni",f"{data}_{asilo}", {"bambini": bambini})

        return {
            "data": data,
            "asilo": asilo,
            "bambini": bambini
        },200
            
#Per ciascuna classe eseguiamo il collegamento con il path corretto all'esterno della classe indicando il nome del parametro (se presente nel path).
api.add_resource(FirstResource, f'{base_path}/mensa/<string:data>')

#Ecco un esempio in cui il path possiede solamente un metodo e non è presente alcun parametro:

class SecondResource(Resource):
    def post(self):
        db_firestone.clean_collection("prenotazioni")
        return None,200
    
api.add_resource(SecondResource, f'{base_path}/clean')


#Per fare debug in locale

if __name__=='__main__':
    app.run(host="localhost", port=8080, debug=True)

