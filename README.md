# Déploiement d'un modèle de Machine Learning de prédiction chez TechNova Partners

Projet de Data Science consacré au développement, à l'évaluation et au
déploiement d'un modèle de Machine Learning pour la prédiction de
l'attrition des employés.

## 1. Présentation du projet

Ce projet vise à transformer un modèle de prédiction de l'attrition des
employés de l'entreprise TechNova Partners en une application
exploitable, en suivant une démarche structurée et reproductible.

Il couvre :

-   la préparation des données ;
-   l'entraînement et l'évaluation du modèle ;
-   le développement d'une API avec FastAPI ;
-   l'intégration d'une base de données PostgreSQL ;
-   la traçabilité des prédictions ;
-   les tests automatisés et l'intégration continue.

## 2. Objectifs

-   Développer et évaluer des modèles de Machine Learning.
-   Structurer le projet selon les bonnes pratiques du développement
    logiciel.
-   Versionner et documenter le code.
-   Exposer le modèle à travers une API.
-   Assurer la traçabilité des prédictions.
-   Améliorer la reproductibilité et la maintenabilité du projet.

## 3. Structure du projet

```text
machine_learning_deployment/
├── .github/
│   └── workflows/
│       └── ci.yml
├── data/
│   ├── raw/
│   └── processed/
├── docs/
├── notebooks/
├── output/
│   └── models/
│       ├── lr_optimise.joblib
│       └── preprocessor.joblib
├── presentation/
│   └── diagramme_bdd.mmd
├── site/
├── src/
│   ├── create_tables.py
│   ├── database.py
│   ├── import_employees.py
│   ├── main.py
│   ├── models.py
│   └── schemas.py
├── tests/
│   ├── test_api.py
│   ├── test_create_tables.py
│   ├── test_database_config.py
│   ├── test_database_integration.py
│   ├── test_import_employees.py
│   ├── test_model_artifacts.py
│   └── test_project_structure.py
├── .env.example
├── .gitignore
├── mkdocs.yml
├── README.md
├── requirements.txt
└── requirements-dev.txt
```

## 4. Installation et configuration

### Prérequis

-   Python 3.12
-   Git
-   PostgreSQL

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

Pour un environnement local de développement, installer les dépendances
de l'application ainsi que les outils de test, de documentation et de
travail sur les notebooks :

```bash
python -m pip install --upgrade pip
pip install -r requirements-dev.txt
```

Le fichier `requirements-dev.txt` inclut `requirements.txt` et ajoute
les dépendances nécessaires au développement, notamment Jupyter,
Matplotlib, Seaborn, Pytest, pytest-cov et MkDocs.

Le fichier `requirements.txt` contient uniquement les dépendances
nécessaires à l'exécution de l'application en production : traitement
des données et chargement du modèle, API et accès à PostgreSQL.

Pour installer uniquement les dépendances de production :

```bash
pip install -r requirements.txt
```

### 4.4. Configurer PostgreSQL

La connexion à la base de données est définie à l'aide de la variable
d'environnement `DATABASE_URL`.

Créer un fichier `.env` à la racine du projet :

```dotenv
DATABASE_URL=postgresql+psycopg://utilisateur:mot_de_passe@localhost:5432/nom_base
API_KEY=votre_cle_api_secrete
```

Remplacer les valeurs d'exemple par les paramètres de votre
environnement local. La variable `API_KEY` protège l'endpoint de
prédiction.

Le fichier `.env` contient des informations sensibles et ne doit pas
être publié dans Git. Le fichier `.env.example` fournit un modèle de
configuration sans secret réel.

### 4.5. Préparer les données et les artefacts

Les deux artefacts nécessaires à la prédiction sont versionnés dans le
dépôt :

-   `output/models/lr_optimise.joblib` : modèle entraîné ;
-   `output/models/preprocessor.joblib` : préprocesseur des données.

Le fichier de données traité `data/processed/df_central.csv`, utilisé
pour l'importation des employés, n'est pas versionné dans le dépôt Git.

Il doit être obtenu à partir du projet de préparation des données (P4)
et placé dans le répertoire `data/processed/` avant l'exécution du
script d'importation.

Le fichier `.gitkeep` permet de conserver la structure des répertoires
dont les données ne sont pas versionnées.

## 5. E4 --- Base de données et traçabilité des prédictions

### 5.1. Architecture et choix techniques

L'application utilise FastAPI pour exposer le modèle de Machine Learning
et PostgreSQL pour conserver les données nécessaires à son
fonctionnement et assurer la traçabilité des prédictions.

La base de données sépare les données des employés, les entrées
transmises au modèle et les résultats produits.

### 5.2. Structure de la base de données

