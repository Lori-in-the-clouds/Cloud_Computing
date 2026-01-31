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

def interpolazioni_consumi(data):

    l = db_firestone.get_all_elements("letture")
    l_filtered = [elem for elem in l if elem['id'] < data]
    l_filtered_sorted = sorted(l_filtered, key=lambda d: datetime.strptime(d["id"], "%d-%m-%Y"), reverse=False)
    print(l_filtered_sorted)
    
    if len(l_filtered_sorted) >= 2:
        t2 = l_filtered_sorted[-1]
        t1 = l_filtered_sorted[-2]
        res = t2["value"] + ((t2["value"] - t1["value"])/((from_string_to_date(t2["id"]) - from_string_to_date(t1["id"])).total_seconds())) * ((from_string_to_date(data) - from_string_to_date(t2["id"])).total_seconds())
    elif len(l_filtered_sorted) == 0:
        res = 0
    elif len(l_filtered_sorted) == 1:
        res = l_filtered_sorted[-1]["value"]
    return res    

class FirstResource(Resource):
    
    # Per ottenere una risorsa
    def get(self, data): 
        if from_string_to_date(data) is None:
            return None,400
        
        elem = db_firestone.get_element("letture", data)
        if elem is None:
            res = interpolazioni_consumi(data)
            #db_firestone.add_element("letture",data,{"value":res,"isInterpolated":True})
            return {
                "value": res,
                "isInterpolated": True
            },200
            
        else:
            return {
                    "value": elem["value"],
                    "isInterpolated": elem["isInterpolated"]
                    },200
        
    # Crea una nuova risorsa
    def post(self, data): 
        
        if from_string_to_date(data) is None:
            return None, 400

        request_info = request.get_json()
        if request_info is None:
            return None, 400

        value = request_info.get("value")
 
        if value is None or not isinstance(value, int) or value < 0:
            return None, 400

        if db_firestone.get_element("letture", data) is not None:
            return None, 409
        
        db_firestone.add_element("letture", data, {"value": value, "isInterpolated": False})
        return {
            "value": value,
            "isInterpolated": False
        }, 201
   
#Per ciascuna classe eseguiamo il collegamento con il path corretto all'esterno della classe indicando il nome del parametro (se presente nel path).
api.add_resource(FirstResource, f'{base_path}/consumi/<string:data>')


#Ecco un esempio in cui il path possiede solamente un metodo e non è presente alcun parametro:

class SecondResource(Resource):
    def post(self):
        db_firestone.clean_collection("letture")
        return None,200
        
api.add_resource(SecondResource, f'{base_path}/clean')

#Per fare debug in locale

if __name__=='__main__':
    app.run(host="localhost", port=8080, debug=True)

