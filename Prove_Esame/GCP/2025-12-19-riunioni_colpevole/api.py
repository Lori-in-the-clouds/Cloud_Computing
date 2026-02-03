from flask import Flask, request
from flask_restful import Resource, Api
from file_firestone import *
from time_utils import *
from flask_cors import CORS
import re
import math

app = Flask(__name__)
CORS(app)
api=Api(app)
base_path='/api/v1'

db_firestone = FirestoreManager()

class FirstResource(Resource):
    
    # Per ottenere una risorsa
    def get(self, data): 
        l = db_firestone.get_all_elements("meeting crimes")
        l_filtered = [elem for elem in l if datetime.strptime(elem["id"].split("_")[1],'%Y-%m-%d').strftime('%d-%m-%Y') == data]

        if from_string_to_date(data) is None: 
            return None,400
        
        if len(l_filtered) == 0:
            return {
                "data": data,
                "riunioni": [],
                "totale_ore": 0
            },200

        totale_ore = 0
        dannato_del_giorno = ""
        max = 0
        for elem in l_filtered:
            totale_ore += elem["durata"]
            if elem["durata"] > max:
                max = elem["durata"]
                dannato_del_giorno = elem["id"].split("_")[0]

        riunioni_giorno = [
            {
                "colepevole": elem["id"].split("_")[0],
                "vittime": elem["vittime"],
                "durata": elem["durata"]
            } for elem in l_filtered
        ]

        return {
            "data": data,
            "totale_ore": totale_ore,
            "dannato_del_giorno": dannato_del_giorno,
            "riunioni": riunioni_giorno
        }, 200
        
    # Crea una nuova risorsa
    def post(self, data): 
        request_info = request.json
        colpevole = request_info.get("colpevole")
        vittime = request_info.get("vittime")
        durata = request_info.get("durata")
        orario_inizio = request_info.get("orario_inizio")

        if colpevole is None or vittime is None or durata is None or orario_inizio is None or from_string_to_time(orario_inizio) is None or from_string_to_date(data) is None:
            return None, 400
        if len(vittime) > 19 or len(vittime) < 0:
            return None, 400
        
        min = 0
        if durata != round(durata):
            min = 30

        if from_string_to_time(orario_inizio) > from_string_to_time("19:00") or from_string_to_time(orario_inizio) < from_string_to_time("08:00"):
            return None,422
        
        if from_string_to_time(somma_ore_minuti(orario_str=orario_inizio,ore=math.floor(durata),minuti=min)) > from_string_to_time("20:00"):
            return None,400 
        
        l = db_firestone.get_all_elements("meeting crimes")
        l_filtered = [elem for elem in l if datetime.strptime(elem["id"].split("_")[1],'%Y-%m-%d').strftime('%d-%m-%Y') == data]
        print(l_filtered)
        for elem in l_filtered:
            if elem["id"].split("_")[0] == colpevole:
                return None,409
        
        if durata > 8 or durata < 0.5 or durata % 0.5 != 0:
            return None, 400
        
        for elem in l_filtered:
            if overlap(t1_str=orario_inizio,durata_1=durata,t2_str=elem["orario_inizio"], durata_2=elem["durata"]):
                return None,422


        db_firestone.add_element("meeting crimes",f"{colpevole}_{datetime.strptime(data, '%d-%m-%Y').strftime('%Y-%m-%d')}", {
            "vittime": vittime,
            "durata": durata,
            "orario_inizio": orario_inizio
        })
        
        return {
            "data": data,
            "colpevole": colpevole,
            "vittime": vittime,
            "durata": durata,
            "orario_inizio": orario_inizio
        },201

    # Aggiorna una risorsa specifica 
    def put(self, data): 
        request_info =request.json
        colpevole = request_info.get("colpevole")
        vittime = request_info.get("vittime")
        durata = request_info.get("durata")
        orario_inizio = request_info.get("orario_inizio")

        if colpevole is None or vittime is None or durata is None or orario_inizio is None or from_string_to_time(orario_inizio) is None or from_string_to_date(data) is None:
            return None, 400
        if len(vittime) > 19 or len(vittime) < 0:
            return None, 400
        
        l = db_firestone.get_all_elements("meeting crimes")
        l_filtered = [elem for elem in l if datetime.strptime(elem["id"].split("_")[1],'%Y-%m-%d').strftime('%d-%m-%Y') == data and elem["id"].split("_")[0] == colpevole]
        print(l_filtered)
        if len(l_filtered) == 0:
            return None, 404
        
        if from_string_to_time(orario_inizio) > from_string_to_time("19:00") or from_string_to_time(orario_inizio) < from_string_to_time("08:00"):
            return None,422
        
        min = 0
        if durata != round(durata):
            min = 30
        if from_string_to_time(somma_ore_minuti(orario_str=orario_inizio,ore=math.floor(durata),minuti=min)) > from_string_to_time("20:00"):
            return None,400 
        
        if durata > 8 or durata < 0.5 or durata % 0.5 != 0:
            return None, 400
        
        l_filtered = [elem for elem in l if datetime.strptime(elem["id"].split("_")[1],'%Y-%m-%d').strftime('%d-%m-%Y') == data]
        for elem in l_filtered:
            if overlap(t1_str=orario_inizio,durata_1=durata,t2_str=elem["orario_inizio"], durata_2=elem["durata"]):
                return None,422
        
        db_firestone.add_element("meeting crimes",f"{colpevole}_{datetime.strptime(data, '%d-%m-%Y').strftime('%Y-%m-%d')}", {
            'vittime': vittime,
            'durata': durata,
            'orario_inizio': orario_inizio
        })
        
        return {
            "data": data,
            "colpevole": colpevole,
            "vittime": vittime,
            "durata": durata,
            "orario_inizio": orario_inizio
        },200
        
