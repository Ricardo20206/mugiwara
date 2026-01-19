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
            loans = my_farm.get("loans", [])
            stock = my_farm.get("soup_factory", {}).get("stock", {})
            
            print(f"\n[Jour {day}] {self.username}")
            print(f"  Argent: {money} EUR | Score: {score} EUR")
            print(f"  Champs: {len(my_farm.get('fields', []))} | Ouvriers: {len(my_farm.get('workers', []))}")
            
            if blocked:
                print(f"  *** FERME BLOQUEE ***")
                print(f"  Raison: plus d'argent pour payer les salaires")
            
            # Avertissement si l'argent est critique
            total_salaries = sum(emp.get("salary", 0) for emp in my_farm.get("employees", []))
            total_debt = sum(loan.get("amount", 0) for loan in loans)
            
            if not blocked and total_salaries > 0:
                days_remaining = money // total_salaries if total_salaries > 0 else 999
                if days_remaining < 10:
                    print(f"  🔴 URGENCE: {days_remaining} jours de salaires!")
                elif days_remaining < 15:
                    print(f"  🟡 ALERTE: {days_remaining} jours de salaires")
                elif days_remaining < 20:
                    print(f"  🟠 Attention: {days_remaining} jours de salaires")
            
            # Afficher les dettes
            if total_debt > 0:
                print(f"  💰 Dette: {total_debt} EUR")
            
            # Afficher la diversité des légumes tous les 20 jours
            if day % 20 == 0 and not blocked:
                print(f"  🌱 Stock: P:{stock.get('POTATO',0)} T:{stock.get('TOMATO',0)} Po:{stock.get('LEEK',0)} O:{stock.get('ONION',0)} C:{stock.get('ZUCCHINI',0)}")
            
            print(f"  État complet: {my_farm}")

            # Stratégie OPTIMALE - Tous les légumes, production équilibrée, durabilité maximale
            
            # Les variables day, money, stock, loans, total_debt sont déjà définies ci-dessus
            fields = my_farm.get("fields", [])
            employees = my_farm.get("employees", [])
            tractors = my_farm.get("tractors", [])
            
            # Buffer adaptatif équilibré
            safety_buffer = total_salaries * 12  # 12 jours (équilibre sécurité/croissance)
            
            # Compter les champs achetés (bought = True)
            owned_fields = [f for f in fields if f.get("bought", False)]
            num_fields = len(owned_fields)
            num_employees = len(employees)
            num_tractors = len(tractors)
            
            # PHASE 1 : Démarrage ÉQUILIBRÉ (production + sécurité)
            if day == 0:
                # Emprunt modéré pour démarrer (50k au lieu de 100k)
                self.add_command("0 EMPRUNTER 50000")
                # Acheter 4 champs (un par type de légume principal)
                self.add_command("0 ACHETER_CHAMP")
                self.add_command("0 ACHETER_CHAMP")
                self.add_command("0 ACHETER_CHAMP")
                self.add_command("0 ACHETER_CHAMP")
            
            elif day == 1:
                # Embaucher 5 ouvriers (bon ratio 1.25 ouvrier/champ)
                self.add_command("0 EMPLOYER")
                self.add_command("0 EMPLOYER")
                self.add_command("0 EMPLOYER")
                self.add_command("0 EMPLOYER")
                self.add_command("0 EMPLOYER")
                # Acheter tracteur
                self.add_command("0 ACHETER_TRACTEUR")
            
            elif day == 2:
                # Semer 4 légumes différents (diversification)
                self.add_command("1 SEMER PATATE 1")
                self.add_command("2 SEMER TOMATE 2")
                self.add_command("3 SEMER POIREAU 3")
                self.add_command("4 SEMER OIGNON 4")
            
            # PHASE 2 : Production continue (jour 6+)
            else:
                # Obtenir les IDs des ouvriers qui sont DISPONIBLES (à la ferme)
                # Un ouvrier est disponible si sa location est "FARM"
                available_employees = [
                    emp.get("id") for emp in employees 
                    if emp.get("location") == "FARM"
                ]
                used_employees = set()
                
                # PRIORITÉ 1 : RÉCOLTER TOUS les légumes mûrs (production maximale!)
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
                                # Ne pas break ici ! Récolter TOUS les champs prêts
                
                # PRIORITÉ 2 : VENDRE selon situation (équilibre cash/stock)
                factory = my_farm.get("soup_factory", {})
                soups_ready = factory.get("days_off", 0) == 0
                total_stock = sum(stock.values())
                
                # Stratégie adaptative intelligente
                if money < safety_buffer * 0.5:  # Urgence
                    min_stock_to_sell = 5
                    min_stock_to_cook = 3
                elif money < safety_buffer * 0.8:  # Attention
                    min_stock_to_sell = 6
                    min_stock_to_cook = 4
                elif money < safety_buffer:  # Prudent
                    min_stock_to_sell = 7
                    min_stock_to_cook = 5
                else:  # Confortable - optimiser
                    min_stock_to_sell = 8
                    min_stock_to_cook = 5
                
                # Vendre dès qu'on a assez de stock
                if soups_ready and total_stock >= min_stock_to_sell and available_employees:
                    for emp_id in available_employees:
                        if emp_id not in used_employees:
                            self.add_command(f"{emp_id} VENDRE")
                            used_employees.add(emp_id)
                            break
                
                # PRIORITÉ 3 : CUISINER en continu (pipeline de production)
                if soups_ready and total_stock >= min_stock_to_cook and total_stock < min_stock_to_sell and available_employees:
                    for emp_id in available_employees:
                        if emp_id not in used_employees:
                            self.add_command(f"{emp_id} CUISINER")
                            used_employees.add(emp_id)
                            break
                
                # PRIORITÉ 4 : ARROSER TOUS les champs en parallèle (croissance rapide!)
                if available_employees:
                    # Trier les champs par urgence : ceux qui ont le moins d'eau restante
                    fields_to_water = []
                    for field in owned_fields:
                        content = field.get("content", "NONE")
                        needed_water = field.get("needed_water", 0)
                        if content != "NONE" and needed_water > 0:
                            location = field.get("location", "")
                            if location.startswith("FIELD"):
                                field_num = location.replace("FIELD", "")
                                fields_to_water.append((needed_water, field_num))
                    
                    # Arroser en priorité les champs les plus proches de la maturation
                    fields_to_water.sort()  # Trier par needed_water (les plus proches d'abord)
                    
                    for _, field_num in fields_to_water:
                        # Assigner un ouvrier à chaque champ
                        for emp_id in available_employees:
                            if emp_id not in used_employees:
                                self.add_command(f"{emp_id} ARROSER {field_num}")
                                used_employees.add(emp_id)
                                break
                
                # PRIORITÉ 5 : SEMER TOUS les légumes (diversification maximale!)
                if available_employees:
                    # Compter TOUS les légumes (stock + en croissance)
                    all_vegetables = {
                        "PATATE": stock.get("POTATO", 0),
                        "POIREAU": stock.get("LEEK", 0),
                        "TOMATE": stock.get("TOMATO", 0),
                        "OIGNON": stock.get("ONION", 0),
                        "COURGETTE": stock.get("ZUCCHINI", 0)
                    }
                    
                    # Ajouter les légumes qui poussent dans les champs
                    for field in owned_fields:
                        content = field.get("content", "NONE")
                        if content in ["POTATO", "LEEK", "TOMATO", "ONION", "ZUCCHINI"]:
                            veg_fr = {
                                "POTATO": "PATATE", "LEEK": "POIREAU",
                                "TOMATO": "TOMATE", "ONION": "OIGNON",
                                "ZUCCHINI": "COURGETTE"
                            }[content]
                            all_vegetables[veg_fr] += 1
                    
                    # Trier par rareté : semer d'abord ce qui manque le plus
                    sorted_veggies = sorted(all_vegetables.items(), key=lambda x: (x[1], x[0]))
                    priority_list = [veg for veg, _ in sorted_veggies]
                    
                    # Afficher la priorité de semis pour debug
                    if day % 10 == 0:
                        print(f"  🌱 Priorité semis: {' > '.join(priority_list[:3])}")
                    
                    # Semer TOUS les champs vides avec rotation intelligente
                    veg_idx = 0
                    for field in owned_fields:
                        if field.get("content") == "NONE":
                            location = field.get("location", "")
                            if location.startswith("FIELD"):
                                field_num = location.replace("FIELD", "")
                                for emp_id in available_employees:
                                    if emp_id not in used_employees:
                                        # Semer le légume le plus rare
                                        veg = priority_list[veg_idx % len(priority_list)]
                                        self.add_command(f"{emp_id} SEMER {veg} {field_num}")
                                        used_employees.add(emp_id)
                                        veg_idx += 1
                                        break
                
                # PRIORITÉ 6 : EXPANSION ÉQUILIBRÉE (croissance contrôlée)
                
                # Limites raisonnables pour éviter explosion des salaires
                MAX_EMPLOYEES = 6  # Maximum 6 ouvriers (bon équilibre)
                MAX_FIELDS = 5     # Maximum 5 champs (un par légume)
                
                # Rembourser les dettes EN PRIORITÉ
                if total_debt > 0 and money > safety_buffer + 80000:
                    self.add_command("0 REMBOURSER 50000")
                
                # Ratio optimal : ~1.2 ouvriers par champ
                target_employees = min(MAX_EMPLOYEES, int(num_fields * 1.2) + 1)
                
                # Embaucher si besoin et argent suffisant
                if money > safety_buffer + 100000 and num_employees < target_employees:
                    self.add_command("0 EMPLOYER")
                
                # Acheter 5ème champ si on a assez d'ouvriers (tous les légumes!)
                if money > safety_buffer + 120000 and num_fields < MAX_FIELDS and num_employees >= num_fields:
                    self.add_command("0 ACHETER_CHAMP")
                
                # Acheter 2ème tracteur pour récoltes multiples
                if money > safety_buffer + 150000 and num_tractors < 2 and num_fields >= 4:
                    self.add_command("0 ACHETER_TRACTEUR")
                
                # Acheter 3ème tracteur si grosse ferme
                if money > safety_buffer + 250000 and num_tractors < 3 and num_fields >= 5:
                    self.add_command("0 ACHETER_TRACTEUR")
                
                # Emprunter SEULEMENT en urgence absolue
                if money < safety_buffer * 0.3 and total_debt == 0 and day % 100 == 0:
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
