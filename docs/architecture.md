# Architecture et choix techniques

## 1. Vue d'ensemble

La solution transforme le modèle de Machine Learning développé dans le cadre du projet P4 en une application opérationnelle de prédiction de l'attrition des employés.

L'application expose une API REST avec FastAPI. Elle valide les données entrantes, applique le prétraitement sauvegardé avec le modèle entraîné, produit une prédiction et conserve les données d'entrée et les résultats dans PostgreSQL.

L'architecture comprend quatre composants fonctionnels principaux :

1. **API FastAPI** : reçoit les requêtes HTTP et expose les endpoints.
2. **Validation Pydantic** : contrôle les champs, les types et les contraintes des données fournies.
3. **Pipeline Machine Learning** : transforme les données avec le préprocesseur et exécute le modèle entraîné.
4. **PostgreSQL** : conserve les données des employés ainsi que l'historique des entrées et des prédictions.

Des composants complémentaires assurent la création et l'importation des données, les tests automatisés, l'intégration continue et la documentation technique.

## 2. Technologies

| Composant | Technologie |
|---|---|
| Langage | Python |
| API REST | FastAPI |
| Validation des entrées | Pydantic |
| Base de données | PostgreSQL |
| Accès aux données | SQLAlchemy |
| Manipulation des données | pandas |
| Chargement des artefacts | joblib |
| Tests | pytest |
| Intégration continue | GitHub Actions |
| Documentation technique | MkDocs |

## 3. Organisation du code

| Fichier ou répertoire | Responsabilité |
|---|---|
| `src/main.py` | Configuration de l'API et endpoints HTTP |
| `src/database.py` | Configuration de la connexion PostgreSQL et gestion des sessions SQLAlchemy |
| `src/models.py` | Définition des modèles ORM et des tables |
| `src/schemas.py` | Validation des données entrantes avec Pydantic |
| `src/create_tables.py` | Création des tables déclarées dans les modèles ORM |
| `src/import_employees.py` | Contrôle et importation des employés depuis le fichier CSV |
| `tests/` | Tests automatisés de la structure, de l'API, de la base et des artefacts |
| `output/models/` | Artefacts nécessaires à la prédiction |
| `data/raw/` | Fichiers de données sources |
| `data/processed/` | Fichiers issus de la préparation des données |
| `docs/` | Documentation technique du projet |
| `.github/workflows/ci.yml` | Configuration du workflow d'intégration continue |

## 4. Architecture globale

Le schéma suivant présente les principaux composants de l'application et leurs interactions.

```mermaid
flowchart TD
    CLIENT["Client HTTP"]
    API["FastAPI<br/>src/main.py"]
    SCHEMA["Validation Pydantic<br/>PredictionRequest"]
    PREPROCESSOR["Préprocesseur<br/>preprocessor.joblib"]
    MODEL["Modèle entraîné<br/>lr_optimise.joblib"]
    DB["PostgreSQL"]
    INPUTS[("prediction_inputs")]
    OUTPUTS[("prediction_outputs")]
    EMPLOYEES[("employees")]
    ARTIFACTS["Artefacts issus du P4"]
    TESTS["Tests pytest"]
    CI["GitHub Actions"]
    DOCS["Documentation MkDocs"]

    CLIENT --> API
    API --> SCHEMA
    SCHEMA --> PREPROCESSOR
    PREPROCESSOR --> MODEL
    MODEL --> API
    API --> INPUTS
    INPUTS --> OUTPUTS
    DB --- INPUTS
    DB --- OUTPUTS
    DB --- EMPLOYEES
    ARTIFACTS -.-> PREPROCESSOR
    ARTIFACTS -.-> MODEL
    TESTS --> CI
```

Les artefacts du P4 sont utilisés par l'application P5. Le workflow CI présenté ici exécute les tests automatisés ; il ne réentraîne pas le modèle et ne déploie pas automatiquement l'API.

## 5. Préparation et organisation des données

### 5.1. Données sources

Le répertoire `data/raw/` contient les fichiers suivants :

| Fichier | Lignes | Colonnes |
|---|---:|---:|
| `extrait_sirh.csv` | 1 470 | 12 |
| `extrait_eval.csv` | 1 470 | 10 |
| `extrait_sondage.csv` | 1 470 | 12 |

### 5.2. Données traitées

Le répertoire `data/processed/` contient les fichiers suivants :

| Fichier | Lignes | Colonnes |
|---|---:|---:|
| `df_central.csv` | 1 470 | 29 |
| `df_modelisation.csv` | 1 470 | 47 |
| `df_modelisation_final.csv` | 1 470 | 46 |
| `resultats_attraction.csv` | 294 | 3 |
| `resultats_attrition.csv` | 294 | 3 |

Ces volumes correspondent à l'inventaire local des fichiers au moment de la vérification. Le script `src/import_employees.py` utilise spécifiquement `data/processed/df_central.csv` pour alimenter la table `employees`.

### 5.3. Importation des employés

Le script `src/import_employees.py` vérifie :

- l'existence du fichier CSV ;
- la compatibilité entre les colonnes du CSV et celles de la table `employees` ;
- l'absence d'identifiants employés dupliqués ou manquants ;
- l'absence de valeurs manquantes ;
- l'absence d'enregistrements déjà présents dans la table `employees`.

Si la table est vide et que les contrôles sont satisfaits, les enregistrements sont insérés dans une transaction SQLAlchemy. Si des employés sont déjà présents, l'importation est interrompue sans modifier les données existantes.

## 6. Base de données

La configuration de la connexion est définie dans `src/database.py`. La variable `DATABASE_URL` est chargée depuis l'environnement après lecture du fichier `.env`. Si elle est absente, le module lève une erreur de configuration.