api.add_resource(FirstResource, f'{base_path}/room42/<string:data>')


#Ecco un esempio in cui il path possiede solamente un metodo e non è presente alcun parametro:

class SecondResource(Resource):
    def post(self):
        db_firestone.clean_collection("meeting crimes")
        return None,200
    
api.add_resource(SecondResource, f'{base_path}/panic')


class ThirdResource(Resource):
    def get(self,mese):
        l =  db_firestone.get_all_elements("productivity nightmare")
        try:
            datetime.strptime(mese,"%m-%Y")
        except (ValueError, TypeError):
            return None,400
        l_filtered = [elem for elem in l if datetime.strptime(elem["id"].split("_")[1],"%Y-%m").strftime("%m-%Y") == mese]
        if len(l_filtered) == 0:
           return None, 404
        
        max_hour = 0
        dipendente = ""

        for elem in l_filtered:
            if elem["total_meeting_hours"] > max_hour:
                max_hour = elem["total_meeting_hours"]
                dipendente = elem["id"].split("_")[0]
        return {
            "mese": mese,
            "dipendente": dipendente,
            "ore_riunioni": max_hour,
            "efficienza": max_hour / 40.0
        }, 200

api.add_resource(ThirdResource, f'{base_path}/stats/slackers/<string:mese>')


class FourthResource(Resource):
    def get(self,mese):
        l =  db_firestone.get_all_elements("productivity nightmare")
        try:
            datetime.strptime(mese,"%m-%Y")
        except (ValueError, TypeError):
            return None,400
        l_filtered = [elem for elem in l if datetime.strptime(elem["id"].split("_")[1],"%Y-%m").strftime("%m-%Y") == mese]
        if len(l_filtered) == 0:
           return None, 404
        
        riunioni_organizzate = 0
        manager = ""

        for elem in l_filtered:
            if elem["organized_meetings"] > riunioni_organizzate:
                riunioni_organizzate = elem["organized_meetings"]
                manager = elem["id"].split("_")[0]

        numero_vittime_totali = 0

        l_t = db_firestone.get_all_elements("meeting crimes")

        l_t_filtered = [elem for elem in l_t if elem["id"].split("_")[0] == manager]
        for elem in l_t_filtered:
            numero_vittime_totali+=len(elem["vittime"])

        return {
            "mese": mese,
            "manager": manager,
            "riunioni_organizzate": riunioni_organizzate,
            "indice_sabotaggio": riunioni_organizzate * numero_vittime_totali
        }, 200
        

api.add_resource(FourthResource, f'{base_path}/stats/saboteurs/<string:mese>')


if __name__=='__main__':
    app.run(host="localhost", port=8080, debug=True)

    