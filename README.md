# Déploiement d'un modèle de Machine Learning de prédiction chez TechNova Partners

Projet de Data Science consacré au développement, à l'évaluation et au déploiement d'un modèle de Machine Learning pour la prédiction de l'attrition des employés.

## 1. Présentation du projet

Ce projet vise à transformer un modèle de prédiction de l'attrition des employés de l'entreprise TechNova Partners en une application exploitable, en suivant une démarche structurée et reproductible.

Il couvre :

- la préparation des données ;

- l'entraînement et l'évaluation du modèle ;

- le développement d'une API avec FastAPI ;

- l'intégration d'une base de données PostgreSQL ;

- la traçabilité des prédictions ;

- la gestion des évolutions du schéma avec Alembic ;

- les tests automatisés et l'intégration continue ;

- le déploiement de l'API.

## 2. Objectifs

- Développer et évaluer des modèles de Machine Learning.

- Structurer le projet selon les bonnes pratiques du développement logiciel.

- Versionner et documenter le code.

- Exposer le modèle à travers une API.

- Assurer la traçabilité des prédictions.

- Gérer l'évolution du schéma de la base de données.

- Améliorer la reproductibilité et la maintenabilité du projet.

## 3. Structure du projet

```text
machine_learning_deployment/
├── .github/
│   └── workflows/
│       └── ci.yml
├── data/
│   ├── raw/
│   └── processed/
├── docs/
├── migrations/
│   ├── versions/
│   │   └── 5e817b511ec1_initial_api_schema.py
│   └── env.py
├── notebooks/
├── output/
│   └── models/
│       ├── lr_optimise.joblib
│       └── preprocessor.joblib
├── presentation/
│   └── diagramme_bdd.mmd
├── site/
├── src/
│   ├── create_tables.py
│   ├── database.py
│   ├── import_employees.py
│   ├── main.py
│   ├── models.py
│   └── schemas.py
├── tests/
│   ├── test_api.py
│   ├── test_create_tables.py
│   ├── test_database_config.py
│   ├── test_database_integration.py
│   ├── test_import_employees.py
│   ├── test_model_artifacts.py
│   └── test_project_structure.py
├── .env.example
├── .gitignore
├── alembic.ini
├── mkdocs.yml
├── README.md
├── requirements.txt
└── requirements-dev.txt
```

## 4. Installation et configuration

### Prérequis

- Python 3.12

- Git

- PostgreSQL

### 4.1. Cloner le dépôt

```bash
git clone https://github.com/rafadmgs/machine_learning_deployment.git
cd machine_learning_deployment
```

### 4.2. Créer et activer un environnement virtuel

**Windows — PowerShell :**

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

**Linux / macOS :**

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 4.3. Installer les dépendances

Pour un environnement local de développement, installer les dépendances de l'application ainsi que les outils de test, de documentation et de travail sur les notebooks :

```bash
python -m pip install --upgrade pip
pip install -r requirements-dev.txt
```

Le fichier `requirements-dev.txt` inclut `requirements.txt` et ajoute les dépendances nécessaires au développement, notamment Jupyter, Matplotlib, Seaborn, Pytest, pytest-cov et MkDocs.

Le fichier `requirements.txt` contient les dépendances nécessaires à l'exécution de l'application : traitement des données et chargement du modèle, API et accès à PostgreSQL.

Pour installer uniquement les dépendances de production :

```bash
pip install -r requirements.txt
```

### 4.4. Configurer PostgreSQL et les variables d'environnement

La connexion à PostgreSQL est configurée à l'aide de variables d'environnement afin de séparer les paramètres de connexion du code source.

Créer un fichier `.env` à la racine du projet :

```dotenv
DATABASE_URL=postgresql+psycopg://utilisateur:mot_de_passe@localhost:5432/nom_base
TEST_DATABASE_URL=postgresql+psycopg://utilisateur:mot_de_passe@localhost:5432/nom_base_test
API_KEY=votre_cle_api_secrete
```

