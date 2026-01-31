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

"""
Per utilizzare i WTForm dichiariamo una classe che eredita da Form in cui spefichiamo i nomi e la tipologia di field 
e validators per i dati che saranno inseriti al loro interno.
"""
class FirstForm(Form):
    name = StringField('Name', [validators.DataRequired()])
    valore = IntegerField('Valore', [validators.NumberRange(min=0, max=1000)])
    data = DateField('Data', format='%Y-%m-%d') 
    email = EmailField('Email', [validators.Email()])
    tipo_scelta = RadioField('Cerca in:', choices=['dumarell', 'cantiere'], default='dumarell')
    submit = SubmitField('Salva Modifiche')

"""
Definiamo quindi le funzioni che gestiscono i metodi dell'applicazione (GET, POST, PUT, DELETE). 
Ogni funzione dichiara che tipo di metodi può gestire attraverso `methods=[LISTA_METODI]. 
La funzione dovrà poi eseguire un return sul render del template HTML inserendo come parametri quelli richiesti da quello specifico template.
"""
@app.route('/list', methods=['GET']) 
def lista():
    elements = db_firestone.get_all_elements("bollette")

    start = datetime.now().replace(day=1)
    l = []
    l.append(f"{start.month}-{start.year}")
    for i in range (0,11):
        #print(start.month)
        if start.month - 1 == 0:
            start = start.replace(year=start.year - 1,month=12)
        else:
            start = start.replace(year=start.year,month=start.month -1)
        
        l.append(f"{start.month}-{start.year}")
    
    elements_filtered = [elem for elem in elements if elem["id"] in l]
    elements_filtered_sorted = sorted(elements_filtered, key=lambda d: datetime.strptime(d["id"], "%m-%Y"), reverse=True)
    
    return render_template("list.html", elements = elements_filtered_sorted)

@app.route('/details/<ID_PARAM>', methods=['GET']) 
def dettagli(ID_PARAM):
    #elem = db_firestone.get_element("bollette",ID_PARAM)
    data = from_string_to_month(ID_PARAM)
    mese_precedente = " "
    
    if data.month - 1 == 0:
        mese_precedente = mese_it_month(from_month_to_string(data.replace(year=data.year - 1,month=12)))
    else:
        mese_precedente = mese_it_month(from_month_to_string(data.replace(year=data.year,month=data.month -1)))

    print(mese_precedente)
    ultima_lettura = db_firestone.get_all_elements("letture")
    ultima_lettura_filtered = [elem for elem in ultima_lettura if mese_it_date(elem["id"]) == mese_precedente]
    ultima_lettura_filtered_sorted = sorted(ultima_lettura_filtered, key=lambda d: datetime.strptime(d["id"], "%d-%m-%Y"), reverse=True)

    return render_template("dettagli.html", element = {
        "data":ID_PARAM,
        "mese_precedente": mese_precedente,
        "costo": ultima_lettura_filtered_sorted[0]["value"]* 0.5 if len(ultima_lettura_filtered_sorted) != 0 else None,
        "consumo_del_mese": ultima_lettura_filtered_sorted[0]["value"] if len(ultima_lettura_filtered_sorted) != 0 else None,
        "ultima_lettura_considerata": ultima_lettura_filtered_sorted[0]["id"] if len(ultima_lettura_filtered_sorted) != 0 else None
    })

'''
"""Per CERCARE un elemento del database attraverso un FORM HTML"""
@app.route('/cerca', methods=["GET", "POST"])
def cerca_elementi():
    # Inizializziamo il form e le variabili di supporto
    cform = FirstForm(request.form)
    risultati = []
    scelta = None

    # AZIONE: L'utente ha premuto il tasto Submit
    if request.method == 'POST' and cform.validate():
        # 1. Recupero parametri dal form
        valore_filtro = cform.cap.data
        collezione = cform.tipo_scelta.data
        scelta = collezione # Per ricordarci cosa stiamo guardando nell'HTML

        # 2. Prendiamo tutto dalla collezione scelta (es. 'umarell' o 'cantiere')
        tutti = db_firestone.get_all_elements(collezione)

        # 3. Filtriamo per il campo 'cap' confrontandolo con quanto inserito dall'utente
        risultati = [item for item in tutti if item.get("cap") == valore_filtro]

    # VISUALIZZAZIONE: Restituiamo sempre lo stesso template
    # In GET: risultati sarà [] e il form sarà vuoto
    # In POST: risultati conterrà i dati filtrati
    return render_template("FILE.html", cform=cform, elements=risultati, tipo=scelta)

"""Per MODIFICARE un elemento preesistente del database attraverso un FORM HTML"""   
@app.route('/path/<ID_PARAM>', methods=['GET', 'POST'])
def funzione_modifica(ID_PARAM):
    # 1. Recupero dati dal Database
    # Questa riga serve a caricare i dati attuali per mostrarli nel form
    elemento_esistente = db_firestone.get_element(collection_name="NOME_COLLEZIONE", document_id=ID_PARAM)
    
    # Controllo di sicurezza: se l'ID non esiste, torna alla home o lista
    if not elemento_esistente:
        return redirect("/url_lista_generale")

    # 2. Gestione INVIO DATI (POST)
    if request.method == 'POST':
        cform = FirstForm(request.form)
        if cform.validate():
            # Creiamo il dizionario con i nuovi dati presi dal form
            dati_aggiornati = {
                "campo1": cform.campo1.data,
                "campo2": cform.campo2.data,
                # ... aggiungi tutti i campi necessari ...
            }
            # Sovrascriviamo il documento nel DB usando lo stesso ID
            db_firestone.add_element("NOME_COLLEZIONE", document_id=ID_PARAM, data_dict=dati_aggiornati)
            
            # Redirect dopo il salvataggio per evitare invii doppi (F5)
            return redirect("/path/" + ID_PARAM)

    # 3. Gestione VISUALIZZAZIONE (GET)
    # Pre-compiliamo il form con i dati recuperati dal database al punto 1
    cform = FirstForm(data=elemento_esistente)
    return render_template("FILE.html", cform=cform, id_elemento=ID_PARAM)
'''

#TRIGGER
def update(data,context): #context
    new_value = data['value'] if len(data["value"]) != 0 else None
    old_value = data['oldValue'] if len(data["oldValue"]) !=0 else None

    if new_value and not old_value: # document added
        data_date = from_string_to_date(new_value["name"].split("/")[-1])
        l = db_firestone.get_all_elements("letture")
        l_filtered = [
                        elem for elem in l
                        if from_string_to_date(elem["id"])
                        and from_string_to_date(elem["id"]).month == data_date.month
                        and from_string_to_date(elem["id"]) > data_date
                    ]
        if len(l_filtered) == 0:
            db_firestone.add_element("bollette",f"{(data_date + relativedelta(months=+1)).month}-{(data_date + relativedelta(months=+1)).year}", {"costo": int(new_value["fields"]["value"]["integerValue"])*0.5})
    
#Per fare debug in locale

if __name__=='__main__':
    app.run(host="localhost", port=8080, debug=True)
    """
    fake_event = {
        "value": {
            "name": "projects/test/databases/(default)/documents/letture/12-05-2026",
            "fields": {
                "value": {
                    "integerValue": "100"
                }
            }
        },
        "oldValue": {}
    }
    """
    #update(fake_event)
    #nome_della_funzione()

