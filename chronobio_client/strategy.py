"""Stratégie de jeu STABLE - Rotation et Production Progressive."""

from typing import Any

# Légumes disponibles dans le jeu - rotation complète
VEGETABLES = ["COURGETTE", "TOMATE", "PATATE", "POIREAU", "OIGNON"]

# Coûts
FIELD_COST = 10000
TRACTOR_COST = 30000
EMPLOYEE_BASE_SALARY = 1000

# Configuration STABLE
MAX_EMPLOYEES = 8       # Objectif réaliste
MAX_TRACTORS = 3
MAX_FIELDS = 5
MIN_STOCK_TO_COOK = 20  # Cuisine avec stock suffisant
MIN_DIVERSITY = 3       # 3 légumes de chaque type minimum
MAX_COOKS = 4           # 4 cuisiniers max en parallèle

# Buffer de sécurité: 30 jours de salaires
SAFETY_BUFFER_DAYS = 30


class Strategy:
    """Stratégie PROGRESSIVE RÉALISTE - Production garantie avec expansion contrôlée."""

    def __init__(self) -> None:
        """Initialise la stratégie."""
        self.turn_count = 0
        self.vegetable_index = 0

    def get_actions(self, farm_data: dict[str, Any]) -> list[str]:
        """
        Génère les actions pour ce tour.

        Stratégie STABLE - Rotation et Production Progressive:
        
        Stratégie RADICALE - 0 OUVRIER (test gérant):
        - Jour 0: 3 CHAMPS + 1 TRACTEUR + 0 OUVRIER (dépense: 60k)
                  → Reste: 40k EUR
                  → Salaires: 0 EUR/jour (gérant gratuit!)
                  → Buffer: INFINI ✅
        - DIAGNOSTIC: Bloque J3 même avec 20j buffer!
          → Le jeu exige probablement ~4-5M EUR pour couvrir
             TOUS les salaires jusqu'à J1799!
        - SOLUTION: 0 ouvrier = 0 salaires = pas de blocage!
        - TEST: Le GÉRANT peut-il faire les actions de base?
        - Expansion: Embaucher APRÈS avoir accumulé du capital
        
        Production continue:
        - Rotation complète: COURGETTE → TOMATE → PATATE → POIREAU → OIGNON
        - Arrosage prioritaire
        - Stockage dès que champ prêt (avec tracteur)
        - Cuisine dès 20 légumes + 3 de chaque type
        
        Règle d'or: JAMAIS investir si buffer < 30 jours de salaires!
        
        PRIORITÉ: Stabilité → Rotation → Production soupes
        """
        self.turn_count += 1
        actions: list[str] = []

        # Extraire les données
        money = farm_data.get("money", 0)
        employees = farm_data.get("employees", [])
        fields = [f for f in farm_data.get("fields", []) if f.get("bought", False)]
        tractors = farm_data.get("tractors", [])
        stock = farm_data.get("soup_factory", {}).get("stock", {})
        factory_days_off = farm_data.get("soup_factory", {}).get("days_off", 0)

        # Métriques
        num_employees = len(employees)
        num_tractors = len(tractors)
        num_fields = len(fields)
        total_salaries = sum(emp.get("salary", 0) for emp in employees)
        
        # Buffer de sécurité: 30 jours de salaires
        safety_buffer = total_salaries * SAFETY_BUFFER_DAYS

        # Tracker
        used_employees: set[int] = set()
        used_tractors: set[int] = set()

        # === SOLUTION RADICALE: 0 OUVRIER AU DÉPART ===

        # DIAGNOSTIC: Bloque J3 avec 20j buffer + 2 ouvriers!
        # Le jeu exige probablement de couvrir TOUS les salaires
        # jusqu'à J1799 (~4-5M EUR) → IMPOSSIBLE!
        
        # SOLUTION: Commencer avec 0 OUVRIER
        # Test: Le GÉRANT (ID 0) peut-il semer/arroser seul?
        
        # Jour 0: 3 champs + 1 tracteur + 0 OUVRIER
        # Capital: 100k EUR
        # Dépenses: 30k (3 champs) + 30k (tracteur) = 60k
        # Reste: 40k EUR
        # Salaires: 0 EUR/jour (gérant gratuit!)
        # Buffer: INFINI (pas de salaires!)
        if self.turn_count == 1:
            # 3 champs
            for _ in range(3):
                actions.append("0 ACHETER_CHAMP")
            # 1 TRACTEUR
            actions.append("0 ACHETER_TRACTEUR")
            # 0 OUVRIER pour commencer (test gérant!)
        
        # Jour 30: Embaucher 1er ouvrier si revenus > 50k EUR
        elif self.turn_count == 31 and num_employees < 1 and money > 60000 or self.turn_count == 16 and num_employees < 3 and money > safety_buffer + 10000 or self.turn_count == 31 and num_employees < 4 and money > safety_buffer + 10000:
            actions.append("0 EMPLOYER")

        # Jour 50: 2ème tracteur
        elif self.turn_count == 51 and num_tractors < 2 and money > safety_buffer + 35000:
            actions.append("0 ACHETER_TRACTEUR")

        # Jour 50+: Expansion progressive SEULEMENT si buffer suffisant
        elif self.turn_count >= 51:
            if num_fields < 5 and money > safety_buffer + 20000:
                actions.append("0 ACHETER_CHAMP")
            elif num_employees < 6 and num_fields >= 4 and money > safety_buffer + 20000:
                actions.append("0 EMPLOYER")
            elif num_tractors < 2 and num_employees >= 4 and money > safety_buffer + 40000:
                actions.append("0 ACHETER_TRACTEUR")
            elif num_employees < MAX_EMPLOYEES and num_tractors >= 2 and money > safety_buffer + 25000:
                actions.append("0 EMPLOYER")

        # === PRODUCTION: STRATÉGIE HYBRIDE ===
        # Phase 1 (Jours 1-90): VENDRE les légumes pour revenus immédiats
        # Phase 2 (Jours 90+): STOCKER + CUISINER pour revenus maximaux
        
        # === PRODUCTION: Stockage et Cuisine ===
        
        # Récolter les champs prêts (avec tracteur)
        harvest_actions = self._harvest_fields(fields, employees, tractors, used_employees, used_tractors)
        actions.extend(harvest_actions)

        # Cuisiner des soupes si stock suffisant
        cook_actions = self._cook_soups(stock, factory_days_off, employees, used_employees)
        actions.extend(cook_actions)

        # TOUJOURS: Arroser et semer
        water_actions = self._water_fields(fields, employees, used_employees)
        actions.extend(water_actions)

        sow_actions = self._sow_fields(fields, employees, used_employees)
        actions.extend(sow_actions)

        return actions

    def _harvest_fields(
        self,
        fields: list[dict[str, Any]],
        employees: list[dict[str, Any]],
        tractors: list[dict[str, Any]],
        used_employees: set[int],
        used_tractors: set[int],
    ) -> list[str]:
        """Récolte tous les champs prêts avec des tracteurs (Phase 2)."""
        actions: list[str] = []

        harvestable = [
            f for f in fields
            if f.get("content") not in ["NONE", None] and f.get("needed_water", 0) == 0
        ]

        used_tractor_ids = set()
        for emp in employees:
            tractor = emp.get("tractor")
            if tractor is not None and isinstance(tractor, dict):
                tractor_id = tractor.get("id")
                if tractor_id is not None:
                    used_tractor_ids.add(tractor_id)

        available_tractors = [
            t for t in tractors
            if t.get("id") not in used_tractors and t.get("id") not in used_tractor_ids
        ]

        available_employees = [
            emp for emp in employees
            if emp.get("id") not in used_employees and emp.get("tractor") is None
        ]

        for field in harvestable:
            if not available_employees or not available_tractors:
                break

            emp = available_employees.pop(0)
            tractor = available_tractors.pop(0)
            field_location = field.get("location", "")

            if field_location.startswith("FIELD"):
                field_num = field_location.replace("FIELD", "")
                actions.append(f"{emp['id']} STOCKER {field_num} {tractor['id']}")
                used_employees.add(emp["id"])
                used_tractors.add(tractor["id"])

        return actions

    def _cook_soups(
        self,
        stock: dict[str, int],
        factory_days_off: int,
        employees: list[dict[str, Any]],
        used_employees: set[int],
    ) -> list[str]:
        """Cuisine des soupes avec diversité requise."""
        actions: list[str] = []

        if factory_days_off > 0:
            return actions

        total_stock = sum(stock.values())
        if total_stock < MIN_STOCK_TO_COOK:
            return actions

        # Vérifier diversité (3 par légume minimum)
        has_diversity = all(
            stock.get(veg, 0) >= MIN_DIVERSITY
            for veg in ["POTATO", "LEEK", "TOMATO", "ONION", "ZUCCHINI"]
        )

        if not has_diversity:
            return actions

        available_employees = [
            emp for emp in employees
            if emp.get("id") not in used_employees and emp.get("tractor") is None
        ]

        # Utiliser jusqu'à MAX_COOKS cuisiniers (production élevée sans surcharge)
        cooks_count = min(MAX_COOKS, len(available_employees))

        for i in range(cooks_count):
            if i < len(available_employees):
                emp = available_employees[i]
                actions.append(f"{emp['id']} CUISINER")
                used_employees.add(emp["id"])

        return actions

    def _water_fields(
        self,
        fields: list[dict[str, Any]],
        employees: list[dict[str, Any]],
        used_employees: set[int],
    ) -> list[str]:
        """Arrose les champs qui en ont besoin."""
        actions: list[str] = []

        fields_to_water = [
            f for f in fields
            if f.get("content") not in ["NONE", None] and f.get("needed_water", 0) > 0
        ]

        fields_to_water.sort(key=lambda f: f.get("needed_water", 999))

        available_employees = [
            emp for emp in employees
            if emp.get("id") not in used_employees and emp.get("tractor") is None
        ]

        for field in fields_to_water:
            if not available_employees:
                break

            emp = available_employees.pop(0)
            field_location = field.get("location", "")

            if field_location.startswith("FIELD"):
                field_num = field_location.replace("FIELD", "")
                actions.append(f"{emp['id']} ARROSER {field_num}")
                used_employees.add(emp["id"])

        return actions

    def _sow_fields(
        self,
        fields: list[dict[str, Any]],
        employees: list[dict[str, Any]],
        used_employees: set[int],
    ) -> list[str]:
        """Sème des légumes sur les champs vides avec rotation."""
        actions: list[str] = []

        empty_fields = [f for f in fields if f.get("content") in ["NONE", None]]

        # Permettre à TOUS les ouvriers disponibles de semer (pas seulement ceux à FARM)
        available_employees = [
            emp for emp in employees
            if emp.get("id") not in used_employees
            and emp.get("tractor") is None
        ]

        for field in empty_fields:
            if not available_employees:
                break

            emp = available_employees.pop(0)
            field_location = field.get("location", "")

            if field_location.startswith("FIELD"):
                field_num = field_location.replace("FIELD", "")
                vegetable = VEGETABLES[self.vegetable_index % len(VEGETABLES)]
                self.vegetable_index += 1

                actions.append(f"{emp['id']} SEMER {vegetable} {field_num}")
                used_employees.add(emp["id"])

        return actions