Remplacer les valeurs d'exemple par les paramètres correspondant à chaque environnement.

- `DATABASE_URL` : connexion PostgreSQL utilisée par l'application et par Alembic.
- `TEST_DATABASE_URL` : connexion PostgreSQL réservée aux tests d'intégration.
- `API_KEY` : clé secrète utilisée pour authentifier les requêtes adressées à l'endpoint `/predict`.

Le fichier `.env` contient des informations sensibles et ne doit jamais être versionné dans Git. Le fichier `.env.example` fournit uniquement un modèle de configuration sans identifiants réels.

Les connexions PostgreSQL utilisent le pilote Psycopg et le paramètre SSL lorsque celui-ci est requis par l'environnement Neon.

## 5. E4 — Base de données et traçabilité des prédictions

### 5.1. Architecture et choix techniques

L'application utilise FastAPI pour exposer le modèle de Machine Learning et PostgreSQL pour conserver les données nécessaires à son fonctionnement et assurer la traçabilité des prédictions.

SQLAlchemy est utilisé comme ORM (*\*Object-Relational Mapping\**) pour représenter les tables de la base de données sous forme de modèles Python.

La gestion de l'évolution du schéma des tables de l'API est assurée par Alembic.

La base de données sépare les données des employés, les entrées transmises au modèle et les résultats produits.

### 5.2. Structure de la base de données

Les trois tables gérées par les modèles SQLAlchemy et les migrations Alembic sont :

| Table | Rôle |
|---|---|
| `employees` | Stocke les données des employés utilisées par l'application. |
| `prediction_inputs` | Enregistre les données d'entrée envoyées au modèle au format JSON, ainsi que leur date de création. |
| `prediction_outputs` | Enregistre la prédiction, la probabilité associée, la référence à l'entrée correspondante et la date de création. |

La table `prediction_outputs` utilise la clé étrangère `prediction_input_id` pour référencer l'entrée à l'origine du résultat.

Le champ `employee_id` de `prediction_inputs` référence l'employé concerné par la prédiction. Dans le fonctionnement actuel de l'API, une prédiction est associée à un employé existant grâce à son identifiant `id_employee`.

Les trois tables historiques issues du projet P4 sont également présentes dans PostgreSQL :

- `extrait_sirh` ;

- `extrait_eval` ;

- `extrait_sondage`.

Elles sont conservées dans la base de données, mais ne font pas partie du périmètre de gestion des migrations Alembic de l'API.

Cette séparation permet de préserver les tables historiques du P4 tout en gérant l'évolution du schéma des tables utilisées par l'API.

Le schéma relationnel est représenté dans `presentation/diagramme_bdd.mmd`.

### 5.3. Création et évolution du schéma avec Alembic

Alembic est utilisé pour versionner et gérer les évolutions du schéma de la base de données.

La configuration se trouve dans :

- `alembic.ini` : configuration générale d'Alembic ;

- `migrations/env.py` : connexion à la base de données et configuration des migrations ;

- `migrations/versions/` : historique des migrations générées.

La migration initiale `5e817b511ec1_initial_api_schema.py` décrit la création des trois tables de l'API :

- `employees` ;

- `prediction_inputs` ;

- `prediction_outputs`.

Les migrations sont générées à partir des modèles SQLAlchemy définis dans `src/models.py`.

**Générer une nouvelle migration :**

Après avoir modifié un modèle SQLAlchemy :

```bash
python -m alembic revision --autogenerate -m "description_de_la_modification"
```

La migration générée doit être relue avant son application. L'autogénération ne remplace pas la vérification manuelle des opérations proposées.

**Appliquer les migrations :**

```bash
python -m alembic upgrade head
```

Cette commande applique les migrations disponibles jusqu'à la dernière révision.

**Consulter la révision actuelle :**

```bash
python -m alembic current
```

**Consulter l'historique des migrations :**

```bash
python -m alembic history
```

