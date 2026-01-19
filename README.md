# Chronobio - Client de jeu

Client pour le jeu Chronobio, un jeu de simulation de production de soupe bio.

## Installation

### Prérequis

- Python 3.11 ou supérieur
- pip

### Installation des dépendances

```bash
# Créer un environnement virtuel
python -m venv .venv

# Activer l'environnement virtuel (Windows)
.venv\Scripts\activate

# Installer les dépendances
pip install -r requirements.txt
```

## Lancer le jeu

**IMPORTANT** : Le serveur Chronobio attend **5 joueurs** avant de démarrer la partie.

### Solution simple : Utiliser le script automatique

```powershell
.\lancer_5clients.ps1
```

Ce script lance automatiquement :
- 1 serveur
- 1 viewer (interface graphique)
- 5 clients (dont le vôtre)

### Lancement manuel (optionnel)

Si vous préférez lancer les composants manuellement ou personnaliser le nombre de clients :

**1. Activer l'environnement virtuel (dans chaque terminal) :**
```powershell
.venv\Scripts\activate
```

**2. Lancer le serveur (terminal 1) :**
```bash
python -m chronobio.game.server -p 16210
```

**3. Lancer le viewer (terminal 2) :**
```bash
python -m chronobio.viewer -p 16210 --width 1100 --height 700
```

**4. Lancer votre client (terminal 3) :**
```bash
python -m chronobio_client -a localhost -p 16210 -u mugiwara
```

**5. Lancer 4 autres clients (terminaux 4-7) :**
```bash
# Terminal 4
python -m chronobio_client -a localhost -p 16210 -u Client2

# Terminal 5
python -m chronobio_client -a localhost -p 16210 -u Client3

# Terminal 6
python -m chronobio_client -a localhost -p 16210 -u Client4

# Terminal 7
python -m chronobio_client -a localhost -p 16210 -u Client5
```

**Notes importantes :**
- Attendez 2-3 secondes entre chaque lancement
- Le serveur démarre la partie **uniquement quand 5 clients** sont connectés
- Pour changer le nom de votre ferme, modifiez le paramètre `-u mugiwara`
- Pour changer le port, modifiez `-p 16210` (doit être identique partout)

### Résultat

Vous verrez **7 fenêtres CMD** s'ouvrir :
1. **Serveur** - Traite les actions
2. **Viewer** - Interface graphique (👉 REGARDEZ CETTE FENÊTRE)
3. **mugiwara** - Votre client avec votre stratégie
4-7. **Client2-5** - Clients factices pour démarrer le jeu

### Où voir les actions ?

**Dans la fenêtre "Viewer" (interface graphique) :**
- Cherchez le panneau **"Events"** sur le côté
- Vous verrez toutes les actions en temps réel :
  ```
  client: 0 ACHETER_CHAMP
  client: 0 EMPLOYER
  client: 1 SEMER PATATE 1
  client: 1 ARROSER 1
  ...
  ```

**Dans la fenêtre "mugiwara" :**
- L'état de votre ferme à chaque tour
- Les actions envoyées au serveur

### Arrêter le jeu

Fermez toutes les fenêtres CMD ou utilisez :
```powershell
Stop-Process -Name python -Force
```

## Structure du projet

```
chronobio_client/
├── chronobio_client/
│   ├── __init__.py
│   ├── __main__.py        # Point d'entrée
│   └── client.py          # Client + STRATÉGIE (MODIFIEZ ICI)
├── lancer_5clients.ps1    # Script de lancement
├── requirements.txt       # Dépendances
└── README.md
```

## 🎯 Stratégie actuelle : AGRESSIVE & OPTIMISÉE

### Vue d'ensemble

La stratégie actuelle vise la **croissance rapide** et la **domination** :
- **Expansion massive** : 5 champs, 8 ouvriers, 3 tracteurs
- **Production parallèle** : Tous les champs travaillés simultanément
- **Focus POIREAU** : 43% des semailles (légume prioritaire)
- **Cycle complet** : Semer → Arroser → Récolter → Cuisiner → Vendre

### Phase 1 : Démarrage agressif (Jours 0-5)

```
Jour 0: EMPRUNTER 100k → ACHETER_CHAMP x3
Jour 1: EMPLOYER x3 → ACHETER_TRACTEUR
Jour 2: SEMER (PATATE, TOMATE, OIGNON) sur 3 champs
Jour 3: ACHETER_CHAMP x2 → Total 5 champs!
Jour 4: EMPLOYER x2 → Total 5 ouvriers!
Jour 5: SEMER (POIREAU, COURGETTE) sur les nouveaux champs
```

### Phase 2 : Production continue (Jour 6+)

**Priorités d'actions (dans l'ordre) :**

1. **RÉCOLTER** (STOCKER) les légumes mûrs
   - Condition : `needed_water == 0` et `content != "NONE"`
   - Nécessite un tracteur

2. **VENDRE** les soupes
   - Condition : Stock >= 15 légumes
   - Génère des revenus importants

3. **CUISINER** des soupes
   - Condition : Stock >= 5 légumes
   - Augmente la valeur des légumes

4. **ARROSER** tous les champs
   - Condition : `needed_water > 0`
   - Tous les champs arrosés en parallèle

5. **SEMER** sur tous les champs vides
   - Rotation : POIREAU (43%), PATATE, TOMATE, OIGNON, COURGETTE
   - Tous les champs semés en parallèle

6. **EXPANSION**
   - Embaucher si argent > 70k (max 8 ouvriers)
   - Acheter champs si argent > 80k (max 5)
   - Acheter tracteurs si argent > 90k (max 3)
   - Emprunter 50k si argent < 50k (tous les 20 jours)

