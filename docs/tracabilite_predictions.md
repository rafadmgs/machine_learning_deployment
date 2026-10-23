# Traçabilité des prédictions

## Objectif

Chaque appel réussi à `POST /predict` conserve les données utilisées et le résultat produit par le modèle. Cette organisation permet de relier une prédiction à son entrée enregistrée.

## Tables concernées

### `employees`

Contient les données des employés importées depuis `data/processed/df_central.csv`. La clé primaire est `id_employee`.

### `prediction_inputs`

| Champ | Rôle |
|---|---|
| `id` | Identifiant de l'entrée enregistrée |
| `employee_id` | Référence facultative vers `employees.id_employee` |
| `input_data` | Données de la requête sérialisées en JSON |
| `created_at` | Date et heure de création |

Dans l'implémentation actuelle de `/predict`, `employee_id` n'est pas renseigné : les données de la requête sont enregistrées dans `input_data`.

### `prediction_outputs`

| Champ | Rôle |
|---|---|
| `id` | Identifiant du résultat |
| `prediction_input_id` | Référence obligatoire vers `prediction_inputs.id` |
| `prediction` | Classe prédite |
| `probability` | Probabilité associée à la classe prédite |
| `created_at` | Date et heure de création |

## Relation entre entrée et résultat

La clé étrangère `prediction_outputs.prediction_input_id` relie le résultat à l'entrée correspondante. L'API enregistre l'entrée, récupère son identifiant, puis enregistre le résultat lié avant de valider la transaction.

## Gestion des erreurs

En cas d'exception pendant le traitement de la prédiction, l'API appelle `rollback()` et retourne une erreur HTTP 500. Le détail technique de l'exception n'est pas exposé dans la réponse client.

## Points de vigilance

- Les données de requête sont conservées dans la base : limiter l'accès à ces données.
- Définir une politique de conservation et de suppression adaptée.
- Protéger les sauvegardes et les identifiants de connexion.
- L'identifiant de prédiction permet de retrouver le résultat, mais l'API actuelle ne propose pas d'endpoint de consultation de l'historique.