**Vérifier la synchronisation entre les modèles et la base de données :**

```bash
python -m alembic check
```

Le résultat attendu lorsque les modèles et le schéma sont synchronisés est :

```text
No new upgrade operations detected.
```

**Enregistrement d'une migration dans une base existante :**

Lorsqu'une base contient déjà les tables décrites par une migration, il est possible d'enregistrer la révision correspondante sans réexécuter les opérations de création :

```bash
python -m alembic stamp head
```

Cette commande modifie uniquement l'historique des révisions Alembic. Elle ne crée, ne modifie et ne supprime pas les tables.

Elle doit être utilisée uniquement après avoir vérifié que la structure existante correspond bien à la migration concernée.

**Périmètre de gestion :**

Dans la configuration actuelle, Alembic gère les trois tables de l'API (`employees`, `prediction_inputs` et `prediction_outputs`).

Les tables historiques `extrait_sirh`, `extrait_eval` et `extrait_sondage` restent en dehors de ce périmètre.

### 5.4. Création des tables avec SQLAlchemy

Le projet conserve également le script `src/create_tables.py`.

Ce script utilise :

```python
Base.metadata.create_all(bind=engine)
```

Il permet de créer les tables déclarées dans les modèles SQLAlchemy lorsqu'elles n'existent pas encore. Il vérifie également que l'environnement est `development` ou `test` avant d'autoriser cette opération.

Pour l'exécuter :

```bash
python -m src.create_tables
```

Ce mécanisme est distinct d'Alembic :

- `create_tables.py` crée les tables manquantes à partir des métadonnées SQLAlchemy ;

- Alembic versionne les évolutions du schéma et permet de suivre leur historique.

Pour les environnements utilisant les migrations, Alembic constitue le mécanisme de référence pour gérer l'évolution du schéma. Il ne faut pas considérer `create_all()` comme un remplacement du système de migrations.

### 5.5. Importation des employés

Le jeu de données des employés est importé depuis :

```text
data/processed/df_central.csv
```

Le script `src/import_employees.py` vérifie notamment :

- la présence du fichier ;

- la compatibilité des colonnes ;

- les identifiants dupliqués ;

- les identifiants manquants ;

- les autres valeurs manquantes.

Le jeu de données utilisé pour cette étape contient 1 470 employés.

Pour lancer l'importation :

```bash
python -m src.import_employees
```

Le script interrompt l'importation si la table `employees` contient déjà des enregistrements, afin d'éviter une réimportation involontaire.

La création ou l'évolution de la structure des tables et l'importation des données sont donc deux opérations distinctes.

### 5.6. Traçabilité des prédictions

Lorsqu'une requête de prédiction est traitée par l'API :

1. L'identifiant `id_employee` reçu est validé par le schéma `PredictionRequest`.

2. L'API recherche l'employé correspondant dans la table `employees`.

3. Les 25 variables attendues par le préprocesseur sont récupérées depuis l'enregistrement de cet employé.

4. Les données sont transformées et la prédiction est calculée avec le modèle et le préprocesseur chargés au démarrage de l'API.

5. Les données utilisées pour la prédiction sont enregistrées dans `prediction_inputs`, avec la référence `employee_id`.

6. Le résultat est enregistré dans `prediction_outputs` et relié à son entrée.

7. La transaction est validée avec `commit()`.

Si l'identifiant ne correspond à aucun employé, l'API retourne une réponse HTTP `404`.

En cas d'erreur pendant le traitement, la transaction est annulée à l'aide de `rollback()`.

## 6. E5 — Développement de l'API

### 6.1. Lancer l'API

Depuis la racine du projet, après avoir configuré l'environnement, la base de données et les artefacts nécessaires, lancer :

```powershell
python -m uvicorn src.main:app --reload
```

L'API est alors accessible à l'adresse :

`http://127.0.0.1:8000`

La documentation interactive est disponible à :

`http://127.0.0.1:8000/docs`

