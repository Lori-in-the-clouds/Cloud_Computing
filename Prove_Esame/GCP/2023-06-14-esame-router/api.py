from flask import Flask, request
from flask_restful import Resource, Api
from file_firestone import *
from time_utils import *
from flask_cors import CORS
import re
import ipaddress

def verifica_net_id(ip_cidr):
    try:
        # strict=True (default) valida che l'hostID sia tutto a zero
        rete = ipaddress.IPv4Network(ip_cidr, strict=True)
        return True
    except ValueError as e:
        return False
#
# Esempi
#test1 = "192.168.1.0/24" # Ok
#test2 = "192.168.1.0/23" # Errore: il bit 24 è 1

#valido, messaggio = verifica_net_id(test2)
#print(messaggio) 
# Output: Errore: 192.168.1.0/23 has host bits set

app = Flask(__name__)
CORS(app)
api=Api(app)
base_path='/api/v1'

db_firestone = FirestoreManager()

def validate_payload(data, required_fields):
    """
    Controlla se i campi richiesti esistono, se i tipi sono corretti e se i valori sono validi.
    """
    for field, expected_type in required_fields.items():
        val = data.get(field)
        # 1. Controllo esistenza
        if val is None:
            return False
        # 2. Controllo tipo (es. int, str, bool)
        if not isinstance(val, expected_type):
            return False
        # 3. Controllo Email
        if field == "email":
            if not re.match(r"[^@]+@[^@]+\.[^@]+", val):
                return False
        return True


class FirstResource(Resource):
    
    # Per ottenere una risorsa
    def get(self, id): 
        print(type(id))
        try:
            id = int(id)
        except (ValueError, TypeError):
            return None, 400
        
        if id < 1 or id is None:
            return None, 400
        
        elem = db_firestone.get_element("net-id",id)
        if elem is None:
            return None,404
        
        return {
            "ip": elem["ip"],
            "netmaskCIDR": elem["netmaskCIDR"],
            "gw": elem["gw"],
            "device": elem["device"]
        }, 200
        
    # Crea una nuova risorsa
    def post(self, id): 
        request_info = request.json
        ip = request_info.get("ip")
        netmaskCIDR = request_info.get("netmaskCIDR")
        gw = request_info.get("gw")
        device = request_info.get("device")

        if ip is None or netmaskCIDR is None or gw is None or device is None or not verifica_net_id(f"{ip}/{netmaskCIDR}") or not verifica_net_id(gw):
            return None,400
        
        try:
            id = int(id)
        except (ValueError, TypeError):
            return None, 400
        
        if not isinstance(ip,str) or not isinstance(netmaskCIDR,int) or not isinstance(gw,str) or not isinstance(device,str):
            return None,400
        
        elem = db_firestone.get_element("net-id",str(id))
        if elem is not None:
            return None,409
        
        db_firestone.add_element("net-id",str(id),{
            "ip": ip,
            "netmaskCIDR": netmaskCIDR,
            "gw": gw,
            "device": device
        })
        
        return {
            "ip": ip,
            "netmaskCIDR": netmaskCIDR,
            "gw": gw,
            "device": device
        }, 201
    
        
    # Aggiorna una risorsa specifica 
    def put(self, id): 

        request_info = request.json
        ip = request_info.get("ip")
        netmaskCIDR = request_info.get("netmaskCIDR")
        gw = request_info.get("gw")
        device = request_info.get("device")

        if gw is not None and device is None and ip is None and netmaskCIDR is None:
            l = db_firestone.get_all_elements("net-id")
            for elem in l:
                if elem["ip"] == "0.0.0.0" and elem["netmaskCIDR"]== 0 and elem["device"]=="eth0" and elem["gw"] == gw:
                    return None,404
            db_firestone.add_element("net-id",str(id),{
                "ip": '0.0.0.0',
                "netmaskCIDR": 0,
                "gw": gw,
                "device":"eth0"
            })

            return {
            "ip":'0.0.0.0',
            "netmaskCIDR": 0,
            "gw": gw,
            "device": "eth0"
        },200
        
        try:
            id = int(id)
        except (ValueError, TypeError):
            return None, 400

        if ip is None or netmaskCIDR is None or gw is None or device is None or not verifica_net_id(f"{ip}/{netmaskCIDR}") or not verifica_net_id(gw):
            return None,400
        
        if not isinstance(ip,str) or not isinstance(netmaskCIDR,int) or not isinstance(gw,str) or not isinstance(device,str):
            return None,400        

        elem = db_firestone.get_element("net-id",str(id))
        if elem is None:
            return None,404   

        db_firestone.add_element("net-id",str(id),{
            "ip": ip,
            "netmaskCIDR": netmaskCIDR,
            "gw": gw,
            "device": device
        })
        
        return {
            "ip": ip,
            "netmaskCIDR": netmaskCIDR,
            "gw": gw,
            "device": device
        }, 200  

    def delete(self, id):
        try:
            id = int(id)
        except (ValueError, TypeError):
            return None, 404
        
        elem = db_firestone.get_element("net-id",str(id))
        
        if elem is None:
            return None,404 
        
        db_firestone.delete_element("net-id",str(id))
        return None,204
                
#Per ciascuna classe eseguiamo il collegamento con il path corretto all'esterno della classe indicando il nome del parametro (se presente nel path).
api.add_resource(FirstResource, f'{base_path}/routing/<id>')

#Ecco un esempio in cui il path possiede solamente un metodo e non è presente alcun parametro:

class SecondResource(Resource):
    def post(self):
        db_firestone.clean_collection("net-id")
        return None,200
    
api.add_resource(SecondResource, f'{base_path}/clean')


class ThirdResource(Resource):
    def get(self): 
        l = db_firestone.get_all_elements("net-id")
        l_sorted = sorted(l, key=lambda x: int(x["netmaskCIDR"]),reverse=True)
        return [elem["id"] for elem in l_sorted],200
    
    def post(self):
       
        ip = request.get_data(as_text=True).strip().replace('"', '')
        
        if ip is None or not isinstance(ip,str):
            return None,400

        
        try:
            ip_r = ipaddress.IPv4Address(ip)
        except ValueError:
            return None, 400

        l = db_firestone.get_all_elements("net-id")
        l_filtered = [elem for elem in l if ip_r in ipaddress.IPv4Network(f"{elem['ip']}/{elem['netmaskCIDR']}", strict=False)]
        l_filtered_sorted = sorted(l_filtered,key=lambda x: x['netmaskCIDR'], reverse=True)
        #PER IL TEST
        #return [str(elem["id"]) for elem in l_filtered_sorted][0],200
        return [elem["id"] for elem in l_filtered_sorted],200
    
api.add_resource(ThirdResource, f'{base_path}/routing')


#Per fare debug in locale
if __name__=='__main__':
    app.run(host="localhost", port=8080, debug=True)
