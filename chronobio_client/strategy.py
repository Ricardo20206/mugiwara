"""
Stratégie ULTRA-SAFE - ZÉRO RISQUE d'erreur
Objectif: Ne JAMAIS bloquer + Score maximum
RÈGLE: Une seule action invalide = blocage permanent !
"""

from typing import Any


class Strategy:
    """Stratégie ULTRA-SAFE : Utilise seulement le gérant au début."""

    def __init__(self) -> None:
        """Initialise la stratégie."""
        self._day = 0
        self._last_harvest_day = 0
        # Rotation des semences sur tous les champs
        self._crop_rotation = ["PATATE", "OIGNON", "TOMATE", "COURGETTE", "POIREAU"]
        self._rotation_index = 0
        # Tracking pour éviter ALREADY_BUSY  
        self._gerant_busy_until = 0  # Tracker quand le gérant est libre
        self._ventes_par_jour = 0  # Limiter ventes (gérant prend 2j)
        # Assignation ouvrier → champ (1 ouvrier par champ)
        self._field_assignments: dict[int, int] = {}  # {emp_id: field_num}

    def get_actions(self, farm: dict[str, Any]) -> list[str]:
        """
        Génère les actions pour un tour selon la stratégie PROGRESSIVE.

        PRIORITÉS (ROTATION D'ABORD):
        1. SEMER (planifier la rotation des légumes!)
        2. ARROSER (faire pousser les cultures)
        3. RÉCOLTER + STOCKER (production!)
        4. CUISINER (transformer en soupes)
        5. EXPANSION (si bon capital)
        """
        self._day += 1
        self._ventes_par_jour = 0  # Reset compteur ventes
        commands: list[str] = []

        # Récupérer les données de la ferme
        money = farm.get("money", 0)
        fields = farm.get("fields", [])
        employees = farm.get("employees", [])
        tractors = farm.get("tractors", [])
        stock = farm.get("soup_factory", {}).get("stock", {})
        factory_days_off = farm.get("soup_factory", {}).get("days_off", 0)

        # Calculer les stats
        owned_fields = [f for f in fields if f.get("bought", False)]
        total_salaries = sum(emp.get("salary", 0) for emp in employees)
        total_stock = sum(stock.values())
        jours_salaires = money / total_salaries if total_salaries > 0 else 999

        # Tracking des ressources utilisées
        used_employees: set[int] = set()
        used_tractors: set[int] = set()

        # Identifier les tracteurs déjà utilisés
        for emp in employees:
            tractor = emp.get("tractor")
            if tractor is not None and isinstance(tractor, dict):
                used_tractors.add(tractor.get("id"))

        # DISPONIBILITÉ : FARM (priorité) OU dans champ sans tracteur (continuation)
        # Un employé à FARM peut tout faire (SEMER, ARROSER, RÉCOLTER)
        # Un employé dans un champ peut continuer (ARROSER, RÉCOLTER) depuis sa position
        available_employees_farm = []  # Pour SEMER (priorité absolue)
        available_employees_any = []   # Pour ARROSER/RÉCOLTER (peuvent être dans champs)
        at_farm = 0
        in_fields = 0
        
        for emp in employees:
            emp_id = emp.get("id")
            location = emp.get("location", "")
            tractor = emp.get("tractor")
            
            if location == "FARM" and tractor is None:
                at_farm += 1
                available_employees_farm.append(emp_id)
                available_employees_any.append(emp_id)
            elif location.startswith("FIELD") and tractor is None:
                in_fields += 1
                available_employees_any.append(emp_id)  # Peut continuer dans son champ
        
        print(f"  👥 Employés: {len(employees)} total | {at_farm} FARM | {in_fields} champs | {len(available_employees_farm)} dispo FARM | {len(available_employees_any)} dispo total")

        print(f"\n  {'='*60}")
        print(f"  🔍 JOUR {self._day} - ROTATION PUIS STOCKAGE")
        print(f"  {'='*60}")
        print(f"  💰 {money}€ | 👷 {len(employees)} employés | 🌾 {len(owned_fields)} champs | 🚜 {len(tractors)} tracteurs")

        # Debug employés (simplifié)
        print("\n  👥 EMPLOYÉS:")
        for emp in employees:
            emp_id = emp.get("id")
            location = emp.get("location", "?")
            tractor = emp.get("tractor")
            tractor_id = tractor.get("id") if tractor else None
            print(f"     Emp#{emp_id}: {location:13s} | tracteur={tractor_id}")

        # Debug champs
        print("\n  🌾 CHAMPS:")
        for field in owned_fields:
            location = field.get("location", "?")
            content = field.get("content", "NONE")
            needed_water = field.get("needed_water", 0)
            print(f"     {location}: {content:10s} | eau={needed_water}")

        # ============================================================
        # PHASE 0 : SETUP INITIAL (jours 1-2)
        # ============================================================
        if self._day <= 2:
            return self._initial_setup(self._day)

        # ============================================================
        # PRIORITÉ 1 : SEMER (rotation complète sur tous les champs!)
        # ============================================================
        # Initialiser assignations ouvrier → champ (2 ouvriers par champ)
        if not self._field_assignments and len(owned_fields) > 0:
            field_nums = []
            for field in owned_fields:
                location = field.get("location", "")
                if location.startswith("FIELD"):
                    field_num = int(location.replace("FIELD", ""))
                    field_nums.append(field_num)
            
            # Assigner 2 ouvriers par champ (rotation)
            for i, emp in enumerate(employees):
                field_index = i // 2  # 2 ouvriers par champ
                if field_index < len(field_nums):
                    self._field_assignments[emp.get("id")] = field_nums[field_index]
        
        fields_to_plant = []
        for field in owned_fields:
            if field.get("content") == "NONE":
                location = field.get("location", "")
                if location.startswith("FIELD"):
                    field_num = int(location.replace("FIELD", ""))
                    fields_to_plant.append(field_num)
        
        if fields_to_plant:
            print(f"  🌾 Champs vides à semer: {fields_to_plant}")
        
        # Semer avec rotation : 1 ouvrier par champ
        for field_num in fields_to_plant:
            # Trouver l'ouvrier assigné à ce champ
            assigned_emp = None
            for emp_id, assigned_field in self._field_assignments.items():
                if assigned_field == field_num:
                    # Vérifier si disponible : dans le champ correspondant OU à FARM (peut continuer)
                    for emp in employees:
                        emp_location = emp.get("location", "")
                        if emp.get("id") == emp_id and emp.get("tractor") is None:
                            # Peut être dans le champ correspondant OU à FARM
                            if emp_location == f"FIELD{field_num}" or emp_location == "FARM":
                                if emp_id in available_employees_any:
                                    assigned_emp = emp_id
                                    break
                    if assigned_emp:
                        break
            
            # Si pas d'ouvrier assigné, chercher d'abord dans le champ, sinon à FARM
            if assigned_emp is None:
                # Chercher un employé déjà dans ce champ
                for emp in employees:
                    emp_id = emp.get("id")
                    if emp.get("location") == f"FIELD{field_num}" and emp.get("tractor") is None:
                        if emp_id in available_employees_any:
                            self._field_assignments[emp_id] = field_num
                            assigned_emp = emp_id
                            break
                # Sinon, prendre le premier disponible (FARM prioritaire)
                if assigned_emp is None and available_employees_farm:
                    emp_id = available_employees_farm[0]
                    self._field_assignments[emp_id] = field_num
                    assigned_emp = emp_id
                elif assigned_emp is None and available_employees_any:
                    emp_id = available_employees_any[0]
                    self._field_assignments[emp_id] = field_num
                    assigned_emp = emp_id
            
            # FALLBACK FINAL : Si aucun ouvrier disponible, utiliser le gérant (id=0) pour SEMER
            # MAIS seulement si le gérant n'est pas occupé (pas de VENDRE en cours)
            if assigned_emp is None:
                if self._day > self._gerant_busy_until:
                    assigned_emp = 0  # Gérant peut semer même seul
                    print(f"  ⚠️ Aucun ouvrier disponible → Gérant (0) va SEMER champ {field_num}")
                else:
                    print(f"  ⚠️ Gérant occupé jusqu'au jour {self._gerant_busy_until} (jour {self._day}) → Ne peut pas SEMER champ {field_num}")
            
            if assigned_emp is not None:
                # Rotation : alterner les 5 légumes
                veg = self._crop_rotation[self._rotation_index % len(self._crop_rotation)]
                self._rotation_index += 1
                
                commands.append(f"{assigned_emp} SEMER {veg} {field_num}")
                if assigned_emp != 0:  # Ne pas retirer le gérant des listes
                    if assigned_emp in available_employees_farm:
                        available_employees_farm.remove(assigned_emp)
                    if assigned_emp in available_employees_any:
                        available_employees_any.remove(assigned_emp)
                print(f"  🌱 SEMER {veg} champ {field_num} ({'gérant' if assigned_emp == 0 else f'ouvrier #{assigned_emp}'}, rotation #{self._rotation_index})")

        # ============================================================
        # PRIORITÉ 2 : ARROSER (chaque ouvrier arrose son champ!)
        # ============================================================
        fields_to_water = []
        for field in owned_fields:
            content = field.get("content", "NONE")
            needed_water = field.get("needed_water", 0)
            if content != "NONE" and needed_water > 0:
                location = field.get("location", "")
                if location.startswith("FIELD"):
                    field_num = int(location.replace("FIELD", ""))
                    fields_to_water.append((field_num, needed_water, content))
        
        # Arroser : ouvrier assigné à chaque champ
        for field_num, water_needed, veg in fields_to_water:
            # Trouver l'ouvrier assigné à ce champ
            assigned_emp = None
            for emp_id, assigned_field in self._field_assignments.items():
                if assigned_field == field_num:
                    # Vérifier si disponible : dans le champ OU à FARM (peut continuer)
                    for emp in employees:
                        emp_location = emp.get("location", "")
                        if emp.get("id") == emp_id and emp.get("tractor") is None:
                            # Peut être dans le champ correspondant OU à FARM
                            if emp_location == f"FIELD{field_num}" or emp_location == "FARM":
                                if emp_id in available_employees_any:
                                    assigned_emp = emp_id
                                    break
                    if assigned_emp:
                        break
            
            # Si pas d'ouvrier assigné, chercher d'abord dans le champ, sinon à FARM
            if assigned_emp is None:
                # Chercher un employé déjà dans ce champ
                for emp in employees:
                    emp_id = emp.get("id")
                    if emp.get("location") == f"FIELD{field_num}" and emp.get("tractor") is None:
                        if emp_id in available_employees_any:
                            self._field_assignments[emp_id] = field_num
                            assigned_emp = emp_id
                            break
                # Sinon, prendre le premier disponible (FARM ou autre champ)
                if assigned_emp is None and available_employees_any:
                    emp_id = available_employees_any[0]
                    self._field_assignments[emp_id] = field_num
                    assigned_emp = emp_id
            
            if assigned_emp and assigned_emp in available_employees_any:
                commands.append(f"{assigned_emp} ARROSER {field_num}")
                if assigned_emp in available_employees_any:
                    available_employees_any.remove(assigned_emp)
                if assigned_emp in available_employees_farm:
                    available_employees_farm.remove(assigned_emp)
                print(f"  💧 ARROSER {veg} champ {field_num} (reste {water_needed}, ouvrier #{assigned_emp})")

        # ============================================================
        # PRIORITÉ 3 : RÉCOLTER (chaque ouvrier récolte son champ avec son tracteur!)
        # ============================================================
        fields_to_harvest = []
        for field in owned_fields:
            content = field.get("content", "NONE")
            needed_water = field.get("needed_water", 0)
            if content != "NONE" and needed_water == 0:
                location = field.get("location", "")
                if location.startswith("FIELD"):
                    field_num = int(location.replace("FIELD", ""))
                    fields_to_harvest.append((field_num, content))
        # Assigner 1 tracteur par ouvrier
        tractor_assignments: dict[int, int] = {}  # {emp_id: tractor_id}
        available_tractors = [
            t.get("id") for t in tractors
            if t.get("id") not in used_tractors
        ]
        
        # Assigner tracteurs aux ouvriers assignés
        for emp_id in self._field_assignments.keys():
            if available_tractors:
                tractor_id = available_tractors.pop(0)
                tractor_assignments[emp_id] = tractor_id
                used_tractors.add(tractor_id)
        
        # Récolter : chaque ouvrier STOCKER son champ avec son tracteur
        for field_num, veg in fields_to_harvest:
            # Trouver l'ouvrier assigné à ce champ
            assigned_emp = None
            for emp_id, assigned_field in self._field_assignments.items():
                if assigned_field == field_num:
                    # Vérifier si disponible : dans le champ OU à FARM (peut continuer)
                    for emp in employees:
                        emp_location = emp.get("location", "")
                        if emp.get("id") == emp_id and emp.get("tractor") is None:
                            # Peut être dans le champ correspondant OU à FARM
                            if emp_location == f"FIELD{field_num}" or emp_location == "FARM":
                                if emp_id in available_employees_any:
                                    assigned_emp = emp_id
                                    break
                    if assigned_emp:
                        break
            
            if assigned_emp and assigned_emp in available_employees_any:
                tractor_id = tractor_assignments.get(assigned_emp)
                if tractor_id:
                    commands.append(f"{assigned_emp} STOCKER {field_num} {tractor_id}")
                    if assigned_emp in available_employees_any:
                        available_employees_any.remove(assigned_emp)
                    if assigned_emp in available_employees_farm:
                        available_employees_farm.remove(assigned_emp)
                    print(f"  🌾 STOCKER {veg} champ {field_num} → +2000 stock (ouvrier #{assigned_emp}, tracteur {tractor_id})")
                else:
                    # Pas de tracteur pour cet ouvrier : VENDRE avec gérant
                    if self._day > self._gerant_busy_until and self._ventes_par_jour < 2:
                        commands.append(f"0 VENDRE {field_num}")
                        self._gerant_busy_until = self._day + 2
                        self._ventes_par_jour += 1
                        print(f"  💰 VENDRE {veg} champ {field_num} → ~3000€ (pas de tracteur, vente #{self._ventes_par_jour})")
                        if self._ventes_par_jour >= 2:
                            break

        # ============================================================
        # PRIORITÉ 4 : CUISINER (quand stock de chaque légume augmente!)
        # ============================================================
        # Vérifier que le stock de chaque légume augmente
        stock_par_legume = {
            "POTATO": stock.get("POTATO", 0),
            "LEEK": stock.get("LEEK", 0),
            "TOMATO": stock.get("TOMATO", 0),
            "ONION": stock.get("ONION", 0),
            "ZUCCHINI": stock.get("ZUCCHINI", 0),
        }
        
        # Afficher le stock pour voir la croissance
        if total_stock > 0:
            print(f"  📦 Stock actuel: P{stock_par_legume['POTATO']} L{stock_par_legume['LEEK']} T{stock_par_legume['TOMATO']} O{stock_par_legume['ONION']} Z{stock_par_legume['ZUCCHINI']} | Total: {total_stock}")
        
        # Cuisiner si : usine OK + stock > 500 + au moins 3 légumes différents
        # Production de soupes = revenus réguliers pour tenir 5 ans
        if factory_days_off == 0 and total_stock > 500:
            legumes_disponibles = sum(1 for v in stock_par_legume.values() if v >= 50)
            if legumes_disponibles >= 3 and available_employees_any:
                # Cuisiner avec 1 employé (production continue) - peut être à FARM ou dans champ
                emp_id = available_employees_any[0]
                commands.append(f"{emp_id} CUISINER")
                if emp_id in available_employees_any:
                    available_employees_any.remove(emp_id)
                if emp_id in available_employees_farm:
                    available_employees_farm.remove(emp_id)
                print(f"  🍲 CUISINER → Soupes (stock: P{stock_par_legume['POTATO']} L{stock_par_legume['LEEK']} T{stock_par_legume['TOMATO']} O{stock_par_legume['ONION']} Z{stock_par_legume['ZUCCHINI']})")
        
        # ============================================================
        # PRIORITÉ 5 : GESTION EMPLOYÉS (1 par champ + tracteurs)
        # ============================================================
        # Calculer jours de salaires restants
        total_salaries = sum(emp.get("salary", 0) for emp in employees)
        jours_salaires = money / total_salaries if total_salaries > 0 else 999
        
        # Objectif : 2 ouvriers par champ + 1 tracteur par champ
        # MAIS LIMITER pour tenir 5 ans (1825 jours) : max 3 champs, max 3 tracteurs
        nb_champs = len(owned_fields)
        nb_champs_max = min(nb_champs, 3)  # Max 3 champs pour sécurité financière
        nb_ouvriers_necessaires = nb_champs_max * 2  # 2 par champ pour rotation FARM
        nb_tracteurs_necessaires = min(nb_champs_max, 3)  # Max 3 tracteurs
        
        # SÉCURITÉ POUR 5 ANS : Buffer de 50 jours de salaires minimum
        buffer_securite = 50  # Jours de salaires en réserve
        
        # Acheter tracteur si besoin (1 par champ) MAIS avec buffer de sécurité élevé
        if (len(tractors) < nb_tracteurs_necessaires and 
            money > 50000 and 
            jours_salaires > buffer_securite and
            len(tractors) < 3):  # Max 3 tracteurs
            commands.append("0 ACHETER_TRACTEUR")
            print(f"  🚜 ACHETER_TRACTEUR ({len(tractors)+1}/{nb_tracteurs_necessaires} tracteurs, {jours_salaires:.0f}j sécurité)")
        
        # Acheter champ si capital TRÈS élevé ET buffer important
        if (money > 150000 and 
            len(owned_fields) < 3 and  # Max 3 champs pour sécurité
            jours_salaires > buffer_securite + 20):  # Buffer encore plus élevé
            commands.append("0 ACHETER_CHAMP")
            print(f"  🏞️ ACHETER_CHAMP ({len(owned_fields)+1}/3 champs, {jours_salaires:.0f}j sécurité)")
        
        # LICENCIER si capital critique (< 10 jours de salaires) ET trop d'employés
        if jours_salaires < 10 and len(employees) > nb_ouvriers_necessaires:
            # Licencier les employés en trop (les plus chers d'abord)
            employees_sorted = sorted(employees, key=lambda e: e.get("salary", 0), reverse=True)
            for emp in employees_sorted:
                if len(employees) <= nb_ouvriers_necessaires:
                    break
                emp_id = emp.get("id")
                if emp_id and emp_id > 0:  # Ne pas licencier le gérant
                    commands.append(f"0 LICENCIER {emp_id}")
                    # Retirer de l'assignation
                    if emp_id in self._field_assignments:
                        del self._field_assignments[emp_id]
                    print(f"  ⚠️ LICENCIER emp #{emp_id} (capital critique: {jours_salaires:.1f}j)")
                    break
        
        # Embaucher si besoin (1 par champ) ET capital TRÈS confortable
        if (len(employees) < nb_ouvriers_necessaires and 
            jours_salaires > buffer_securite and 
            money > 50000):
            commands.append("0 EMPLOYER")
            print(f"  👤 EMPLOYER ({len(employees)+1}/{nb_ouvriers_necessaires} ouvriers, {jours_salaires:.0f}j sécurité)")

        return commands

    def _initial_setup(self, day: int) -> list[str]:
        """Setup STRUCTURÉ : 2 champs, 4 ouvriers (2 par champ), 2 tracteurs."""
        commands: list[str] = []

        if day == 1:
            # Jour 1 : Acheter 2 champs + 2 tracteurs
            # 1 tracteur par champ = récolte optimale
            for _ in range(2):
                commands.append("0 ACHETER_CHAMP")
            for _ in range(2):
                commands.append("0 ACHETER_TRACTEUR")
            print("  🎬 SETUP J1: 2 champs + 2 tracteurs (1 tracteur/champ)")

        elif day == 2:
            # Jour 2 : Embaucher 4 ouvriers (2 par champ)
            # Avec 2 ouvriers par champ, il y en a toujours 1 à FARM pendant que l'autre travaille
            for _ in range(4):
                commands.append("0 EMPLOYER")
            print("  🎬 SETUP J2: 4 ouvriers (2 ouvriers/champ pour rotation FARM)")

        return commands

    def _get_planting_priority(
        self,
        stock: dict[str, int],
        fields: list[dict[str, Any]]
    ) -> list[str]:
        """
        Détermine l'ordre de semis selon ce qui manque.

        Retourne une liste de légumes français ordonnés par priorité.
        """
        # Mapper stock anglais → légumes français
        veg_count = {
            "PATATE": stock.get("POTATO", 0),
            "POIREAU": stock.get("LEEK", 0),
            "TOMATE": stock.get("TOMATO", 0),
            "OIGNON": stock.get("ONION", 0),
            "COURGETTE": stock.get("ZUCCHINI", 0),
        }

        # Compter les légumes en croissance
        for field in fields:
            content = field.get("content", "NONE")
            if content in ["POTATO", "LEEK", "TOMATO", "ONION", "ZUCCHINI"]:
                veg_fr_map = {
                    "POTATO": "PATATE",
                    "LEEK": "POIREAU",
                    "TOMATO": "TOMATE",
                    "ONION": "OIGNON",
                    "ZUCCHINI": "COURGETTE",
                }
                veg_fr = veg_fr_map[content]
                veg_count[veg_fr] += 1

        # Trier par rareté (les plus rares en premier)
        sorted_veggies = sorted(veg_count.items(), key=lambda x: (x[1], x[0]))
        return [veg for veg, _ in sorted_veggies]
