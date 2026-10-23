# Déploiement d'un modèle de Machine Learning de prédiction chez TechNova Partners

Projet de Data Science consacré au développement, à l'évaluation et au déploiement d'un modèle de Machine Learning pour la prédiction de l'attrition des employés.

## Présentation du projet

Ce projet vise à transformer un modèle de prédiction de l'attrition des employés de l'entreprise TechNova Partners en une application exploitable, en suivant une démarche structurée et reproductible.

Il couvre :

- la préparation des données,
- l'entraînement et l'évaluation du modèle,
-  la mise en place d'une API,
- l'intégration d'une base de données PostgreSQL,
-  les tests automatisés et l'intégration continue.

## Objectifs

- Développer et évaluer des modèles de Machine Learning.
- Structurer le projet selon les bonnes pratiques du développement logiciel.
- Versionner et documenter le code.
- Exposer le modèle à travers une API.
- Assurer la traçabilité des prédictions.
- Améliorer la reproductibilité et la maintenabilité du projet.

## Structure du projet

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

Les données, les artefacts du modèle et les fichiers de configuration locaux ne sont pas nécessairement versionnés dans Git. Leur disponibilité doit être vérifiée avant l'exécution de l'application.

## Installation et configuration

### Prérequis

- Python 3.12 ou version ultérieure
- Git
- PostgreSQL
- Les données traitées et les artefacts du modèle nécessaires à l'exécution de l'API

### 1. Cloner le dépôt

```bash
git clone https://github.com/rafadmgs/machine_learning_deployment.git
cd machine_learning_deployment
```

### 2. Créer et activer un environnement virtuel

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

### 3. Installer les dépendances

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Configurer la connexion à PostgreSQL

La connexion à la base de données est définie à l'aide de la variable d'environnement `DATABASE_URL`.

Créer un fichier `.env` à la racine du projet et y définir cette variable avec les paramètres de connexion de l'environnement local :

```dotenv
DATABASE_URL=postgresql+psycopg://utilisateur:mot_de_passe@localhost:5432/nom_base
```

Remplacer les valeurs d'exemple par celles de votre environnement. Le fichier `.env` contient des informations sensibles et ne doit pas être publié dans Git.

La base de données doit être accessible et les tables doivent être créées avant l'utilisation des fonctionnalités qui enregistrent des données.

### 5. Exécuter les tests

```bash
python -m pytest -v
```

Les tests vérifient plusieurs composants du projet, notamment les endpoints de l'API, la validation des entrées, la gestion des erreurs, la configuration de la base de données, l'importation des employés et le chargement des artefacts du modèle.

## E4 — Base de données et traçabilité des prédictions

### Architecture et choix techniques

L'application utilise FastAPI pour exposer le modèle de Machine Learning et PostgreSQL pour conserver les données nécessaires à son fonctionnement et assurer la traçabilité des prédictions.

La base de données sépare les données des employés, les entrées transmises au modèle et les résultats produits. Cette organisation permet de relier chaque résultat aux données qui l'ont généré.

### Structure de la base de données

| Table | Rôle |
|---|---|
| `employees` | Stocke les données des employés utilisées par l'application. |
| `prediction_inputs` | Enregistre les données d'entrée envoyées au modèle au format JSON, ainsi que leur date de création. |
| `prediction_outputs` | Enregistre la prédiction, la probabilité associée, la référence à l'entrée correspondante et la date de création. |

La table `prediction_inputs` possède un identifiant unique. La table `prediction_outputs` utilise la clé étrangère `prediction_input_id` pour référencer l'entrée à l'origine du résultat.

Le champ `employee_id` de `prediction_inputs` est nullable : une prédiction peut donc être enregistrée sans être associée directement à un employé existant.

Le schéma relationnel est représenté dans `presentation/diagramme_bdd.mmd`.

### Importation des données

Le jeu de données des employés est importé depuis le fichier traité `data/processed/df_central.csv`.

Le script `src/import_employees.py` vérifie notamment la présence du fichier, la compatibilité des colonnes, les identifiants dupliqués, les identifiants manquants et les autres valeurs manquantes.

