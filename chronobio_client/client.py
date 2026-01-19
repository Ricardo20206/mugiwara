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
                print("  *** FERME BLOQUEE ***")
                print("  Raison: plus d'argent pour payer les salaires")

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

            # Afficher l'état détaillé CHAQUE TOUR
            if not blocked:
                factory = my_farm.get("soup_factory", {})
                total_stock = sum(stock.values())
                days_off = factory.get("days_off", 0)
                employees_list = my_farm.get("employees", [])
                available = [e for e in employees_list if e.get("location") == "FARM"]
                busy = [e for e in employees_list if e.get("location") != "FARM"]

                # Affichage CHAQUE TOUR
                print(f"  👥 Ouvriers: {len(available)} dispo, {len(busy)} occupés")
                print(f"  🌱 Stock légumes: P:{stock.get('POTATO',0)} T:{stock.get('TOMATO',0)} Po:{stock.get('LEEK',0)} O:{stock.get('ONION',0)} C:{stock.get('ZUCCHINI',0)} | Total: {total_stock}")
                print(f"  🍲 Usine: {'✅ PRÊTE' if days_off == 0 else f'⏳ Occupe encore {days_off}j'}")

            print(f"  État complet: {my_farm}")

            # Stratégie OPTIMALE - Tous les légumes, production équilibrée, durabilité maximale

            # Les variables day, money, stock, loans, total_debt sont déjà définies ci-dessus
            fields = my_farm.get("fields", [])
            employees = my_farm.get("employees", [])
            tractors = my_farm.get("tractors", [])

            # Buffer adaptatif ÉQUILIBRÉ (production + sécurité)
            safety_buffer = total_salaries * 12  # 12 jours (équilibre)

            # Compter les champs achetés (bought = True)
            owned_fields = [f for f in fields if f.get("bought", False)]
            num_fields = len(owned_fields)
            num_employees = len(employees)
            num_tractors = len(tractors)

            # PHASE 1 : Démarrage ULTRA-MINIMALISTE (1 seul ouvrier!)
            if day == 0:
                # PAS D'EMPRUNT ! On démarre avec 100k€ de base
                # Acheter 2 champs seulement (simplicité)
                self.add_command("0 ACHETER_CHAMP")
                self.add_command("0 ACHETER_CHAMP")

            elif day == 1:
                # Embaucher SEULEMENT 1 ouvrier (économie maximale!)
                # Salaires réduits = plus de temps pour première récolte
                self.add_command("0 EMPLOYER")
                print("  👔 EMPLOYER 1 ouvrier (démarrage prudent)")
                # Acheter 1 tracteur
                self.add_command("0 ACHETER_TRACTEUR")

            elif day == 2:
                # Acheter 1 champ supplémentaire (total 3)
                self.add_command("0 ACHETER_CHAMP")

            elif day == 3:
                # Semer 1 seul champ (on n'a qu'1 ouvrier)
                available = [e.get("id") for e in employees
                           if e.get("location") == "FARM" and e.get("tractor") is None]
                if len(available) >= 1:
                    self.add_command(f"{available[0]} SEMER PATATE 1")
                    print("  🌱 Semis jour 3: PATATE champ 1")

            elif day == 4:
                # Semer 2ème champ
                available = [e.get("id") for e in employees
                           if e.get("location") == "FARM" and e.get("tractor") is None]
                if len(available) >= 1:
                    self.add_command(f"{available[0]} SEMER TOMATE 2")
                    print("  🌱 Semis jour 4: TOMATE champ 2")

            elif day == 5:
                # Semer 3ème champ
                available = [e.get("id") for e in employees
                           if e.get("location") == "FARM" and e.get("tractor") is None]
                if len(available) >= 1:
                    self.add_command(f"{available[0]} SEMER POIREAU 3")
                    print("  🌱 Semis jour 5: POIREAU champ 3")

            # PHASE 2 : Production HYBRIDE (jour 6+)
            else:
                # STRATÉGIE HYBRIDE :
                # - Pour SEMER : Seulement ouvriers à FARM (prudent)
                # - Pour ARROSER/RÉCOLTER : Tous sans tracteur (agressif)

                employees_at_farm = [
                    emp.get("id") for emp in employees
                    if emp.get("location") == "FARM" and emp.get("tractor") is None
                ]

                all_available = [
                    emp.get("id") for emp in employees
                    if emp.get("tractor") is None
                ]

                used_employees = set()

                # Debug: afficher les ouvriers
                total = len(employees)
                at_farm = len(employees_at_farm)
                all_free = len(all_available)
                print(f"  👥 Ouvriers: {at_farm} à FARM, {all_free} sans tracteur (total: {total})")

                # PRIORITÉ 1 : VENDRE directement depuis champ (si urgence ou pas de tracteur)
                # Vendre est moins rentable que cuisiner, mais donne du cash immédiat
                # Prix: 3000€ - 50 * (nb de champs concurrents avec même légume)
                gerant_available = not my_farm.get("blocked", False)

                if money < safety_buffer * 0.2 and num_tractors == 0 and gerant_available:
                    # Situation d'urgence ET pas de tracteur → vendre directement
                    for field in owned_fields:
                        content = field.get("content", "NONE")
                        needed_water = field.get("needed_water", 0)
                        if content != "NONE" and needed_water == 0:
                            location = field.get("location", "")
                            if location.startswith("FIELD"):
                                field_num = location.replace("FIELD", "")
                                print(f"  💰 VENDRE champ {field_num} : {content} (~3000€)")
                                self.add_command(f"0 VENDRE {field_num}")
                                break  # Une seule vente par tour (gérant occupé 2 jours)

                # PRIORITÉ 2 : RÉCOLTER TOUS les légumes mûrs (avec gestion tracteurs!)
                if num_tractors > 0 and all_available:
                    # Trouver les tracteurs disponibles (pas déjà assignés à un ouvrier)
                    tractors = my_farm.get("tractors", [])
                    used_tractors = set()

                    # Marquer les tracteurs déjà utilisés par des ouvriers
                    for emp in employees:
                        if emp.get("tractor") is not None:
                            tractor = emp.get("tractor", {})
                            if isinstance(tractor, dict):
                                used_tractors.add(tractor.get("id"))

                    available_tractors = [t.get("id") for t in tractors if t.get("id") not in used_tractors]

                    recoltes = 0
                    for field in owned_fields:
                        content = field.get("content", "NONE")
                        needed_water = field.get("needed_water", 0)
                        if content != "NONE" and needed_water == 0:
                            location = field.get("location", "")
                            if location.startswith("FIELD"):
                                field_num = location.replace("FIELD", "")

                                # Trouver un ouvrier ET un tracteur disponibles
                                emp_found = None
                                tractor_found = None

                                for emp_id in all_available:
                                    if emp_id not in used_employees and available_tractors:
                                        emp_found = emp_id
                                        tractor_found = available_tractors[0]
                                        break

                                if emp_found and tractor_found:
                                    self.add_command(f"{emp_found} STOCKER {field_num} {tractor_found}")
                                    used_employees.add(emp_found)
                                    available_tractors.remove(tractor_found)
                                    print(f"  🌾 RÉCOLTER champ {field_num} : {content} (ouvrier {emp_found}, tracteur {tractor_found})")
                                    recoltes += 1

                    if recoltes > 0:
                        print(f"  ✅ {recoltes} récolte(s) effectuée(s)")
                    elif len(available_tractors) == 0:
                        print("  ⏸️  Récolte impossible: tous les tracteurs occupés")

                # PRIORITÉ 2 : VENDRE selon situation (équilibre cash/stock)
                factory = my_farm.get("soup_factory", {})
                soups_ready = factory.get("days_off", 0) == 0
                total_stock = sum(stock.values())

                # Stratégie : CUISINER AGRESSIVEMENT (vente automatique!)
                # Vérifier qu'on a les 5 types de légumes pour faire des soupes "5 légumes"
                min_each_veg = 10  # Minimum réduit à 10 (au lieu de 20)
                has_diversity = all(stock.get(veg, 0) >= min_each_veg for veg in ["POTATO", "LEEK", "TOMATO", "ONION", "ZUCCHINI"])

                # Seuil ULTRA-BAS : cuisiner dès 50 légumes!
                min_stock_to_cook = 50

                # Utiliser TOUS les ouvriers sans tracteur pour cuisiner
                max_cooks = min(5, len([e for e in all_available if e not in used_employees]))

                # PRIORITÉ 4 : CUISINER avec PLUSIEURS ouvriers (revenus x3!)
                if soups_ready and total_stock >= min_stock_to_cook and all_available:
                    cooks_assigned = 0
                    for emp_id in all_available:
                        if emp_id not in used_employees and cooks_assigned < max_cooks:
                            self.add_command(f"{emp_id} CUISINER")
                            used_employees.add(emp_id)
                            cooks_assigned += 1

                    if cooks_assigned > 0:
                        diversity_bonus = "✨ 5 légumes" if has_diversity else "⚠️ diversité limitée"
                        print(f"  🍲 CUISINER x{cooks_assigned}: {total_stock} légumes ({diversity_bonus})")
                elif total_stock >= min_stock_to_cook:
                    if not soups_ready:
                        print("  ⏸️  Cuisine impossible: usine occupée")
                    elif not all_available:
                        print("  ⏸️  Cuisine impossible: tous ouvriers occupés")
                elif total_stock > 0:
                    missing_vegs = [v for v in ["POTATO", "LEEK", "TOMATO", "ONION", "ZUCCHINI"] if stock.get(v, 0) < min_each_veg]
                    if missing_vegs:
                        print(f"  ⏸️  Accumulation: {total_stock}/{min_stock_to_cook} légumes (manque: {', '.join(missing_vegs)})")
                    else:
                        print(f"  ⏸️  Accumulation: {total_stock}/{min_stock_to_cook} légumes")

                # PRIORITÉ 5 : ARROSER TOUS les champs (utilise tous les ouvriers!)
                if all_available:
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

                    arrosages = 0
                    for _needed, field_num in fields_to_water:
                        # Assigner un ouvrier à chaque champ (tous disponibles)
                        for emp_id in all_available:
                            if emp_id not in used_employees:
                                self.add_command(f"{emp_id} ARROSER {field_num}")
                                used_employees.add(emp_id)
                                arrosages += 1
                                break

                    if arrosages > 0:
                        print(f"  💧 ARROSER : {arrosages} champ(s)")

                # PRIORITÉ 8 : SEMER (seulement ouvriers à FARM, prudent!)
                if employees_at_farm:
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
                    semis = 0
                    for field in owned_fields:
                        if field.get("content") == "NONE":
                            location = field.get("location", "")
                            if location.startswith("FIELD"):
                                field_num = location.replace("FIELD", "")
                                for emp_id in employees_at_farm:
                                    if emp_id not in used_employees:
                                        # Semer le légume le plus rare
                                        veg = priority_list[veg_idx % len(priority_list)]
                                        self.add_command(f"{emp_id} SEMER {veg} {field_num}")
                                        used_employees.add(emp_id)
                                        print(f"  🌱 SEMER champ {field_num} : {veg}")
                                        semis += 1
                                        veg_idx += 1
                                        break

                    if semis > 0:
                        print(f"  ✅ {semis} semis effectué(s)")

                # PRIORITÉ 6 : GESTION DES OUVRIERS (licencier si nécessaire)

                # LICENCIER si trop d'ouvriers et pas assez d'argent
                # Licencier le dernier ouvrier embauché (salaire le plus bas normalement)
                if num_employees > 0 and money < safety_buffer * 0.3 and num_employees > 3:
                    # Trouver l'ouvrier avec le salaire le plus bas
                    sorted_employees = sorted(employees, key=lambda e: e.get("salary", 0))
                    if sorted_employees:
                        emp_to_fire = sorted_employees[0]
                        emp_id = emp_to_fire.get("id")
                        salary = emp_to_fire.get("salary", 0)
                        print(f"  🔴 LICENCIER ouvrier {emp_id} (salaire: {salary}€)")
                        self.add_command(f"0 LICENCIER {emp_id}")

                # PRIORITÉ 7 : EXPANSION PROGRESSIVE (croissance lente mais sûre!)

                # Limites MINIMALISTES pour survie maximale
                MAX_EMPLOYEES = 5    # Maximum 5 ouvriers
                MAX_TRACTORS = 2     # Maximum 2 tracteurs
                # MAX_FIELDS = 3 déjà fixé au jour 2

                # PAS DE DETTE = PAS DE REMBOURSEMENT NÉCESSAIRE
                # (score toujours positif!)

                # Ratio équilibré : 1.5 ouvriers par champ
                target_employees = min(MAX_EMPLOYEES, int(num_fields * 1.5))

                # Embaucher progressivement APRÈS première récolte
                # Seuil réduit pour le 2ème ouvrier (nécessaire pour la production)
                hiring_threshold = 40000 if num_employees < 2 else safety_buffer + 80000

                if money > hiring_threshold and num_employees < target_employees:
                    self.add_command("0 EMPLOYER")
                    print(f"  👤 EMPLOYER (total: {num_employees + 1}/{target_employees})")

                # Acheter des tracteurs seulement si très rentable
                if money > safety_buffer + 100000 and num_tractors < MAX_TRACTORS:
                    self.add_command("0 ACHETER_TRACTEUR")
                    print(f"  🚜 ACHETER_TRACTEUR (total: {num_tractors + 1})")

                # NE JAMAIS EMPRUNTER (stratégie sans dette!)

                # Afficher si aucune action ce tour
                if len(self._commands) == 0:
                    print("  😴 Aucune action ce tour (ouvriers occupés ou en attente)")

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