### Modifier la stratégie

Ouvrez `chronobio_client/client.py` et cherchez la méthode `run()` dans la classe `PlayerGameClient`.

**Exemples de modifications :**

#### Changer les seuils d'expansion

```python
# Plus agressif (risqué mais rapide)
if money > 50000 and num_employees < 10:  # Au lieu de 70000 et 8
    self.add_command("0 EMPLOYER")

# Plus conservateur (stable mais lent)
if money > 120000 and num_employees < 5:  # Au lieu de 70000 et 8
    self.add_command("0 EMPLOYER")
```

#### Changer les légumes prioritaires

```python
# Favoriser TOMATE au lieu de POIREAU
vegetables = ["TOMATE", "TOMATE", "TOMATE", "PATATE", "OIGNON", "POIREAU", "COURGETTE"]

# Rotation équilibrée (tous égaux)
vegetables = ["PATATE", "TOMATE", "OIGNON", "POIREAU", "COURGETTE"]
```

#### Ajuster la gestion des soupes

```python
# Cuisiner plus tôt (production rapide)
if total_stock >= 3:  # Au lieu de 5
    self.add_command(f"{emp_id} CUISINER")

# Vendre moins (accumuler du stock)
if total_stock >= 25:  # Au lieu de 15
    self.add_command(f"{emp_id} VENDRE")
```

### Actions disponibles

Format : `"ID_OUVRIER ACTION PARAMÈTRES"`

```python
# Actions d'investissement (ID_OUVRIER = 0)
self.add_command("0 ACHETER_CHAMP")
self.add_command("0 EMPLOYER")
self.add_command("0 ACHETER_TRACTEUR")
self.add_command("0 EMPRUNTER 50000")

# Actions de production (nécessitent un ouvrier disponible)
self.add_command(f"{emp_id} SEMER PATATE {field_num}")
self.add_command(f"{emp_id} ARROSER {field_num}")
self.add_command(f"{emp_id} STOCKER {field_num} 1")  # 1 = ID tracteur
self.add_command(f"{emp_id} CUISINER")
self.add_command(f"{emp_id} VENDRE")
```

**IMPORTANT** : Un ouvrier occupé (`location != "FARM"`) ne peut pas recevoir de nouvelle action !

## Problèmes courants

### Le jeu ne démarre pas
- **Vérifiez que 5 clients sont lancés** : Le serveur attend 5 joueurs
- Utilisez `.\lancer_5clients.ps1` qui lance tout automatiquement
- Si problème persiste : `Stop-Process -Name python -Force` puis relancez

### Les fermes se bloquent rapidement
**Causes possibles :**
- Trop d'ouvriers = salaires trop élevés
- Pas assez de récoltes = pas de revenus
- Emprunts trop nombreux = intérêts élevés

**Solutions :**
```python
# Dans client.py, réduire les seuils d'expansion :

# Au lieu de :
if money > 70000 and num_employees < 8:

# Mettre :
if money > 100000 and num_employees < 5:
```

### Score n'augmente pas assez vite
**Optimisations possibles :**
- Réduire les seuils d'embauche (plus d'ouvriers = plus de production)
- Augmenter la fréquence de vente (`if total_stock >= 10` au lieu de 15)
- Favoriser les légumes rentables (plus de POIREAU)

### Erreur "Employee is already busy"
- **Normal** : Un ouvrier qui travaille ne peut pas recevoir de nouvelle action
- La stratégie actuelle vérifie `location == "FARM"` pour éviter ce problème
- Si erreur persiste, vérifiez que vous utilisez bien `available_employees`

### Actions pas visibles dans le Viewer
- Vérifiez le **panneau "Events"** sur le côté droit
- Si vide : Le serveur n'a peut-être pas démarré correctement
- Solution : Fermez tout et relancez `.\lancer_5clients.ps1`

### Performances et résultats

**Stratégie AGRESSIVE actuelle :**
- ✅ Démarrage rapide (5 champs, 5 ouvriers en 5 jours)
- ✅ Production massive (tous champs travaillés en parallèle)
- ✅ Score croissant (ventes de soupes régulières)
- ⚠️ Risqué (emprunt initial, salaires élevés)

**Si vous voulez plus de stabilité :**
- Augmentez les seuils d'argent (100k au lieu de 70k)
- Réduisez le nombre max d'ouvriers (5 au lieu de 8)
- Supprimez l'emprunt initial du jour 0

## 🧪 Tests

Le projet inclut une suite complète de tests unitaires.

### Lancer les tests

**Solution simple (Windows) :**
```powershell
.\lancer_tests.ps1
```

**Ou manuellement :**
```bash
# Installer les dépendances de test
pip install pytest pytest-cov pytest-mock

# Lancer tous les tests
pytest

# Avec rapport de couverture
pytest --cov=chronobio_client --cov-report=html

# Voir le rapport
start htmlcov/index.html
```

### Ce qui est testé

- ✅ **Gestion des commandes** (ajout, envoi, format)
- ✅ **Équilibrage des légumes** (tri par rareté, priorités)
- ✅ **Gestion des ouvriers** (disponibilité, suivi d'utilisation)
- ✅ **Seuils d'expansion** (embauche, achat champs/tracteurs)
- ✅ **Priorités d'actions** (récolte, vente, cuisine, arrosage)
- ✅ **Parsing des champs** (extraction numéros, validation)

### Résultats attendus

```
========================= test session starts =========================
collected 25 items

tests/test_client.py ......................                    [100%]

========================= 25 passed in 0.15s =========================
```

Plus de détails dans `tests/README.md`.

## Support

Pour toute question, consultez la documentation officielle de Chronobio.
