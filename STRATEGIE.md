# Stratégie ULTRA-SAFE - Production de légumes

## 🎯 Objectif
Ne **JAMAIS** bloquer (une seule erreur INVALID_ACTION = blocage permanent !)

## 🏗️ Setup initial (jours 1-2)

### Jour 1
- Acheter 3 champs (15 000€)
- Acheter 1 tracteur (30 000€)
- **Capital restant** : ~55 000€

### Jour 2
- Embaucher 3 employés d'un coup (30 000€)
- **Capital restant** : ~25 000€

**Pourquoi 3 employés ?**
- Avec 3 employés, il y en aura toujours 1-2 à la FARM
- Quand certains sont occupés dans les champs, d'autres restent disponibles
- **Zéro risque** d'erreur INVALID_ACTION

## 📊 Production (jour 3+)

### Priorités
1. **ARROSER** - Les légumes doivent pousser !
2. **RÉCOLTER + STOCKER** - Accumulation de stock
3. **SEMER** - Rotation intelligente (semer ce qui manque)
4. **VENDRE** - Cash immédiat si urgence (< 40 jours de salaires)
5. **CUISINER** - Seulement si capital > 50k€ ET stock > 200
6. **EMBAUCHER** - Seulement si capital > 100k€

### Règles de sécurité
- ✅ Utiliser SEULEMENT les employés à `location == "FARM"`
- ✅ Ne jamais utiliser un employé déjà occupé
- ✅ Ne jamais utiliser un tracteur déjà assigné
- ✅ Tracker tous les employés/tracteurs utilisés dans un tour

## 💰 Budget prévisionnel

```
Jour 1 : 100 030€ → 55 030€ (3 champs + 1 tracteur)
Jour 2 :  55 030€ → 22 030€ (3 employés + salaires)
Jour 3 :  22 030€ → 19 030€ (salaires 3000€/jour)
Jour 10:  ~10 000€ (salaires continus)
Jour 15:  Première récolte → +stock
Jour 20:  Stock > 100 → Vente ou cuisine
Jour 30+: Production stable
```

## 🎮 Lancement

### Test rapide (1 joueur, 100 jours)
```powershell
.\test_strategy_live.ps1
```

### Jeu complet (5 joueurs)
```powershell
.\lancer_5clients.ps1
```

## 📈 Résultats attendus

- ✅ **Survie** : Pas de blocage avant jour 100+
- ✅ **Production** : Stock qui se remplit progressivement
- ✅ **Score** : 50 000€ - 200 000€ selon la compétition
- ✅ **Stabilité** : Zéro erreur INVALID_ACTION

## ⚠️ Points d'attention

1. **Les employés restent dans les champs** après avoir travaillé
   - Solution : En avoir 3+ pour toujours en avoir à FARM

2. **L'arrosage prend du temps** (10 jours par légume)
   - Solution : Arroser en priorité dès le début

3. **Le transport (STOCKER) prend plusieurs jours**
   - Solution : Anticiper et ne pas compter sur le stock immédiat

4. **Les salaires augmentent chaque mois** (+1%)
   - Solution : Générer des revenus réguliers (vente ou cuisine)

## 🏴‍☠️ La clé du succès

**PATIENCE** : Les légumes prennent 10+ jours à pousser. Ne pas paniquer si rien ne se passe les 15 premiers jours !
