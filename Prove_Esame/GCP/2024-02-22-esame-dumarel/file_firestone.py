from google.cloud import firestore
from datetime import datetime
from time_utils import *
import json

DB_NAME = "db-dumarell"

class FirestoreManager(object):
    
    def __init__(self):
        if DB_NAME:
            self.db = firestore.Client(database=DB_NAME)
        else:
            print("Attenzione: nessun database specificato, uso il default.")

    def add_element(self, collection_name, document_id, data_dict):
        """
        Salva o sovrascrive un documento.
        Accetta document_id sia come stringa che come intero.
        """
        # Firestore richiede che l'ID del documento sia una stringa.
        # Usiamo str() per assicurarci che anche gli interi vengano accettati.
        ref = self.db.collection(collection_name).document(str(document_id))
        ref.set(data_dict)

    def get_element(self, collection_name, document_id):
        """Recupera un singolo documento (document_id può essere int o str)"""
        doc_ref = self.db.collection(collection_name).document(str(document_id))
        doc = doc_ref.get()
        if doc.exists:
            return doc.to_dict()
        return None

    def get_all_elements(self, collection_name):
        collection_ref = self.db.collection(collection_name)
        results = []
        for doc in collection_ref.stream():
            data = doc.to_dict()
            # Se vuoi che l'ID torni a essere un intero se possibile:
            try:
                data['id'] = int(doc.id)
            except ValueError:
                data['id'] = doc.id 
            results.append(data)
        return results

    def clean_db(self):
        for collection in self.db.collections():
            for doc in collection.stream():
                doc.reference.delete()

    def clean_collection(self, collection_name):
        docs = self.db.collection(collection_name).stream()
        for doc in docs:
            doc.reference.delete()

    def populate_from_json(self, filename, collection_target):
        try:
            with open(filename, 'r') as f:
                data_list = json.load(f)
                for item in data_list:
                    # Estrae l'id (che ora può essere un numero nel JSON)
                    doc_id = item.pop('id', None) 
                    if doc_id is not None: # Verifica che l'id esista (0 è un id valido)
                        self.add_element(collection_target, doc_id, item)
        except FileNotFoundError:
            print(f"File {filename} non trovato.")

if __name__ == '__main__':
    db = FirestoreManager()
    # Ora puoi passare ID interi o caricare JSON con ID numerici
    db.populate_from_json('db.json', collection_target="dumarell")
    db.populate_from_json('db1.json', collection_target="cantiere")
    #db.clean_db()