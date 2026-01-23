# 🌱 Cycle de Base - Ferme Mugiwara

## 📋 Stratégie Minimaliste

### Phase 1 : Démarrage (2 champs, 2 ouvriers)

```
Jour 1 : Acheter 2 champs + 1 tracteur
Jour 2 : Embaucher 2 ouvriers
Jour 3 : Démarrage du cycle
```

## 🔄 Le Cycle en 3 Étapes

### 1️⃣ SEMER (Rotation automatique)

- **Champ 1** : PATATE
- **Champ 2** : OIGNON
- Puis : TOMATE → COURGETTE → POIREAU → PATATE → ...

**Rotation** : Les 5 légumes alternent pour avoir de la diversité

### 2️⃣ ARROSER (Faire pousser)

- Arroser **10 fois** chaque champ
- Les légumes poussent progressivement
- `needed_water` diminue de 10 → 0

**Priorité** : Arroser en premier pour accélérer la croissance

### 3️⃣ RÉCOLTER (Stocker)

- Quand `needed_water = 0`, le champ est mûr
- Un ouvrier + tracteur vont **STOCKER** le champ
- **+2000 légumes** ajoutés au stock de l'usine
- Le champ redevient vide (`NONE`)

**Puis on recommence le cycle !**

## 📊 Exemple de Cycle Complet

```
Jour 3  : SEMER PATATE champ 1
Jour 4  : ARROSER champ 1 (eau: 10→9)
Jour 5  : ARROSER champ 1 (eau: 9→8)
...
Jour 13 : ARROSER champ 1 (eau: 1→0) ✅ MÛR!
Jour 14 : STOCKER champ 1 → +2000 PATATE
Jour 15 : SEMER TOMATE champ 1 (rotation continue)
```

## 🎯 Avantages de cette Stratégie

✅ **Simple** : Seulement 3 actions (SEMER, ARROSER, STOCKER)
✅ **Stable** : 2000€/jour de salaires (gérable)
✅ **Rotation naturelle** : Diversité automatique pour les soupes
✅ **Pas de blocage** : Employés utilisés seulement s'ils sont à FARM
✅ **Progressive** : Expansion basée sur les résultats

## 📈 Expansion Conditionnelle

| Condition | Action |
|-----------|--------|
| 50k€ + 1000 légumes | +1 champ, +1 ouvrier |
| 80k€ + 2000 légumes | +1 champ, +1 ouvrier |
| 120k€ + 3000 légumes | +1 champ, +1 tracteur, +1 ouvrier |

## 🍲 Cuisine (Bonus)

- Activée seulement si stock > 5000 légumes
- ET diversité complète (500+ de chaque légume)
- Un seul ouvrier cuisine pour ne pas bloquer la production

## 🏴‍☠️ Résumé

**Mugiwara commence petit, construit du stock, puis s'agrandit progressivement !**

```
2 champs → Stock → 3 champs → Plus de stock → 4 champs → 5 champs → VICTOIRE!
```
