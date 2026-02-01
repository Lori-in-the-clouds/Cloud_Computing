from flask import Flask, render_template, request, redirect
from file_firestone import *
from wtforms import DateField, EmailField, Form, RadioField, StringField, IntegerField, SubmitField, validators
from time_utils import *
import uuid

#Creiamo applicazione web
app = Flask(__name__)
db_firestone = FirestoreManager()

#Trasformare un dizionario in un oggetto con attributi. Tipo color.red
class Struct:
    def __init__(self, **entries):
        self.__dict__.update(entries)

class MessaggioForm(Form):
    message = StringField('message', [validators.DataRequired()])
    submit = SubmitField('Invia')

class RicercaHashtag(Form):
    hashtag = StringField('hashtag', [validators.DataRequired()])
    submit = SubmitField('Cerca')
    
 
"""Per CERCARE un elemento del database attraverso un FORM HTML"""
@app.route('/cerca', methods=["GET", "POST"])
def cerca_elementi():
    # Inizializziamo il form e le variabili di supporto
    mform = MessaggioForm(request.form)
    rform = RicercaHashtag(request.form)

    # AZIONE: L'utente ha premuto il tasto Submit
    if request.method == 'POST' and mform.validate():
        message = mform.message.data
        print(message)
        if message is None or len(message) < 1 or len(message) > 100: 
            return render_template("inizio.html", rform=rform, mform=mform, corretto = False, ack =False)

        id = str(uuid.uuid4())
        db_firestone.add_element("messages",id,{
             "message": message,
            "hashtags": get_hashtags(message),
            "timestamp": from_date_full_to_string(datetime.now())
        })
        return render_template("inizio.html", rform=rform, mform=mform, corretto = True,ack=True)

    if request.method == 'POST' and rform.validate():
        hashtag = rform.hashtag.data
        if hashtag[0] != '#':
            return render_template("inizio.html", mform=mform, rform=rform,ack=False,corretto = True,error_tag = True)
        l = db_firestone.get_all_elements("messages")
        l_filtered = [elem for elem in l if hashtag in elem["hashtags"]]
        
        res = [
            elem["message"]
            for elem in l_filtered
        ]
        return render_template("dettagli.html", rform=rform, res=res)
        
    
    return render_template("inizio.html", mform=mform, rform=rform,ack=False,corretto = True, error_tag = False)


if __name__=='__main__':
    app.run(host="localhost", port=8080, debug=True)

    