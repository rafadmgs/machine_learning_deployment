# Documentation technique du modèle

## Objectif

Le modèle vise à prédire l'attrition d'un employé, c'est-à-dire s'il est susceptible de quitter l'entreprise.

Le modèle et le préprocesseur utilisés par l'API proviennent du travail réalisé dans le projet P4.

## Artefacts

L'API recherche les fichiers suivants dans `output/models/` :

- `lr_optimise.joblib` : modèle entraîné ;
- `preprocessor.joblib` : prétraitement des données d'entrée.

Ces artefacts doivent être présents et compatibles avec l'environnement Python et les bibliothèques installées.

## Modèle retenu

D'après l'évaluation du projet P4, le modèle est une régression logistique avec les paramètres suivants :

| Paramètre | Valeur |
|---|---|
| `C` | `0.01` |
| `solver` | `lbfgs` |
| `class_weight` | `balanced` |
| `max_iter` | `5000` |

Le préprocesseur produit 46 variables après transformation.

## Résultats d'évaluation du projet P4

| Indicateur | Résultat |
|---|---:|
| Accuracy | 0,796 |
| Precision de la classe `Oui` | 0,418 |
| Recall de la classe `Oui` | 0,702 |
| F1-score de la classe `Oui` | 0,524 |
| ROC-AUC | 0,814 |
| Meilleur F1 moyen en validation croisée | 0,5069 |

Le jeu de test contenait 294 observations : 47 de classe `Oui` et 247 de classe `Non`.

## Interprétation

Le recall de 0,702 pour la classe `Oui` indique que le modèle identifie une partie importante des départs observés dans le jeu de test. La précision de 0,418 indique toutefois qu'une proportion des prédictions `Oui` correspond à des cas qui n'ont pas quitté l'entreprise.

L'accuracy ne suffit donc pas à évaluer ce modèle, notamment parce que les classes sont déséquilibrées.

## Limites

- Les performances observées pendant l'évaluation ne garantissent pas les mêmes résultats sur de nouvelles données.
- Une probabilité de prédiction ne constitue pas une certitude.
- Les résultats ne doivent pas être utilisés seuls pour prendre des décisions concernant les employés.
- Les métriques doivent être réévaluées lorsque les données ou le contexte métier évoluent.
