"""Client de connexion au serveur Chronobio."""

import argparse
from typing import NoReturn

from chronobio.network.client import Client


class PlayerGameClient(Client):
    def __init__(
        self: "PlayerGameClient", server_addr: str, port: int, username: str
    ) -> None:
        super().__init__(server_addr, port, username, spectator=False)
        self._commands: list[str] = []

    def run(self: "PlayerGameClient") -> NoReturn:
        while True:
            game_data = self.read_json()
            for farm in game_data["farms"]:
                if farm["name"] == self.username:
                    my_farm = farm
                    break
            else:
                raise ValueError(f"My farm is not found ({self.username})")
            
            # Afficher les informations importantes
            day = game_data.get("day", 0)
            money = my_farm.get("money", 0)
            blocked = my_farm.get("blocked", False)
            score = my_farm.get("score", 0)
            
            print(f"\n[Jour {day}] {self.username}")
            print(f"  Argent: {money} EUR | Score: {score} EUR")
            print(f"  Champs: {len(my_farm.get('fields', []))} | Ouvriers: {len(my_farm.get('workers', []))}")
            
            if blocked:
                print(f"  *** FERME BLOQUEE ***")
                print(f"  Raison: plus d'argent pour payer les salaires")
            
            print(f"  État complet: {my_farm}")

            # Stratégie AMÉLIORÉE - Progressive et rentable
            
            day = game_data["day"]
            money = my_farm.get("money", 0)
            fields = my_farm.get("fields", [])
            employees = my_farm.get("employees", [])
            tractors = my_farm.get("tractors", [])
            stock = my_farm.get("soup_factory", {}).get("stock", {})
            
            # Compter les champs achetés (bought = True)
            owned_fields = [f for f in fields if f.get("bought", False)]
            num_fields = len(owned_fields)
            num_employees = len(employees)
            num_tractors = len(tractors)
            
            # PHASE 1 : Setup COMPÉTITION (expansion rapide)
            if day == 0:
                # Acheter 3 champs dès le départ
                self.add_command("0 ACHETER_CHAMP")
                self.add_command("0 ACHETER_CHAMP")
                self.add_command("0 ACHETER_CHAMP")
            
            elif day == 1:
                # Embaucher 3 ouvriers + acheter tracteur
                self.add_command("0 EMPLOYER")
                self.add_command("0 EMPLOYER")
                self.add_command("0 EMPLOYER")
                if money > 50000:
                    self.add_command("0 ACHETER_TRACTEUR")
            
            elif day == 2:
                # Semer sur les 3 champs (variété équilibrée)
                self.add_command("1 SEMER PATATE 1")
                self.add_command("2 SEMER TOMATE 2")
                self.add_command("3 SEMER OIGNON 3")
            
            elif day == 3:
                # Acheter 4ème champ
                if money > 50000:
                    self.add_command("0 ACHETER_CHAMP")
            
            elif day == 4:
                # Acheter 5ème champ + embaucher 4ème ouvrier
                if money > 55000:
                    self.add_command("0 ACHETER_CHAMP")
                if money > 60000:
                    self.add_command("0 EMPLOYER")
            
            elif day == 5:
                # Embaucher 5ème ouvrier
                if money > 60000:
                    self.add_command("0 EMPLOYER")
            
            # PHASE 2 : Production continue (jour 6+)
            else:
                # Obtenir les IDs des ouvriers qui sont DISPONIBLES (à la ferme)
                # Un ouvrier est disponible si sa location est "FARM"
                available_employees = [
                    emp.get("id") for emp in employees 
                    if emp.get("location") == "FARM"
                ]
                used_employees = set()
                
                # PRIORITÉ 1 : RÉCOLTER les légumes mûrs (needed_water == 0, content != NONE)
                if num_tractors > 0 and available_employees:
                    for field in owned_fields:
                        content = field.get("content", "NONE")
                        needed_water = field.get("needed_water", 0)
                        if content != "NONE" and needed_water == 0:
                            location = field.get("location", "")
                            if location.startswith("FIELD"):
                                field_num = location.replace("FIELD", "")
                                # Trouver un ouvrier disponible
                                for emp_id in available_employees:
                                    if emp_id not in used_employees:
                                        self.add_command(f"{emp_id} STOCKER {field_num} 1")
                                        used_employees.add(emp_id)
                                        break
                                break  # Une récolte à la fois
                
                # PRIORITÉ 2 : VENDRE AGRESSIVEMENT (revenus maximaux!)
                factory = my_farm.get("soup_factory", {})
                soups_ready = factory.get("days_off", 0) == 0
                total_stock = sum(stock.values())
                
                # Vendre dès qu'on a 8 légumes (cycle rapide)
                if soups_ready and total_stock >= 8 and available_employees:
                    for emp_id in available_employees:
                        if emp_id not in used_employees:
                            self.add_command(f"{emp_id} VENDRE")
                            used_employees.add(emp_id)
                            break
                
                # PRIORITÉ 3 : CUISINER très souvent (transformer en valeur)
                if soups_ready and total_stock >= 4 and total_stock < 8 and available_employees:
                    for emp_id in available_employees:
                        if emp_id not in used_employees:
                            self.add_command(f"{emp_id} CUISINER")
                            used_employees.add(emp_id)
                            break
                
                # PRIORITÉ 4 : ARROSER les champs qui ont besoin d'eau (TOUS!)
                if available_employees:
                    for field in owned_fields:
                        content = field.get("content", "NONE")
                        needed_water = field.get("needed_water", 0)
                        if content != "NONE" and needed_water > 0:
                            location = field.get("location", "")
                            if location.startswith("FIELD"):
                                field_num = location.replace("FIELD", "")
                                # Trouver un ouvrier disponible
                                for emp_id in available_employees:
                                    if emp_id not in used_employees:
                                        self.add_command(f"{emp_id} ARROSER {field_num}")
                                        used_employees.add(emp_id)
                                        break
                
                # PRIORITÉ 5 : SEMER sur les champs vides (ÉQUILIBRÉ pour soupes)
                if available_employees:
                    # Stratégie intelligente : semer ce qui manque dans le stock
                    # Cela garantit une production équilibrée pour les soupes
                    
                    # Compter ce qu'on a déjà en stock
                    stock_counts = {
                        "PATATE": stock.get("POTATO", 0),
                        "POIREAU": stock.get("LEEK", 0),
                        "TOMATE": stock.get("TOMATO", 0),
                        "OIGNON": stock.get("ONION", 0),
                        "COURGETTE": stock.get("ZUCCHINI", 0)
                    }
                    
                    # Compter ce qui pousse dans les champs
                    for field in owned_fields:
                        content = field.get("content", "NONE")
                        if content in ["POTATO", "LEEK", "TOMATO", "ONION", "ZUCCHINI"]:
                            content_fr = {
                                "POTATO": "PATATE", "LEEK": "POIREAU", 
                                "TOMATO": "TOMATE", "ONION": "OIGNON", 
                                "ZUCCHINI": "COURGETTE"
                            }.get(content, content)
                            stock_counts[content_fr] = stock_counts.get(content_fr, 0) + 1
                    
                    # Trier par quantité (semer d'abord ce qui manque le plus)
                    sorted_vegetables = sorted(stock_counts.items(), key=lambda x: x[1])
                    vegetables_priority = [veg for veg, count in sorted_vegetables]
                    
                    # Semer sur TOUS les champs vides
                    veg_index = 0
                    for field in owned_fields:
                        if field.get("content") == "NONE":
                            location = field.get("location", "")
                            if location.startswith("FIELD"):
                                field_num = location.replace("FIELD", "")
                                # Trouver un ouvrier disponible
                                for emp_id in available_employees:
                                    if emp_id not in used_employees:
                                        # Semer le légume le plus rare
                                        veg = vegetables_priority[veg_index % len(vegetables_priority)]
                                        self.add_command(f"{emp_id} SEMER {veg} {field_num}")
                                        used_employees.add(emp_id)
                                        veg_index += 1
                                        break
                
                # PRIORITÉ 6 : EXPANSION COMPÉTITION (score maximal)
                
                # Embaucher rapidement (max 6 ouvriers pour production massive)
                if money > 80000 and num_employees < 6:
                    self.add_command("0 EMPLOYER")
                
                # Acheter des champs dès que possible (tous les 5 champs!)
                if money > 90000 and num_fields < 5:
                    self.add_command("0 ACHETER_CHAMP")
                
                # Acheter 2ème et 3ème tracteurs (récolte ultra-rapide)
                if money > 120000 and num_tractors < 2:
                    self.add_command("0 ACHETER_TRACTEUR")
                if money > 180000 and num_tractors < 3:
                    self.add_command("0 ACHETER_TRACTEUR")
                
                # Emprunter stratégiquement si on stagne
                if money < 60000 and num_fields >= 4 and day % 50 == 0:
                    self.add_command("0 EMPRUNTER 50000")

            self.send_commands()

    def add_command(self: "PlayerGameClient", command: str) -> None:
        self._commands.append(command)

    def send_commands(self: "PlayerGameClient") -> None:
        # Créer une copie de la liste pour éviter les effets de bord
        data = {"commands": self._commands.copy()}
        print("sending", data)
        self.send_json(data)
        self._commands.clear()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Game client.")
    parser.add_argument(
        "-a",
        "--address",
        type=str,
        help="name of server on the network",
        default="localhost",
    )
    parser.add_argument(
        "-p",
        "--port",
        type=int,
        help="location where server listens",
        default=16210,
    )
    parser.add_argument(
        "-u",
        "--username",
        type=str,
        help="name of the user",
        default="unknown",
        required=True,
    )
    args = parser.parse_args()

    client = PlayerGameClient(args.address, args.port, args.username).run()
