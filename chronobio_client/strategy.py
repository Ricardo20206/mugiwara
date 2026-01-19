"""Stratégie de jeu optimisée."""

from typing import List

from chronobio_client.actions import Actions
from chronobio_client.game_state import Field, GameState

# Légumes disponibles dans le jeu
VEGETABLES = ["PATATE", "POIREAU", "TOMATE", "OIGNON", "COURGETTE"]

# Coûts
FIELD_COST = 10000
TRACTOR_COST = 30000
WORKER_SALARY_FIRST_MONTH = 1000

# Constantes stratégiques - ULTRA MINIMALISTE pour éviter blocages
MIN_WORKERS = 1  # Nombre minimum d'ouvriers
TARGET_WORKERS = 1  # UN SEUL ouvrier maximum au début
MIN_MONEY_RESERVE = 2000  # Réserve minimale très faible
TARGET_FIELDS = 1  # UN SEUL champ au début (très prudent)
MAX_TRACTORS = 0  # Jamais de tracteurs (trop cher)
SAFETY_MARGIN = 1.0  # Aucune marge (on calcule juste)


class Strategy:
    """Stratégie de jeu - VERSION OBSERVATION PURE pour diagnostiquer les blocages."""

    def __init__(self) -> None:
        """Initialise la stratégie."""
        self.vegetable_rotation = 0  # Pour varier les légumes
        self.turn_count = 0  # Compteur de tours

    def get_actions(self, game_state: GameState) -> List[str]:
        """Génère les actions - MODE OBSERVATION PURE (pas d'investissements)."""
        actions: List[str] = []
        self.turn_count += 1
        
        # Créer une copie de l'état pour tracker les ouvriers utilisés
        used_workers = set()
        used_fields = set()
        
        # NE RIEN FAIRE qui coûte de l'argent pendant les premiers tours
        # Juste observer ce qui se passe
        
        # Seulement faire des actions GRATUITES si on a déjà des ressources
        # (ce qui ne devrait pas être le cas au début)
        
        # PRIORITÉ 1: Arroser (gratuit) - seulement si on a des champs ET des ouvriers
        if len(game_state.fields) > 0 and len(game_state.workers) > 0:
            new_actions, used_workers, used_fields = self._water_fields_safe(
                game_state, used_workers, set()
            )
            actions.extend(new_actions)
        
        # PRIORITÉ 2: Semer (gratuit) - seulement si on a des champs vides ET des ouvriers
        if len(game_state.fields) > 0 and len(game_state.workers) > 0:
            new_actions, used_workers, used_fields = self._sow_fields_safe(
                game_state, used_workers, used_fields, []
            )
            actions.extend(new_actions)
        
        # Ne JAMAIS acheter de champs
        # Ne JAMAIS embaucher d'ouvriers
        # Ne JAMAIS acheter de tracteurs
        # On observe juste ce qui se passe avec 100,030 EUR de départ

        return actions

    def _buy_fields(self, game_state: GameState, available_money: int, required_reserve: int) -> List[str]:
        """Achete des champs si possible - VERSION TRES PRUDENTE."""
        actions: List[str] = []
        owned_fields_count = len(game_state.fields)

        # Acheter UN SEUL champ à la fois avec une GRANDE marge de sécurité
        if owned_fields_count < TARGET_FIELDS:
            # Besoin de beaucoup plus d'argent que juste le coût du champ
            total_cost_needed = FIELD_COST + required_reserve + 20000  # Marge de 20000
            if available_money >= total_cost_needed:
                next_field = game_state.get_next_field_to_buy()
                if next_field is not None:
                    actions.append(Actions.buy_field())

        return actions

    def _employ_workers_force(self, game_state: GameState, available_money: int, required_reserve: int) -> List[str]:
        """Force l'embauche d'un ouvrier (utilisé quand on a des champs mais aucun ouvrier)."""
        actions: List[str] = []
        
        # Coût approximatif d'un nouvel ouvrier avec GRANDE marge
        estimated_new_worker_salary = WORKER_SALARY_FIRST_MONTH
        worker_cost = estimated_new_worker_salary * 10  # Estimation très large pour sécurité
        
        # Ne pas embaucher si on n'a pas BEAUCOUP d'argent
        total_needed = worker_cost + required_reserve + 10000  # Marge supplémentaire
        if available_money < total_needed:
            return actions
        
        # Embaucher UN ouvrier (force l'embauche)
        actions.append(Actions.employ())
        return actions

    def _employ_workers(self, game_state: GameState, available_money: int, required_reserve: int) -> List[str]:
        """Embauche des ouvriers si nécessaire - VERSION TRES PRUDENTE."""
        actions: List[str] = []
        workers_count = len(game_state.workers)

        # Ne pas embaucher si on n'a pas de champs (inutile sans champs à travailler)
        if len(game_state.fields) == 0:
            return actions

        # Coût approximatif d'un nouvel ouvrier avec GRANDE marge de sécurité
        estimated_new_worker_salary = WORKER_SALARY_FIRST_MONTH
        worker_cost = estimated_new_worker_salary * 10  # Très large pour éviter blocage

        # Calculer la nouvelle réserve nécessaire (incluant le nouvel ouvrier)
        new_total_salary = sum(worker.salary for worker in game_state.workers) + estimated_new_worker_salary
        new_required_reserve = new_total_salary * SAFETY_MARGIN + MIN_MONEY_RESERVE

        # Ne pas embaucher si on n'a pas BEAUCOUP d'argent
        total_needed = worker_cost + new_required_reserve + 20000  # Grande marge
        if available_money < total_needed:
            return actions

        # Embaucher UN SEUL ouvrier par tour maximum
        if workers_count < TARGET_WORKERS:
            actions.append(Actions.employ())

        return actions

    def _buy_tractors(self, game_state: GameState, available_money: int, required_reserve: int) -> List[str]:
        """Achète des tracteurs si nécessaire."""
        actions: List[str] = []
        tractors_count = len(game_state.tractors)
        fields_count = len(game_state.fields)

        # Acheter des tracteurs seulement si on a au moins 2 champs
        # 1 tracteur peut gérer 2 champs efficacement
        # Ne pas acheter si on n'a pas de champs ou pas assez d'argent
        total_needed = TRACTOR_COST + required_reserve
        if (
            fields_count >= 2  # Au moins 2 champs pour justifier l'achat
            and tractors_count < MAX_TRACTORS
            and tractors_count < (fields_count + 1) // 2  # 1 tracteur pour 2 champs
            and available_money >= total_needed
        ):
            actions.append(Actions.buy_tractor())

        return actions

    def _sow_fields_safe(
        self, game_state: GameState, used_workers: set, used_fields: set, newly_bought_fields: List[int] = None
    ) -> tuple[List[str], set, set]:
        """Sème des légumes sur les champs vides (version sécurisée).
        
        Args:
            newly_bought_fields: Liste des numéros de champs achetés dans ce tour
        """
        if newly_bought_fields is None:
            newly_bought_fields = []
            
        actions: List[str] = []
        empty_fields = game_state.get_empty_fields()
        available_workers = [
            w for w in game_state.get_available_workers()
            if w.number not in used_workers
        ]

        # Ajouter les champs nouvellement achetés à la liste des champs vides
        # (ils seront créés par le serveur avant le semis dans le même tour)
        for field_num in newly_bought_fields:
            # Vérifier que ce champ n'est pas déjà dans les champs existants
            existing_field = game_state.get_field(field_num)
            if existing_field is None:
                # Créer un champ temporaire pour représenter le nouveau champ acheté
                # Le serveur créera le champ avant de traiter l'action de semis
                temp_field = Field({"number": field_num, "bought": True, "content": "NONE"})
                empty_fields.append(temp_field)

        if not empty_fields or not available_workers:
            return actions, used_workers, used_fields

        # Semer sur autant de champs vides que possible avec des légumes VARIÉS
        # Changer de légume à chaque champ pour avoir une diversité visible dans le viewer
        for field in empty_fields:
            if field.number not in used_fields and available_workers:
                # Choisir un légume différent pour chaque champ (rotation)
                vegetable = VEGETABLES[self.vegetable_rotation % len(VEGETABLES)]
                worker = available_workers.pop(0)
                actions.append(Actions.sow(worker.number, vegetable, field.number))
                used_workers.add(worker.number)
                used_fields.add(field.number)
                # Changer de légume pour le prochain champ
                self.vegetable_rotation += 1
                # Semer jusqu'à 5 champs par tour (tous les champs peuvent être semés)
                if len(actions) >= 5:
                    break

        return actions, used_workers, used_fields

    def _sow_fields(self, game_state: GameState) -> List[str]:
        """Sème des légumes sur les champs vides (ancienne méthode, conservée pour compatibilité)."""
        actions, _, _ = self._sow_fields_safe(game_state, set(), set())
        return actions

    def _water_fields_safe(
        self, game_state: GameState, used_workers: set, used_fields: set
    ) -> tuple[List[str], set, set]:
        """Arrose les champs qui en ont besoin (version sécurisée)."""
        actions: List[str] = []
        fields_needing_water = game_state.get_fields_needing_watering()
        available_workers = [
            w for w in game_state.get_available_workers()
            if w.number not in used_workers
        ]

        if not fields_needing_water or not available_workers:
            return actions, used_workers, used_fields

        # Arroser les champs dans l'ordre de priorité
        # (ceux qui ont le plus besoin d'eau en premier)
        fields_needing_water.sort(key=lambda f: f.water_needed, reverse=True)

        # Utiliser les ouvriers disponibles pour arroser
        for field in fields_needing_water:
            if field.number not in used_fields and available_workers:
                worker = available_workers.pop(0)
                actions.append(Actions.water(worker.number, field.number))
                used_workers.add(worker.number)
                used_fields.add(field.number)

        return actions, used_workers, used_fields

    def _water_fields(self, game_state: GameState) -> List[str]:
        """Arrose les champs qui en ont besoin (ancienne méthode, conservée pour compatibilité)."""
        actions, _, _ = self._water_fields_safe(game_state, set(), set())
        return actions

    def _store_vegetables_safe(
        self, game_state: GameState, used_workers: set, used_fields: set
    ) -> tuple[List[str], set, set]:
        """Stocke les légumes récoltables dans l'usine (version sécurisée)."""
        actions: List[str] = []
        harvestable_fields = game_state.get_harvestable_fields()
        available_workers = [
            w for w in game_state.get_available_workers()
            if w.number not in used_workers
        ]
        available_tractors = game_state.get_available_tractors()

        if not harvestable_fields or not available_workers or not available_tractors:
            return actions, used_workers, used_fields

        # Stocker autant de champs que possible (maximiser la production)
        # Utiliser tous les tracteurs et ouvriers disponibles
        for tractor in available_tractors:
            if not available_workers:
                break
            for field in harvestable_fields:
                if field.number not in used_fields and available_workers:
                    worker = available_workers.pop(0)
                    actions.append(Actions.store(worker.number, field.number, tractor.number))
                    used_workers.add(worker.number)
                    used_fields.add(field.number)
                    break  # Un champ par tracteur à la fois

        return actions, used_workers, used_fields

    def _store_vegetables(self, game_state: GameState) -> List[str]:
        """Stocke les légumes récoltables dans l'usine (ancienne méthode, conservée pour compatibilité)."""
        actions, _, _ = self._store_vegetables_safe(game_state, set(), set())
        return actions

    def _cook_soups_safe(
        self, game_state: GameState, used_workers: set
    ) -> tuple[List[str], set]:
        """Cuisine des soupes si l'usine n'est pas arrêtée (version sécurisée)."""
        actions: List[str] = []

        # Ne pas cuisiner si l'usine est arrêtée
        if game_state.soup_factory_shutdown > 0:
            return actions, used_workers

        # Vérifier qu'on a des légumes en stock
        total_stock = sum(game_state.soup_factory_stock.values())
        if total_stock == 0:
            return actions, used_workers

        # Utiliser plusieurs ouvriers pour cuisiner (maximiser la production de soupes)
        # Les soupes rapportent plus que les légumes seuls
        available_workers = [
            w for w in game_state.get_available_workers()
            if w.number not in used_workers
        ]
        
        # Utiliser jusqu'à 2 ouvriers pour cuisiner (si on en a assez)
        workers_to_use = min(2, len(available_workers))
        for i in range(workers_to_use):
            worker = available_workers[i]
            actions.append(Actions.cook(worker.number))
            used_workers.add(worker.number)

        return actions, used_workers

    def _cook_soups(self, game_state: GameState) -> List[str]:
        """Cuisine des soupes si l'usine n'est pas arrêtée (ancienne méthode, conservée pour compatibilité)."""
        actions, _ = self._cook_soups_safe(game_state, set())
        return actions

    def _sell_vegetables(self, game_state: GameState) -> List[str]:
        """Vend des légumes d'un champ si on manque vraiment d'argent et qu'on a trop de stock."""
        actions: List[str] = []
        
        # Ne vendre que si on manque vraiment d'argent (moins de 5000€)
        # et qu'on a des champs récoltables qu'on ne peut pas stocker
        if game_state.money < 5000:
            harvestable_fields = game_state.get_harvestable_fields()
            available_tractors = game_state.get_available_tractors()
            available_workers = game_state.get_available_workers()
            
            # Vendre seulement si on a un champ récoltable mais pas de moyen de le stocker
            if harvestable_fields and (not available_tractors or not available_workers):
                # Vendre le premier champ récoltable
                field = harvestable_fields[0]
                actions.append(Actions.sell(0, field.number))

        return actions
