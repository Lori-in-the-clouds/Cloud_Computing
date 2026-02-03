from flask import Flask, render_template, request, redirect
from file_firestone import *
from wtforms import DateField, EmailField, Form, RadioField, StringField, IntegerField, SubmitField, validators
from time_utils import *

#Creiamo applicazione web
app = Flask(__name__)
db_firestone = FirestoreManager()

#Trasformare un dizionario in un oggetto con attributi. Tipo color.red
class Struct:
    def __init__(self, **entries):
        self.__dict__.update(entries)

@app.route('/lista', methods=['GET']) 
def mappa_follia():
    
    l = db_firestone.get_all_elements("meeting crimes")
    l_filtered = [elem for elem in l if datetime.strptime(elem["id"].split("_")[1],"%Y-%m-%d").strftime("%d-%m-%Y") in giorni_della_settimana()]

    
    l_filtered = [
        {
            "colpevole": elem["id"].split("_")[0],
            "data":  datetime.strptime(elem["id"].split("_")[1],"%Y-%m-%d").strftime("%d-%m-%Y"),
            "vittime": elem["vittime"],
            "durata": elem["durata"],
            "orario_inizio": elem["orario_inizio"],
            "gravità": elem["durata"] * len(elem["vittime"]),
            "rosso": True if elem["durata"] > 4 else False
        } for elem in l_filtered
    ]

    l_filtered = ordina_lista_di_dizionari_per_data(l_filtered,"data", formato_data="%d-%m-%Y",reverse=True)
    ore_di_vita_sprecate = 0

    l_filtered_mese = [elem for elem in l if datetime.strptime(elem["id"].split("_")[1],"%Y-%m-%d").strftime("%d-%m-%Y") in giorni_del_mese()]
    for elem in l_filtered_mese:
        ore_di_vita_sprecate += elem["durata"]

    return render_template("mappa_follia.html", lista = l_filtered, ore_di_vita_sprecate = ore_di_vita_sprecate)
    

@app.route('/dettagli/<data>', methods=['GET']) 
def dettagli_data(data):
    l = db_firestone.get_all_elements("meeting crimes")
    l_filtered = [elem for elem in l if datetime.strptime(elem["id"].split("_")[1],"%Y-%m-%d").strftime("%d-%m-%Y") == data]
    

    dannato_del_giorno = ""
    max = 0
    totale_ore_perse = 0

    for elem in l_filtered:
        if elem["durata"] > max:
            max = elem["durata"]
            dannato_del_giorno = elem["id"].split("_")[0]
        totale_ore_perse += elem["durata"]

    l_filtered = [
        {
            "colpevole": elem["id"].split("_")[0],
            "vittime":  elem["vittime"]
        } for elem in l_filtered
    ]

    return render_template("dettagli.html", data= data,lista = l_filtered, totale_ore_perse = totale_ore_perse, dannato_del_giorno = dannato_del_giorno)


#Function----------------------------------------
db = firestore.Client(database="db-riunioni")
# Funzione helper per estrarre valori in modo sicuro dal formato Proto
def get_val(fields, key, type='stringValue'):
    return fields.get(key, {}).get(type)

def update_stats(key, user_id, month, hours, is_manager):
    # Usiamo il client 'db' (firestore.Client()) definito globalmente
    doc_ref = db.collection("productivity nightmare").document(key)
    
    update_data = {
        "employee_id": user_id,
        "month_year": month,
        "total_meeting_hours": firestore.Increment(float(hours))
    }
    
    if is_manager:
        update_data["organized_meetings"] = firestore.Increment(1)
    #inserito ora
    else:
        update_data["organized_meetings"] = firestore.Increment(0)
        
    doc_ref.set(update_data, merge=True)

def update_db(data, context): 
    # Trasformiamo data in dizionario se arriva come stringa
    if isinstance(data, str):
        import json
        data = json.loads(data)

    document_name = context.resource.split("/")[-1]
    colpevole = document_name.split("_")[0]
    data_mese = document_name.split("_")[1][:7] 

    new_value = data.get('value')
    old_value = data.get('oldValue')

    if new_value:
        fields = new_value.get('fields', {})
        durata = fields.get('durata', {}).get('doubleValue') or fields.get('durata', {}).get('integerValue') or 0
        vittime_raw = fields.get('vittime', {}).get('arrayValue', {}).get('values', [])
        vittime = [v.get('stringValue') for v in vittime_raw]
    else:
        durata = 0
        vittime = []

    if new_value and not old_value: # Caso POST (Nuova)
        colpevole_key = f"{colpevole}_{data_mese}"
        update_stats(colpevole_key, colpevole, data_mese, durata, is_manager=True)
       
        for v in vittime:
            vittima_key = f"{v}_{data_mese}"
            update_stats(vittima_key, v, data_mese, durata, is_manager=False)
#---------------------------------
if __name__=='__main__':
    app.run(host="localhost", port=8080, debug=True)

    