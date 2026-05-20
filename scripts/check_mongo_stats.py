import os
import json
from dotenv import load_dotenv
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, OperationFailure

def run_stats():
    # Učitaj MONGODB_URI iz .env fajla
    load_dotenv()
    uri = os.environ.get("MONGODB_URI")
    
    if not uri or "<TVOJA_LOZINKA>" in uri:
        print("❌ GREŠKA: Lozinka u .env fajlu nije podešena! Molimo otvorite .env i zamenite <TVOJA_LOZINKA> sa vašom stvarnos MongoDB lozinkom.")
        return

    print("Povezivanje na MongoDB Atlas klaster...")
    try:
        client = MongoClient(uri, serverSelectionTimeoutMS=5000)
        # Verifikacija konekcije
        client.admin.command('ping')
        print("✅ Konekcija uspešna!")
        
        db_name = "ai_workflow_orchestrator"
        db = client[db_name]
        
        print("\n--- STATISTIKA BAZE ---")
        try:
            stats = db.command("dbStats")
            print(f"Ime baze: {db_name}")
            print(f"Kolekcije: {stats.get('collections', 0)}")
            print(f"Broj dokumenata (objects): {stats.get('objects', 0)}")
            print(f"Veličina podataka (dataSize): {stats.get('dataSize', 0) / 1024 / 1024:.2f} MB")
        except OperationFailure as e:
            print(f"Nemate prava za pun dbStats (česta pojava na Atlas shared instancama): {e}")
            
        print("\n--- PREGLED KOLEKCIJA ---")
        collections = db.list_collection_names()
        if not collections:
            print("Baza je prazna ili ne postoje kolekcije.")
        for coll in collections:
            count = db[coll].count_documents({})
            print(f" 📦 '{coll}': {count} dokumenata")
            
        if "debates" in collections:
            print("\n--- UZORAK: POSLEDNJA DEBATE SESIJA ---")
            last_debate = db["debates"].find_one(sort=[("created_at", -1)])
            if last_debate:
                print(json.dumps(last_debate, indent=2, default=str))
            else:
                print("Nema debate dokumenata.")
                
        if "decision_history" in collections:
            print("\n--- UZORAK: POSLEDNJA ODLUKA IZ MEMORIJE ---")
            last_dec = db["decision_history"].find_one(sort=[("created_at", -1)])
            if last_dec:
                print(json.dumps(last_dec, indent=2, default=str))

    except ConnectionFailure as e:
        print(f"❌ Konekcija nije uspela: {e}")
    except Exception as e:
        print(f"❌ Greška prilikom provere: {e}")

if __name__ == "__main__":
    run_stats()