| Table | Rôle |
|---|---|
| `employees` | Stocke les données des employés utilisées par l'application. |
| `prediction_inputs` | Enregistre les données d'entrée envoyées au modèle au format JSON, ainsi que leur date de création. |
| `prediction_outputs` | Enregistre la prédiction, la probabilité associée, la référence à l'entrée correspondante et la date de création. |

La table `prediction_outputs` utilise la clé étrangère
`prediction_input_id` pour référencer l'entrée à l'origine du résultat.

Le champ `employee_id` de `prediction_inputs` référence l'employé
concerné par la prédiction. Dans le fonctionnement actuel de l'API, une
prédiction est associée à un employé existant grâce à son identifiant
`id_employee`.

Le schéma relationnel est représenté dans
`presentation/diagramme_bdd.mmd`.

### 5.3. Création des tables

Après avoir configuré PostgreSQL et la variable `DATABASE_URL`, exécuter
:

```bash
python -m src.create_tables
```

### 5.4. Importation des employés

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

Le script interrompt l'importation si la table `employees` contient déjà
des enregistrements, afin d'éviter une réimportation involontaire.

### 5.5. Traçabilité des prédictions

Lorsqu'une requête de prédiction est traitée par l'API :

1.  L'identifiant `id_employee` reçu est validé par le schéma
    `PredictionRequest`.
2.  L'API recherche l'employé correspondant dans la table `employees`.
3.  Les 25 variables attendues par le préprocesseur sont récupérées
    depuis l'enregistrement de cet employé.
4.  Les données sont transformées et la prédiction est calculée avec
    le modèle et le préprocesseur chargés au démarrage de l'API.
5.  Les données utilisées pour la prédiction sont enregistrées dans
    `prediction_inputs`, avec la référence `employee_id`.
6.  Le résultat est enregistré dans `prediction_outputs` et relié à
    son entrée.
7.  La transaction est validée avec `commit()`.

Si l'identifiant ne correspond à aucun employé, l'API retourne une
réponse HTTP `404`. En cas d'erreur pendant le traitement, la transaction
est annulée à l'aide de `rollback()`.

## 6. E5 --- Développement de l'API

### 6.1. Lancer l'API

Depuis la racine du projet, après avoir configuré l'environnement, la
base de données et les artefacts nécessaires, lancer :

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

L'endpoint `POST /predict` est protégé par une clé API transmise dans
l'en-tête HTTP `X-API-Key`.

La clé attendue est définie dans la variable d'environnement `API_KEY`
et n'est pas enregistrée directement dans le code source.

-   Une clé absente ou incorrecte entraîne une réponse HTTP
    `401 Unauthorized`.
-   Si la clé n'est pas configurée dans l'environnement, l'API retourne
    une erreur HTTP `500`.
-   Les endpoints `GET /` et `GET /health` restent accessibles sans
    authentification.

La comparaison de la clé est réalisée avec `secrets.compare_digest()`.

### 6.3. Endpoints disponibles

| Méthode | Endpoint | Description |
|---|---|---|
| `GET` | `/` | Retourne un message indiquant que l'API est opérationnelle et le chemin vers la documentation. |
| `GET` | `/health` | Retourne le statut de l'API. |
| `POST` | `/predict` | Reçoit l'identifiant d'un employé, calcule une prédiction et enregistre les données d'entrée et le résultat dans PostgreSQL. |

### 6.4. Fonctionnement de la prédiction

Le modèle `lr_optimise.joblib` et le préprocesseur
`preprocessor.joblib` sont chargés une seule fois au démarrage de
l'application, grâce au mécanisme `lifespan` de FastAPI. Ils sont
conservés dans `app.state` et réutilisés pour chaque requête.

L'endpoint `POST /predict` suit les étapes suivantes :

1.  Validation de l'identifiant reçu à l'aide du schéma
    `PredictionRequest`.
2.  Recherche de l'employé dans la table `employees`.
3.  Récupération des 25 variables utilisées par le modèle.
4.  Transformation des données avec le préprocesseur déjà chargé.
5.  Calcul de la classe prédite et de la probabilité associée.
6.  Enregistrement des données utilisées dans `prediction_inputs`,
    avec la clé étrangère `employee_id`.
7.  Enregistrement du résultat dans `prediction_outputs`.
8.  Validation de la transaction PostgreSQL et retour du résultat au
    client.

Si l'employé n'existe pas, l'API retourne une réponse HTTP `404`.

En cas d'erreur pendant le traitement, la transaction est annulée et
l'API retourne une erreur HTTP 500 avec un message générique.

Les données invalides sont rejetées lors de la validation de la requête,
avant l'exécution de la logique de prédiction, avec une réponse HTTP
422.

### 6.5. Format de la requête

