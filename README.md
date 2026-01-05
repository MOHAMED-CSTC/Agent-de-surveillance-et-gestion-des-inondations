# 🌊 Agent Intelligent de Surveillance et de Gestion des Inondations

## 📌 Présentation du projet

Ce projet implémente un **agent intelligent basé sur l'utilité**, destiné à la **surveillance en temps réel des zones à risque d'inondation** et à l'**optimisation des interventions d'urgence** (évacuation et déplacement des équipes de secours).

Il s'appuie sur :

* une **modélisation PEAS complète**,
* un **graphe de zones géographiques** avec coûts multi-critères,
* plusieurs **algorithmes de recherche** (BFS, DFS, UCS, A*),
* une **architecture agent–environnement** inspirée de l'IA classique.

Le système permet de déterminer **les chemins les plus sûrs et efficaces** en tenant compte :

* du risque d'inondation,
* de la distance,
* du temps,
* de l'urgence,
* de la population exposée.

---

## 🎯 Objectifs

* Surveiller les niveaux d'eau et les zones critiques
* Prioriser les interventions d'urgence
* Planifier des itinéraires optimaux pour les équipes de secours
* Comparer différents algorithmes de recherche
* Simuler le comportement d'un agent de secours autonome

---

## 🧠 Type d'agent

**Agent basé sur l'utilité avec composante apprenante (conceptuelle)**

L'agent optimise une fonction de coût intégrant plusieurs critères conflictuels :

[ U = -\alpha·distance - \beta·risque - \gamma·temps - \delta·urgence + \varepsilon·population ]

➡️ Le compromis sécurité / rapidité / impact humain est au cœur de la décision.

---

## 🌍 Environnement

* **Partiellement observable**
* **Stochastique** (météo, montée des eaux)
* **Dynamique**
* **Séquentiel**
* **Mixte (discret / continu)**
* **Multi-agent**

L'environnement est modélisé sous forme de **graphe pondéré**.

---

## 🗺️ Graphe des zones

* **12 zones** (centre de secours, zones résidentielles, hôpital, école, pont, refuge, etc.)
* **17 connexions bidirectionnelles**
* Chaque arête possède :

  * distance (km)
  * risque (0–10)
  * temps (minutes)

Le **coût composite** est défini par :

```
coût = distance + 2 × risque + 0.5 × temps
```

---

## 🔍 Algorithmes implémentés

| Algorithme | Description                                 |
| ---------- | ------------------------------------------- |
| BFS        | Recherche en largeur (non optimale en coût) |
| DFS        | Recherche en profondeur (limitée)           |
| UCS        | Recherche à coût uniforme (optimale)        |
| A*         | Recherche informée (g + heuristique)        |

➡️ **A*** est recommandé pour ce problème (rapide et optimal).

---

## 🧩 Architecture logicielle

### Principales classes

* `GrapheInondations` : réseau de zones et coûts
* `ProblemeRecherche` : formalisation IA du problème
* `Noeud` : nœud de l'arbre de recherche
* `AgentSecours` : agent autonome
* `EnvironnementInondation` : environnement dynamique
* `CapteurInondation` : perception
* `ActionneurSecours` : exécution des actions

---

## 🚀 Exécution du programme

### Prérequis

* Python **3.8+**
* Aucun module externe requis

### Lancer la simulation

```bash
python main.py
```

---

## 📊 Sorties du programme

1. **Comparaison des algorithmes**

   * coût total
   * nombre de nœuds explorés
   * temps d'exécution

2. **Simulation agent–environnement**

   * affichage du plan calculé
   * déplacements successifs de l'agent
   * performance finale

Exemple :

```
🤖 Équipe_Alpha - Plan: Centre_Secours → Centre_Ville → Hopital → Refuge_Colline
🚁 Équipe_Alpha: Centre_Secours → Centre_Ville (coût: 12.0)
🚁 Équipe_Alpha: Centre_Ville → Hopital (coût: 7.5)
🚁 Équipe_Alpha: Hopital → Refuge_Colline (coût: 13.0)
```

---

## ✅ Résultats clés

* L'agent atteint toujours le refuge par un **chemin sûr et optimisé**
* A* explore moins de nœuds que UCS
* Le modèle est facilement extensible (multi-agents, apprentissage, mise à jour temps réel)

---

## 🔮 Améliorations possibles

* Apprentissage par renforcement (Q-learning, MDP)
* Évolution dynamique du niveau d'eau pendant la simulation
* Coordination de plusieurs agents de secours
* Intégration de vraies données météo
* Visualisation graphique du graphe

---

## 👨‍💻 Auteur

Projet académique – **Intelligence Artificielle / Systèmes Multi-Agents**

---

## 📄 Licence

Projet fourni à des fins **pédagogiques et de démonstration**.
