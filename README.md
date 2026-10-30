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
- les tests automatisés et l'intégration continue.

## 2. Objectifs

- Développer et évaluer des modèles de Machine Learning.
- Structurer le projet selon les bonnes pratiques du développement logiciel.
- Versionner et documenter le code.
- Exposer le modèle à travers une API.
- Assurer la traçabilité des prédictions.
- Améliorer la reproductibilité et la maintenabilité du projet.

## 3. Structure du projet

```text
machine_learning_deployment/
├── .github/
│   └── workflows/
│       └── ci.yml
├── data/
│   ├── raw/
│   └── processed/
├── notebooks/
├── output/
│   └── models/
│       ├── lr_optimise.joblib
│       └── preprocessor.joblib
├── presentation/
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
│   ├── test_import_employees.py
│   ├── test_model_artifacts.py
│   └── test_project_structure.py
├── .gitignore
├── README.md
└── requirements.txt
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

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

Les principales dépendances sont :
- pandas, numpy et scikit-learn pour le traitement des données et le Machine Learning ;
- FastAPI et Pydantic pour l'API et la validation des données ;
- SQLAlchemy et psycopg pour l'accès à PostgreSQL ;
- pytest et pytest-cov pour les tests et la couverture du code ;
- joblib pour le chargement des artefacts du modèle.

Les versions des dépendances directes sont précisées dans `requirements.txt`.

### 4.4. Configurer PostgreSQL

La connexion à la base de données est définie à l'aide de la variable d'environnement `DATABASE_URL`.

Créer un fichier `.env` à la racine du projet :

```dotenv
DATABASE_URL=postgresql+psycopg://utilisateur:mot_de_passe@localhost:5432/nom_base
```

Remplacer les valeurs d'exemple par les paramètres de votre environnement local.

Le fichier `.env` contient des informations sensibles et ne doit pas être publié dans Git.

### 4.5. Préparer les données et les artefacts

Les deux artefacts nécessaires à la prédiction sont versionnés dans le dépôt :

- `output/models/lr_optimise.joblib` : modèle entraîné ;
- `output/models/preprocessor.joblib` : préprocesseur des données.

Le fichier de données traité `data/processed/df_central.csv`, utilisé pour l'importation des employés, n'est pas versionné dans le dépôt Git.

Il doit être obtenu à partir du projet de préparation des données (P4) et placé dans le répertoire `data/processed/` avant l'exécution du script d'importation.

Le fichier `.gitkeep` permet de conserver la structure des répertoires dont les données ne sont pas versionnées.

## 5. E4 — Base de données et traçabilité des prédictions

### 5.1. Architecture et choix techniques

L'application utilise FastAPI pour exposer le modèle de Machine Learning et PostgreSQL pour conserver les données nécessaires à son fonctionnement et assurer la traçabilité des prédictions.

La base de données sépare les données des employés, les entrées transmises au modèle et les résultats produits.

### 5.2. Structure de la base de données

| Table | Rôle |
|---|---|
| `employees` | Stocke les données des employés utilisées par l'application. |
| `prediction_inputs` | Enregistre les données d'entrée envoyées au modèle au format JSON, ainsi que leur date de création. |
| `prediction_outputs` | Enregistre la prédiction, la probabilité associée, la référence à l'entrée correspondante et la date de création. |

La table `prediction_outputs` utilise la clé étrangère `prediction_input_id` pour référencer l'entrée à l'origine du résultat.

Le champ `employee_id` de `prediction_inputs` est nullable : une prédiction peut donc être enregistrée sans être associée directement à un employé existant.

Le schéma relationnel est représenté dans `presentation/diagramme_bdd.mmd`.

### 5.3. Création des tables

Après avoir configuré PostgreSQL et la variable `DATABASE_URL`, exécuter :

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

Le script interrompt l'importation si la table `employees` contient déjà des enregistrements, afin d'éviter une réimportation involontaire.

### 5.5. Traçabilité des prédictions

Lorsqu'une requête de prédiction est traitée par l'API :

1. Les données reçues sont validées par le schéma `PredictionRequest`.
2. Le modèle et le préprocesseur sont chargés.
3. Les données d'entrée sont transformées et la prédiction est calculée.
4. Les données d'entrée sont enregistrées dans `prediction_inputs`.
5. Le résultat est enregistré dans `prediction_outputs` et relié à son entrée.
6. La transaction est validée avec `commit()`.

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

### 6.2. Endpoints disponibles

| Méthode | Endpoint | Description |
|---|---|---|
| `GET` | `/` | Retourne un message indiquant que l'API est opérationnelle et le chemin vers la documentation. |
| `GET` | `/health` | Retourne le statut de l'API. |
| `POST` | `/predict` | Reçoit les caractéristiques d'un employé, calcule une prédiction et enregistre les données d'entrée et le résultat dans PostgreSQL. |

### 6.3. Fonctionnement de la prédiction

L'endpoint `POST /predict` suit les étapes suivantes :

1. Validation des données reçues à l'aide du schéma `PredictionRequest`.
2. Chargement du modèle `lr_optimise.joblib` et du préprocesseur `preprocessor.joblib`.
3. Transformation des données d'entrée.
4. Calcul de la classe prédite et de la probabilité associée.
5. Enregistrement des données d'entrée dans `prediction_inputs`.
6. Enregistrement du résultat dans `prediction_outputs`.
7. Validation de la transaction PostgreSQL et retour du résultat au client.

En cas d'erreur pendant le traitement, la transaction est annulée et l'API retourne une erreur HTTP 500 avec un message générique.

Les données invalides sont rejetées lors de la validation de la requête, avant l'exécution de la logique de prédiction, avec une réponse HTTP 422.

### 6.4. Format de la requête

L'endpoint `POST /predict` attend un objet JSON contenant les 25 champs définis dans le schéma `PredictionRequest`.

Exemple de requête :

```json
{
  "age": 35,
  "genre": "F",
  "revenu_mensuel": 5000,
  "statut_marital": "Marié(e)",
  "departement": "Consulting",
  "poste": "Consultant",
  "nombre_experiences_precedentes": 2,
  "annee_experience_totale": 10,
  "annees_dans_l_entreprise": 4,
  "satisfaction_employee_environnement": 3,
  "note_evaluation_precedente": 3,
  "niveau_hierarchique_poste": 2,
  "satisfaction_employee_nature_travail": 3,
  "satisfaction_employee_equipe": 4,
  "satisfaction_employee_equilibre_pro_perso": 3,
  "note_evaluation_actuelle": 4,
  "heure_supplementaires": "Non",
  "augementation_salaire_precedente": 15,
  "nombre_participation_pee": 1,
  "nb_formations_suivies": 2,
  "distance_domicile_travail": 10,
  "niveau_education": 3,
  "domaine_etude": "Marketing",
  "frequence_deplacement": "Occasionnel",
  "annees_depuis_la_derniere_promotion": 2
}
```

Les valeurs numériques doivent respecter les limites définies dans `src/schemas.py`. Les champs catégoriels doivent utiliser exactement l'une des valeurs autorisées par le schéma.

Les champs manquants, les données invalides et les champs supplémentaires sont rejetés par FastAPI avec une réponse HTTP 422.

### 6.5. Format de la réponse

Une réponse réussie contient les champs suivants :

- `prediction_id` : identifiant du résultat enregistré dans la base de données ;
- `prediction` : classe prédite par le modèle ;
- `probability` : probabilité associée à la classe prédite ;
- `message` : message décrivant le résultat, soit un départ prédit, soit un maintien prédit.

Exemple illustratif :

```json
{
  "prediction_id": 1,
  "prediction": "Non",
  "probability": 0.92,
  "message": "Le modèle prédit un maintien."
}
```

Les valeurs de cet exemple sont illustratives : le résultat réel dépend des données transmises au modèle et de la prédiction calculée.

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
- `test_import_employees.py`
- `test_model_artifacts.py`
- `test_project_structure.py`

### Exécuter les tests

```bash
python -m pytest -v
```

### Générer le rapport de couverture

```bash
python -m pytest --cov=src --cov-report=term-missing --cov-report=html --cov-fail-under=100
```

Le rapport détaillé est généré dans le répertoire `htmlcov/`. Ouvrir `htmlcov/index.html` dans un navigateur pour consulter le résultat.

### Résultats obtenus

Dernière exécution locale :

- **24 tests réussis** ;
- **186 instructions analysées** ;
- **100 % de couverture du code source (`src/`)** ;
- aucune instruction non couverte.

La couverture mesure l'exécution des instructions du code pendant les tests. Certains tests utilisent des mocks pour isoler les composants : ce résultat ne constitue donc pas, à lui seul, une validation de bout en bout avec une instance PostgreSQL réelle.

## 9. Intégration continue — GitHub Actions

Le projet contient un workflow GitHub Actions dans `.github/workflows/ci.yml`.

Le workflow :
- récupère le code du dépôt ;
- configure Python 3.12 ;
- installe les dépendances ;
- exécute les tests automatisés.

Il est déclenché lors des événements `push` sur les branches configurées et lors des `pull_request` vers `main`.

Ce workflow correspond à une intégration continue (CI). Il automatise les tests, mais ne réalise pas de déploiement automatique de l'API.

Le résultat de l'exécution du workflow doit être vérifié dans GitHub Actions.

## 10. Sécurité et limites

- Le fichier `.env` ne doit jamais être publié dans Git.
- Les identifiants de connexion à PostgreSQL doivent rester confidentiels.
- Les données personnelles des employés doivent être protégées.
- Le fichier `data/processed/df_central.csv` doit être obtenu séparément à partir du projet P4.
- Le fonctionnement avec une instance PostgreSQL réelle doit être vérifié dans l'environnement de livraison.
- Les tests avec mocks ne remplacent pas les tests d'intégration.
- Les métriques du modèle doivent être réévaluées périodiquement sur des données récentes.

## 11. Maintenance et pistes d'amélioration

1. Surveiller les performances du modèle à l'aide de données récentes et de métriques adaptées à la classe `Oui`.
2. Contrôler la qualité des données d'entrée et leur compatibilité avec le préprocesseur.
3. Détecter les évolutions dans la distribution des données et dans la fréquence de l'attrition.
4. Définir une procédure de réentraînement et d'évaluation avant le remplacement du modèle.
5. Versionner les artefacts et conserver la traçabilité des modèles utilisés.
6. Renforcer la gestion des secrets et la protection des données avant tout déploiement en production.

Tout remplacement du modèle ou du préprocesseur doit être accompagné d'une vérification de compatibilité des variables et d'une nouvelle évaluation des performances.