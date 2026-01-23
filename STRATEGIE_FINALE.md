# 🏴‍☠️ Stratégie Finale - Mugiwara Farm

## 🎯 Principe Fondamental

**Un employé n'est disponible QUE s'il est à la FARM**

### Pourquoi ?

Les employés **ne reviennent PAS automatiquement** à la FARM après une action. Ils restent sur place (FIELD1, FIELD2, SOUP_FACTORY, etc.) jusqu'à ce qu'ils aient fini leur tâche.

**Problèmes constatés** :
- Jour 1317 : 4 employés, 0 à FARM, 0 actions possibles
- Ferme paralysée pendant 1300+ jours
- Tracteur bloqué par un employé occupé

## ✅ Nouvelle Stratégie

### Setup Initial

```
Jour 1 : Acheter 2 champs + 1 tracteur (60k€)
Jour 2 : Embaucher 6 ouvriers (6k€)
```

**Salaires** : 6,000€/jour (gérable avec 50k€)

### Critère de Disponibilité

```python
if location == "FARM" and tractor is None:
    # Employé disponible !
```

**Avantages** :
- ✅ 100% sûr : l'employé a fini son action précédente
- ✅ Pas de risque "ALREADY_BUSY"
- ✅ Pas de cooldown compliqué

### Rotation Naturelle

Avec 6 employés et 2 champs :
- Certains employés reviennent à FARM après avoir terminé
- D'autres sont en mission (SEMER, ARROSER, STOCKER)
- Il y a **toujours** 1-2 employés disponibles à FARM

## 🔄 Cycle de Production

### Actions Prioritaires

1. **ARROSER** - Les légumes doivent pousser (10x)
2. **RÉCOLTER** - Stocker quand mûr (+2000 légumes)
3. **SEMER** - Rotation : PATATE → OIGNON → TOMATE → COURGETTE → POIREAU
4. **CUISINER** - Seulement si stock > 5000

### Exemple de Cycle

```
Jour 3  : Emp#1 SEMER PATATE champ 1 (va à FIELD1)
Jour 4  : Emp#2 ARROSER champ 1 (va à FIELD1)
Jour 5  : Emp#3 ARROSER champ 1 (va à FIELD1)
...
Jour 13 : Emp#1 revient à FARM (action terminée)
Jour 13 : Emp#4 ARROSER champ 1 (dernier arrosage)
Jour 14 : Emp#2 revient à FARM
Jour 14 : Emp#5 STOCKER champ 1 avec tracteur 1
...
Jour 16 : Emp#5 revient à FARM avec tracteur
Jour 16 : Emp#1 SEMER TOMATE champ 1 (nouveau cycle)
```

## 📊 Résultats Attendus

### Avant (Stratégie avec cooldown)
- ❌ 0 employés à FARM après 1317 jours
- ❌ Ferme paralysée
- ❌ Stock stagnant (2000 légumes max)
- ❌ Score : 938€

### Après (Stratégie FARM ONLY)
- ✅ Toujours 1-2 employés disponibles
- ✅ Production continue
- ✅ Stock croissant (rotation 5 légumes)
- ✅ Score progressif

## 🚀 Expansion Progressive

| Condition | Action |
|-----------|--------|
| 50k€ + 1000 légumes | +1 champ, +2 ouvriers |
| 80k€ + 2000 légumes | +1 champ, +1 tracteur, +2 ouvriers |
| 120k€ + 3000 légumes | +1 champ, +2 ouvriers |

**Total maximal** : 5 champs, 12 ouvriers, 3 tracteurs

## ⚠️ Erreurs à Éviter

1. ❌ **Ne PAS utiliser un employé qui n'est pas à FARM**
   → Risque "ALREADY_BUSY"

2. ❌ **Ne PAS utiliser un tracteur occupé**
   → Vérifié automatiquement (tracteur référencé par employé)

3. ❌ **Ne PAS embaucher trop tôt**
   → Salaires exponentiels (augmentation 1%/mois)

4. ❌ **Ne PAS stocker sans tracteur**
   → Transport impossible

## 🎯 Objectif : 5 Ans

**5 ans = 1800 jours**

Avec production optimale :
- ~50 cycles complets (15-20 jours/cycle)
- ~100,000 légumes stockés
- Soupes diversifiées (5-8€/soupe)
- **Score final estimé : 200,000€+**

---

**La ferme Mugiwara est prête à dominer pendant 5 ans !** 🏴‍☠️
