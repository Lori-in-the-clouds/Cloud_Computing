from google.cloud import firestore
from datetime import datetime
from time_utils import *
import json

DB_NAME = "db-riunioni" #MODIFICA

class FirestoreManager(object):
    
    def __init__(self):
        # Inizializza il client. Se DB_NAME è None, usa il default.
        if DB_NAME:
            self.db = firestore.Client(database=DB_NAME)
        else:
            print("Attenzione: nessun database specificato, uso il default.")

    def add_element(self, collection_name, document_id, data_dict):
        """
        Salva o sovrascrive un documento.
        collection_name: nome della collezione (es. 'letture' o 'bollette')
        document_id: chiave primaria (es. '01-01-2023' o '01-2023')
        data_dict: dizionario con i dati { 'valore': 100, 'costo': 50 }
        """
        ref = self.db.collection(collection_name).document(str(document_id))
        ref.set(data_dict)

    def get_element(self, collection_name, document_id):
        """Recupera un singolo documento"""
        doc_ref = self.db.collection(collection_name).document(str(document_id))
        doc = doc_ref.get()
        if doc.exists:
            return doc.to_dict()
        return None

    def get_all_elements(self, collection_name):
        """Ritorna una lista di dizionari contententi anche l'ID."""
        collection_ref = self.db.collection(collection_name)
        results = []
        for doc in collection_ref.stream():
            data = doc.to_dict()
            data['id'] = doc.id  # Aggiungo l'ID al dizionario dati per comodità
            results.append(data)
        return results

    # --- PULIZIA DATABASE ---

    def clean_db(self):
        """Cancella TUTTE le collezioni nel database"""
        for collection in self.db.collections():
            for doc in collection.stream():
                doc.reference.delete()

    def clean_collection(self, collection_name):
        """Svuota una singola collezione"""
        docs = self.db.collection(collection_name).stream()
        for doc in docs:
            doc.reference.delete()

    # --- POPOLAMENTO INIZIALE ---
    def populate_from_json(self, filename, collection_target):
        try:
            with open(filename, 'r') as f:
                data_list = json.load(f)
                for item in data_list:
                    # Assumiamo che nel JSON ci sia un campo 'id' da usare come chiave
                    doc_id = item.pop('id', None) 
                    if doc_id:
                        self.add_element(collection_target, doc_id, item)
        except FileNotFoundError:
            print(f"File {filename} non trovato, salto il popolamento.")


if __name__ == '__main__':
    db = FirestoreManager()
    db.populate_from_json('db.json',collection_target="meeting crimes")
    #db.clean_db()
    