# Déploiement d’un modèle de Machine Learning – Prédiction du turnover

**Auteur :** Rafael DA SILVA
**Projet :** OpenClassrooms – Data Scientist
**Technologies :** Python, FastAPI, PostgreSQL, SQLAlchemy, Alembic, Pydantic, Pytest, GitHub Actions, Render, MkDocs.

---

## 1. Présentation du projet

Ce projet consiste à déployer un modèle de Machine Learning permettant de prédire le risque de départ des employés (*attrition*).

Le modèle a été développé et optimisé dans le cadre du projet précédent (P4). L'objectif du P5 est de mettre ce modèle à disposition via une API REST, afin de permettre à une application cliente de demander des prédictions à partir des données d'un employé.

L'architecture repose sur les composants suivants :

- **FastAPI** : développement de l'API REST.
- **Pydantic** : validation des données entrantes et sortantes.
- **PostgreSQL (Neon)** : stockage des données employés et des résultats de prédiction.
- **SQLAlchemy** : interaction avec la base de données.
- **Alembic** : gestion des migrations de schéma.
- **Pytest** : tests automatisés.
- **GitHub Actions** : intégration continue (CI).
- **Render** : hébergement et déploiement de l'API.
- **MkDocs** : génération de la documentation technique.

L'ensemble des interactions entre l'API et les données employés passe par PostgreSQL.

## 2. Structure du projet

```text
project_5/
│
├── src/
│   ├── create_tables.py
│   ├── database.py
│   ├── import_employees.py
│   ├── main.py
│   ├── models.py
│   └── schemas.py
│
├── migrations/
│   ├── env.py
│   └── versions/
│
├── output/
│   └── models/
│
├── presentation/
│   └── diagramme_bdd.mmd
│
├── docs/
│   ├── index.md
│   ├── architecture.md
│   ├── tracabilite_predictions.md
│   ├── documentation_modele.md
│   ├── guide_api.md
│   └── protocole_maintenance.md
│
├── tests/
│   ├── conftest.py
│   ├── test_api.py
│   ├── test_create_tables.py
│   ├── test_database_config.py
│   ├── test_database_integration.py
│   ├── test_import_employees.py
│   ├── test_model_artifacts.py
│   └── test_project_structure.py
│
├── .github/
│   └── workflows/
│
├── .env.example
├── .gitignore
├── alembic.ini
├── mkdocs.yml
├── requirements.txt
├── requirements-dev.txt
└── README.md
```

Les artefacts du modèle de Machine Learning sont conservés dans `output/models/`.

## 3. Installation et configuration

### 3.1. Prérequis

- Python 3.12
- PostgreSQL
- Git

### 3.2. Cloner le dépôt

```bash
git clone <URL_DU_DEPOT>
cd project_5
```

### 3.3. Créer l'environnement virtuel

Sous Windows :

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

Sous Linux ou macOS :

```bash
python -m venv .venv
source .venv/bin/activate
```

### 3.4. Installer les dépendances