Le schéma OpenAPI est disponible à :

`http://127.0.0.1:8000/openapi.json`

### 6.2. Authentification par clé API

L'endpoint `POST /predict` est protégé par une clé API transmise dans l'en-tête HTTP `X-API-Key`.

La clé attendue est définie dans la variable d'environnement `API_KEY` et n'est pas enregistrée directement dans le code source.

- Une clé absente ou incorrecte entraîne une réponse HTTP `401 Unauthorized`.

- Si la clé n'est pas configurée dans l'environnement, l'API retourne une erreur HTTP `500`.

- Les endpoints `GET /` et `GET /health` restent accessibles sans authentification.

La comparaison de la clé est réalisée avec `secrets.compare_digest()`.

### 6.3. Endpoints disponibles

| Méthode | Endpoint | Description |
|---|---|---|
| `GET` | `/` | Retourne un message indiquant que l'API est opérationnelle et le chemin vers la documentation. |
| `GET` | `/health` | Retourne le statut de l'API. |
| `POST` | `/predict` | Reçoit l'identifiant d'un employé, calcule une prédiction et enregistre les données d'entrée et le résultat dans PostgreSQL. |

### 6.4. Fonctionnement de la prédiction

Le modèle `lr_optimise.joblib` et le préprocesseur `preprocessor.joblib` sont chargés une seule fois au démarrage de l'application, grâce au mécanisme `lifespan` de FastAPI. Ils sont conservés dans `app.state` et réutilisés pour chaque requête.

L'endpoint `POST /predict` suit les étapes suivantes :

1. Validation de l'identifiant reçu à l'aide du schéma `PredictionRequest`.

2. Recherche de l'employé dans la table `employees`.

3. Récupération des 25 variables utilisées par le modèle.

4. Transformation des données avec le préprocesseur déjà chargé.

5. Calcul de la classe prédite et de la probabilité associée.

6. Enregistrement des données utilisées dans `prediction_inputs`, avec la clé étrangère `employee_id`.

7. Enregistrement du résultat dans `prediction_outputs`.

8. Validation de la transaction PostgreSQL et retour du résultat au client.

Si l'employé n'existe pas, l'API retourne une réponse HTTP `404`.

En cas d'erreur pendant le traitement, la transaction est annulée et l'API retourne une erreur HTTP 500 avec un message générique.

Les données invalides sont rejetées lors de la validation de la requête, avant l'exécution de la logique de prédiction, avec une réponse HTTP `422`.

### 6.5. Format de la requête

L'endpoint `POST /predict` attend uniquement l'identifiant d'un employé déjà enregistré dans la table `employees`.

Exemple de requête :

```json
{
  "id_employee": 1
}
```

L'API récupère ensuite automatiquement les 25 variables nécessaires depuis PostgreSQL. Le client n'a donc pas besoin de transmettre les caractéristiques de l'employé dans le corps de la requête.

Si l'identifiant est invalide, manquant ou inférieur ou égal à zéro, FastAPI retourne une réponse HTTP `422`. Si l'employé n'existe pas, l'API retourne une réponse HTTP `404`.

Le champ `id_employee` doit être un entier strictement positif. Les champs manquants, les identifiants invalides et les champs supplémentaires sont rejetés par FastAPI avec une réponse HTTP `422`.

### 6.6. Format de la réponse

Une réponse réussie contient les champs suivants :

- `employee_id` : identifiant de l'employé concerné ;

- `prediction_id` : identifiant du résultat enregistré dans la base de données ;

- `prediction` : classe prédite par le modèle (`Oui` ou `Non`) ;

- `probability` : probabilité associée à la classe prédite, exprimée en pourcentage ;

- `message` : message décrivant le résultat, soit un départ prédit, soit un maintien prédit ;

- `inference_time_ms` : durée du prétraitement, de la prédiction et du calcul des facteurs explicatifs, en millisecondes ;

- `model_version` : version du modèle utilisée pour produire la prédiction ;

