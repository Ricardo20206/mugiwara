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

### 🏷️ Personnaliser le nom de votre ferme

Ouvrez `lancer_5clients.ps1` et modifiez la ligne 7 :

```powershell
$NOM_DE_VOTRE_FERME = "mugiwara"  # ← Changez ce nom comme vous voulez!
```

**Exemples :**
```powershell
$NOM_DE_VOTRE_FERME = "ma_ferme"
$NOM_DE_VOTRE_FERME = "BioFarm2026"
$NOM_DE_VOTRE_FERME = "LesFermiersFous"
```

C'est le **seul endroit** où vous devez changer le nom !

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
# Remplacez "mugiwara" par le nom que vous avez choisi
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
- Pour changer le nom : modifiez `-u mugiwara` par votre nom (voir section "Personnaliser le nom")
- Pour changer le port : modifiez `-p 16210` (doit être identique partout)

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

## 🎯 Stratégie actuelle : OPTIMALE - Tous les Légumes + Équilibre

### Vue d'ensemble

La stratégie actuelle combine **production diversifiée** et **durabilité** :
- **🌱 Tous les légumes** : PATATE, TOMATE, POIREAU, OIGNON, COURGETTE
- **⚖️ Équilibre** : 4-5 champs, 5-6 ouvriers (ratio optimal 1.2)
- **🔒 Protection solide** : Buffer 12 jours de salaires
- **📈 Croissance contrôlée** : Expansion basée sur rentabilité
- **🔄 Rotation intelligente** : Sème ce qui manque le plus

### Phase 1 : Démarrage ÉQUILIBRÉ (Jours 0-2)

```
Jour 0: EMPRUNTER 50k + ACHETER 4 champs (diversification)
Jour 1: EMPLOYER x5 + TRACTEUR (bon ratio ouvriers/champs)
Jour 2: SEMER 4 légumes différents (PATATE, TOMATE, POIREAU, OIGNON)
```

**Avantages :**
- Capital modéré pour démarrer (50k emprunt, pas 100k)
- 5 ouvriers pour 4 champs = ratio 1.25 (efficace)
- Diversification dès le départ
- Production de toutes les variétés de soupes

### Phase 2 : Production DIVERSIFIÉE (Jour 3+)

**Priorités d'actions (équilibre production/sécurité) :**

1. **REMBOURSER les dettes** (priorité haute)
   - Rembourser dès que argent > buffer + 80k
   - Réduire les intérêts rapidement

2. **RÉCOLTER TOUS les légumes mûrs** (production maximale)
   - Récolte parallèle de tous les champs prêts
   - Génère stock pour soupes

3. **VENDRE selon situation** (cash flow adaptatif)
   - 🔴 Urgence (< buffer/2) : Vendre dès 5 légumes
   - 🟡 Attention (< buffer*0.8) : Vendre dès 6 légumes
   - 🟢 Normal : Vendre dès 7-8 légumes

4. **CUISINER intelligemment** (transformation optimale)
   - Adapté selon situation financière (3-5 légumes)
   - Production continue de soupes

5. **ARROSER TOUS les champs** (priorité intelligente)
   - Tri par urgence : champs les plus proches de maturation d'abord
   - Arrosage parallèle de tous

6. **SEMER TOUS LES LÉGUMES** (diversification maximale!)
   - 🌱 Rotation de TOUS les légumes : PATATE, TOMATE, POIREAU, OIGNON, COURGETTE
   - Analyse en temps réel : sème ce qui manque le plus
   - Équilibrage automatique du stock
   - Affichage priorité tous les 10 jours

7. **EXPANSION ÉQUILIBRÉE** (croissance contrôlée)
   - Maximum 6 ouvriers, 5 champs
   - Ratio cible : 1.2 ouvriers par champ
   - Embaucher si argent > buffer + 100k
   - Acheter champs si argent > buffer + 120k
   - Tracteurs supplémentaires si argent > buffer + 150k
   - **Buffer = 12 jours de salaires**

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

