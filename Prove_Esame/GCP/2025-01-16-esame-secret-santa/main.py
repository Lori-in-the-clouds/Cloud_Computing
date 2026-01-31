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


class RegistrazioneForm(Form):
    email = EmailField('Email', [validators.Email()])
    firstname = StringField('firstname', [validators.DataRequired()])
    lastname = StringField('lastname', [validators.DataRequired()])
    submit = SubmitField('Salva')


class RicercaDestinatarioForm(Form):
    email = EmailField('Email', [validators.Email()])
    submit = SubmitField('Cerca Destinatario')


def discover_secret_santa(email):
    l = db_firestone.get_all_elements("lista_partecipanti")

    l_sorted = sorted(l,key=lambda d: from_string_to_date_full(d["timestamp"]),reverse=False)
    res = {}
    from_t = {}
    if l_sorted[-1]["id"] == email:
        res = l_sorted[0]
        elem =  [elem for elem in l_sorted if elem["id"] == email]
        from_t = {
            "id": elem[0]["id"],
            "firstname": elem[0]["firstname"],
            "lastname": elem[0]["lastname"]
        }
    
    else:
        for i in range(len(l_sorted)):
            if l_sorted[i]["id"] == email:
                res = l_sorted[i+1]
                from_t = l_sorted[i]
    
    return {
        "fromEmail": email,
        "fromFirstName": from_t["firstname"],
        "fromLastName": from_t["lastname"],
        "toEmail": res["id"],
        "toFirstName": res["firstname"],
        "toLastName": res["lastname"]
    }


    
"""Per CERCARE un elemento del database attraverso un FORM HTML"""
@app.route('/cerca', methods=["GET", "POST"])
def cerca_elementi():
    # Inizializziamo il form e le variabili di supporto
    rform = RegistrazioneForm(request.form)
    cform = RicercaDestinatarioForm(request.form)

    # AZIONE: L'utente ha premuto il tasto Submit
    if request.method == 'POST' and rform.validate():
        email = rform.email.data
        firstname = rform.firstname.data
        lastname = rform.lastname.data

        db_firestone.add_element("lista_partecipanti",str(email),{
            "firstname": firstname,
            "lastname": lastname,
            "timestamp": from_date_full_to_string(datetime.now())
        })
        return redirect('/cerca')

    if request.method == "POST" and cform.validate():
        email = cform.email.data
        res = discover_secret_santa(email)
        return render_template("pagina.html", rform=rform, cform=cform,res=res)

    # VISUALIZZAZIONE: Restituiamo sempre lo stesso template
    # In GET: risultati sarà [] e il form sarà vuoto
    # In POST: risultati conterrà i dati filtrati
    return render_template("pagina.html", rform=rform, cform=cform, res="")


if __name__=='__main__':
    app.run(host="localhost", port=8080, debug=True)

    