- `explainability` : informations permettant d'interpréter localement la prédiction.

L'objet `explainability` contient :

- `method` : méthode utilisée pour calculer les facteurs explicatifs ;

- `top_factors` : jusqu'à trois variables ayant les contributions absolues les plus importantes.

Chaque facteur contient :

- `feature` : nom de la variable ;

- `impact` : sens de la contribution (`positive` ou `negative`) ;

- `contribution` : contribution calculée à partir de la valeur standardisée de la variable et du coefficient de la régression logistique.

Les contributions sont exprimées sur l'échelle des log-odds. Elles ne représentent ni des points de pourcentage de probabilité, ni une relation causale.

Exemple illustratif :

```json
{
  "employee_id": 1,
  "prediction_id": 20,
  "prediction": "Oui",
  "probability": 84.43,
  "message": "Le modèle prédit un départ.",
  "inference_time_ms": 12.5,
  "model_version": "1.0.0",
  "explainability": {
    "method": "Régression logistique - contributions locales des coefficients",
    "top_factors": [
      {
        "feature": "satisfaction_environnement",
        "impact": "positive",
        "contribution": 0.8241
      },
      {
        "feature": "annees_dans_le_poste_actuel",
        "impact": "negative",
        "contribution": -0.5123
      }
    ]
  }
}
```

Les valeurs de cet exemple sont illustratives : le résultat réel dépend des données de l'employé et de la prédiction calculée. Le temps d'inférence correspond au traitement et à l'inférence du modèle ; il n'inclut pas les opérations d'accès à PostgreSQL.

## 7. Documentation technique du modèle

### 7.1. Modèle retenu

Le modèle retenu est une régression logistique optimisée à l'aide de `RandomizedSearchCV`.

Le modèle est enregistré dans `output/models/lr_optimise.joblib`.

Les principaux hyperparamètres sont :

| Paramètre | Valeur |
|---|---|
| `C` | `0.01` |
| `solver` | `lbfgs` |
| `class_weight` | `balanced` |
| `max_iter` | `5000` |

Le prétraitement des données est assuré par `output/models/preprocessor.joblib`, qui utilise un `ColumnTransformer` et transforme les données d'entrée en 46 variables.

### 7.2. Performances du modèle

Les métriques suivantes proviennent de l'évaluation du modèle optimisé sur le jeu de test du projet P4, composé de 294 observations, dont 47 cas d'attrition (`Oui`) et 247 cas sans attrition (`Non`).

| Métrique | Résultat |
|---|---:|
| Accuracy | 0,796 |
| Précision — classe `Oui` | 0,418 |
| Recall — classe `Oui` | 0,702 |
| F1-score — classe `Oui` | 0,524 |
| ROC-AUC | 0,814 |

Le F1-score moyen obtenu lors de la validation croisée est de **0,5069**.

Le rappel de 0,702 indique que le modèle identifie environ 70 % des cas d'attrition présents dans le jeu de test. En contrepartie, la précision de 0,418 montre qu'une proportion importante des prédictions positives est incorrecte.

L'accuracy doit être interprétée avec prudence en raison du déséquilibre entre les classes.

Le modèle constitue un outil d'aide à l'analyse et ne doit pas être utilisé seul pour prendre des décisions concernant les employés.

## 8. Tests automatisés et couverture du code

Les tests automatisés sont réalisés avec Pytest.

Les fichiers de tests sont regroupés dans le répertoire `tests/` :

- `test_api.py`

- `test_create_tables.py`

- `test_database_config.py`

- `test_database_integration.py`

- `test_import_employees.py`

- `test_model_artifacts.py`

- `test_project_structure.py`

### 8.1. Exécuter les tests

Depuis la racine du projet, utiliser :

```bash
python -m pytest
```

L'utilisation de `python -m pytest` permet d'exécuter Pytest avec l'interpréteur Python de l'environnement virtuel actif et de résoudre correctement les imports du package `src`.

