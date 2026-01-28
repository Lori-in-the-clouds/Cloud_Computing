from flask import Flask, render_template, request, redirect
from file_firestone import *
from wtforms import DateField, EmailField, Form, StringField, IntegerField, SubmitField, validators
from time_utils import *

#Creiamo applicazione web
app = Flask(__name__)
db_firestone = FirestoreManager()

#Trasformare un dizionario in un oggetto con attributi. Tipo color.red
class Struct:
    def __init__(self, **entries):
        self.__dict__.update(entries)


@app.route('/trend/<data>', methods=['GET'])         
@app.route('/api/v1/trend/<data>', methods=['GET'])   
def get_trend_api(data):
    """
    Questa funzione è SIA la 'Web Function' CHE l'API REST.
    """
    date_str = get_past_dates(7,exclude_today=True)
    l = db_firestone.get_all_elements("prenotazioni")
    l_filtered = [elem for elem in l if elem['id'].split('_')[0] in date_str]

    if len(l_filtered) == 0:
        return {
            "trend": 0
        }, 200
    
    sum_s = 0
    for elem in l_filtered:
        sum_s += elem['bimbi']
    avg = sum_s / 7.0   
    print(avg)
    trend = ((sum([elem["bimbi"] for elem in l if elem['id'].split('_')[0] == data]) - avg) / avg) * 100

    return {
        "trend": trend
    }, 200

@app.route('/lista', methods=['GET']) 
def riepilogo_pasti():

    l = db_firestone.get_all_elements("prenotazioni")
    days = get_past_dates(7)
    
    asili_l = {
    day: {
        "nomi_asili": [], 
        "totale_bambini": 0,        
        "ev": False
    } 
    for day in days
    }

    for elem in l:
        if elem['id'].split('_')[0] in days:
            day = elem['id'].split('_')[0]
            asili_l[day]["nomi_asili"].append({
                "asilo": elem['id'].split('_')[1],
                "bimbi": elem['bimbi']
            })
            asili_l[day]["totale_bambini"] += elem['bimbi']
            if elem['id'].split('_')[0] == datetime.now().strftime("%d-%m-%Y"):
               asili_l[day]["ev"] = True
                          
    print(asili_l)
    return render_template("riepilogo.html", asili_l=asili_l)


@app.route('/lista/<data>', methods=['GET']) 
def dettaglio(data):
    l = db_firestone.get_all_elements("prenotazioni")
    l_filtered = [elem for elem in l if elem['id'].split('_')[0] == data]
    l_filtered = [
        {
            "asilo": item["id"].split("_", 1)[1], 
            "bambini": item["bimbi"]
        } 
        for item in l_filtered 
    ]
    return render_template("dettagli.html", asili=l_filtered, data=data)

#Per fare debug in locale
if __name__=='__main__':
    app.run(host="localhost", port=8080, debug=True)