Le module crée le moteur SQLAlchemy, configure les sessions et fournit la dépendance `get_db()` utilisée par l'API.

### 6.1. Tables principales

| Table | Rôle |
|---|---|
| `employees` | Stockage des données des employés importées depuis le CSV |
| `prediction_inputs` | Stockage des données soumises à l'API |
| `prediction_outputs` | Stockage des classes prédites et des probabilités associées |

La table `prediction_inputs` possède une clé étrangère facultative `employee_id` vers `employees.id_employee`. Dans le flux actuel de l'endpoint `/predict`, cette clé n'est pas renseignée automatiquement.

La table `prediction_outputs` référence `prediction_inputs` par la clé étrangère `prediction_input_id`.

### 6.2. Création des tables

Le script `src/create_tables.py` utilise `Base.metadata.create_all()` pour créer les tables déclarées dans les modèles ORM lorsqu'elles n'existent pas. Il ne constitue pas un système de migration de schéma.

La création des tables et l'importation des employés sont des opérations distinctes de l'exécution de l'API.

## 7. Flux d'une prédiction

L'endpoint `POST /predict` exécute les étapes suivantes :

1. Le client envoie les données d'un employé.
2. FastAPI et Pydantic valident les champs, les types et les contraintes.
3. L'API charge les artefacts `lr_optimise.joblib` et `preprocessor.joblib`.
4. Les données validées sont converties en DataFrame pandas.
5. Le préprocesseur transforme les données d'entrée.
6. Le modèle calcule la classe prédite et les probabilités associées aux classes.
7. L'entrée est enregistrée dans `prediction_inputs`.
8. `db.flush()` permet de récupérer l'identifiant de l'entrée avant la création du résultat.
9. Le résultat est enregistré dans `prediction_outputs`.
10. `db.commit()` confirme la transaction.
11. L'API retourne l'identifiant de prédiction, la classe, la probabilité associée et un message interprétatif.

La probabilité retournée correspond à la probabilité associée à la classe prédite. Elle ne doit pas être interprétée automatiquement comme la probabilité de départ sans vérifier la classe prédite.

### 7.1. Diagramme de séquence

```mermaid
sequenceDiagram
    autonumber
    actor Client
    participant API as FastAPI
    participant Pydantic
    participant ML as Modèle et préprocesseur
    participant DB as PostgreSQL via SQLAlchemy

    Client->>API: POST /predict
    API->>Pydantic: Validation de PredictionRequest

    alt Données invalides
        Pydantic-->>Client: HTTP 422
    else Données valides
        Pydantic-->>API: Données validées
        API->>ML: Chargement des artefacts
        ML->>ML: Transformation des données
        ML->>ML: Prédiction et calcul des probabilités
        ML-->>API: Classe et probabilité associée
        API->>DB: INSERT prediction_inputs
        DB-->>API: Identifiant de l'entrée après flush
        API->>DB: INSERT prediction_outputs
        API->>DB: COMMIT
        DB-->>API: Transaction confirmée
        API-->>Client: HTTP 200 et résultat
    end

    opt Exception pendant le traitement
        API->>DB: ROLLBACK
        API-->>Client: HTTP 500
    end
```

Le diagramme décrit le flux nominal et les principales catégories d'erreurs. Le traitement des exceptions est réalisé dans l'endpoint, qui annule la transaction en cas d'erreur et renvoie une erreur HTTP 500.

## 8. Gestion des erreurs et limites actuelles

- Les données invalides sont rejetées lors de la validation de la requête.
- Une erreur survenant pendant le traitement de la prédiction entraîne un `rollback` de la session et une réponse HTTP 500 générique.
- Les artefacts du modèle et du préprocesseur sont chargés à chaque appel de `POST /predict`, car `load_artifacts()` est invoqué dans l'endpoint.
- La table `employees` est alimentée par un script distinct ; l'endpoint `/predict` ne rattache pas automatiquement chaque requête à un employé existant.
- Le workflow CI exécute les tests automatisés, mais ne met pas en œuvre de déploiement automatique.

## 9. Tests et intégration continue

Les tests sont regroupés dans le répertoire `tests/`. Ils couvrent notamment la structure du projet, les endpoints de l'API, la configuration de la base de données, la création des tables, l'importation des employés et les artefacts du modèle.

Le workflow `.github/workflows/ci.yml` :

1. s'exécute sur Ubuntu ;
2. configure Python 3.12 ;
3. installe les dépendances du projet et les outils de test ;
4. exécute `python -m pytest`.

Le workflow est configuré pour les pushs sur `main`, les branches `feature/**` et les pull requests vers `main`. Il ne réalise pas de déploiement de l'application.

## 10. Configuration de la base de données

La variable `DATABASE_URL` doit être définie dans l'environnement ou dans un fichier `.env` local.

Exemple de format à adapter à l'environnement :

```dotenv
DATABASE_URL=postgresql+psycopg://utilisateur:mot_de_passe@localhost:5432/nom_base
```

Ne pas publier les identifiants de connexion dans le dépôt Git.

## 11. Gestion des fichiers et des artefacts

Le fichier `.gitignore` exclut les fichiers de données contenus dans `data/raw/` et `data/processed/`, ainsi que le contenu de `output/`. Les fichiers `.gitkeep` permettent de conserver les répertoires dans Git.

Les artefacts nécessaires à l'exécution de l'API doivent néanmoins être disponibles dans `output/models/`. Leur présence dans l'environnement d'exécution est nécessaire au fonctionnement de l'endpoint de prédiction.

La documentation technique est construite avec MkDocs à partir des fichiers du répertoire `docs/`.
