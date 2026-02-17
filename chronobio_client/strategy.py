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
        # Tracking des actions en cours pour éviter ALREADY_BUSY
        self._last_actions: dict[int, str] = {}  # {emp_id: "SEMER 2"} pour tracker les actions en cours
        # Tracteurs en cours de STOCKER (multi-jour) → ne pas réassigner avant fin
        self._stocker_tractors: dict[int, int] = {}  # {emp_id: tractor_id}

    def get_actions(self, farm: dict[str, Any]) -> list[str]:
        """
        Génère les actions pour un tour selon la stratégie PROGRESSIVE.

        PRIORITÉS:
        1. RÉCOLTER + STOCKER (champs mûrs d'abord → stock + diversité)
        2. SEMER (ouvriers depuis FARM ou FIELD — le gérant ne sème pas)
        3. ARROSER (faire pousser les cultures)
        4. CUISINER (soupes 3+ variétés ; mode survie 1 variété si < 15j salaires)
        5. EXPANSION + EMPRUNTER si < 5j salaires
        """
        self._day += 1
        self._ventes_par_jour = 0  # Reset compteur ventes
        commands: list[str] = []

        # Récupérer les données de la ferme (nécessaire pour le nettoyage)
        money = farm.get("money", 0)
        fields = farm.get("fields", [])
        employees = farm.get("employees", [])
        
        # Nettoyer les actions terminées (utilise fields et employees)
        actions_to_remove = []
        for emp_id, action in self._last_actions.items():
            emp = next((e for e in employees if e.get("id") == emp_id), None)
            if not emp:
                continue
            emp_loc = emp.get("location", "")
            
            if action.startswith("SEMER"):
                # Pour SEMER, vérifier si l'employé est dans le champ cible
                if emp_id in self._field_assignments:
                    assigned_field = self._field_assignments[emp_id]
                    target_loc = f"FIELD{assigned_field}"
                    # Si l'employé est arrivé dans le champ, l'action SEMER est terminée
                    if emp_loc == target_loc:
                        actions_to_remove.append(emp_id)
            elif action.startswith("ARROSER"):
                # ARROSER : nettoyer seulement si l'employé est dans le bon champ OU à FARM
                # Si l'employé est dans un autre champ, il est peut-être en transit → garder l'action
                field_num = int(action.split()[1])
                target_loc = f"FIELD{field_num}"
                if emp_loc == target_loc:
                    # L'employé est dans le bon champ → action ARROSER terminée
                    actions_to_remove.append(emp_id)
                elif emp_loc == "FARM":
                    # L'employé est à FARM → action ARROSER terminée (peut avoir fini et être revenu)
                    actions_to_remove.append(emp_id)
                # Si l'employé est dans un autre champ, garder l'action (en transit)
            elif action.startswith("CUISINER"):
                # CUISINER : action instantanée, terminée dès que l'employé quitte SOUP_FACTORY
                # Si l'employé reste à SOUP_FACTORY, il peut cuisiner à nouveau immédiatement
                # Nettoyer dès qu'il quitte SOUP_FACTORY pour éviter les conflits
                if emp_loc != "SOUP_FACTORY":
                    # L'employé a quitté SOUP_FACTORY → action CUISINER terminée, nettoyer
                    actions_to_remove.append(emp_id)
                # Si l'employé est toujours à SOUP_FACTORY, on garde l'action mais on permet de cuisiner à nouveau
                # (action instantanée, peut être répétée le même jour)
            elif action.startswith("STOCKER"):
                # STOCKER est multi-jour : terminé quand l'employé est à FARM et a rendu le tracteur
                emp_tractor = emp.get("tractor") if isinstance(emp, dict) else None
                if emp_loc == "FARM" and not emp_tractor:
                    actions_to_remove.append(emp_id)
                    if emp_id in self._stocker_tractors:
                        del self._stocker_tractors[emp_id]
        for emp_id in actions_to_remove:
            del self._last_actions[emp_id]
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

        # Identifier les tracteurs déjà utilisés (état actuel + STOCKER en cours)
        for emp in employees:
            tractor = emp.get("tractor")
            if tractor is not None:
                tid = tractor.get("id") if isinstance(tractor, dict) else (tractor if isinstance(tractor, int) else None)
                if tid is not None:
                    used_tractors.add(tid)
        for emp_id, act in self._last_actions.items():
            if act.startswith("STOCKER") and emp_id in self._stocker_tractors:
                used_tractors.add(self._stocker_tractors[emp_id])

        # DISPONIBILITÉ : FARM (priorité) OU dans champ sans tracteur (continuation)
        # Un employé à FARM peut tout faire (SEMER, ARROSER, RÉCOLTER)
        # Un employé dans un champ peut continuer (ARROSER, RÉCOLTER) depuis sa position
        # IMPORTANT : Exclure les employés qui viennent de recevoir une action (en transit)
        available_employees_farm = []  # Pour SEMER (priorité absolue)
        available_employees_any = []   # Pour ARROSER/RÉCOLTER (peuvent être dans champs)
        at_farm = 0
        in_fields = 0
        
        for emp in employees:
            emp_id = emp.get("id")
            location = emp.get("location", "")
            tractor = emp.get("tractor")
            
            # Vérifier si l'employé est occupé (en transit ou action en cours)
            is_busy = False
            
            # 1) Vérifier si l'employé a une action CUISINER en cours
            # CUISINER est une action instantanée : si l'employé est à SOUP_FACTORY, il peut cuisiner à nouveau
            # Il est occupé seulement s'il est en transit (pas encore à SOUP_FACTORY)
            if emp_id in self._last_actions and self._last_actions[emp_id].startswith("CUISINER"):
                if location == "SOUP_FACTORY":
                    # À SOUP_FACTORY → action précédente terminée (instantanée), peut cuisiner à nouveau
                    # Ne pas marquer comme occupé
                    pass
                elif location != "SOUP_FACTORY":
                    # L'employé a quitté SOUP_FACTORY → action CUISINER terminée
                    # Mais s'il est dans un champ invalide (FIELD3), il est peut-être en transit
                    # Pour sécurité, on le considère comme occupé seulement s'il est vraiment en transit
                    # (pas à FARM et pas dans un champ valide)
                    if location != "FARM":
                        field_exists = False
                        if location.startswith("FIELD"):
                            field_exists = any(
                                f.get("location", "") == location and f.get("bought", False)
                                for f in fields
                            )
                        if not field_exists:
                            # L'employé est dans un lieu invalide ou en transit → occupé
                            is_busy = True
                    # Si à FARM ou dans un champ valide, l'action est terminée (nettoyée plus tôt)
            
            # 2) Vérifier si l'employé a une action ARROSER en cours sur un autre champ
            if not is_busy and emp_id in self._last_actions:
                action = self._last_actions[emp_id]
                if action.startswith("ARROSER"):
                    action_field_num = int(action.split()[1])
                    action_target = f"FIELD{action_field_num}"
                    # Si l'employé arrose un champ mais n'est pas dans ce champ, il est en transit ou occupé
                    if location != action_target and location != "FARM":
                        # L'employé est en transit vers le champ à arroser → occupé
                        is_busy = True
                    elif location == action_target:
                        # L'employé est dans le bon champ → action terminée (sera nettoyée)
                        pass
                    # Si à FARM, l'action est terminée (sera nettoyée)
            
            # 3) Vérifier si l'employé est en transit vers un champ (SEMER)
            if not is_busy and emp_id in self._field_assignments:
                assigned_field = self._field_assignments[emp_id]
                target_loc = f"FIELD{assigned_field}"
                # Si l'employé est assigné à un champ mais n'est pas encore dedans ET n'est pas à FARM, il est en transit
                if location != target_loc and location != "FARM" and emp_id in self._last_actions:
                    action = self._last_actions[emp_id]
                    if action.startswith("SEMER"):
                        # L'employé a reçu une action SEMER récente et n'est pas encore arrivé → occupé
                        is_busy = True
            
            # 4) STOCKER est multi-jour : ne pas réassigner tant que l'employé n'est pas revenu à FARM
            if not is_busy and emp_id in self._last_actions and self._last_actions[emp_id].startswith("STOCKER"):
                is_busy = True
            
            if not is_busy:
                if location == "FARM" and tractor is None:
                    at_farm += 1
                    available_employees_farm.append(emp_id)
                    available_employees_any.append(emp_id)
                elif location.startswith("FIELD") and tractor is None:
                    in_fields += 1
                    available_employees_any.append(emp_id)  # Peut continuer dans son champ
                elif location == "SOUP_FACTORY":
                    # Employé à SOUP_FACTORY → peut cuisiner (CUISINER libère automatiquement le tracteur)
                    # Même avec tracteur, CUISINER est possible (le jeu libère le tracteur automatiquement)
                    available_employees_any.append(emp_id)
        
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

        # Initialiser assignations ouvrier → champ (avant RÉCOLTER et SEMER)
        if not self._field_assignments and len(owned_fields) > 0:
            field_nums = []
            for field in owned_fields:
                loc = field.get("location", "")
                if loc.startswith("FIELD"):
                    field_nums.append(int(loc.replace("FIELD", "")))
            for i, emp in enumerate(employees):
                fi = i // 2
                if fi < len(field_nums):
                    self._field_assignments[emp.get("id")] = field_nums[fi]

        # ============================================================
        # PRIORITÉ 1 : RÉCOLTER (champs mûrs d'abord → stock + libère ouvriers)
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
        # Assigner 1 tracteur par ouvrier DISPONIBLE (exclure SOUP_FACTORY / occupés)
        tractor_assignments: dict[int, int] = {}
        available_tractors = [
            t.get("id") for t in tractors
            if t.get("id") not in used_tractors
        ]
        for emp_id in self._field_assignments.keys():
            if emp_id in available_employees_any and available_tractors:
                tractor_id = available_tractors.pop(0)
                tractor_assignments[emp_id] = tractor_id
                used_tractors.add(tractor_id)

        for field_num, veg in fields_to_harvest:
            assigned_emp = None
            for emp_id, assigned_field in self._field_assignments.items():
                if assigned_field == field_num:
                    for emp in employees:
                        emp_location = emp.get("location", "")
                        if emp.get("id") == emp_id and emp.get("tractor") is None:
                            if emp_location == f"FIELD{field_num}" or emp_location == "FARM":
                                if emp_id in available_employees_any:
                                    assigned_emp = emp_id
                                    break
                    if assigned_emp:
                        break

            if assigned_emp is None:
                for emp in employees:
                    emp_id = emp.get("id")
                    if emp.get("location") == f"FIELD{field_num}" and emp.get("tractor") is None:
                        if emp_id in available_employees_any:
                            self._field_assignments[emp_id] = field_num
                            assigned_emp = emp_id
                            break
                if assigned_emp is None and available_employees_any:
                    emp_id = available_employees_any[0]
                    self._field_assignments[emp_id] = field_num
                    assigned_emp = emp_id

            if assigned_emp and assigned_emp in available_employees_any:
                tractor_id = tractor_assignments.get(assigned_emp)
                if tractor_id:
                    commands.append(f"{assigned_emp} STOCKER {field_num} {tractor_id}")
                    self._last_actions[assigned_emp] = f"STOCKER {field_num}"  # Multi-jour : ne pas réassigner avant fin
                    self._stocker_tractors[assigned_emp] = tractor_id  # Tracteur occupé jusqu'à fin STOCKER
                    if assigned_emp in available_employees_any:
                        available_employees_any.remove(assigned_emp)
                    if assigned_emp in available_employees_farm:
                        available_employees_farm.remove(assigned_emp)
                    print(f"  🌾 STOCKER {veg} champ {field_num} → +2000 stock (ouvrier #{assigned_emp}, tracteur {tractor_id})")
                else:
                    gerant_deja_utilise = any(c.startswith("0 ") for c in commands)
                    if (not gerant_deja_utilise and self._day > self._gerant_busy_until and self._ventes_par_jour < 2):
                        commands.append(f"0 VENDRE {field_num}")
                        self._gerant_busy_until = self._day + 2
                        self._ventes_par_jour += 1
                        print(f"  💰 VENDRE {veg} champ {field_num} → ~3000€ (pas de tracteur, vente #{self._ventes_par_jour})")
                        if self._ventes_par_jour >= 2:
                            break

        # ============================================================
        # PRIORITÉ 2 : SEMER (ouvriers uniquement — gérant = vente seulement)
        # Règle: le jeu permet SEMER depuis toute position (l'ouvrier rejoint le champ).
        # On utilise available_employees_any (FARM ou FIELD) — pas seulement FARM.
        # ============================================================
        fields_to_plant = []
        for field in owned_fields:
            if field.get("content") == "NONE":
                location = field.get("location", "")
                if location.startswith("FIELD"):
                    field_num = int(location.replace("FIELD", ""))
                    fields_to_plant.append(field_num)
        
        if fields_to_plant:
            print(f"  🌾 Champs vides à semer: {fields_to_plant}")
        
        # Priorité: semer les légumes les plus RARES en stock pour avoir les 5 variétés (soupe)
        plantation_priorite = self._get_planting_priority(stock, fields)

        # Semer : OUVRIERS (id>0) depuis FARM ou FIELD — le gérant ne sème pas.
        # Préférer l'ouvrier déjà dans ce champ (gain de temps).
        # Éviter de réassigner un ouvrier déjà assigné à un autre champ.
        for i, field_num in enumerate(fields_to_plant):
            assigned_emp = None
            target_loc = f"FIELD{field_num}"
            # 1) Ouvrier assigné à ce champ ET déjà dans ce champ ET dispo
            for emp_id, assigned_field in self._field_assignments.items():
                if assigned_field == field_num and emp_id and emp_id in available_employees_any:
                    emp_loc = next((e.get("location", "") for e in employees if e.get("id") == emp_id), "")
                    if emp_loc == target_loc:
                        assigned_emp = emp_id
                        break
            # 2) Sinon, ouvrier assigné à ce champ (FARM ou autre) ET dispo
            if assigned_emp is None:
                for emp_id, assigned_field in self._field_assignments.items():
                    if assigned_field == field_num and emp_id and emp_id in available_employees_any:
                        assigned_emp = emp_id
                        break
            # 3) Sinon, premier ouvrier dispo NON assigné (jamais le gérant 0)
            if assigned_emp is None and available_employees_any:
                for emp_id in available_employees_any:
                    if emp_id and emp_id != 0:
                        # Ne pas réassigner un ouvrier déjà assigné à un autre champ
                        if emp_id not in self._field_assignments:
                            self._field_assignments[emp_id] = field_num
                            assigned_emp = emp_id
                            break
            # 4) Dernier recours : réassigner un ouvrier libre (si vraiment nécessaire)
            # Permettre de réassigner pour assurer la rotation des semences
            if assigned_emp is None and available_employees_any:
                for emp_id in available_employees_any:
                    if emp_id and emp_id != 0:
                        # Réassigner si l'ouvrier est disponible (peut semer depuis n'importe où)
                        # Le jeu permet SEMER depuis toute position
                        self._field_assignments[emp_id] = field_num
                        assigned_emp = emp_id
                        break

            if assigned_emp is not None:
                veg = plantation_priorite[i % len(plantation_priorite)]
                commands.append(f"{assigned_emp} SEMER {veg} {field_num}")
                # Tracker cette action pour éviter de réassigner l'employé trop tôt
                self._last_actions[assigned_emp] = f"SEMER {field_num}"
                if assigned_emp in available_employees_farm:
                    available_employees_farm.remove(assigned_emp)
                if assigned_emp in available_employees_any:
                    available_employees_any.remove(assigned_emp)
                print(f"  🌱 SEMER {veg} champ {field_num} (ouvrier #{assigned_emp}, priorité diversité)")
            else:
                print(f"  ⚠️ Aucun ouvrier dispo → skip SEMER champ {field_num}")

        # ============================================================
        # PRIORITÉ 3 : ARROSER (chaque ouvrier arrose son champ!)
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
                    # ET pas déjà en train d'arroser un autre champ
                    for emp in employees:
                        emp_location = emp.get("location", "")
                        if emp.get("id") == emp_id and emp.get("tractor") is None:
                            # Vérifier qu'il n'a pas déjà une action ARROSER sur un autre champ
                            has_other_water_action = False
                            if emp_id in self._last_actions:
                                action = self._last_actions[emp_id]
                                if action.startswith("ARROSER"):
                                    action_field = int(action.split()[1])
                                    if action_field != field_num:
                                        has_other_water_action = True
                            if not has_other_water_action:
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
                        # Vérifier qu'il n'a pas déjà une action ARROSER sur un autre champ
                        has_other_water_action = False
                        if emp_id in self._last_actions:
                            action = self._last_actions[emp_id]
                            if action.startswith("ARROSER"):
                                action_field = int(action.split()[1])
                                if action_field != field_num:
                                    has_other_water_action = True
                        if not has_other_water_action and emp_id in available_employees_any:
                            self._field_assignments[emp_id] = field_num
                            assigned_emp = emp_id
                            break
                # Sinon, prendre le premier disponible (FARM ou autre champ) sans action ARROSER en cours
                if assigned_emp is None and available_employees_any:
                    for emp_id in available_employees_any:
                        # Vérifier qu'il n'a pas déjà une action ARROSER en cours
                        has_water_action = False
                        if emp_id in self._last_actions:
                            action = self._last_actions[emp_id]
                            if action.startswith("ARROSER"):
                                has_water_action = True
                        if not has_water_action:
                            self._field_assignments[emp_id] = field_num
                            assigned_emp = emp_id
                            break
            
            if assigned_emp and assigned_emp in available_employees_any:
                commands.append(f"{assigned_emp} ARROSER {field_num}")
                # Tracker cette action (ARROSER est instantané si l'employé est déjà dans le champ)
                self._last_actions[assigned_emp] = f"ARROSER {field_num}"
                if assigned_emp in available_employees_any:
                    available_employees_any.remove(assigned_emp)
                if assigned_emp in available_employees_farm:
                    available_employees_farm.remove(assigned_emp)
                print(f"  💧 ARROSER {veg} champ {field_num} (reste {water_needed}, ouvrier #{assigned_emp})")

        # ============================================================
        # PRIORITÉ 4 : CUISINER (MAXIMISER la production de soupes pour revenus!)
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
        
        # Soupe : 3+ variétés (30+ chacune) en normal ; mode SURVIE si jours_salaires < 15 :
        # 1 variété (≥100) suffit pour encaisser ~100€/cuisinier. Uniquement OUVRIERS (gérant = vente).
        # CUISINER même avec 1 variété si stock élevé pour maximiser les revenus.
        legumes_30 = sum(1 for v in stock_par_legume.values() if v >= 30)
        max_veg = max(stock_par_legume.values()) if stock_par_legume else 0
        can_cook_normal = factory_days_off == 0 and total_stock > 300 and legumes_30 >= 3
        can_cook_survival = (
            factory_days_off == 0
            and total_stock >= 100
            and max_veg >= 100
            and (jours_salaires < 15 or money < total_salaries * 5)
        )
        # Mode production : cuisiner avec 1 variété si stock élevé (≥1000) pour revenus réguliers
        can_cook_production = (
            factory_days_off == 0
            and total_stock >= 1000
            and max_veg >= 100
            and legumes_30 < 3  # Pas assez de variétés pour mode normal
        )
        if (can_cook_normal or can_cook_survival or can_cook_production) and available_employees_any:
            # Filtrer les employés disponibles pour cuisiner
            # CUISINER nécessite d'être à SOUP_FACTORY (action instantanée, peut être répétée)
            available_for_cooking = []
            for emp_id in available_employees_any:
                emp = next((e for e in employees if e.get("id") == emp_id), None)
                if not emp:
                    continue
                emp_loc = emp.get("location", "")
                
                # CUISINER nécessite d'être à SOUP_FACTORY (le tracteur est libéré automatiquement par le jeu)
                if emp_loc == "SOUP_FACTORY":
                    # À SOUP_FACTORY → peut cuisiner (action instantanée, peut être répétée même avec CUISINER dans _last_actions)
                    # Le tracteur est libéré automatiquement lors de CUISINER selon les règles du jeu
                    available_for_cooking.append(emp_id)
                # Ne pas permettre CUISINER depuis d'autres locations (même si l'employé est disponible)
            cuisiniers_max = min(3, len(available_for_cooking))
            for _ in range(cuisiniers_max):
                if available_for_cooking:
                    emp_id = available_for_cooking[0]
                    # Vérification finale : l'employé doit être à SOUP_FACTORY pour cuisiner
                    emp = next((e for e in employees if e.get("id") == emp_id), None)
                    if emp and emp.get("location") == "SOUP_FACTORY":
                        commands.append(f"{emp_id} CUISINER")
                        # Tracker cette action CUISINER
                        self._last_actions[emp_id] = "CUISINER"
                        available_employees_any.remove(emp_id)
                        if emp_id in available_employees_farm:
                            available_employees_farm.remove(emp_id)
                    available_for_cooking.remove(emp_id)
            if can_cook_normal:
                mode = "soupes"
            elif can_cook_survival:
                mode = "survie (1+ variétés)"
            else:
                mode = "production (1 variété)"
            if cuisiniers_max > 0:
                print(f"  🍲 CUISINER ×{cuisiniers_max} → {mode} (P{stock_par_legume['POTATO']} L{stock_par_legume['LEEK']} T{stock_par_legume['TOMATO']} O{stock_par_legume['ONION']} Z{stock_par_legume['ZUCCHINI']}) → +revenus")
        
        # ============================================================
        # PRIORITÉ 5 : INVESTISSEMENT (1 seule action GÉRANT/jour! VENDRE/EMPRUNTER/ACHETER/EMPLOYER/LICENCIER)
        # Le gérant reste "busy" pendant 2j après un VENDRE → ne pas envoyer EMPLOYER/ACHETER tant qu'il n'est pas libre.
        # ============================================================
        gerant_utilise = any(c.startswith("0 ") for c in commands)
        gerant_libre_periode = self._day > self._gerant_busy_until  # Pas en plein VENDRE multi-jour
        total_salaries = sum(emp.get("salary", 0) for emp in employees)
        jours_salaires = money / total_salaries if total_salaries > 0 else 999
        loans = farm.get("loans", [])
        
        # Objectif : MAXIMISER la production = plus de champs + plus de tracteurs + plus d'ouvriers
        nb_champs = len(owned_fields)
        nb_champs_max = min(nb_champs, 5)
        nb_ouvriers_necessaires = nb_champs_max * 2
        nb_tracteurs_necessaires = nb_champs_max
        buffer_securite = 30
        
        # LICENCIER en priorité si survie et trop d'ouvriers (1 seul/jour, gérant)
        if (not gerant_utilise and gerant_libre_periode and jours_salaires < 5 and len(employees) > nb_ouvriers_necessaires):
            employees_sorted = sorted(employees, key=lambda e: e.get("salary", 0), reverse=True)
            for emp in employees_sorted:
                if len(employees) <= nb_ouvriers_necessaires:
                    break
                emp_id = emp.get("id")
                if emp_id and emp_id > 0:
                    commands.append(f"0 LICENCIER {emp_id}")
                    if emp_id in self._field_assignments:
                        del self._field_assignments[emp_id]
                    print(f"  ⚠️ LICENCIER emp #{emp_id} (capital critique: {jours_salaires:.1f}j)")
                break

        # Recalculer si le gérant a été utilisé (ex. LICENCIER ou VENDRE avant)
        gerant_utilise = any(c.startswith("0 ") for c in commands)

        # EMPRUNTER en urgence si < 5j salaires et pas pu LICENCIER (éviter la faillite)
        if not gerant_utilise and gerant_libre_periode and jours_salaires < 5 and len(loans) < 10:
            commands.append("0 EMPRUNTER 50000")
            gerant_utilise = True
            print(f"  🏦 EMPRUNTER 50000 (survie: {jours_salaires:.1f}j salaires)")

        # Une seule expansion/jour : tracteur > champ > embauche (si gérant libre et pas en période VENDRE)
        if (not gerant_utilise and gerant_libre_periode and len(tractors) < nb_tracteurs_necessaires and
            money > 35000 and jours_salaires > buffer_securite and len(tractors) < 5):
            commands.append("0 ACHETER_TRACTEUR")
            print(f"  🚜 ACHETER_TRACTEUR ({len(tractors)+1}/{nb_tracteurs_necessaires} tracteurs, {jours_salaires:.0f}j) → +stock")
        elif (not gerant_utilise and gerant_libre_periode and money > 80000 and len(owned_fields) < 5 and jours_salaires > buffer_securite + 10):
            commands.append("0 ACHETER_CHAMP")
            print(f"  🏞️ ACHETER_CHAMP ({len(owned_fields)+1}/5 champs, {jours_salaires:.0f}j) → +production")
        elif (not gerant_utilise and gerant_libre_periode and len(employees) < nb_ouvriers_necessaires and jours_salaires > buffer_securite and money > 30000):
            commands.append("0 EMPLOYER")
            print(f"  👤 EMPLOYER ({len(employees)+1}/{nb_ouvriers_necessaires} ouvriers, {jours_salaires:.0f}j) → +actions/jour")

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