Le jeu de données utilisé pour cette étape contient 1 470 employés. Le script interrompt l'importation si la table `employees` contient déjà des enregistrements, afin d'éviter une réimportation involontaire.

### Traçabilité des prédictions

Lorsqu'une requête de prédiction est traitée par l'API :

1. Les données reçues sont validées par le schéma `PredictionRequest`.
2. Le modèle et le préprocesseur sont chargés.
3. Les données d'entrée sont transformées et la prédiction est calculée.
4. Les données d'entrée sont enregistrées dans `prediction_inputs`.
5. Le résultat est enregistré dans `prediction_outputs` et relié à son entrée.
6. La transaction est validée avec `commit()`.

En cas d'erreur pendant le traitement, la transaction est annulée à l'aide de `rollback()`.

### Sécurité et configuration

La connexion à PostgreSQL est configurée à l'aide de la variable d'environnement `DATABASE_URL`, définie dans le fichier local `.env`.

Le fichier `.env` et les artefacts locaux du modèle ne doivent pas être versionnés dans Git. Les identifiants de connexion ne doivent jamais être intégrés au code source ni publiés dans le dépôt.

Pour un déploiement en production, il est recommandé d'utiliser un compte de base de données disposant uniquement des privilèges nécessaires, de protéger les secrets et de limiter l'accès aux données personnelles.

### Lancer l'API

Depuis la racine du projet, après avoir configuré l'environnement, la base de données et les artefacts nécessaires, lancer :

```powershell
python -m uvicorn src.main:app --reload
```

La documentation interactive de l'API est accessible à l'adresse suivante :

`http://127.0.0.1:8000/docs`

Pour consulter le schéma OpenAPI :

`http://127.0.0.1:8000/openapi.json`

## Documentation de l'API

L'API REST est développée avec FastAPI et permet de prédire l'attrition des employés à partir de leurs caractéristiques professionnelles et personnelles.

### Endpoints disponibles

| Méthode | Endpoint | Description |
|---|---|---|
| `GET` | `/` | Retourne un message indiquant que l'API est opérationnelle et le chemin vers la documentation. |
| `GET` | `/health` | Retourne le statut de l'API. |
| `POST` | `/predict` | Reçoit les caractéristiques d'un employé, calcule une prédiction et enregistre les données d'entrée et le résultat dans PostgreSQL. |

### Fonctionnement de la prédiction

L'endpoint `POST /predict` suit les étapes suivantes :

1. Validation des données reçues à l'aide du schéma `PredictionRequest`.
2. Chargement du modèle `lr_optimise.joblib` et du préprocesseur `preprocessor.joblib`.
3. Transformation des données d'entrée.
4. Calcul de la classe prédite et de la probabilité associée.
5. Enregistrement des données d'entrée dans `prediction_inputs`.
6. Enregistrement du résultat dans `prediction_outputs`.
7. Validation de la transaction PostgreSQL et retour du résultat au client.

En cas d'erreur pendant le traitement, la transaction est annulée et l'API retourne une erreur HTTP 500 avec un message générique. Les données invalides sont rejetées lors de la validation de la requête, avant l'exécution de la logique de prédiction.

### Format de la requête

L'endpoint `POST /predict` attend un objet JSON contenant les 25 champs définis dans le schéma `PredictionRequest`. Tous les champs sont obligatoires et les champs supplémentaires sont refusés.

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

Une requête contenant des données invalides, des champs manquants ou des champs supplémentaires est rejetée par FastAPI avec une réponse HTTP 422.

### Format de la réponse

Une réponse réussie contient les champs suivants :

- `prediction_id` : identifiant du résultat enregistré dans la base de données ;
- `prediction` : classe prédite par le modèle ;
- `probability` : probabilité associée à la classe prédite ;
- `message` : message décrivant le résultat, soit un départ prédit, soit un maintien prédit.

Exemple illustratif de réponse :