L'endpoint `POST /predict` attend uniquement l'identifiant d'un
employé déjà enregistré dans la table `employees`.

Exemple de requête :

```json
{
  "id_employee": 1
}
```

L'API récupère ensuite automatiquement les 25 variables nécessaires
depuis PostgreSQL. Le client n'a donc pas besoin de transmettre les
caractéristiques de l'employé dans le corps de la requête.

Si l'identifiant est invalide, manquant ou inférieur ou égal à zéro,
FastAPI retourne une réponse HTTP `422`. Si l'employé n'existe pas,
l'API retourne une réponse HTTP `404`.

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

Le modèle retenu est une régression logistique optimisée à l'aide de
`RandomizedSearchCV`.

Le modèle est enregistré dans `output/models/lr_optimise.joblib`.

Les principaux hyperparamètres sont :

| Paramètre | Valeur |
|---|---|
| `C` | `0.01` |
| `solver` | `lbfgs` |
| `class_weight` | `balanced` |
| `max_iter` | `5000` |

Le prétraitement des données est assuré par
`output/models/preprocessor.joblib`, qui utilise un `ColumnTransformer`
et transforme les données d'entrée en 46 variables.

### 7.2. Performances du modèle

Les métriques suivantes proviennent de l'évaluation du modèle optimisé
sur le jeu de test du projet P4, composé de 294 observations, dont 47
cas d'attrition (`Oui`) et 247 cas sans attrition (`Non`).

| Métrique | Résultat |
|---|---:|
| Accuracy | 0,796 |
| Précision — classe `Oui` | 0,418 |
| Recall — classe `Oui` | 0,702 |
| F1-score — classe `Oui` | 0,524 |
| ROC-AUC | 0,814 |

Le F1-score moyen obtenu lors de la validation croisée est de
**0,5069**.

Le rappel de 0,702 indique que le modèle identifie environ 70 % des cas
d'attrition présents dans le jeu de test. En contrepartie, la précision
de 0,418 montre qu'une proportion importante des prédictions positives
est incorrecte.

L'accuracy doit être interprétée avec prudence en raison du déséquilibre
entre les classes.

Le modèle constitue un outil d'aide à l'analyse et ne doit pas être
utilisé seul pour prendre des décisions concernant les employés.

## 8. Tests automatisés et couverture du code

Les tests automatisés sont réalisés avec Pytest.

Les fichiers de tests sont regroupés dans le répertoire `tests/` :

-   `test_api.py`
-   `test_create_tables.py`
-   `test_database_config.py`
-   `test_database_integration.py`
-   `test_import_employees.py`
-   `test_model_artifacts.py`
-   `test_project_structure.py`

### Exécuter les tests

```bash
python -m pytest -v
```

### Générer le rapport de couverture

```bash
python -m pytest --cov=src --cov-report=term-missing --cov-report=html
```

Le rapport détaillé est généré dans le répertoire `htmlcov/`. Ouvrir
`htmlcov/index.html` dans un navigateur pour consulter le résultat.

### Résultats obtenus

Dernière exécution locale :

-   **33 tests réussis** ;
-   **0 test en échec** ;
-   durée d'exécution : **40,23 secondes** ;
-   **100 % de couverture du code source**.

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

## 9. Intégration continue et déploiement continu --- GitHub Actions

Le projet contient un workflow GitHub Actions dans
`.github/workflows/ci.yml`.

Le workflow automatise les vérifications du projet et le déploiement de
l'API sur Render selon l'événement déclencheur.

### 9.1. Intégration continue (CI)

Le job de test :

-   récupère le code du dépôt ;
-   configure Python 3.12 ;
-   installe les dépendances nécessaires à l'application et aux tests ;
-   configure l'environnement d'exécution avec `APP_ENV=test` ;
-   récupère `TEST_DATABASE_URL` depuis les GitHub Secrets ;
-   utilise la branche Neon `p5_test` pour les tests d'intégration ;
-   exécute la suite de tests automatisés.

`TEST_DATABASE_URL` pointe vers la branche Neon `p5_test`, réservée aux
tests. Elle est distincte de la base utilisée par l'API en production.

Le workflow est déclenché lors des événements `push` sur les branches
configurées et lors des `pull_request` vers `main`.

### 9.2. Déploiement continu (CD)

Un job de déploiement distinct est exécuté uniquement lors d'un `push`
sur la branche `main`, et seulement après la réussite du job de tests.

Ce job déclenche le déploiement du service Render à l'aide du Deploy Hook
stocké dans le secret GitHub `RENDER_DEPLOY_HOOK_URL`.

Le déploiement n'est donc pas lancé pour les simples `pull_request` ni
pour les pushes sur les branches de fonctionnalité.

