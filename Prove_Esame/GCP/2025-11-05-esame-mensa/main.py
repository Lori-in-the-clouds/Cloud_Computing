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


def get_trend(data):
    l = db_firestone.get_all_elements("prenotazioni")
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

@app.route('/list', methods=['GET',"POST"]) 
def lista():
    l = db_firestone.get_all_elements("prenotazioni")

    days = []
    for i in range (0,7):
        days.append(from_date_to_string(datetime.now() - timedelta(days=i)))

    print(days)

    #l_filtered = [elem for elem in l if elem["id"].split("_")[0] in days]

    res = []
    
    for day in days:
        totale = sum([elem["bambini"] for elem in l if elem["id"].split("_")[0] in day])
        if totale > 0:
            if day == from_date_to_string(datetime.now()):
                res.append({"data":day,"bambini": totale,"mark":True})
            else:
                res.append({"data":day,"bambini": totale,"mark":False})

    l_f_sorted = ordina_lista_di_dizionari_per_data(res,"data","%d-%m-%Y",True)

    return render_template("list.html", lista=l_f_sorted)

@app.route('/dettagli/<data>', methods=['GET',"POST"]) 
def dettagli(data):

    l = db_firestone.get_all_elements("prenotazioni")
    l_filtered = [elem for elem in l if elem["id"].split("_")[0] == data]
    l_filtered = [
        {
            "asilo": elem["id"].split("_")[1],
            "data": elem["id"].split("_")[0],
            "bambini": elem["bambini"]
        } for elem in l_filtered
    ]

    totale = 0
    for elem in l_filtered:
        totale+= elem["bambini"]

    return render_template("dettagli.html", lista=l_filtered,totale=totale)


#FUNCTION
def update_db(data,context): 

    document_name = context.resource.split("/")[-1]

    new_value = data['value'] if len(data["value"]) != 0 else None
    old_value = data['oldValue'] if len(data["oldValue"]) !=0 else None

    valore = new_value["name"].split("/")[-1]
    data = valore.split("_")[0]
    asilo = valore.split("_")[1]
    
    if new_value and not old_value: # document added
        
        elem = db_firestone.get_element("prenotazioni",f"{data}_{asilo}")
        elem_riep = db_firestone.get_element("riepiloghi",data)

        if elem_riep is None:
            db_firestone.add_element("riepiloghi",data,{
                "totale_pasti": elem["bambini"],
                "asili": [{"nome_asilo": asilo, "trend": get_trend(data)}]
            })
        else:
            db_firestone.add_element("riepiloghi",data,{
                "totale_pasti": elem_riep["totale_pasti"] + elem["bambini"],
                "asili": elem_riep["asili"] + [{"nome_asilo": asilo, "trend": get_trend(data)}]
            })

    elif not new_value and old_value: # document removed
        pass
    else: # document updated
        
        elem = db_firestone.get_element("prenotazioni",f"{data}_{asilo}")
        elem_riep = db_firestone.get_element("riepiloghi",data)
        if elem_riep is None:
            db_firestone.add_element("riepiloghi",data,{
                "totale_pasti": elem["bambini"],
                "asili": [{"nome_asilo": asilo, "trend": get_trend(data)}]
            })
        else:
            db_firestone.add_element("riepiloghi",data,{
                "totale_pasti": elem_riep["totale_pasti"] + elem["bambini"],
                "asili": elem_riep["asili"] + [{"nome_asilo": asilo, "trend": get_trend(data)}]
            })


def HTTP_FUNCTION(request):
    if request.method == 'GET':
        path = request.path
        if path.split('/')[-2] != "trend":
            return None, 400
        
        data = path.split('/')[-1]
        return {"trend":get_trend(data)},200

#Per fare debug in locale
if __name__=='__main__':
    app.run(host="localhost", port=8080, debug=True)

    #update_db(fake_event)
