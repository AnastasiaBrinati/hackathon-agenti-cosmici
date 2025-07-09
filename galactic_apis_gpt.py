# galactic_apis.py

import json

class GalacticState:
    """Classe singleton per gestire lo stato condiviso della galassia"""
    _instance = None
    _state = None
    
    def __new__(cls, galaxy_state_file=None):
        if cls._instance is None:
            cls._instance = super(GalacticState, cls).__new__(cls)
            if galaxy_state_file:
                with open(galaxy_state_file, "r") as f:
                    cls._state = json.load(f)
        return cls._instance
    
    @property
    def state(self):
        return self._state
    
    def save_to_file(self, filepath):
        """Salva lo stato corrente su file"""
        with open(filepath, "w") as f:
            json.dump(self._state, f, indent=2)

class GalacticMarketplace:
    def __init__(self, galaxy_state_file=None):
        if galaxy_state_file:
            self.galactic_state = GalacticState(galaxy_state_file)
        else:
            self.galactic_state = GalacticState()
        self.galaxy_state = self.galactic_state.state

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

    def item_on_planet(self, item_name, planet):
        for item_id, item in self.galaxy_state.get("marketplace", {}).items():
            if planet.lower() in item["planet"].lower() and item_name.lower() == item["name"].lower():
                return True
        return False


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
    def __init__(self, galaxy_state_file=None):
        if galaxy_state_file:
            self.galactic_state = GalacticState(galaxy_state_file)
        else:
            self.galactic_state = GalacticState()
        self.galaxy_state = self.galactic_state.state

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
        
        print(f"Selected ship: {selected_ship_name}")
        print(f"Selected ship location: {selected_ship['location']}")
        print(f"Destination: {destination}")
        print(f"Total cost: {total_cost}")
        print(f"Client balance: {self.galaxy_state['client']['balance']}")

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
    
    def get_client_budget(self):
        return self.galaxy_state["client"]["balance"]


class InfoSphere:
    def __init__(self, galaxy_state_file=None):
        if galaxy_state_file:
            self.galactic_state = GalacticState(galaxy_state_file)
        else:
            self.galactic_state = GalacticState()
        self.galaxy_state = self.galactic_state.state


    def get_travel_cost(self, origin, destination):
        route = f"{origin}-{destination}"
        return self.galaxy_state["travel_costs"].get(route, 0)

    def get_all_planets(self):
        planets = set()

        # Droids locations
        for droid in self.galaxy_state.get("droids", {}).values():
            if "location" in droid:
                planets.add(droid["location"])

        # Ships locations
        for ship in self.galaxy_state.get("ships", {}).values():
            if "location" in ship:
                planets.add(ship["location"])

        # Marketplace planets
        for item in self.galaxy_state.get("marketplace", {}).values():
            if "planet" in item:
                planets.add(item["planet"])

        # Infosphere planets
        for info in self.galaxy_state.get("infosphere", {}).values():
            if "planet" in info:
                planets.add(info["planet"])
            # A few entries might have the planet as the key itself (e.g., "Alderaan")
            # and only 'status'/'threat_level' inside; if so, also add the key
        for key, info in self.galaxy_state.get("infosphere", {}).items():
            if isinstance(info, dict) and "planet" not in info and "status" in info:
                planets.add(key)

        return sorted(planets)

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