Pour afficher davantage de détails :

```bash
python -m pytest -v
```

### 8.2. Générer le rapport de couverture

```bash
python -m pytest --cov=src --cov-report=term-missing --cov-report=html
```

Le rapport détaillé est généré dans le répertoire `htmlcov/`. Ouvrir `htmlcov/index.html` dans un navigateur pour consulter le résultat.

### 8.3. Résultats obtenus

Dernière campagne locale de tests et de couverture :

- **33 tests réussis** ;

- **0 test en échec** ;

- durée de la dernière exécution des tests : **42,82 secondes** ;

- **100 % de couverture du code source**.

La couverture concerne les 222 instructions des modules analysés dans `src/` :

| Fichier | Instructions | Couverture |
|---|---:|---:|
| `create_tables.py` | 13 | 100 % |
| `database.py` | 16 | 100 % |
| `import_employees.py` | 38 | 100 % |
| `main.py` | 86 | 100 % |
| `models.py` | 48 | 100 % |
| `schemas.py` | 21 | 100 % |
| **Total** | **222** | **100 %** |

Les tests comprennent des tests unitaires, des tests avec dépendances simulées (mocks), des tests de l'API avec les artefacts réels du modèle P4 et des tests d'intégration avec PostgreSQL. Les tests d'intégration vérifient notamment les opérations `INSERT`, `SELECT` et `DELETE`, ainsi que les relations entre les tables.

La couverture à 100 % signifie que toutes les instructions mesurées dans les modules listés ont été exécutées pendant cette campagne de tests. Elle ne garantit pas, à elle seule, l'absence de défauts.

## 9. Intégration continue et déploiement continu — GitHub Actions

Le projet utilise GitHub Actions pour automatiser les tests et déclencher le déploiement de l'API sur Render.

Le workflow est défini dans `.github/workflows/ci.yml`.

### 9.1. Intégration continue (CI)

Le job `Run tests` automatise les étapes suivantes :

- récupération du code du dépôt ;
- configuration de Python 3.12 ;
- installation des dépendances de l'application et des outils de test ;
- configuration de l'environnement avec `APP_ENV=test` ;
- configuration des variables de connexion PostgreSQL ;
- exécution des tests automatisés avec Pytest et génération du rapport de couverture.

Les secrets suivants sont configurés dans GitHub Actions :

| Secret GitHub | Utilisation |
|---|---|
| `DATABASE_URL` | Connexion utilisée par l'application pendant les tests |
| `TEST_DATABASE_URL` | Connexion utilisée explicitement par les tests d'intégration PostgreSQL |

Dans le workflow CI, ces deux variables pointent vers la branche Neon `p5_test`. Cette configuration garantit que les tests automatisés n'utilisent ni la base de développement ni la base de production.

La branche `p5_test` est réservée aux tests d'intégration PostgreSQL.

Le workflow est déclenché lors des événements suivants :

- `push` sur les branches `main` et `feature/**` ;
- `pull_request` à destination de `main`.

La réussite du job de tests constitue une condition nécessaire au déploiement.

### 9.2. Déploiement continu (CD)

Le job `Deploy to Render` est indépendant du job de tests et dépend explicitement de sa réussite grâce à la directive `needs: test`.

Il est exécuté uniquement lorsque les conditions suivantes sont réunies :

- l'événement déclencheur est un `push` ;
- la branche concernée est `main` ;
- le job de tests s'est terminé avec succès.

Le déclenchement du déploiement est effectué à l'aide du secret GitHub `RENDER_DEPLOY_HOOK_URL`.

Ce secret contient l'URL du Deploy Hook Render et n'est jamais inscrite directement dans le code source ou dans le fichier YAML.

Les déploiements ne sont donc pas déclenchés par les pull requests ni par les pushes sur les branches de fonctionnalité.

Le statut des jobs de test et de déploiement peut être consulté dans l'onglet **Actions** du dépôt GitHub.

## 10. Déploiement de l'API sur Render

