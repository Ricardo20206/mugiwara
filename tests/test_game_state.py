"""Tests pour le module game_state."""

import pytest

from chronobio_client.game_state import Field, GameState, Tractor, Worker


class TestField:
    """Tests pour la classe Field."""

    def test_field_with_location(self):
        """Test de création d'un champ avec location."""
        data = {"location": "FIELD1", "content": "POTATO", "needed_water": 5}
        field = Field(data)
        assert field.number == 1
        assert field.vegetable == "POTATO"
        assert field.water_needed == 5

    def test_field_with_number(self):
        """Test de création d'un champ avec number."""
        data = {"number": 3, "vegetable": "TOMATO", "water_needed": 3}
        field = Field(data)
        assert field.number == 3
        assert field.vegetable == "TOMATO"
        assert field.water_needed == 3

    def test_field_none_content(self):
        """Test d'un champ vide."""
        data = {"location": "FIELD2", "content": "NONE"}
        field = Field(data)
        assert field.number == 2
        assert field.vegetable is None

    def test_field_vegetable_none_string(self):
        """Test d'un champ avec vegetable='NONE'."""
        data = {"location": "FIELD2", "vegetable": "NONE"}
        field = Field(data)
        assert field.number == 2
        assert field.vegetable is None

    def test_field_needs_watering(self):
        """Test de la vérification d'arrosage nécessaire."""
        field1 = Field({"location": "FIELD1", "needed_water": 5})
        field2 = Field({"location": "FIELD2", "needed_water": 0})
        assert field1.needs_watering() is True
        assert field2.needs_watering() is False

    def test_field_ready_to_harvest(self):
        """Test de la vérification de récolte possible."""
        field1 = Field({"location": "FIELD1", "harvestable": True, "harvest_in_progress": False})
        field2 = Field({"location": "FIELD2", "harvestable": True, "harvest_in_progress": True})
        field3 = Field({"location": "FIELD3", "harvestable": False})
        assert field1.is_ready_to_harvest() is True
        assert field2.is_ready_to_harvest() is False
        assert field3.is_ready_to_harvest() is False


class TestTractor:
    """Tests pour la classe Tractor."""

    def test_tractor_creation(self):
        """Test de création d'un tracteur."""
        data = {"number": 1, "location": 0, "worker": None}
        tractor = Tractor(data)
        assert tractor.number == 1
        assert tractor.location == 0
        assert tractor.worker is None

    def test_tractor_with_worker(self):
        """Test d'un tracteur avec un ouvrier."""
        data = {"number": 2, "location": 3, "worker": 1}
        tractor = Tractor(data)
        assert tractor.number == 2
        assert tractor.worker == 1


class TestWorker:
    """Tests pour la classe Worker."""

    def test_worker_creation(self):
        """Test de création d'un ouvrier."""
        data = {"number": 1, "location": 0, "tractor": None, "salary": 1000}
        worker = Worker(data)
        assert worker.number == 1
        assert worker.location == 0
        assert worker.tractor is None
        assert worker.salary == 1000

    def test_worker_with_tractor(self):
        """Test d'un ouvrier avec un tracteur."""
        data = {"number": 2, "location": 1, "tractor": 1, "salary": 1050}
        worker = Worker(data)
        assert worker.number == 2
        assert worker.tractor == 1
        assert worker.salary == 1050


