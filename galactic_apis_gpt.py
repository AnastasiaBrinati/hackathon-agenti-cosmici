# galactic_apis.py

import json

class GalacticMarketplace:
    def __init__(self, galaxy_state_file):
        with open(galaxy_state_file, "r") as f:
            self.galaxy_state = json.load(f)

    def find_item(self, item_name):
        """
        Restituisce un elenco di oggetti il cui nome contiene item_name.
        """
        results = []
        for item_id, item in self.galaxy_state.get("marketplace", {}).items():
            if item_name.lower() in item["name"].lower():
                results.append({"id": item_id, **item})
        return results

    def purchase_item(self, item_id):
        """
        Acquista un oggetto, aggiornando inventario e bilancio.
        """
        item = self.galaxy_state["marketplace"].get(item_id)
        if not item:
            raise ValueError("Oggetto non trovato.")

        price = item["price"]
        balance = self.galaxy_state["client"]["balance"]
        if price > balance:
            raise ValueError("Fondi insufficienti.")

        # Aggiorna saldo
        self.galaxy_state["client"]["balance"] -= price

        # Aggiungi all'inventario
        self.galaxy_state["client"]["inventory"].append(item)

        return {
            "item": item,
            "remaining_balance": self.galaxy_state["client"]["balance"]
        }

    def calculate_transport_cost(self, origin, destination):
        """
        Restituisce il costo di trasporto tra due pianeti.
        """
        route = f"{origin}-{destination}"
        return self.galaxy_state["travel_costs"].get(route, 0)

    def get_budget(self):
        """
        Restituisce il saldo attuale.
        """
        return self.galaxy_state["client"]["balance"]

    def get_inventory(self):
        """
        Restituisce l'inventario del cliente.
        """
        return self.galaxy_state["client"]["inventory"]


class GalaxyNavigator:
    def __init__(self, galaxy_state_file):
        with open(galaxy_state_file, "r") as f:
            self.galaxy_state = json.load(f)

    def find_asset_position(self, droid_name):
        """
        Restituisce la posizione del droide.
        """
        droid = self.galaxy_state["droids"].get(droid_name)
        if not droid:
            raise ValueError("Droide non trovato.")
        return droid["location"]

    def book_travel(self, ship_name, origin, destination):
        """
        Prenota un viaggio con una nave disponibile.
        """
        ship = self.galaxy_state["ships"].get(ship_name)
        if not ship:
            raise ValueError("Nave non trovata.")
        if not ship["available"]:
            raise ValueError("La nave non è disponibile.")

        travel_cost = self.galaxy_state["travel_costs"].get(f"{origin}-{destination}", None)
        if travel_cost is None:
            raise ValueError("Percorso non disponibile.")

        rental_cost = ship["rental_cost"]
        total_cost = rental_cost + travel_cost

        # Marcare la nave come non disponibile
        ship["available"] = False

        return {
            "ship": ship_name,
            "origin": origin,
            "destination": destination,
            "rental_cost": rental_cost,
            "travel_cost": travel_cost,
            "total_cost": total_cost
        }

    def get_fleet_status(self):
        """
        Restituisce lo stato della flotta.
        """
        return self.galaxy_state["ships"]


class InfoSphere:
    def __init__(self, galaxy_state_file):
        with open(galaxy_state_file, "r") as f:
            self.galaxy_state = json.load(f)

    def search_info(self, subject):
        """
        Cerca informazioni sul subject (es. azienda, pianeta).
        """
        info = self.galaxy_state["infosphere"].get(subject)
        if not info:
            raise ValueError("Informazioni non trovate.")
        return info

    def search_droid_info(self, droid_name):
        """
        Restituisce informazioni su un droide.
        """
        droid = self.galaxy_state["droids"].get(droid_name)
        if not droid:
            raise ValueError("Droide non trovato.")
        return droid

    def search_item_info(self, item_name):
        """
        Cerca informazioni sugli oggetti.
        """
        results = []
        for item_id, item in self.galaxy_state.get("marketplace", {}).items():
            if item_name.lower() in item["name"].lower():
                results.append({"id": item_id, **item})
        return results
