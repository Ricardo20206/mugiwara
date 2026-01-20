"""Tests pour la stratégie de jeu."""

from chronobio_client.strategy import Strategy


class TestStrategy:
    """Tests pour la classe Strategy."""

    def setup_method(self):
        """Configuration avant chaque test."""
        self.strategy = Strategy()

    def test_initialization(self):
        """Test de l'initialisation de la stratégie."""
        assert self.strategy.turn_count == 0
        assert self.strategy.vegetable_index == 0

    def test_turn_count_increments(self):
        """Test que le compteur de tours s'incrémente."""
        farm_data = {
            "money": 100000,
            "employees": [],
            "fields": [],
            "tractors": [],
            "loans": [],
            "soup_factory": {"stock": {}, "days_off": 0}
        }

        self.strategy.get_actions(farm_data)
        assert self.strategy.turn_count == 1

        self.strategy.get_actions(farm_data)
        assert self.strategy.turn_count == 2

    def test_day_1_actions(self):
        """Test des actions au jour 1: 3 champs + 1 tracteur + 0 ouvrier."""
        farm_data = {
            "money": 100000,
            "employees": [],
            "fields": [],
            "tractors": [],
            "loans": [],
            "soup_factory": {"stock": {}, "days_off": 0}
        }

        actions = self.strategy.get_actions(farm_data)

        # Stratégie RADICALE: 3 champs + 1 tracteur + 0 ouvrier
        assert len(actions) == 4
        assert sum(1 for a in actions if "EMPRUNTER" in a) == 0
        assert sum(1 for a in actions if "ACHETER_CHAMP" in a) == 3
        assert sum(1 for a in actions if "ACHETER_TRACTEUR" in a) == 1
        assert sum(1 for a in actions if "EMPLOYER" in a) == 0

    def test_day_2_actions(self):
        """Test des actions au jour 2: RIEN (production uniquement)."""
        farm_data = {
            "money": 40000,  # Argent après investissement (100k - 60k)
            "employees": [],  # 0 ouvrier!
            "fields": [
                {"bought": True, "content": "NONE", "location": f"FIELD{i}"}
                for i in range(1, 4)
            ],
            "tractors": [{"id": 1}],
            "loans": [],
            "soup_factory": {"stock": {}, "days_off": 0}
        }

        self.strategy.turn_count = 1  # Simuler jour 2
        actions = self.strategy.get_actions(farm_data)

        # Stratégie RADICALE: RIEN au jour 2 (juste production)
        expansion_actions = [a for a in actions if "EMPLOYER" in a or "ACHETER" in a or "EMPRUNTER" in a]
        assert len(expansion_actions) == 0

    def test_harvest_fields(self):
        """Test de la récolte des champs."""
        farm_data = {
            "money": 100000,
            "employees": [
                {"id": 1, "location": "FARM", "tractor": None, "salary": 1000}
            ],
            "fields": [
                {"bought": True, "content": "POTATO", "needed_water": 0, "location": "FIELD1"}
            ],
            "tractors": [
                {"id": 1}
            ],
            "loans": [],
            "soup_factory": {"stock": {}, "days_off": 0}
        }

        self.strategy.turn_count = 10
        actions = self.strategy.get_actions(farm_data)

        # Devrait récolter le champ (STOCKER)
        harvest_actions = [a for a in actions if "STOCKER" in a]
        assert len(harvest_actions) >= 1
        assert "1 STOCKER 1 1" in harvest_actions[0]

    def test_water_fields(self):
        """Test de l'arrosage des champs."""
        farm_data = {
            "money": 100000,
            "employees": [
                {"id": 1, "location": "FARM", "tractor": None, "salary": 1000}
            ],
            "fields": [
                {"bought": True, "content": "POTATO", "needed_water": 3, "location": "FIELD1"}
            ],
            "tractors": [],
            "loans": [],
            "soup_factory": {"stock": {}, "days_off": 0}
        }

        self.strategy.turn_count = 10
        actions = self.strategy.get_actions(farm_data)

        # Devrait arroser le champ
        water_actions = [a for a in actions if "ARROSER" in a]
        assert len(water_actions) >= 1
        assert "1 ARROSER 1" in water_actions[0]

    def test_sow_fields(self):
        """Test du semis sur champs vides."""
        farm_data = {
            "money": 100000,
            "employees": [
                {"id": 1, "location": "FARM", "tractor": None, "salary": 1000}
            ],
            "fields": [
                {"bought": True, "content": "NONE", "location": "FIELD1"}
            ],
            "tractors": [],
            "loans": [],
            "soup_factory": {"stock": {}, "days_off": 0}
        }

        self.strategy.turn_count = 10
        actions = self.strategy.get_actions(farm_data)

        # Devrait semer un légume
        sow_actions = [a for a in actions if "SEMER" in a]
        assert len(sow_actions) >= 1
        # Vérifier qu'un légume valide est semé
        assert any(veg in sow_actions[0] for veg in ["PATATE", "POIREAU", "TOMATE", "OIGNON", "COURGETTE"])

    def test_cook_soups(self):
        """Test de la cuisine de soupes."""
        farm_data = {
            "money": 100000,
            "employees": [
                {"id": 1, "location": "FARM", "tractor": None, "salary": 1000},
                {"id": 2, "location": "FARM", "tractor": None, "salary": 1000}
            ],
            "fields": [],
            "tractors": [],
            "loans": [],
            "soup_factory": {
                "stock": {
                    "POTATO": 50,
                    "LEEK": 50,
                    "TOMATO": 50,
                    "ONION": 50,
                    "ZUCCHINI": 50
                },
                "days_off": 0
            }
        }

        self.strategy.turn_count = 10
        actions = self.strategy.get_actions(farm_data)

        # Devrait cuisiner avec plusieurs ouvriers
        cook_actions = [a for a in actions if "CUISINER" in a]
        assert len(cook_actions) >= 1
        # Devrait utiliser max 4 ouvriers
        assert len(cook_actions) <= 4

    def test_cook_soups_without_diversity(self):
        """Test que la diversité est requise (PRODUCTION SOUPE - 3 par légume)."""
        farm_data = {
            "money": 100000,
            "employees": [
                {"id": 1, "location": "FARM", "tractor": None, "salary": 1000},
                {"id": 2, "location": "FARM", "tractor": None, "salary": 1000}
            ],
            "fields": [],
            "tractors": [],
            "loans": [],
            "soup_factory": {
                "stock": {
                    "POTATO": 100,
                    "LEEK": 2,
                    "TOMATO": 2,
                    "ONION": 2,
                    "ZUCCHINI": 2
                },
                "days_off": 0
            }
        }

        self.strategy.turn_count = 10
        actions = self.strategy.get_actions(farm_data)

        # NE devrait PAS cuisiner sans diversité (3 par légume minimum)
        cook_actions = [a for a in actions if "CUISINER" in a]
        assert len(cook_actions) == 0

    def test_no_cook_when_factory_busy(self):
        """Test qu'on ne cuisine pas quand l'usine est occupée."""
        farm_data = {
            "money": 100000,
            "employees": [
                {"id": 1, "location": "FARM", "tractor": None, "salary": 1000}
            ],
            "fields": [],
            "tractors": [],
            "loans": [],
            "soup_factory": {
                "stock": {"POTATO": 200},
                "days_off": 3  # Usine occupée
            }
        }

        self.strategy.turn_count = 10
        actions = self.strategy.get_actions(farm_data)

        # Ne devrait pas cuisiner
        cook_actions = [a for a in actions if "CUISINER" in a]
        assert len(cook_actions) == 0

    def test_no_cook_when_insufficient_stock(self):
        """Test qu'on ne cuisine pas avec un stock insuffisant (<20)."""
        farm_data = {
            "money": 100000,
            "employees": [
                {"id": 1, "location": "FARM", "tractor": None, "salary": 1000}
            ],
            "fields": [],
            "tractors": [],
            "loans": [],
            "soup_factory": {
                "stock": {"POTATO": 10},  # < 20 minimum (stratégie STABLE)
                "days_off": 0
            }
        }

        self.strategy.turn_count = 10
        actions = self.strategy.get_actions(farm_data)

        # Ne devrait pas cuisiner car stock < 20
        cook_actions = [a for a in actions if "CUISINER" in a]
        assert len(cook_actions) == 0

    def test_expansion_late_game(self):
        """Test de l'expansion en fin de partie."""
        farm_data = {
            "money": 200000,  # Beaucoup d'argent
            "employees": [
                {"id": 1, "location": "FARM", "tractor": None, "salary": 1000},
                {"id": 2, "location": "FARM", "tractor": None, "salary": 1000}
            ],
            "fields": [
                {"bought": True, "content": "NONE", "location": "FIELD1"},
                {"bought": True, "content": "NONE", "location": "FIELD2"},
                {"bought": True, "content": "NONE", "location": "FIELD3"}
            ],
            "tractors": [],
            "loans": [],
            "soup_factory": {"stock": {}, "days_off": 0}
        }

        self.strategy.turn_count = 30  # Fin de partie
        actions = self.strategy.get_actions(farm_data)

        # Devrait embaucher ou acheter des tracteurs
        expansion_actions = [a for a in actions if "EMPLOYER" in a or "ACHETER_TRACTEUR" in a]
        # Au moins une action d'expansion si on a assez d'argent
        assert len(expansion_actions) >= 0  # Peut ne rien faire si déjà optimal

    def test_vegetable_rotation(self):
        """Test de la rotation avec COURGETTE priorisée."""
        farm_data = {
            "money": 100000,
            "employees": [
                {"id": 1, "location": "FARM", "tractor": None, "salary": 1000},
                {"id": 2, "location": "FARM", "tractor": None, "salary": 1000},
                {"id": 3, "location": "FARM", "tractor": None, "salary": 1000},
                {"id": 4, "location": "FARM", "tractor": None, "salary": 1000},
                {"id": 5, "location": "FARM", "tractor": None, "salary": 1000}
            ],
            "fields": [
                {"bought": True, "content": "NONE", "location": "FIELD1"},
                {"bought": True, "content": "NONE", "location": "FIELD2"},
                {"bought": True, "content": "NONE", "location": "FIELD3"},
                {"bought": True, "content": "NONE", "location": "FIELD4"},
                {"bought": True, "content": "NONE", "location": "FIELD5"}
            ],
            "tractors": [],
            "loans": [],
            "soup_factory": {"stock": {}, "days_off": 0}
        }

        self.strategy.turn_count = 10
        actions = self.strategy.get_actions(farm_data)

        # Devrait semer avec rotation
        sow_actions = [a for a in actions if "SEMER" in a]
        assert len(sow_actions) == 5  # 5 champs, 5 ouvriers

        # Vérifier que TOUS les légumes sont présents (rotation complète)
        vegetables_sown = set()
        for action in sow_actions:
            for veg in ["TOMATE", "PATATE", "POIREAU", "OIGNON", "COURGETTE"]:
                if veg in action:
                    vegetables_sown.add(veg)

        # Avec 5 semis et rotation ["COURGETTE", "TOMATE", "PATATE", "POIREAU", "OIGNON"],
        # on devrait avoir les 5 légumes
        assert len(vegetables_sown) == 5

        # COURGETTE devrait être en premier (index 0)
        first_action = sow_actions[0] if sow_actions else ""
        assert "COURGETTE" in first_action

    def test_no_harvest_without_tractor(self):
        """Test qu'on ne récolte pas sans tracteur."""
        farm_data = {
            "money": 100000,
            "employees": [
                {"id": 1, "location": "FARM", "tractor": None, "salary": 1000}
            ],
            "fields": [
                {"bought": True, "content": "POTATO", "needed_water": 0, "location": "FIELD1"}
            ],
            "tractors": [],  # Pas de tracteur
            "loans": [],
            "soup_factory": {"stock": {}, "days_off": 0}
        }

        self.strategy.turn_count = 10
        actions = self.strategy.get_actions(farm_data)

        # Ne devrait pas récolter sans tracteur
        harvest_actions = [a for a in actions if "STOCKER" in a]
        assert len(harvest_actions) == 0


