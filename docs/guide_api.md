# Guide d'utilisation de l'API

## Démarrer le serveur

Après configuration de PostgreSQL, création des tables et disponibilité des artefacts :

```bash
python -m uvicorn src.main:app --reload
```

Adresses locales :

- API : `http://127.0.0.1:8000/`
- Documentation interactive : `http://127.0.0.1:8000/docs`
- Schéma OpenAPI : `http://127.0.0.1:8000/openapi.json`

## Endpoints

### `GET /`

Retourne un message indiquant que l'API est opérationnelle et le chemin de la documentation interactive.

### `GET /health`

Retourne un statut simple :

```json
{
  "status": "ok"
}
```

Ce contrôle confirme que l'endpoint répond ; il ne vérifie pas à lui seul la disponibilité de PostgreSQL ou des artefacts.

### `POST /predict`

Reçoit les caractéristiques d'un employé, valide les données, exécute le pipeline et enregistre l'entrée et le résultat dans PostgreSQL.

La requête doit respecter le schéma `PredictionRequest` défini dans `src/schemas.py`. Les types, catégories autorisées et intervalles numériques sont validés par Pydantic.

Pour connaître le schéma exact à jour, consulter `http://127.0.0.1:8000/docs` ou `http://127.0.0.1:8000/openapi.json`.

Exemple de structure de réponse :

```json
{
  "prediction_id": 1,
  "prediction": "Non",
  "probability": 0.5707,
  "message": "Le modèle prédit un maintien."
}
```

Cet exemple illustre la structure de la réponse ; les valeurs dépendent des données transmises et des artefacts chargés.

`prediction` contient la classe prédite (`Oui` ou `Non`). `probability` est la probabilité associée à cette classe, et non nécessairement la probabilité de départ.

## Codes de réponse

- `200` : traitement réussi.
- `422` : données de requête invalides selon la validation FastAPI/Pydantic.
- `500` : erreur interne pendant le traitement de la prédiction.

## Exemple d'appel

```bash
curl -X POST "http://127.0.0.1:8000/predict" \
  -H "Content-Type: application/json" \
  -d @request.json
```

Le fichier `request.json` doit contenir un objet conforme au schéma `PredictionRequest`. Consulter `/docs` pour voir tous les champs requis et leurs valeurs autorisées.