class TestGameState:
    """Tests pour la classe GameState."""

    def test_game_state_creation(self):
        """Test de création de l'état du jeu."""
        data = {
            "day": 10,
            "money": 50000,
            "name": "TestFarm",
            "score": 1000,
            "blocked": False,
            "fields": [],
            "tractors": [],
            "workers": [],
            "loans": []
        }
        state = GameState(data)
        assert state.day == 10
        assert state.money == 50000
        assert state.name == "TestFarm"
        assert state.score == 1000
        assert state.blocked is False

    def test_get_field(self):
        """Test de récupération d'un champ."""
        data = {
            "day": 1,
            "money": 100000,
            "fields": [
                {"location": "FIELD1", "content": "POTATO", "bought": True},
                {"location": "FIELD2", "content": "TOMATO", "bought": True}
            ]
        }
        state = GameState(data)
        field1 = state.get_field(1)
        field2 = state.get_field(2)
        field3 = state.get_field(3)

        assert field1 is not None
        assert field1.number == 1
        assert field2 is not None
        assert field2.number == 2
        assert field3 is None

    def test_get_available_fields(self):
        """Test de récupération des champs disponibles."""
        data = {
            "day": 1,
            "money": 100000,
            "fields": [
                {"location": "FIELD1", "bought": True},
                {"location": "FIELD2", "bought": True}
            ]
        }
        state = GameState(data)
        available = state.get_available_fields()
        assert available == [3, 4, 5]

    def test_get_next_field_to_buy(self):
        """Test de récupération du prochain champ à acheter."""
        data = {
            "day": 1,
            "money": 100000,
            "fields": [
                {"location": "FIELD1", "bought": True},
                {"location": "FIELD3", "bought": True}
            ]
        }
        state = GameState(data)
        next_field = state.get_next_field_to_buy()
        assert next_field == 2  # Le champ 2 n'est pas acheté

    def test_get_next_field_when_all_bought(self):
        """Test quand tous les champs sont achetés."""
        data = {
            "day": 1,
            "money": 100000,
            "fields": [
                {"location": f"FIELD{i}", "bought": True} for i in range(1, 6)
            ]
        }
        state = GameState(data)
        next_field = state.get_next_field_to_buy()
        assert next_field is None

    def test_get_fields_needing_watering(self):
        """Test de récupération des champs nécessitant arrosage."""
        data = {
            "day": 1,
            "money": 100000,
            "fields": [
                {"location": "FIELD1", "needed_water": 5, "bought": True},
                {"location": "FIELD2", "needed_water": 0, "bought": True},
                {"location": "FIELD3", "needed_water": 3, "bought": True}
            ]
        }
        state = GameState(data)
        fields = state.get_fields_needing_watering()
        assert len(fields) == 2
        assert all(f.water_needed > 0 for f in fields)

    def test_get_harvestable_fields(self):
        """Test de récupération des champs récoltables."""
        data = {
            "day": 1,
            "money": 100000,
            "fields": [
                {"location": "FIELD1", "harvestable": True, "harvest_in_progress": False, "bought": True},
                {"location": "FIELD2", "harvestable": False, "bought": True},
                {"location": "FIELD3", "harvestable": True, "harvest_in_progress": True, "bought": True}
            ]
        }
        state = GameState(data)
        fields = state.get_harvestable_fields()
        assert len(fields) == 1
        assert fields[0].number == 1

    def test_get_empty_fields(self):
        """Test de récupération des champs vides."""
        data = {
            "day": 1,
            "money": 100000,
            "fields": [
                {"location": "FIELD1", "content": "POTATO", "bought": True},
                {"location": "FIELD2", "content": "NONE", "bought": True},
                {"location": "FIELD3", "vegetable": None, "bought": True}
            ]
        }
        state = GameState(data)
        empty = state.get_empty_fields()
        assert len(empty) == 2

    def test_get_available_workers(self):
        """Test de récupération des ouvriers disponibles."""
        data = {
            "day": 1,
            "money": 100000,
            "workers": [
                {"number": 1, "location": 0, "tractor": None},
                {"number": 2, "location": 1, "tractor": 1},
                {"number": 3, "location": 0, "tractor": None}
            ]
        }
        state = GameState(data)
        available = state.get_available_workers()
        assert len(available) == 2
        assert all(w.tractor is None for w in available)

    def test_get_available_tractors(self):
        """Test de récupération des tracteurs disponibles."""
        data = {
            "day": 1,
            "money": 100000,
            "tractors": [
                {"number": 1, "location": 0, "worker": None},
                {"number": 2, "location": 1, "worker": 2}
            ]
        }
        state = GameState(data)
        available = state.get_available_tractors()
        assert len(available) == 1
        assert available[0].number == 1

    def test_get_worker(self):
        """Test de récupération d'un ouvrier par son numéro."""
        data = {
            "day": 1,
            "money": 100000,
            "workers": [
                {"number": 1, "location": 0, "tractor": None, "salary": 1000},
                {"number": 2, "location": 1, "tractor": 1, "salary": 1050}
            ]
        }
        state = GameState(data)
        worker1 = state.get_worker(1)
        worker2 = state.get_worker(2)
        worker3 = state.get_worker(99)

        assert worker1 is not None
        assert worker1.number == 1
        assert worker2 is not None
        assert worker2.number == 2
        assert worker3 is None

    def test_get_tractor(self):
        """Test de récupération d'un tracteur par son numéro."""
        data = {
            "day": 1,
            "money": 100000,
            "tractors": [
                {"number": 1, "location": 0, "worker": None},
                {"number": 2, "location": 1, "worker": 2}
            ]
        }
        state = GameState(data)
        tractor1 = state.get_tractor(1)
        tractor2 = state.get_tractor(2)
        tractor3 = state.get_tractor(99)

        assert tractor1 is not None
        assert tractor1.number == 1
        assert tractor2 is not None
        assert tractor2.number == 2
        assert tractor3 is None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