```json
{
  "prediction_id": 1,
  "prediction": "Non",
  "probability": 0.92,
  "message": "Le modèle prédit un maintien."
}
```

Les valeurs de cet exemple sont illustratives : le résultat réel dépend des données transmises au modèle et de la prédiction calculée.

## Documentation technique du modèle

### Modèle retenu

Le modèle retenu est une régression logistique optimisée à l'aide de `RandomizedSearchCV`. Il est enregistré dans `output/models/lr_optimise.joblib`.

Le modèle est constitué d'un pipeline comprenant les étapes suivantes :

1. **StandardScaler** : standardisation des variables numériques après prétraitement.
2. **LogisticRegression** : classification des employés en deux catégories : `Oui` (attrition) et `Non` (absence d'attrition).

Les principaux hyperparamètres du modèle sont :

| Paramètre | Valeur |
|---|---|
| `C` | `0.01` |
| `solver` | `lbfgs` |
| `class_weight` | `balanced` |
| `max_iter` | `5000` |

Le prétraitement des données est assuré par le fichier `output/models/preprocessor.joblib`, qui utilise un `ColumnTransformer`. Il transforme les données d'entrée en 46 variables. Le notebook P4 confirme que les noms et l'ordre des variables produites par le préprocesseur correspondent à ceux attendus par le modèle.

### Performances du modèle

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

L'accuracy doit être interprétée avec prudence en raison du déséquilibre entre les classes. Le modèle constitue un outil d'aide à l'analyse et ne doit pas être utilisé seul pour prendre des décisions concernant les employés.

### Limites du modèle

- Les performances mesurées dépendent des données utilisées pour l'entraînement et l'évaluation.
- Les résultats peuvent varier selon la population étudiée et l'évolution des facteurs associés à l'attrition.
- Les faux positifs et les faux négatifs doivent être pris en compte dans l'interprétation des prédictions.
- Les prédictions ne démontrent pas de relation causale et ne doivent pas remplacer une analyse humaine.
- Les métriques présentées correspondent à l'évaluation réalisée dans P4 ; elles ne constituent pas, à elles seules, une validation de bout en bout de l'API P5.

### Maintenance et suivi du modèle

Pour maintenir la solution, les actions suivantes sont recommandées :

1. **Surveiller les performances** : réévaluer périodiquement le modèle à l'aide de données récentes et de métriques adaptées à la classe `Oui`.
2. **Contrôler les données** : vérifier la qualité des données d'entrée, les valeurs manquantes, les catégories et la compatibilité des variables.
3. **Détecter les évolutions** : rechercher les changements dans la distribution des données et dans la fréquence de l'attrition.
4. **Réentraîner si nécessaire** : comparer tout nouveau modèle au modèle actuel sur un protocole d'évaluation documenté avant son remplacement.
5. **Versionner les artefacts** : conserver la traçabilité du modèle, du préprocesseur, des données d'entraînement et des métriques associées.
6. **Valider avant déploiement** : exécuter les tests automatisés et vérifier le fonctionnement de l'API et de la connexion à PostgreSQL avant toute mise à jour en production.

Tout remplacement du modèle ou du préprocesseur doit être accompagné d'une vérification de compatibilité des variables et d'une nouvelle évaluation des performances.

## Intégration continue

Le projet contient un workflow GitHub Actions dans `.github/workflows/ci.yml`. Ce workflow installe les dépendances Python et exécute la suite de tests lors des événements configurés dans le dépôt.

Le résultat de l'exécution du workflow doit être vérifié dans GitHub Actions avant de conclure que la validation continue est opérationnelle.

## Limites et pistes d'amélioration

- Documenter la procédure complète de génération ou d'obtention des données traitées et des artefacts du modèle.
- Vérifier le fonctionnement avec une instance PostgreSQL réelle.
- Vérifier le résultat du workflow GitHub Actions.
- Envisager un verrouillage des versions des dépendances pour améliorer la reproductibilité.
- Définir une procédure de réentraînement, d'évaluation et de remplacement du modèle.
- Renforcer la gestion des secrets et la protection des données avant tout déploiement en production.