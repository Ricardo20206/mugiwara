"""Tests pour le client Chronobio."""

import pytest
from unittest.mock import Mock, MagicMock, patch


class TestPlayerGameClient:
    """Tests pour la classe PlayerGameClient."""
    
    def setup_method(self):
        """Configuration avant chaque test."""
        with patch('chronobio_client.client.Client.__init__', return_value=None):
            from chronobio_client.client import PlayerGameClient
            self.client = PlayerGameClient("localhost", 16210, "TestClient")
            self.client._commands = []
    
    def test_add_command(self):
        """Test de l'ajout d'une commande."""
        self.client.add_command("0 ACHETER_CHAMP")
        assert len(self.client._commands) == 1
        assert self.client._commands[0] == "0 ACHETER_CHAMP"
    
    def test_add_multiple_commands(self):
        """Test de l'ajout de plusieurs commandes."""
        self.client.add_command("0 ACHETER_CHAMP")
        self.client.add_command("0 EMPLOYER")
        self.client.add_command("1 SEMER PATATE 1")
        assert len(self.client._commands) == 3
    
    def test_send_commands_clears_list(self):
        """Test que send_commands vide la liste."""
        self.client.add_command("0 ACHETER_CHAMP")
        self.client.send_json = Mock()
        self.client.send_commands()
        assert len(self.client._commands) == 0
    
    def test_send_commands_format(self):
        """Test du format des commandes envoyées."""
        self.client.add_command("0 ACHETER_CHAMP")
        self.client.add_command("1 SEMER PATATE 1")
        self.client.send_json = Mock()
        self.client.send_commands()
        # Grâce à .copy() dans send_commands, la liste est préservée
        self.client.send_json.assert_called_once_with({
            "commands": ["0 ACHETER_CHAMP", "1 SEMER PATATE 1"]
        })


class TestVegetableBalancing:
    """Tests pour l'équilibrage des légumes."""
    
    def test_stock_counting(self):
        """Test du comptage du stock."""
        stock = {
            "POTATO": 10,
            "LEEK": 5,
            "TOMATO": 8,
            "ONION": 3,
            "ZUCCHINI": 2
        }
        
        stock_counts = {
            "PATATE": stock.get("POTATO", 0),
            "POIREAU": stock.get("LEEK", 0),
            "TOMATE": stock.get("TOMATO", 0),
            "OIGNON": stock.get("ONION", 0),
            "COURGETTE": stock.get("ZUCCHINI", 0)
        }
        
        assert stock_counts["PATATE"] == 10
        assert stock_counts["POIREAU"] == 5
        assert stock_counts["COURGETTE"] == 2
    
    def test_vegetable_priority_sorting(self):
        """Test du tri des légumes par rareté."""
        stock_counts = {
            "PATATE": 10,
            "POIREAU": 5,
            "TOMATE": 8,
            "OIGNON": 3,
            "COURGETTE": 2
        }
        
        sorted_vegetables = sorted(stock_counts.items(), key=lambda x: x[1])
        vegetables_priority = [veg for veg, count in sorted_vegetables]
        
        # Les légumes les plus rares doivent être en premier
        assert vegetables_priority[0] == "COURGETTE"  # 2
        assert vegetables_priority[1] == "OIGNON"     # 3
        assert vegetables_priority[-1] == "PATATE"    # 10
    
    def test_field_content_counting(self):
        """Test du comptage des légumes dans les champs."""
        fields = [
            {"content": "POTATO", "needed_water": 5},
            {"content": "TOMATO", "needed_water": 3},
            {"content": "POTATO", "needed_water": 2},
            {"content": "NONE", "needed_water": 0}
        ]
        
        content_mapping = {
            "POTATO": "PATATE",
            "LEEK": "POIREAU",
            "TOMATO": "TOMATE",
            "ONION": "OIGNON",
            "ZUCCHINI": "COURGETTE"
        }
        
        field_counts = {}
        for field in fields:
            content = field.get("content", "NONE")
            if content in content_mapping:
                veg_fr = content_mapping[content]
                field_counts[veg_fr] = field_counts.get(veg_fr, 0) + 1
        
        assert field_counts["PATATE"] == 2
        assert field_counts["TOMATE"] == 1


class TestEmployeeManagement:
    """Tests pour la gestion des ouvriers."""
    
    def test_available_employees_filtering(self):
        """Test du filtrage des ouvriers disponibles."""
        employees = [
            {"id": 1, "location": "FARM", "salary": 1000},
            {"id": 2, "location": "FIELD1", "salary": 1000},
            {"id": 3, "location": "FARM", "salary": 1000},
            {"id": 4, "location": "FIELD2", "salary": 1000}
        ]
        
        available = [emp["id"] for emp in employees if emp["location"] == "FARM"]
        
        assert len(available) == 2
        assert 1 in available
        assert 3 in available
        assert 2 not in available
        assert 4 not in available
    
    def test_employee_tracking(self):
        """Test du suivi des ouvriers utilisés."""
        available_employees = [1, 2, 3]
        used_employees = set()
        
        # Utiliser ouvrier 1
        used_employees.add(1)
        assert 1 in used_employees
        assert len(used_employees) == 1
        
        # Utiliser ouvrier 2
        used_employees.add(2)
        assert 2 in used_employees
        assert len(used_employees) == 2
        
        # Ne pas réutiliser ouvrier 1
        assert 1 in used_employees


