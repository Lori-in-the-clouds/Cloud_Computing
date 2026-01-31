from flask import Flask, request
from flask_restful import Resource, Api
from file_firestone import *
from time_utils import *
from flask_cors import CORS
import re
import email_validator


app = Flask(__name__)
CORS(app)
api=Api(app)
base_path='/api/v1'

def validazione_email(email):
    try:
        email_validator.validate_email(email)
        return True
    except email_validator.EmailNotValidError:
        return False

db_firestone = FirestoreManager()


class FirstResource(Resource):
    
    def get(self, email): 
        
        if not validazione_email(email):
            return None,400
        
        if db_firestone.get_element("lista_partecipanti",email) is None:
            return None,404
        
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

        #print(l_sorted)

        return {
            "fromEmail": email,
            "fromFirstName": from_t["firstname"],
            "fromLastName": from_t["lastname"],
            "toEmail": res["id"],
            "toFirstName": res["firstname"],
            "toLastName": res["lastname"]
        },200
        
    # Crea una nuova risorsa
    def post(self, email): 
        request_info = request.json
        firstname = request_info.get("firstName")
        lastname = request_info.get("lastName")

        print(firstname,lastname)

        if firstname is None or lastname is None or not validazione_email(email):
            return None,400
        
        if db_firestone.get_element("lista_partecipanti",email) is not None:
            return None,409
        
        db_firestone.add_element("lista_partecipanti",email,{
            "firstname": firstname,
            "lastname": lastname,
            "timestamp": from_date_full_to_string(datetime.now())
        })
        
        return {
            "firstname": firstname,
            "lastname": lastname
        }, 201
        
     
#Per ciascuna classe eseguiamo il collegamento con il path corretto all'esterno della classe indicando il nome del parametro (se presente nel path).
api.add_resource(FirstResource, f'{base_path}/santa/<string:email>')


class SecondResource(Resource):
    def get(self):
        db_firestone.clean_collection("lista_partecipanti")
        return None,200
    
api.add_resource(SecondResource, f'{base_path}/clean')


#Per fare debug in locale
if __name__=='__main__':
    app.run(host="localhost", port=8080, debug=True)

    