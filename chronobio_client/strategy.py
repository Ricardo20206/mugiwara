"""Stratégie de jeu PROGRESSIVE RÉALISTE - Production Garantie."""

from typing import Any

# Légumes disponibles dans le jeu (COURGETTE priorisée pour 5ème champ)
VEGETABLES = ["COURGETTE", "TOMATE", "PATATE", "POIREAU", "OIGNON"]

# Coûts
FIELD_COST = 10000
TRACTOR_COST = 30000
EMPLOYEE_BASE_SALARY = 1000

# Configuration PROGRESSIVE RÉALISTE
MAX_EMPLOYEES = 10      # Objectif à long terme
MAX_TRACTORS = 3
MAX_FIELDS = 5
MIN_STOCK_TO_COOK = 15  # Cuisine dès 15 légumes
MIN_DIVERSITY = 3       # Flexible
MAX_COOKS = 5           # 5 cuisiniers en parallèle


class Strategy:
    """Stratégie PROGRESSIVE RÉALISTE - Production garantie avec expansion contrôlée."""

    def __init__(self) -> None:
        """Initialise la stratégie."""
        self.turn_count = 0
        self.vegetable_index = 0

    def get_actions(self, farm_data: dict[str, Any]) -> list[str]:
        """
        Génère les actions pour ce tour.

        Stratégie PROGRESSIVE RÉALISTE - Garantir la production:
        - Jour 0: 3 CHAMPS (reste 70k EUR - capital de démarrage suffisant!)
        - Jour 1: 2 OUVRIERS + 1 TRACTEUR (production immédiate!)
        - Jour 3: 1 OUVRIER (total: 3)
        - Jour 5: 1 CHAMP (total: 4)
        - Jour 8: 1 OUVRIER (total: 4)
        - Jour 12: 1 TRACTEUR (total: 2)
        - Jour 16: 1 CHAMP (total: 5, complet!)
        - Jour 20+: 1 OUVRIER tous les 5 jours jusqu'à 10
        - Jour 25: 1 TRACTEUR (total: 3, complet!)
        - Buffer adaptatif: 5 jours (début) → 10 jours (établi) → 15 jours (mature)
        - Cuisine: seuil 15 légumes, diversité 3, jusqu'à 5 cuisiniers
        - Rotation: COURGETTE prioritaire, tous les légumes équilibrés
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
        total_salaries = sum(emp.get("salary", 0) for emp in employees)
        num_employees = len(employees)
        num_tractors = len(tractors)
        num_fields = len(fields)

        # Buffer adaptatif: croît avec la maturité de la ferme
        if self.turn_count <= 10:
            buffer_days = 5  # Début: très agressif
        elif self.turn_count <= 50:
            buffer_days = 10  # Établissement: modéré
        else:
            buffer_days = 15  # Mature: prudent

        safety_buffer = total_salaries * buffer_days

        # Tracker
        used_employees: set[int] = set()
        used_tractors: set[int] = set()

        # === EXPANSION PROGRESSIVE ET RÉALISTE ===

        # Jour 0: 3 champs (garde 70k EUR!)
        if self.turn_count == 1:
            for _ in range(3):
                actions.append("0 ACHETER_CHAMP")

        # Jour 1: 2 ouvriers + 1 TRACTEUR (CRITIQUE pour récolter!)
        elif self.turn_count == 2:
            for _ in range(2):
                actions.append("0 EMPLOYER")
            if num_tractors < 1:
                actions.append("0 ACHETER_TRACTEUR")

        # Jour 3: 1 ouvrier (total: 3)
        elif self.turn_count == 4 and num_employees < 3 and money > safety_buffer + 5000:
            actions.append("0 EMPLOYER")

        # Jour 5: 1 champ (total: 4)
        elif self.turn_count == 6 and num_fields < 4 and money > safety_buffer + 10000:
            actions.append("0 ACHETER_CHAMP")

        # Jour 8: 1 ouvrier (total: 4)
        elif self.turn_count == 9 and num_employees < 4 and money > safety_buffer + 5000:
            actions.append("0 EMPLOYER")

        # Jour 12: 1 tracteur (total: 2)
        elif self.turn_count == 13 and num_tractors < 2 and money > safety_buffer + 30000:
            actions.append("0 ACHETER_TRACTEUR")

        # Jour 16: 1 champ (total: 5, complet!)
        elif self.turn_count == 17 and num_fields < 5 and money > safety_buffer + 10000:
            actions.append("0 ACHETER_CHAMP")

        # Jour 20+: 1 ouvrier tous les 5 jours jusqu'à 10
        elif self.turn_count >= 21 and self.turn_count % 5 == 1 and num_employees < MAX_EMPLOYEES and money > safety_buffer + 10000:
            actions.append("0 EMPLOYER")

        # Jour 25: 1 tracteur (total: 3, complet!)
        elif self.turn_count == 26 and num_tractors < 3 and money > safety_buffer + 30000:
            actions.append("0 ACHETER_TRACTEUR")

        # === PRODUCTION: RÉCOLTER, CUISINER, ARROSER, SEMER ===
        harvest_actions = self._harvest_fields(fields, employees, tractors, used_employees, used_tractors)
        actions.extend(harvest_actions)

        cook_actions = self._cook_soups(stock, factory_days_off, employees, used_employees)
        actions.extend(cook_actions)

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
        """Récolte tous les champs prêts avec des tracteurs."""
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
