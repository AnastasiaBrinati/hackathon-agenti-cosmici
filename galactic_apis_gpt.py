# galactic_apis.py

import json

class GalacticMarketplace:
    def __init__(self, galaxy_state_file):
        with open(galaxy_state_file, "r") as f:
            self.galaxy_state = json.load(f)

    def find_item(self, item_name):
        results = []
        for item_id, item in self.galaxy_state.get("marketplace", {}).items():
            if item_name.lower() in item["name"].lower():
                results.append({"id": item_id, **item})
        return results

    def find_items(self, planet):
        results = []
        for item_id, item in self.galaxy_state.get("marketplace", {}).items():
            if planet.lower() in item["planet"].lower():
                results.append({"id": item_id, **item})
        return results

    def purchase_item(self, item_id):
        item = self.galaxy_state["marketplace"].get(item_id)
        if not item:
            raise ValueError("Oggetto non trovato.")

        price = item["price"]
        if price > self.galaxy_state["client"]["balance"]:
            raise ValueError("Fondi insufficienti.")

        # Aggiorna saldo
        self.galaxy_state["client"]["balance"] -= price

        # Aggiungi all'inventario
        self.galaxy_state["client"]["inventory"].append(item)

        purchase_info = {
            "item": item,
            "price": price,
            "remaining_balance": self.galaxy_state["client"]["balance"]
        }

        return purchase_info

    def calculate_transport_cost(self, origin, destination):
        route = f"{origin}-{destination}"
        return self.galaxy_state["travel_costs"].get(route, 0)

    def get_budget(self):
        return self.galaxy_state["client"]["balance"]

    def get_inventory(self):
        return self.galaxy_state["client"]["inventory"]


class GalaxyNavigator:
    def __init__(self, galaxy_state_file):
        with open(galaxy_state_file, "r") as f:
            self.galaxy_state = json.load(f)

    def find_asset_position(self, droid_name):
        droid = self.galaxy_state["droids"].get(droid_name)
        if not droid:
            raise ValueError("Droide non trovato.")
        return droid["location"]

    def move_asset(self, droid_name, asset_position):
        droid = self.galaxy_state["droids"].get(droid_name)
        if not droid:
            raise ValueError("Droide non trovato.")
        droid["location"] = asset_position

    def book_travel(self, origin, destination):
        available_ships = [
            (name, ship)
            for name, ship in self.galaxy_state["ships"].items()
            if ship["available"] and ship["location"] == origin
        ]

        if not available_ships:
            # TO-DO: migliora implementazione considerando navi da altri pianeti
            # valutando il costo del trasferimento
            raise ValueError("Nessuna nave disponibile da questo pianeta.")

        selected_ship_name, selected_ship = min(
            available_ships, key=lambda item: item[1]["rental_cost"]
        )

        travel_cost = self.galaxy_state["travel_costs"].get(f"{origin}-{destination}", None)
        if travel_cost is None:
            raise ValueError("Percorso non disponibile.")

        rental_cost = selected_ship["rental_cost"]
        total_cost = rental_cost + travel_cost

        if total_cost > self.galaxy_state["client"]["balance"]:
            raise ValueError("Fondi insufficienti per il viaggio.")

        # Marca la nave come non disponibile
        #selected_ship["available"] = False
        selected_ship["location"] = destination
        # TO-DO: quando verrà segnalata come dinuovo disponibile?

        # Scala il bilancio del cliente
        self.galaxy_state["client"]["balance"] -= total_cost

        travel_info = {
            "ship": selected_ship_name,
            "rental_cost": rental_cost,
            "travel_cost": travel_cost,
            "total_cost": total_cost
        }

        return travel_info

    def get_fleet_status(self):
        return self.galaxy_state["ships"]


class InfoSphere:
    def __init__(self, galaxy_state_file):
        with open(galaxy_state_file, "r") as f:
            self.galaxy_state = json.load(f)

    def search_info(self, subject):
        info = self.galaxy_state["infosphere"].get(subject)
        if not info:
            raise ValueError("Informazioni non trovate.")
        return info

    def search_droid_info(self, droid_name):
        droid = self.galaxy_state["droids"].get(droid_name)
        if not droid:
            raise ValueError("Droide non trovato.")
        return droid

    def search_item_info(self, item_name):
        results = []
        for item_id, item in self.galaxy_state.get("marketplace", {}).items():
            if item_name.lower() in item["name"].lower():
                results.append({"id": item_id, **item})
        return results

    def get_client_budget(self):
        return self.galaxy_state["client"]["balance"]
