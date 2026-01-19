"""Stratégie de jeu ÉQUILIBRÉE OPTIMISÉE - Production Maximale Stable."""

from typing import Any

# Légumes disponibles dans le jeu (COURGETTE priorisée pour 5ème champ)
VEGETABLES = ["COURGETTE", "TOMATE", "PATATE", "POIREAU", "OIGNON"]

# Coûts
FIELD_COST = 10000
TRACTOR_COST = 30000
EMPLOYEE_BASE_SALARY = 1000

# Configuration OPTIMISÉE PRODUCTION
MAX_EMPLOYEES = 8       # Équilibré pour production soutenue
MAX_TRACTORS = 3
MAX_FIELDS = 5
MIN_STOCK_TO_COOK = 20  # Cuisine dès 20 légumes
MIN_DIVERSITY = 3       # Flexible
MAX_COOKS = 4           # 4 cuisiniers en parallèle


class Strategy:
    """Stratégie OPTIMISÉE PRODUCTION SOUPE - Production massive de soupes."""

    def __init__(self) -> None:
        """Initialise la stratégie."""
        self.turn_count = 0
        self.vegetable_index = 0

    def get_actions(self, farm_data: dict[str, Any]) -> list[str]:
        """
        Génère les actions pour ce tour.

        Stratégie PRODUCTION OPTIMISÉE - Équilibre croissance/stabilité:
        - Jour 0: ACHETER 5 CHAMPS (50k, reste 50k) - COURGETTES priorisées!
        - Jour 1: EMPLOYER 3 OUVRIERS (démarrage rapide)
        - Jour 3: ACHETER 1 TRACTEUR
        - Jour 5: EMPLOYER 2 OUVRIERS (total: 5)
        - Jour 10: ACHETER 1 TRACTEUR (total: 2)
        - Jour 15: EMPLOYER 1 OUVRIER (total: 6)
        - Jour 20: ACHETER 1 TRACTEUR (total: 3, complet!)
        - Jour 25+: Expansion continue jusqu'à 8 ouvriers
        - Buffer fixe: 20 jours (équilibre sécurité/croissance)
        - Cuisine: seuil 20 légumes, diversité 3, jusqu'à 4 cuisiniers
        - Rotation: COURGETTE prioritaire, tous les légumes équilibrés
        - Conditions simplifiées pour garantir la production
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
        # Buffer simplifié: 20 jours fixe
        safety_buffer = total_salaries * 20
        num_employees = len(employees)
        num_tractors = len(tractors)

        # Tracker
        used_employees: set[int] = set()
        used_tractors: set[int] = set()

        # === EXPANSION SIMPLIFIÉE ET EFFICACE ===

        # Jour 0: 5 champs TOUS
        if self.turn_count == 1:
            for _ in range(5):
                actions.append("0 ACHETER_CHAMP")

        # Jour 1: 3 ouvriers immédiatement
        elif self.turn_count == 2:
            for _ in range(3):
                actions.append("0 EMPLOYER")

        # Jour 3: 1 tracteur
        elif self.turn_count == 4 and num_tractors < 1 and money > safety_buffer + 30000:
            actions.append("0 ACHETER_TRACTEUR")

        # Jour 5: 2 ouvriers (total: 5)
        elif self.turn_count == 6 and num_employees < 5 and money > safety_buffer + 20000:
            for _ in range(2):
                actions.append("0 EMPLOYER")

        # Jour 10: 1 tracteur (total: 2)
        elif self.turn_count == 11 and num_tractors < 2 and money > safety_buffer + 30000:
            actions.append("0 ACHETER_TRACTEUR")

        # Jour 15: 1 ouvrier (total: 6)
        elif self.turn_count == 16 and num_employees < 6 and money > safety_buffer + 25000:
            actions.append("0 EMPLOYER")

        # Jour 20: 1 tracteur (total: 3, complet!)
        elif self.turn_count == 21 and num_tractors < 3 and money > safety_buffer + 30000:
            actions.append("0 ACHETER_TRACTEUR")

        # Jour 25+: Expansion continue jusqu'à 8 ouvriers
        elif self.turn_count > 25 and num_employees < MAX_EMPLOYEES and money > safety_buffer + 50000:
            actions.append("0 EMPLOYER")

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

        # Utiliser jusqu'à 5 cuisiniers (production élevée sans surcharge)
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

        available_employees = [
            emp for emp in employees
            if emp.get("id") not in used_employees
            and emp.get("location") == "FARM"
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