L'API FastAPI est hébergée sur Render en tant que service Web.

- **Dépôt source :** `rafadmgs/machine_learning_deployment`
- **Branche de production :** `main`
- **Commande de build :**

```bash
pip install -r requirements.txt
```

- **Commande de démarrage :**

```bash
uvicorn src.main:app --host 0.0.0.0 --port $PORT
```

### Variables d'environnement de production

Les variables suivantes sont configurées dans le tableau de bord Render :

| Variable | Utilisation |
|---|---|
| `DATABASE_URL` | Connexion à la branche Neon `production` |
| `API_KEY` | Authentification des requêtes vers `/predict` |

Les valeurs sensibles sont configurées dans les paramètres du service et ne sont pas intégrées au dépôt Git.

L'API est accessible à l'adresse :

`https://machine-learning-deployment-q0xp.onrender.com`

Les endpoints `/health` et `/docs` ont été vérifiés en ligne. Une requête authentifiée sur `/predict` a également été exécutée avec succès sur une version précédemment déployée.

La mise en production des dernières modifications doit être confirmée après leur intégration dans `main` et la réussite du workflow GitHub Actions.

Le plan gratuit de Render peut mettre le service en veille après une période d'inactivité. La première requête après cette veille peut donc prendre davantage de temps.

## 11. Sécurité et gestion des accès

La sécurité du projet repose sur la séparation des environnements, la gestion des identifiants par variables d'environnement et l'authentification des requêtes de prédiction.

### 11.1. Authentification et accès à l'API

L'API expose trois endpoints principaux :

| Endpoint | Authentification | Accès |
|---|---|---|
| `GET /` | Non requise | Public |
| `GET /health` | Non requise | Public |
| `POST /predict` | Clé API obligatoire | Clients disposant d'une clé valide |

L'endpoint `POST /predict` est protégé par une clé API transmise dans l'en-tête HTTP `X-API-Key`.

La clé attendue est définie dans la variable d'environnement `API_KEY`.

La vérification est effectuée avant le traitement de la prédiction. La comparaison utilise la fonction `secrets.compare_digest()` afin de limiter les risques liés aux comparaisons de chaînes sensibles.

Les réponses associées à l'authentification sont les suivantes :

- clé absente ou incorrecte : HTTP `401 Unauthorized` ;
- clé non configurée dans l'environnement : erreur HTTP `500`.

Les endpoints de statut et de vérification de disponibilité restent accessibles sans authentification afin de permettre les contrôles techniques du service.

La clé API constitue le mécanisme d'authentification actuellement implémenté. Le projet ne comporte pas, à ce stade, de système de gestion individuelle des utilisateurs ou de rôles applicatifs.

### 11.2. Accès à PostgreSQL et comptes techniques

L'application accède à PostgreSQL par l'intermédiaire de SQLAlchemy et du pilote Psycopg.

La connexion est définie par la variable d'environnement `DATABASE_URL`.

L'accès à la base de données est réalisé par le compte technique associé à cette URL. Les identifiants ne sont pas codés en dur dans l'application.

Les accès sont répartis selon les environnements :

- **Développement local :** connexion à la branche Neon `p5_dev`.
- **Tests automatisés :** connexion à la branche Neon `p5_test`.
- **Production :** connexion à la branche Neon `production`, configurée dans Render.

L'application utilise SQLAlchemy pour effectuer les opérations nécessaires à son fonctionnement, notamment la lecture des employés et l'enregistrement des entrées et des résultats de prédiction.

Alembic utilise également la configuration de connexion `DATABASE_URL` pour gérer les migrations du schéma de l'API.

Les tests d'intégration utilisent `TEST_DATABASE_URL` afin d'isoler les opérations de test de la base de développement et de production.

### 11.3. Gestion des secrets et des identifiants

Les identifiants PostgreSQL, les clés API et les URL de déploiement sont traités comme des informations sensibles.

Leur stockage est séparé du code source :

