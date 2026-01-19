# Tests Chronobio Client

Suite de tests complète pour le client Chronobio.

## Installation des dépendances de test

```bash
pip install -r requirements.txt
```

## Lancer tous les tests

```bash
# Depuis la racine du projet
pytest

# Avec rapport de couverture
pytest --cov=chronobio_client --cov-report=html

# Mode verbose
pytest -v

# Avec détails complets
pytest -vv
```

## Lancer des tests spécifiques

```bash
# Un seul fichier
pytest tests/test_client.py

# Une seule classe
pytest tests/test_client.py::TestPlayerGameClient

# Un seul test
pytest tests/test_client.py::TestPlayerGameClient::test_add_command

# Tests par marqueur
pytest -m unit
pytest -m integration
```

## Structure des tests

### `test_client.py`

- **TestPlayerGameClient** : Tests de base du client
  - `test_add_command()` : Ajout de commandes
  - `test_send_commands_format()` : Format d'envoi
  
- **TestVegetableBalancing** : Tests d'équilibrage des légumes
  - `test_stock_counting()` : Comptage du stock
  - `test_vegetable_priority_sorting()` : Tri par rareté
  
- **TestEmployeeManagement** : Tests de gestion des ouvriers
  - `test_available_employees_filtering()` : Filtrage des disponibles
  - `test_employee_tracking()` : Suivi d'utilisation
  
- **TestExpansionThresholds** : Tests des seuils d'expansion
  - `test_employee_hiring_threshold()` : Seuil embauche
  - `test_field_buying_threshold()` : Seuil achat champs
  - `test_tractor_buying_threshold()` : Seuil achat tracteurs
  
- **TestActionPriorities** : Tests des priorités d'actions
  - `test_harvest_priority()` : Récolte prioritaire
  - `test_sell_threshold()` : Seuil de vente
  - `test_cook_threshold()` : Seuil de cuisine
  
- **TestFieldParsing** : Tests de parsing des champs
  - `test_field_number_extraction()` : Extraction numéro

## Couverture de code

Après avoir lancé les tests avec `--cov`, ouvrez le rapport HTML :

```bash
# Windows
start htmlcov/index.html

# Linux/Mac
open htmlcov/index.html
```

## Résultats attendus

```
========================= test session starts =========================
collected 25 items

tests/test_client.py::TestPlayerGameClient::test_add_command PASSED
tests/test_client.py::TestPlayerGameClient::test_send_commands_format PASSED
tests/test_client.py::TestVegetableBalancing::test_stock_counting PASSED
...
========================= 25 passed in 0.15s =========================
```

## Ajouter de nouveaux tests

1. Créer une nouvelle classe `TestXXX` dans `test_client.py`
2. Ajouter des méthodes `test_xxx()`
3. Utiliser `assert` pour vérifier les résultats
4. Lancer `pytest` pour valider

Exemple :

```python
class TestMyFeature:
    """Tests pour ma nouvelle fonctionnalité."""
    
    def test_something(self):
        """Test de quelque chose."""
        result = my_function(42)
        assert result == 84
```

## Bonnes pratiques

- ✅ Un test = une fonctionnalité testée
- ✅ Noms descriptifs (`test_employee_hiring_threshold`)
- ✅ Docstrings explicites
- ✅ Tests indépendants (pas d'ordre requis)
- ✅ Assertions claires et simples
- ✅ Couverture > 80%
