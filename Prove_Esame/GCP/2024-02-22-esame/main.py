import os
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

class FirstForm(Form):
    cap = IntegerField('Valore', [validators.NumberRange(min=10000, max=99999)])
    tipo_scelta = RadioField('Cerca in:', choices=[('dumarell'), ('cantiere')], default='dumarell')
    submit = SubmitField('Cerca') 

@app.route('/list', methods=["GET", "POST"])
def nome_della_funzione():

    cform = FirstForm(request.form)
   
    if request.method == 'POST' and cform.validate():
        cap_cercato = cform.cap.data
        collezione = cform.tipo_scelta.data
        elements = db_firestone.get_all_elements(collezione)

        elements_filtrati = [elem for elem in elements if elem["cap"] == cap_cercato]
        
        if len(elements_filtrati) == 0:
            print("qui1")
            return render_template("interrogare_database.html", cform=cform, messaggio="Nessun elemento trovato con il CAP specificato.")
        else:
            print("qui2")
            return render_template("interrogare_database.html", elements=elements_filtrati, cform=cform,tipo=collezione,messaggio="")
    
    return render_template("interrogare_database.html", cform=cform)

#Per fare debug in locale
if __name__=='__main__':
    app.run(host="localhost", port=8080, debug=True)