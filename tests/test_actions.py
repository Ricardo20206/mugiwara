"""Tests pour le module actions."""

import pytest

from chronobio_client.actions import Actions


class TestActions:
    """Tests pour la classe Actions."""

    def test_buy_field(self):
        """Test de l'achat de champ."""
        assert Actions.buy_field() == "0 ACHETER_CHAMP"
        assert Actions.buy_field(0) == "0 ACHETER_CHAMP"

    def test_sow(self):
        """Test du semis."""
        assert Actions.sow(1, "PATATE", 1) == "1 SEMER PATATE 1"
        assert Actions.sow(2, "TOMATE", 3) == "2 SEMER TOMATE 3"
        assert Actions.sow(5, "POIREAU", 5) == "5 SEMER POIREAU 5"

    def test_water(self):
        """Test de l'arrosage."""
        assert Actions.water(1, 1) == "1 ARROSER 1"
        assert Actions.water(3, 2) == "3 ARROSER 2"

    def test_sell(self):
        """Test de la vente."""
        assert Actions.sell(0, 1) == "0 VENDRE 1"
        assert Actions.sell(0, 3) == "0 VENDRE 3"

    def test_buy_tractor(self):
        """Test de l'achat de tracteur."""
        assert Actions.buy_tractor() == "0 ACHETER_TRACTEUR"
        assert Actions.buy_tractor(0) == "0 ACHETER_TRACTEUR"

    def test_store(self):
        """Test du stockage."""
        assert Actions.store(1, 1, 1) == "1 STOCKER 1 1"
        assert Actions.store(2, 3, 1) == "2 STOCKER 3 1"

    def test_cook(self):
        """Test de la cuisine."""
        assert Actions.cook(1) == "1 CUISINER"
        assert Actions.cook(3) == "3 CUISINER"

    def test_employ(self):
        """Test de l'embauche."""
        assert Actions.employ() == "0 EMPLOYER"
        assert Actions.employ(0) == "0 EMPLOYER"

    def test_fire(self):
        """Test du licenciement."""
        assert Actions.fire(0, 1) == "0 LICENCIER 1"
        assert Actions.fire(0, 5) == "0 LICENCIER 5"

    def test_borrow(self):
        """Test de l'emprunt."""
        assert Actions.borrow(0, 50000) == "0 EMPRUNTER 50000"
        assert Actions.borrow(0, 100000) == "0 EMPRUNTER 100000"

    def test_move(self):
        """Test du déplacement."""
        # Le déplacement retourne None car automatique
        assert Actions.move(1, 1) is None
        assert Actions.move(2, 3) is None


class TestAllVegetables:
    """Tests avec tous les types de légumes."""

    def test_all_vegetables(self):
        """Test du semis avec tous les légumes."""
        vegetables = ["PATATE", "TOMATE", "POIREAU", "OIGNON", "COURGETTE"]
        for veg in vegetables:
            command = Actions.sow(1, veg, 1)
            assert veg in command
            assert "1 SEMER" in command


class TestMultipleWorkers:
    """Tests avec plusieurs ouvriers."""

    def test_multiple_workers_water(self):
        """Test avec plusieurs ouvriers qui arrosent."""
        commands = [Actions.water(i, i) for i in range(1, 6)]
        assert len(commands) == 5
        assert commands[0] == "1 ARROSER 1"
        assert commands[4] == "5 ARROSER 5"

    def test_multiple_workers_cook(self):
        """Test avec plusieurs ouvriers qui cuisinent."""
        commands = [Actions.cook(i) for i in range(1, 4)]
        assert len(commands) == 3
        assert all("CUISINER" in cmd for cmd in commands)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
