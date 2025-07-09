import json

class GalacticMarketplace:
    """
    Gestisce le operazioni di trading nel marketplace galattico.
    Permette di cercare e acquistare oggetti, gestendo budget, inventario e costi di trasporto.
    """
    def __init__(self, galaxy_state, navigator):
        """
        Inizializza il marketplace con lo stato della galassia e un navigatore.
        
        Args:
            galaxy_state (dict): Il dizionario contenente lo stato corrente della galassia.
            navigator (GalaxyNavigator): Un'istanza di GalaxyNavigator per i calcoli di trasporto.
        """
        self.state = galaxy_state
        self.navigator = navigator
        self.client = self.state['client']

    def find_item(self, item_name):
        """
        Cerca un oggetto per nome nel marketplace.

        Args:
            item_name (str): Il nome dell'oggetto da cercare (case-insensitive).

        Returns:
            list: Una lista di dizionari, dove ogni dizionario rappresenta un oggetto trovato.
                  Restituisce una lista vuota se nessun oggetto viene trovato.
        """
        found_items = []
        for item_id, details in self.state['marketplace'].items():
            if item_name.lower() in details['name'].lower():
                item_info = details.copy()
                item_info['id'] = item_id
                found_items.append(item_info)
        return found_items

    def calculate_transport_cost(self, destination_planet, origin_planet):
        """
        Calcola il costo di trasporto di un oggetto.

        Args:
            destination_planet (str): Il pianeta di destinazione.
            origin_planet (str): Il pianeta di origine dell'oggetto.

        Returns:
            int or None: Il costo del trasporto, o None se la rotta non è disponibile.
        """
        return self.navigator.get_route_cost(origin_planet, destination_planet)

    def purchase_item(self, item_id, buyer_location):
        """
        Acquista un oggetto dal marketplace, aggiornando il budget e l'inventario.

        Args:
            item_id (str): L'ID dell'oggetto da acquistare.
            buyer_location (str): La posizione attuale dell'acquirente per calcolare il trasporto.

        Returns:
            str: Un messaggio che indica il successo o il fallimento dell'operazione.
        """
        if item_id not in self.state['marketplace']:
            return "Errore: Oggetto non trovato nel marketplace."

        item = self.state['marketplace'][item_id]
        item_price = item['price']
        origin_planet = item['planet']
        
        transport_cost = self.calculate_transport_cost(buyer_location, origin_planet)
        if transport_cost is None:
             return f"Errore: Impossibile calcolare il costo di trasporto da {origin_planet} a {buyer_location}."
        
        total_cost = item_price + transport_cost

        if self.client['balance'] >= total_cost:
            # Aggiorna il bilancio del cliente
            self.client['balance'] -= total_cost
            
            # Aggiunge l'oggetto all'inventario
            self.client['inventory'].append(item['name'])
            
            # Rimuove l'oggetto dal marketplace
            del self.state['marketplace'][item_id]
            
            return (f"Acquisto completato! '{item['name']}' aggiunto all'inventario.\n"
                    f"Costo oggetto: {item_price} crediti.\n"
                    f"Costo trasporto: {transport_cost} crediti.\n"
                    f"Saldo rimanente: {self.client['balance']} crediti.")
        else:
            return f"Errore: Fondi insufficienti. Costo totale ({total_cost}) supera il saldo ({self.client['balance']})."

# ---

class GalaxyNavigator:
    """
    Gestisce la navigazione, la localizzazione di asset e la logistica dei trasporti.
    """
    def __init__(self, galaxy_state):
        """
        Inizializza il navigatore con lo stato della galassia.

        Args:
            galaxy_state (dict): Il dizionario contenente lo stato corrente della galassia.
        """
        self.state = galaxy_state

    def get_asset_location(self, asset_name):
        """
        Trova la posizione corrente di un droide o di una nave.

        Args:
            asset_name (str): Il nome dell'asset (es. "R2-D2", "Millennium Falcon").

        Returns:
            str or None: La posizione dell'asset o None se non trovato.
        """
        if asset_name in self.state['droids']:
            return self.state['droids'][asset_name]['location']
        if asset_name in self.state['ships']:
            return self.state['ships'][asset_name]['location']
        return None

    def get_available_ships(self, location=None):
        """
        Restituisce una lista di navi disponibili, opzionalmente filtrate per posizione.

        Args:
            location (str, optional): Filtra le navi per pianeta. Defaults to None.

        Returns:
            dict: Un dizionario di navi disponibili.
        """
        available = {}
        for ship_name, details in self.state['ships'].items():
            if details['available']:
                if location is None or details['location'] == location:
                    available[ship_name] = details
        return available

    def get_route_cost(self, origin, destination):
        """
        Calcola il costo di un viaggio tra due pianeti.

        Args:
            origin (str): Pianeta di partenza.
            destination (str): Pianeta di arrivo.

        Returns:
            int or None: Il costo del viaggio o None se la rotta non esiste.
        """
        route_key = f"{origin}-{destination}"
        return self.state['travel_costs'].get(route_key)

    def optimize_route(self, start_planet, end_planet):
        """
        (Funzione di esempio) Ottimizza una rotta trovando il percorso più economico.
        Per ora, restituisce solo il costo del viaggio diretto.

        Args:
            start_planet (str): Il pianeta di partenza.
            end_planet (str): Il pianeta di destinazione.

        Returns:
            str: Un messaggio con il costo della rotta ottimizzata.
        """
        cost = self.get_route_cost(start_planet, end_planet)
        if cost:
            return f"Rotta ottimizzata trovata da {start_planet} a {end_planet} con un costo di {cost} crediti."
        return "Nessuna rotta diretta trovata."