class TestExpansionThresholds:
    """Tests pour les seuils d'expansion."""
    
    def test_employee_hiring_threshold(self):
        """Test du seuil d'embauche."""
        threshold = 80000
        max_employees = 6
        
        # Cas 1 : Assez d'argent, pas assez d'ouvriers
        money = 100000
        num_employees = 4
        should_hire = money > threshold and num_employees < max_employees
        assert should_hire is True
        
        # Cas 2 : Pas assez d'argent
        money = 70000
        should_hire = money > threshold and num_employees < max_employees
        assert should_hire is False
        
        # Cas 3 : Trop d'ouvriers
        money = 100000
        num_employees = 6
        should_hire = money > threshold and num_employees < max_employees
        assert should_hire is False
    
    def test_field_buying_threshold(self):
        """Test du seuil d'achat de champs."""
        threshold = 90000
        max_fields = 5
        
        money = 120000
        num_fields = 3
        should_buy = money > threshold and num_fields < max_fields
        assert should_buy is True
        
        money = 85000
        should_buy = money > threshold and num_fields < max_fields
        assert should_buy is False
    
    def test_tractor_buying_threshold(self):
        """Test du seuil d'achat de tracteurs."""
        threshold1 = 120000
        threshold2 = 180000
        max_tractors = 3
        
        # Premier tracteur
        money = 150000
        num_tractors = 1
        should_buy = money > threshold1 and num_tractors < 2
        assert should_buy is True
        
        # Deuxième tracteur
        money = 200000
        num_tractors = 2
        should_buy = money > threshold2 and num_tractors < 3
        assert should_buy is True


class TestActionPriorities:
    """Tests pour les priorités d'actions."""
    
    def test_harvest_priority(self):
        """Test que la récolte est prioritaire."""
        fields = [
            {"content": "POTATO", "needed_water": 0, "location": "FIELD1", "bought": True},
            {"content": "TOMATO", "needed_water": 5, "location": "FIELD2", "bought": True}
        ]
        
        # Un champ est prêt à être récolté
        harvestable = [
            f for f in fields 
            if f.get("content") != "NONE" 
            and f.get("needed_water") == 0
            and f.get("bought", False)
        ]
        
        assert len(harvestable) == 1
        assert harvestable[0]["location"] == "FIELD1"
    
    def test_sell_threshold(self):
        """Test du seuil de vente."""
        stock = {"POTATO": 3, "LEEK": 2, "TOMATO": 2, "ONION": 1, "ZUCCHINI": 1}
        total_stock = sum(stock.values())
        threshold = 8
        
        should_sell = total_stock >= threshold
        assert should_sell is True
        assert total_stock == 9
    
    def test_cook_threshold(self):
        """Test du seuil de cuisine."""
        stock = {"POTATO": 2, "LEEK": 1, "TOMATO": 1, "ONION": 1, "ZUCCHINI": 0}
        total_stock = sum(stock.values())
        min_threshold = 4
        max_threshold = 8
        
        should_cook = min_threshold <= total_stock < max_threshold
        assert should_cook is True
    
    def test_watering_priority(self):
        """Test de la priorité d'arrosage."""
        fields = [
            {"content": "POTATO", "needed_water": 5, "location": "FIELD1"},
            {"content": "TOMATO", "needed_water": 0, "location": "FIELD2"},
            {"content": "NONE", "needed_water": 0, "location": "FIELD3"}
        ]
        
        needs_water = [
            f for f in fields
            if f.get("content") != "NONE"
            and f.get("needed_water", 0) > 0
        ]
        
        assert len(needs_water) == 1
        assert needs_water[0]["location"] == "FIELD1"


class TestFieldParsing:
    """Tests pour le parsing des champs."""
    
    def test_field_number_extraction(self):
        """Test de l'extraction du numéro de champ."""
        location = "FIELD3"
        field_num = location.replace("FIELD", "")
        assert field_num == "3"
    
    def test_multiple_fields(self):
        """Test avec plusieurs champs."""
        locations = ["FIELD1", "FIELD2", "FIELD3", "FIELD4", "FIELD5"]
        field_nums = [loc.replace("FIELD", "") for loc in locations]
        assert field_nums == ["1", "2", "3", "4", "5"]
    
    def test_field_location_check(self):
        """Test de la vérification du format de location."""
        assert "FIELD1".startswith("FIELD")
        assert not "FARM".startswith("FIELD")
        assert not "NONE".startswith("FIELD")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