**Pourquoi une ferme se bloque :**
Une ferme se bloque quand elle n'a **plus assez d'argent pour payer les salaires** à la fin du jour. Les salaires augmentent avec le temps, donc plus vous avez d'ouvriers, plus le risque est élevé.

**La stratégie actuelle inclut une PROTECTION ANTI-BLOCAGE :**

1. **Buffer de sécurité automatique**
   - Calcule 10 jours de salaires en réserve
   - N'embauche/achète que si `argent > buffer + seuil`

2. **Alerte argent critique**
   - Affiche `⚠️ ALERTE` quand il reste moins de 5 jours de salaires
   - Exemple : `⚠️ ALERTE: Argent critique! Seulement 3 jours de salaires restants`

3. **Mode survie automatique**
   - Vend dès 5 légumes (au lieu de 8) si argent < buffer
   - Cuisine dès 3 légumes (au lieu de 4) si argent < buffer
   - Génère des revenus plus rapidement en situation critique

4. **Embauche limitée**
   - Maximum 4 ouvriers (au lieu de 6-8)
   - Seuils élevés : 120 000 EUR + buffer de sécurité
   - Empêche l'accumulation de salaires trop élevés

**Si votre ferme se bloque malgré tout :**
- La partie est perdue pour cette ferme
- Relancez une nouvelle partie
- La stratégie actuelle devrait éviter ce problème

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

**Stratégie OPTIMALE (équilibre production/durabilité) :**
- 🌱 **Diversification** : TOUS les 5 légumes en rotation
- ⚖️ **Équilibre** : 4-5 champs, 5-6 ouvriers (ratio 1.2)
- 🔒 **Protection solide** : Buffer 12 jours (sécurité + croissance)
- 📈 **Expansion intelligente** : Basée sur ratio et rentabilité
- 💰 **Vente adaptative** : 5-8 légumes selon situation

**Caractéristiques :**
- ✅ **Production diversifiée** : Tous les types de soupes possibles
- ✅ **Rotation intelligente** : Sème automatiquement ce qui manque
- ✅ **Récolte parallèle** : Tous les champs en même temps
- ✅ **Croissance contrôlée** : Maximum 6 ouvriers (évite explosion salaires)
- ✅ **Affichage stocks** : Monitoring des 5 légumes tous les 20 jours

**Comparaison stratégies :**

| Stratégie | Production | Diversité | Durabilité | Score |
|-----------|------------|-----------|------------|-------|
| **Minimaliste** (2-3 ouvriers) | 📉 Faible | 🟡 Limitée | ✅ Excellente | Bas |
| **OPTIMALE** (5-6 ouvriers) | 📈 Élevée | ✅ Maximale | ✅ Très bonne | **Élevé** |
| **Aggressive** (8+ ouvriers) | 🚀 Maximale | ✅ Maximale | ❌ Risqué | Très élevé puis crash |

**Résultats attendus :**
- 🎯 **Score élevé ET stable** : Production massive + durabilité
- 🌱 **5 types de légumes** : Diversification maximale
- 🔒 **Blocage rare** : Seulement si salaires explosent (jour 500+)
- 📊 **Performance** : Meilleur équilibre score/durabilité
- 🏆 **Objectif** : Dominer puis survivre

**Affichages utiles :**
```
🌱 Stock: P:12 T:8 Po:15 O:10 C:5  ← Tous les légumes
🌱 Priorité semis: COURGETTE > TOMATE > OIGNON  ← Rotation auto
🟠 Attention: 18 jours de salaires  ← Alertes graduées
```

**Personnalisation :**
- Plus conservateur : `safety_buffer = total_salaries * 15`
- Plus agressif : `MAX_EMPLOYEES = 7` (attention salaires!)
- Focus légume : Modifier priorité dans code semis

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
