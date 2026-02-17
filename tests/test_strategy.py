"""Tests pour la stratégie de jeu."""

from chronobio_client.strategy import Strategy


class TestStrategy:
    """Tests de la classe Strategy."""

    def test_initial_setup_day1(self):
        """Teste le setup initial au jour 1."""
        strategy = Strategy()
        strategy._day = 0  # Car get_actions() incrémente _day
        farm = self._create_empty_farm()

        commands = strategy.get_actions(farm)

        # Jour 1: 2 champs + 2 tracteurs (stratégie PROGRESSIVE)
        assert len(commands) == 4
        assert commands.count("0 ACHETER_CHAMP") == 2
        assert commands.count("0 ACHETER_TRACTEUR") == 2

    def test_initial_setup_day2(self):
        """Teste le setup au jour 2."""
        strategy = Strategy()
        strategy._day = 1  # Car get_actions() incrémente _day

        farm = self._create_farm_with_fields(2, tractors=2, employees=0)

        commands = strategy.get_actions(farm)

        # Jour 2: embaucher 4 ouvriers (2 par champ, stratégie PROGRESSIVE)
        assert len(commands) == 4
        assert commands.count("0 EMPLOYER") == 4

    def test_watering_priority(self):
        """Teste que l'arrosage est prioritaire."""
        strategy = Strategy()
        strategy._day = 10  # Après le setup initial

        farm = self._create_farm_with_fields(2, tractors=1, employees=1)
        # Ajouter des champs avec légumes qui ont besoin d'eau
        farm["fields"][0]["content"] = "POTATO"
        farm["fields"][0]["needed_water"] = 5
        farm["fields"][1]["content"] = "TOMATO"
        farm["fields"][1]["needed_water"] = 3

        # Employé disponible à la FARM
        farm["employees"][0]["location"] = "FARM"
        farm["employees"][0]["tractor"] = None

        commands = strategy.get_actions(farm)

        # Doit arroser (au moins un champ)
        arroser_commands = [c for c in commands if "ARROSER" in c]
        assert len(arroser_commands) > 0

    def test_harvest_mature_fields(self):
        """Teste la récolte des champs mûrs."""
        strategy = Strategy()
        strategy._day = 20

        farm = self._create_farm_with_fields(2, tractors=1, employees=1)
        # Champ mûr (needed_water = 0)
        farm["fields"][0]["content"] = "POTATO"
        farm["fields"][0]["needed_water"] = 0

        # Employé et tracteur disponibles
        farm["employees"][0]["location"] = "FARM"
        farm["employees"][0]["tractor"] = None

        commands = strategy.get_actions(farm)

        # Doit stocker
        stocker_commands = [c for c in commands if "STOCKER" in c]
        assert len(stocker_commands) > 0

    def test_planting_rotation(self):
        """Teste que le semis suit une rotation intelligente."""
        strategy = Strategy()
        strategy._day = 15

        farm = self._create_farm_with_fields(3, tractors=1, employees=1)
        # Stock déséquilibré : beaucoup de patates, peu de tomates
        farm["soup_factory"]["stock"] = {
            "POTATO": 100,
            "TOMATO": 5,
            "LEEK": 20,
            "ONION": 20,
            "ZUCCHINI": 20,
        }

        # Champ vide disponible
        farm["fields"][0]["content"] = "NONE"
        farm["employees"][0]["location"] = "FARM"
        farm["employees"][0]["tractor"] = None

        commands = strategy.get_actions(farm)

        # Doit semer quelque chose
        semer_commands = [c for c in commands if "SEMER" in c]
        assert len(semer_commands) > 0

        # Doit privilégier TOMATE (le moins abondant)
        assert any("TOMATE" in c for c in semer_commands)

    def test_no_cooking_when_poor(self):
        """Teste qu'on ne cuisine pas si pas assez d'argent."""
        strategy = Strategy()
        strategy._day = 30

        farm = self._create_farm_with_fields(2, tractors=1, employees=1)
        farm["money"] = 10000  # Pas assez d'argent
        farm["soup_factory"]["stock"] = {
            "POTATO": 100,
            "TOMATO": 100,
            "LEEK": 100,
            "ONION": 100,
            "ZUCCHINI": 100,
        }
        farm["employees"][0]["location"] = "FARM"

        commands = strategy.get_actions(farm)

        # NE DOIT PAS cuisiner
        cuisiner_commands = [c for c in commands if "CUISINER" in c]
        assert len(cuisiner_commands) == 0

    def test_cooking_when_rich_and_stocked(self):
        """Teste qu'on cuisine si total_stock>300, 3+ variétés>=30, usine dispo."""
        strategy = Strategy()
        strategy._day = 30

        farm = self._create_farm_with_fields(2, tractors=1, employees=2)
        farm["money"] = 60000
        farm["soup_factory"]["stock"] = {
            "POTATO": 100,
            "TOMATO": 100,
            "LEEK": 100,
            "ONION": 100,
            "ZUCCHINI": 100,
        }
        farm["soup_factory"]["days_off"] = 0
        farm["employees"][0]["location"] = "FARM"
        farm["employees"][0]["tractor"] = None
        # Emp#2 à SOUP_FACTORY pour pouvoir CUISINER (stratégie n'envoie CUISINER qu'à partir de SOUP_FACTORY)
        farm["employees"][1]["location"] = "SOUP_FACTORY"
        farm["employees"][1]["tractor"] = None

        # Champs mûrs: 1 STOCKER (emp1 + tracteur), 1 VENDRE (gérant) ; emp2 à l'usine → peut CUISINER
        farm["fields"][0]["content"] = "POTATO"
        farm["fields"][0]["needed_water"] = 0
        farm["fields"][1]["content"] = "TOMATO"
        farm["fields"][1]["needed_water"] = 0

        commands = strategy.get_actions(farm)

        # DOIT cuisiner (stock 500>300, 5 variétés>=30, 1 ouvrier dispo après RÉCOLTER)
        cuisiner_commands = [c for c in commands if "CUISINER" in c]
        assert len(cuisiner_commands) > 0

    def test_no_hiring_when_poor(self):
        """Teste qu'on n'embauche pas si pas assez d'argent."""
        strategy = Strategy()
        strategy._day = 50

        farm = self._create_farm_with_fields(3, tractors=1, employees=0)
        farm["money"] = 50000  # Pas assez

        commands = strategy.get_actions(farm)

        # NE DOIT PAS embaucher
        employer_commands = [c for c in commands if "EMPLOYER" in c]
        assert len(employer_commands) == 0

    def test_hiring_when_rich(self):
        """Teste qu'on embauche si beaucoup d'argent et gérant libre."""
        strategy = Strategy()
        strategy._day = 50

        farm = self._create_farm_with_fields(3, tractors=3, employees=3)
        farm["money"] = 100000  # Assez pour buffer 30j, pas >80k pour éviter ACHETER_CHAMP
        # 3 ouvriers à la FARM pour SEMER les 3 champs vides → gérant non utilisé
        for i in range(3):
            farm["employees"][i]["location"] = "FARM"
            farm["employees"][i]["tractor"] = None

        commands = strategy.get_actions(farm)

        # DOIT embaucher (3 < 6 ouvriers, tracteurs déjà 3/3 → pas ACHETER_TRACTEUR, gérant libre)
        employer_commands = [c for c in commands if "EMPLOYER" in c]
        assert len(employer_commands) > 0

    def test_fire_employee_when_bankrupt(self):
        """Teste qu'on licencie si jours_salaires<5 et trop d'ouvriers vs champs."""
        strategy = Strategy()
        strategy._day = 100

        farm = self._create_farm_with_fields(2, tractors=1, employees=5)
        farm["money"] = 5000
        # Salaires: emp2 le plus élevé → licencié en premier
        farm["employees"][0]["salary"] = 500
        farm["employees"][1]["salary"] = 2000
        for i in range(2, 5):
            farm["employees"][i]["salary"] = 500
        # Champs en culture (pas vides) → pas de SEMER, gérant libre pour LICENCIER
        farm["fields"][0]["content"] = "POTATO"
        farm["fields"][0]["needed_water"] = 5
        farm["fields"][1]["content"] = "TOMATO"
        farm["fields"][1]["needed_water"] = 3

        commands = strategy.get_actions(farm)

        # DOIT licencier (5 > 4 nécessaires pour 2 champs, jours_salaires < 5)
        licencier_commands = [c for c in commands if "LICENCIER" in c]
        assert len(licencier_commands) > 0
        # On licencie le plus gros salaire en priorité (emp #2 = 2000)
        assert "0 LICENCIER 2" in commands

    # Helpers

    def _create_empty_farm(self):
        """Crée une ferme vide pour les tests."""
        return {
            "money": 100000,
            "fields": [
                {"content": "NONE", "needed_water": 0, "bought": False, "location": f"FIELD{i}"}
                for i in range(1, 6)
            ],
            "employees": [],
            "tractors": [],
            "soup_factory": {
                "days_off": 0,
                "stock": {
                    "POTATO": 0,
                    "TOMATO": 0,
                    "LEEK": 0,
                    "ONION": 0,
                    "ZUCCHINI": 0,
                },
            },
        }

    def _create_farm_with_fields(self, num_fields: int, tractors: int = 0, employees: int = 0):
        """Crée une ferme avec un nombre spécifique de champs, tracteurs et employés."""
        farm = self._create_empty_farm()

        # Acheter les champs
        for i in range(num_fields):
            farm["fields"][i]["bought"] = True

        # Ajouter les tracteurs
        for i in range(tractors):
            farm["tractors"].append({"id": i + 1, "location": "FARM"})

        # Ajouter les employés
        for i in range(employees):
            farm["employees"].append({
                "id": i + 1,
                "location": "FIELD1",
                "tractor": None,
                "salary": 1000,
            })

        return farm
