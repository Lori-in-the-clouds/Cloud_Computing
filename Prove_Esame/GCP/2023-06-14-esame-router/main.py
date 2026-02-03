
from flask import Flask, render_template, request, redirect
from file_firestone import *
from wtforms import DateField, EmailField, Form, RadioField, StringField, IntegerField, SubmitField, validators
from time_utils import *
import ipaddress

#Creiamo applicazione web
app = Flask(__name__)
db_firestone = FirestoreManager()

#Trasformare un dizionario in un oggetto con attributi. Tipo color.red
class Struct:
    def __init__(self, **entries):
        self.__dict__.update(entries)


class FirstForm(Form):
    ip = StringField('ip', [validators.DataRequired()])#,validators.IPAddress()])
    submit = SubmitField('Salva') 
      
    
"""Per CERCARE un elemento del database attraverso un FORM HTML"""
@app.route('/lista', methods=["GET", "POST"])
def cerca_elementi():
    # Inizializziamo il form e le variabili di supporto
    cform = FirstForm(request.form)
    risultati = []
    scelta = None

    # AZIONE: L'utente ha premuto il tasto Submit
    if request.method == 'POST' and cform.validate():
        # 1. Recupero parametri dal form
        ip = cform.ip.data
        l = db_firestone.get_all_elements("net-id")
        try:
            ip_r = ipaddress.IPv4Address(ip)
        except ValueError:
            return render_template("lista.html",cform=cform,lista=l,sbagliato=True)

        
        l_filtered = [elem for elem in l if ip_r in ipaddress.IPv4Network(f"{elem['ip']}/{elem['netmaskCIDR']}", strict=False)]
        l_filtered_sorted = sorted(l_filtered,key=lambda x: x['netmaskCIDR'], reverse=True)
        
        elem_to_red =  [elem["id"] for elem in l_filtered_sorted][0]
        l = [
            {
            "id": elem["id"],
            "device": elem["device"],
            "gw": elem["gw"],
            "ip": elem["ip"],
            "netmaskCIDR": elem["netmaskCIDR"],
            "red": True if str(elem_to_red) == str(elem["id"]) else False,
            } for elem in l
        ]
        return render_template("lista.html", cform=cform, lista=l,sbagliato=False)

    
    l = db_firestone.get_all_elements("net-id")
    l = [
            {
            "id": elem["id"],
            "device": elem["device"],
            "gw": elem["gw"],
            "ip": elem["ip"],
            "netmaskCIDR": elem["netmaskCIDR"],
            "red": False,
            } for elem in l
        ]
    return render_template("lista.html", cform=cform, lista=l,sbagliato=False)

#Per fare debug in locale
if __name__=='__main__':
    app.run(host="localhost", port=8080, debug=True)
