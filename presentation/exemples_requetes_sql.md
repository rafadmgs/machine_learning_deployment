
# Exemples de requêtes SQL et résultats

Les exemples ci-dessous illustrent les données stockées dans les trois tables principales de la base PostgreSQL.

## 1. Table EMPLOYEES

### Requête SQL

```sql
SELECT
    id_employee,
    age,
    departement,
    poste,
    annees_dans_l_entreprise,
    a_quitte_l_entreprise
FROM employees
WHERE id_employee = 1;
```

### Résultat

| id_employee | age | departement | poste | annees_dans_l_entreprise | a_quitte_l_entreprise |
|---:|---:|---|---|---:|---|
| 1 | 41 | Commercial | Cadre Commercial | 6 | Oui |

## 2. Table PREDICTION_INPUTS

### Requête SQL

```sql
SELECT
    id,
    employee_id,
    created_at
FROM prediction_inputs
WHERE id = 58;
```

### Résultat

| id | employee_id | created_at |
|---:|---:|---|
| 58 | 1 | 2026-11-13 15:42:50 |

Cette table conserve les données utilisées comme entrée du modèle. Le champ `input_data` contient les variables au format JSON.

## 3. Table PREDICTION_OUTPUTS

### Requête SQL

```sql
SELECT
    id,
    prediction_input_id,
    prediction,
    probability,
    model_version,
    inference_time_ms,
    created_at
FROM prediction_outputs
WHERE id = 58;
```

### Résultat

| id | prediction_input_id | prediction | probability | model_version | inference_time_ms |
|---:|---:|---|---:|---|---:|
| 58 | 58 | Oui | 0.8443 | 1.0.0 | 41.86 |

La probabilité de départ prédite est de 84,43 %. Le modèle utilisé est la version 1.0.0 et le temps d'inférence enregistré est de 41,86 ms.

## 4. Jointure des trois tables

Cette requête permet de retrouver les informations du salarié, l'entrée utilisée et le résultat de la prédiction dans une seule consultation.

```sql
SELECT
    e.id_employee,
    e.departement,
    e.poste,
    pi.id AS input_id,
    po.id AS output_id,
    po.prediction,
    po.probability,
    po.model_version,
    po.inference_time_ms
FROM prediction_outputs po
JOIN prediction_inputs pi
    ON pi.id = po.prediction_input_id
LEFT JOIN employees e
    ON e.id_employee = pi.employee_id
WHERE po.id = 58;
```

### Résultat

| id_employee | departement | poste | input_id | output_id | prediction | probability | model_version | inference_time_ms |
|---:|---|---|---:|---:|---|---:|---|---:|
| 1 | Commercial | Cadre Commercial | 58 | 58 | Oui | 0.8443 | 1.0.0 | 41.86 |