```bash
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

### 3.5. Configurer les variables d'environnement

Créer un fichier `.env` à partir de `.env.example`.

Variables utilisées :

| Variable | Description |
|---|---|
| `APP_ENV` | Environnement d'exécution : development, test ou production |
| `DATABASE_URL` | URL de connexion PostgreSQL utilisée par l'API |
| `TEST_DATABASE_URL` | URL de connexion à la base de données de test |
| `MIGRATION_DATABASE_URL` | URL utilisée pour exécuter les migrations Alembic |
| `API_KEY` | Clé d'authentification de l'API |

Exemple de configuration :

```env
APP_ENV=development
DATABASE_URL=postgresql+psycopg://USER:PASSWORD@HOST/DATABASE?sslmode=require
TEST_DATABASE_URL=postgresql+psycopg://USER:PASSWORD@HOST/DATABASE?sslmode=require
MIGRATION_DATABASE_URL=postgresql+psycopg://USER:PASSWORD@HOST/DATABASE?sslmode=require
API_KEY=your_api_key_here
```

**Important :** les identifiants réels et les clés API ne doivent jamais être versionnés dans Git. Le fichier `.env` est exclu du dépôt via `.gitignore`.

## 4. Base de données PostgreSQL

### 4.1. Organisation

La base de données PostgreSQL contient trois tables principales :

| Table | Description |
|---|---|
| `employees` | Données des employés utilisées pour les prédictions |
| `prediction_inputs` | Historique des données transmises au modèle |
| `prediction_outputs` | Résultats des prédictions générées |

La table `employees` contient 1 470 enregistrements.

Les tables `prediction_inputs` et `prediction_outputs` permettent de conserver la traçabilité des prédictions.

### 4.2. Gestion des migrations

Alembic est utilisé pour gérer l'évolution du schéma de la base de données.

Commandes principales :

```bash
alembic current
alembic history
alembic upgrade head
```

Les migrations permettent notamment de faire évoluer la table `prediction_outputs` avec les champs suivants :

- `model_version` : version du modèle utilisé.
- `inference_time_ms` : durée d'exécution de la prédiction en millisecondes.

La migration correspondante a été appliquée avec succès sur la base de production.

**Remarque :** les migrations doivent être exécutées avec un compte disposant des droits nécessaires à la modification du schéma. Le compte utilisé par l'API en production n'a pas ces privilèges.

### 4.3. Sécurité et gestion des privilèges

L'API utilise un compte PostgreSQL dédié nommé `api_role`, conformément au principe du moindre privilège (*Least Privilege*).

Les autorisations accordées sont limitées aux opérations nécessaires :

| Table | Autorisations |
|---|---|
| `employees` | SELECT |
| `prediction_inputs` | SELECT, INSERT |
| `prediction_outputs` | SELECT, INSERT |

Le compte dispose également des droits nécessaires sur les séquences associées aux tables de prédiction.

Il ne possède pas de droits de création, de modification ou de suppression des tables et des données employés.

Cette séparation permet de limiter les risques en cas de compromission de l'application.

## 5. API REST avec FastAPI

### 5.1. Lancement en local

```bash
uvicorn src.main:app --reload
```

L'API est alors accessible à l'adresse :

```text
http://127.0.0.1:8000
```

La documentation interactive Swagger est disponible à :

```text
http://127.0.0.1:8000/docs
```

### 5.2. Endpoints disponibles

| Méthode | Endpoint | Description |
|---|---|---|
| GET | `/` | Vérification de disponibilité de l'API |
| GET | `/health` | Vérification de l'état de santé du service |
| POST | `/predict` | Génération d'une prédiction d'attrition |

### 5.3. Endpoint de prédiction

L'endpoint `/predict` reçoit l'identifiant d'un employé.

**Requête :**

```json
{
  "id_employee": 1
}
```

L'authentification est obligatoire via le header HTTP `X-API-Key`.

Exemple :

```http
X-API-Key: YOUR_API_KEY
Content-Type: application/json
```

Le fonctionnement de l'endpoint est le suivant :

1. Vérification de la clé API.
2. Validation de la requête avec Pydantic.
3. Récupération des données de l'employé dans PostgreSQL.
4. Préparation des variables d'entrée selon le prétraitement du modèle.
5. Exécution de la prédiction.
6. Enregistrement des données d'entrée dans `prediction_inputs`.
7. Enregistrement du résultat dans `prediction_outputs`.
8. Retour de la prédiction et des informations complémentaires.

### 5.4. Exemple de réponse

```json
{
  "employee_id": 1,
  "prediction_id": 38,
  "prediction": "Oui",
  "probability": 84.43,
  "message": "Le modèle prédit un départ.",
  "inference_time_ms": 422.64,
  "model_version": "1.0.0",
  "explainability": {
    "method": "Régression logistique - contributions locales des coefficients",
    "top_factors": []
  }
}
```

La réponse contient :

- La prédiction : départ potentiel ou absence de départ prédit.
- La probabilité associée à la prédiction, exprimée en pourcentage.
- La version du modèle.
- Le temps d'inférence.
- Les principaux facteurs contribuant à la prédiction.

Les valeurs de `top_factors` sont calculées pour chaque prédiction.

## 6. Modèle de Machine Learning

Le modèle utilisé provient du projet P4.

Il s'agit d'un modèle de régression logistique optimisé pour la prédiction de l'attrition.

Les étapes de préparation des données et de transformation des variables doivent rester cohérentes avec le pipeline utilisé lors de l'entraînement.

Les artefacts nécessaires à l'inférence sont stockés dans :

```text
output/models/
```

### 6.1. Indicateurs d'évaluation issus du P4

| Indicateur | Résultat |
|---|---:|
| Accuracy | 0.796 |
| Precision – classe Oui | 0.418 |
| Recall – classe Oui | 0.702 |
| F1-score – classe Oui | 0.524 |
| ROC-AUC | 0.814 |
| F1-score moyen en validation croisée | 0.5069 |

Ces résultats correspondent à l'évaluation du modèle réalisée dans le cadre du P4. Ils ne constituent pas une nouvelle évaluation indépendante effectuée en production.

## 7. Tests automatisés

Les tests sont réalisés avec Pytest.

Ils permettent de vérifier notamment :

- Le fonctionnement des endpoints.
- La validation des données entrantes.
- La gestion des erreurs.
- Le contrôle d'accès via la clé API.
- Les interactions avec la base de données.
- Le comportement des fonctions de préparation et de prédiction.

Exécution des tests :

```bash
python -m pytest
```

Pour générer un rapport de couverture :

```bash
python -m pytest --cov=src --cov-report=term-missing
```

Les tests doivent être exécutés avec une base de données de test distincte de la base de production.

### 7.1. Résultats des tests

La suite de tests automatisés a été exécutée avec succès :

- **34 tests réussis.**
- **Couverture globale du code : 100 %.**
- Toutes les instructions du code source sont couvertes par les tests.

La documentation technique a également été générée avec succès à l'aide de MkDocs.

## 8. Intégration continue – GitHub Actions

GitHub Actions permet d'automatiser les vérifications du projet à chaque modification du code.

Le workflow CI assure notamment l'exécution des tests automatisés.

Les variables sensibles nécessaires à l'exécution du workflow sont configurées dans les secrets GitHub.

Les environnements de test et de production doivent rester séparés afin d'éviter toute modification accidentelle des données de production pendant les tests.

## 9. Déploiement en production – Render

L'API est déployée sur Render.

**URL de production :**

https://machine-learning-deployment-q0xp.onrender.com

Documentation interactive :

https://machine-learning-deployment-q0xp.onrender.com/docs

### 9.1. Configuration

Les variables d'environnement sont configurées directement dans le tableau de bord Render :

- `API_KEY`
- `APP_ENV`
- `DATABASE_URL`

La variable `DATABASE_URL` utilise le compte PostgreSQL `api_role` de la branche de production Neon.

Les migrations de base de données sont gérées séparément avec un compte disposant des privilèges administratifs nécessaires.

### 9.2. Validation du déploiement

Le déploiement a été vérifié en production à l'aide de l'endpoint `POST /predict`.

Un test réalisé avec l'employé d'identifiant `1` a retourné une réponse HTTP 200.

Résultat observé :

| Élément | Résultat |
|---|---|
| Code HTTP | 200 |
| Employee ID | 1 |
| Prediction ID | 38 |
| Prédiction | Oui |
| Probabilité | 84,43 % |
| Version du modèle | 1.0.0 |
| Temps d'inférence | 422,64 ms |

La vérification directe dans PostgreSQL a confirmé que la prédiction était bien enregistrée dans `prediction_outputs`, avec les informations associées dans `prediction_inputs`.

Cette validation confirme le bon fonctionnement de la chaîne complète en production : accès aux données, inférence du modèle, réponse API et persistance du résultat.

**Remarque :** sur l'offre gratuite de Render, le service peut être mis en veille après une période d'inactivité. La première requête suivant cette période peut donc prendre davantage de temps.

## 10. Exploitation des données

Les données stockées dans PostgreSQL permettent de suivre les prédictions réalisées et d'envisager une exploitation analytique à destination des équipes RH.

### 10.1. Nombre de prédictions par jour

```sql
SELECT
    DATE(created_at) AS prediction_date,
    COUNT(*) AS total_predictions