| Environnement | Emplacement | Informations concernées |
|---|---|---|
| Développement local | Fichier `.env` | `DATABASE_URL`, `TEST_DATABASE_URL`, `API_KEY` |
| GitHub Actions | GitHub Repository Secrets | `DATABASE_URL`, `TEST_DATABASE_URL`, `RENDER_DEPLOY_HOOK_URL` |
| Render | Variables d'environnement du service | `DATABASE_URL`, `API_KEY` |

Les mesures appliquées sont les suivantes :

- le fichier `.env` est exclu du versionnement grâce au `.gitignore` ;
- le fichier `.env.example` ne contient aucun identifiant réel ;
- les secrets GitHub sont configurés dans les paramètres du dépôt et ne sont pas inscrits dans le workflow ;
- les identifiants de production sont configurés dans Render ;
- aucune clé API ou aucun mot de passe PostgreSQL ne doit être publié dans le dépôt.

L'accès à la configuration des secrets est réservé aux personnes disposant des autorisations appropriées sur le dépôt GitHub. De même, l'accès aux variables d'environnement de production dépend des permissions accordées sur le service Render.

Les valeurs des secrets ne doivent jamais être copiées dans les journaux d'exécution, les captures d'écran ou la documentation publique.

### 11.4. Séparation des environnements et permissions PostgreSQL

Les environnements de développement, de test et de production sont isolés à l'aide de branches distinctes de Neon.

| Environnement | Branche Neon | Utilisation |
|---|---|---|
| Développement | `p5_dev` | Développement local et vérification du schéma |
| Test | `p5_test` | Tests automatisés et tests d'intégration |
| Production | `production` | Fonctionnement de l'API hébergée sur Render |

Cette séparation évite que les opérations de test modifient directement les données utilisées par l'application en production.

Concernant les comptes PostgreSQL :

- la connexion de test vérifiée pendant le développement utilisait le rôle `neondb_owner` ;
- le service Render utilise actuellement le rôle `neondb_owner` pour accéder à la base de production.

Le rôle `neondb_owner` possède des privilèges étendus sur la base de données. Cette configuration fonctionne pour le projet, mais ne respecte pas pleinement le principe du moindre privilège.

Une amélioration de sécurité consiste à créer un rôle technique dédié à l'API, avec uniquement les droits nécessaires sur les tables utilisées par l'application : lecture des employés et lecture/écriture des tables de traçabilité des prédictions.

Les droits d'administration du schéma et les opérations de migration devraient être séparés des droits nécessaires au fonctionnement courant de l'API.

Cette séparation des rôles n'est pas encore mise en place dans la configuration actuelle.

### 11.5. Protection des données et utilisation des prédictions

Les données des employés peuvent contenir des informations personnelles et professionnelles sensibles. Leur accès doit être limité aux personnes et aux applications autorisées.

Les connexions à PostgreSQL doivent utiliser les paramètres SSL requis par l'environnement Neon.

Les prédictions produites par le modèle constituent un outil d'aide à l'analyse. Elles ne doivent pas être utilisées seules pour prendre des décisions concernant les employés.

## 12. Maintenance et pistes d'amélioration

1. Surveiller les performances du modèle à l'aide de données récentes et de métriques adaptées à la classe `Oui`.

2. Contrôler la qualité des données d'entrée et leur compatibilité avec le préprocesseur.

3. Détecter les évolutions dans la distribution des données et dans la fréquence de l'attrition.

4. Définir une procédure de réentraînement et d'évaluation avant le remplacement du modèle.

5. Versionner les artefacts et conserver la traçabilité des modèles utilisés.

6. Surveiller la disponibilité de l'API déployée et renforcer la protection des données ainsi que la gestion des accès.

7. Continuer à versionner les évolutions du schéma de la base de données avec Alembic.

Tout remplacement du modèle ou du préprocesseur doit être accompagné d'une vérification de compatibilité des variables et d'une nouvelle évaluation des performances.