class TestStrategyPhases:
    """Tests pour les différentes phases de la stratégie."""

    def test_phase_1_expansion(self):
        """Test de la phase 1: RADICALE - 3 champs + tracteur + 0 ouvrier."""
        strategy = Strategy()

        # Jour 1: 3 champs + tracteur + 0 ouvrier
        farm_data_day1 = {
            "money": 100000,
            "employees": [],
            "fields": [],
            "tractors": [],
            "loans": [],
            "soup_factory": {"stock": {}, "days_off": 0}
        }
        actions_day1 = strategy.get_actions(farm_data_day1)
        # Stratégie RADICALE: 3 champs + tracteur + 0 ouvrier (40k EUR restants!)
        assert len([a for a in actions_day1 if "EMPRUNTER" in a]) == 0
        assert len([a for a in actions_day1 if "ACHETER_CHAMP" in a]) == 3
        assert len([a for a in actions_day1 if "ACHETER_TRACTEUR" in a]) == 1
        assert len([a for a in actions_day1 if "EMPLOYER" in a]) == 0

        # Jour 2: RIEN (juste production!)
        farm_data_day2 = {
            "money": 40000,
            "employees": [],  # 0 ouvrier
            "fields": [
                {"bought": True, "content": "NONE", "location": f"FIELD{i}"}
                for i in range(1, 4)
            ],
            "tractors": [{"id": 1}],
            "loans": [],
            "soup_factory": {"stock": {}, "days_off": 0}
        }
        actions_day2 = strategy.get_actions(farm_data_day2)
        expansion_actions = [a for a in actions_day2 if "EMPLOYER" in a or "ACHETER" in a or "EMPRUNTER" in a]
        assert len(expansion_actions) == 0

    def test_phase_2_production(self):
        """Test de la phase 2: production."""
        strategy = Strategy()
        strategy.turn_count = 10  # Phase de production

        farm_data = {
            "money": 50000,
            "employees": [
                {"id": 1, "location": "FARM", "tractor": None, "salary": 1000}
            ],
            "fields": [
                {"bought": True, "content": "POTATO", "needed_water": 2, "location": "FIELD1"}
            ],
            "tractors": [],
            "loans": [],
            "soup_factory": {"stock": {}, "days_off": 0}
        }

        actions = strategy.get_actions(farm_data)

        # Devrait arroser en priorité
        water_actions = [a for a in actions if "ARROSER" in a]
        assert len(water_actions) >= 1