FROM prediction_outputs
GROUP BY DATE(created_at)
ORDER BY prediction_date;
```

### 10.2. Répartition des départs prédits

```sql
SELECT
    prediction,
    COUNT(*) AS total,
    ROUND(
        COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (),
        2
    ) AS percentage
FROM prediction_outputs
GROUP BY prediction
ORDER BY total DESC;
```

### 10.3. Taux de départ prédit par département

```sql
SELECT
    e.departement,
    COUNT(*) AS total_predictions,
    SUM(
        CASE WHEN po.prediction = 'Oui' THEN 1 ELSE 0 END
    ) AS predicted_departures,
    ROUND(
        100.0 * SUM(
            CASE WHEN po.prediction = 'Oui' THEN 1 ELSE 0 END
        ) / NULLIF(COUNT(*), 0),
        2
    ) AS predicted_departure_rate
FROM prediction_outputs po
JOIN prediction_inputs pi
    ON pi.id = po.prediction_input_id
JOIN employees e
    ON e.id_employee = pi.employee_id
GROUP BY e.departement
ORDER BY predicted_departure_rate DESC;
```

### 10.4. Proposition de tableau de bord RH

Les données enregistrées pourraient alimenter un tableau de bord Power BI afin de faciliter le suivi des indicateurs :

- Nombre de prédictions réalisées.
- Répartition des prédictions de départ et de non-départ.
- Évolution du nombre de départs prédits.
- Taux de départ prédit par département.
- Suivi des probabilités de départ.

Ces indicateurs pourraient aider les équipes RH à identifier les populations nécessitant une analyse plus approfondie.

Les prédictions constituent une aide à la décision et ne doivent pas être interprétées comme une certitude de départ individuel.

## 11. Sécurité et bonnes pratiques

Les principales mesures de sécurité mises en place sont :

- Authentification des requêtes de prédiction via une clé API.
- Stockage des secrets dans les variables d'environnement.
- Séparation des bases de test et de production.
- Utilisation d'un compte PostgreSQL dédié à l'API.
- Application du principe du moindre privilège.
- Gestion du schéma avec Alembic.
- Exclusion des fichiers sensibles du dépôt Git.

Les clés API et mots de passe ne doivent jamais être intégrés directement dans le code source ou dans la documentation.

## 12. Conclusion

Ce projet a permis de passer d'un modèle de Machine Learning développé et évalué dans le P4 à une solution accessible via une API REST déployée en production.

L'intégration de FastAPI, PostgreSQL et Render permet de proposer un service de prédiction avec authentification, traçabilité des résultats et gestion des versions du modèle.

La mise en place des migrations Alembic, des tests automatisés et d'un compte PostgreSQL à privilèges limités contribue à rendre la solution plus fiable, maintenable et sécurisée.

Le projet constitue ainsi une première étape vers une solution d'aide à la décision destinée aux équipes RH.