# ---

class InfoSphere:
    """
    Fornisce accesso al database galattico per informazioni su pianeti, entità e dati.
    """
    def __init__(self, galaxy_state):
        """
        Inizializza l'InfoSphere con lo stato della galassia.

        Args:
            galaxy_state (dict): Il dizionario contenente lo stato corrente della galassia.
        """
        self.state = galaxy_state

    def search_info(self, query):
        """
        Cerca informazioni nel database galattico.

        Args:
            query (str): Il termine da cercare (es. "Alderaan", "Cybersystems Inc.").

        Returns:
            dict or str: I dati trovati o un messaggio di errore.
        """
        return self.state['infosphere'].get(query, "Nessuna informazione trovata per la tua ricerca.")

    def get_historical_data(self, topic):
        """
        (Funzione di esempio) Accede a dati storici. Non implementato con i dati attuali.
        """
        return f"Accesso ai dati storici per '{topic}' non ancora implementato."

    def analyze_trends(self, data_type):
        """
        (Funzione di esempio) Analizza trend e statistiche. Non implementato con i dati attuali.
        """
        return f"Analisi dei trend per '{data_type}' non ancora disponibile."

# --- Esempio di utilizzo (opzionale, per test) ---
if __name__ == '__main__':
    # Carica lo stato iniziale da un file JSON (o usa il dizionario direttamente)
    galaxy_data_str = """
    {
      "droids": { "R2-D2": { "location": "Coruscant", "type": "astromech" } },
      "ships": {
        "Millennium Falcon": { "type": "cargo", "location": "Coruscant", "available": true, "rental_cost": 300, "speed": "fast" },
        "StarHopper": { "type": "cargo", "location": "Tatooine", "available": true, "rental_cost": 200, "speed": "medium" }
      },
      "travel_costs": {
        "Tatooine-Coruscant": 120, "Coruscant-Tatooine": 120, "Tatooine-Alderaan": 180,
        "Alderaan-Tatooine": 180, "Coruscant-Alderaan": 100, "Alderaan-Coruscant": 100
      },
      "marketplace": {
        "HC001": { "name": "Holocron", "price": 800, "planet": "Alderaan" },
        "WA001": { "name": "Walkman degli Antichi", "price": 200, "planet": "Coruscant" },
        "CR001": { "name": "Crystal Shard", "price": 100, "planet": "Coruscant" },
        "MS001": { "name": "Map Scanner", "price": 150, "planet": "Alderaan" }
      },
      "client": { "balance": 700, "inventory": [] },
      "infosphere": {
        "Cybersystems Inc.": { "affiliation": "legitimate", "planet": "Coruscant" },
        "Alderaan": { "status": "peaceful", "threat_level": "low" }
      }
    }
    """
    galaxy_state = json.loads(galaxy_data_str)

    # Inizializza le API
    navigator = GalaxyNavigator(galaxy_state)
    marketplace = GalacticMarketplace(galaxy_state, navigator)
    infosphere = InfoSphere(galaxy_state)

    # Esempio 1: Ricerca oggetto
    print("--- Ricerca Oggetto ---")
    holocrons = marketplace.find_item("Holocron")
    print(f"Oggetti trovati: {holocrons}")

    # Esempio 2: Acquistare un oggetto
    print("\n--- Acquisto Oggetto ---")
    # Il nostro droide R2-D2 è a Coruscant, quindi compriamo lì per la spedizione
    droid_location = navigator.get_asset_location("R2-D2")
    print(f"Posizione del droide: {droid_location}")
    print(f"Saldo iniziale: {marketplace.client['balance']}")
    
    result = marketplace.purchase_item("WA001", droid_location)
    print(result)
    print(f"Nuovo inventario: {marketplace.client['inventory']}")

    # Esempio 3: InfoSphere
    print("\n--- InfoSphere ---")
    alderaan_info = infosphere.search_info("Alderaan")
    print(f"Info su Alderaan: {alderaan_info}")