Les secrets utilisés par le workflow sont configurés dans GitHub et ne
doivent jamais être inscrits directement dans le fichier YAML ou dans le
code source.

Le résultat de chaque exécution, ainsi que le statut des jobs de test et
de déploiement, doit être vérifié dans GitHub Actions.

## 10. Déploiement de l'API sur Render

L'API FastAPI est déployée sur Render en tant que service Web.

-   **Dépôt source :** `rafadmgs/machine_learning_deployment`
-   **Branche déployée :** `main`
-   **Commande de build :** `pip install -r requirements.txt`
-   **Commande de démarrage :**
    `uvicorn src.main:app --host 0.0.0.0 --port $PORT`

Les variables d'environnement sont configurées dans le tableau de bord
Render :

-   `API_KEY` : clé utilisée pour authentifier les demandes envoyées à
    `/predict` ;
-   `DATABASE_URL` : URL de connexion à la branche Neon `production`.

L'API est accessible à l'adresse :

`https://machine-learning-deployment-q0xp.onrender.com`

Les endpoints `/health` et `/docs` ont été vérifiés en ligne. Une
requête authentifiée sur `/predict` a également été exécutée avec
succès sur la version précédemment déployée. La version actuelle de
l'API, qui reçoit uniquement `id_employee` et récupère les variables
de l'employé depuis PostgreSQL, a été validée localement avec la base
de production. Son déploiement sur Render doit être confirmé après la
publication des dernières modifications sur la branche `main` et la
réussite du workflow GitHub Actions.

Le plan gratuit de Render peut mettre le service en veille après une
période d'inactivité. La première requête après cette veille peut donc
prendre plus de temps.

## 11. Sécurité et gestion des accès

### 11.1. Authentification de l'API

L'endpoint `POST /predict` est protégé par une clé API transmise dans l'en-tête HTTP `X-API-Key`.

La clé est stockée dans la variable d'environnement `API_KEY` et vérifiée avant le traitement de la demande.

Les endpoints `GET /` et `GET /health` restent accessibles sans authentification.

### 11.2. Gestion des identifiants

Les identifiants de connexion à PostgreSQL et la clé API sont stockés dans des variables d'environnement.

- En local, les variables sont définies dans le fichier `.env`, qui n'est pas versionné dans Git.
- Dans GitHub Actions, la connexion à la base de test est configurée dans le secret `TEST_DATABASE_URL`.
- Dans Render, les variables `DATABASE_URL` et `API_KEY` sont configurées dans les paramètres du service.

Les valeurs sensibles ne doivent jamais être publiées dans le dépôt.

### 11.3. Séparation des environnements et des rôles PostgreSQL

Les environnements de test et de production utilisent deux branches distinctes de Neon :

| Environnement | Branche | Rôle PostgreSQL |
|---|---|---|
| Tests automatisés | `p5_test` | `p5_test_user` |
| Production | `production` | `neondb_owner` |

Le rôle `p5_test_user` a été créé spécifiquement pour les tests automatisés.

Ses permissions sont limitées aux opérations `SELECT`, `INSERT` et `DELETE` sur les tables suivantes :

- `employees`
- `prediction_inputs`
- `prediction_outputs`

Les tests d'intégration PostgreSQL du workflow GitHub Actions utilisent ce rôle dédié.

En production, l'API hébergée sur Render utilise actuellement le rôle `neondb_owner`. Cette configuration possède des privilèges plus larges que ceux strictement nécessaires à l'application. La création d'un rôle dédié à l'API en production constitue donc une amélioration de sécurité future.

### 11.4. Protection des données

Les données des employés peuvent contenir des informations personnelles et professionnelles sensibles. Leur accès doit être limité aux personnes et aux applications autorisées.

Les prédictions doivent être utilisées comme un outil d'aide à l'analyse et ne doivent pas constituer, à elles seules, une base de décision concernant les employés.

## 12. Maintenance et pistes d'amélioration

1.  Surveiller les performances du modèle à l'aide de données récentes
    et de métriques adaptées à la classe `Oui`.
2.  Contrôler la qualité des données d'entrée et leur compatibilité avec
    le préprocesseur.
3.  Détecter les évolutions dans la distribution des données et dans la
    fréquence de l'attrition.
4.  Définir une procédure de réentraînement et d'évaluation avant le
    remplacement du modèle.
5.  Versionner les artefacts et conserver la traçabilité des modèles
    utilisés.
6.  Surveiller la disponibilité de l'API déployée et renforcer la
    protection des données ainsi que la gestion des accès.

Tout remplacement du modèle ou du préprocesseur doit être accompagné
d'une vérification de compatibilité des variables et d'une nouvelle
évaluation des performances.
