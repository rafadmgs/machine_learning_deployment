# Machine Learning Deployment

Machine learning project covering model development, evaluation, deployment, and production integration.

## Project Overview

This project focuses on developing and deploying a Machine Learning model following a structured and reproducible workflow.

The project covers the different stages required to move from model development to a production-ready solution.

## Objectives

- Develop and evaluate Machine Learning models.
- Structure the project following software engineering best practices.
- Version and document the development process.
- Prepare the model for deployment.
- Ensure reproducibility and maintainability.

## Project Structure

```text
machine_learning_deployment/
│
├── data/
│   ├── raw/
│   └── processed/
│
├── notebooks/
│
├── output/
│
├── src/
│
├── tests/
│
├── .github/
│   └── workflows/
│       └── ci.yml
│
├── .gitignore
├── README.md
└── requirements.txt

## Installation and Setup

### Prerequisites

- Python 3.12 or higher
- Git

### 1. Clone the repository

```bash
git clone https://github.com/rafadmgs/machine_learning_deployment.git
cd machine_learning_deployment
```

### 2. Create and activate a virtual environment

**Windows (PowerShell):**

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

**Linux / macOS:**

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencies

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Run the tests

```bash
python -m pytest

```
## E4 — Base de données et traçabilité des prédictions

### Architecture et choix techniques

L'application utilise FastAPI pour exposer le modèle de Machine Learning et PostgreSQL pour conserver les données nécessaires à son fonctionnement et assurer la traçabilité des prédictions.

La base de données sépare les données des employés, les entrées transmises au modèle et les résultats produits. Cette organisation facilite le suivi des prédictions et permet de relier chaque résultat aux données qui l'ont généré.

### Structure de la base de données

| Table | Rôle |
|---|---|
| `employees` | Stocke les données des employés utilisées par l'application. |
| `prediction_inputs` | Enregistre les données d'entrée envoyées au modèle, au format JSON, ainsi que leur date de création. |
| `prediction_outputs` | Enregistre la prédiction, la probabilité associée, la référence à l'entrée correspondante et la date de création. |

La table `prediction_inputs` possède un identifiant unique. La table `prediction_outputs` utilise la clé étrangère `prediction_input_id` pour référencer l'entrée à l'origine du résultat. Le champ `employee_id` dans `prediction_inputs` est nullable : une prédiction peut donc être enregistrée sans être associée directement à un employé existant.

Le schéma relationnel est représenté dans `presentation/diagramme_bdd.mmd`.

### Importation des données

Le jeu de données des employés est importé depuis le fichier CSV traité. Le script `src/import_employees.py` vérifie notamment la présence du fichier, la structure attendue des colonnes, les identifiants dupliqués, les valeurs manquantes et le nombre de lignes importées.

Le jeu de données utilisé pour cette étape contient 1 470 employés. Le script empêche un nouvel import lorsque la table `employees` contient déjà des données, afin d'éviter une duplication lors d'une importation initiale.

### Traçabilité des prédictions

Lorsqu'une requête de prédiction est traitée par l'API :

1. Les données reçues sont validées par le schéma de requête.
2. Les données d'entrée sont enregistrées dans `prediction_inputs`.
3. L'identifiant de l'entrée est récupéré afin de relier le résultat à sa source.
4. Le modèle calcule la prédiction et la probabilité associée.
5. Le résultat est enregistré dans `prediction_outputs`.
6. Les écritures sont validées dans une transaction de base de données.

Cette organisation permet de retrouver les données d'entrée associées à une prédiction et de vérifier le résultat enregistré. Les opérations d'écriture sont annulées en cas d'erreur afin d'éviter de conserver une transaction incomplète.


### Configuration et sécurité

La connexion à PostgreSQL est configurée à l'aide de la variable d'environnement `DATABASE_URL`, définie dans le fichier local `.env`.

Le fichier `.env` et les artefacts locaux du modèle ne doivent pas être versionnés dans Git. Les identifiants de connexion ne doivent jamais être ajoutés au code source ni publiés dans le dépôt.

Pour un déploiement en production, il est recommandé d'utiliser un compte de base de données disposant uniquement des privilèges nécessaires, de protéger les secrets et de limiter l'accès aux données personnelles.

### Lancer l'API et vérifier son fonctionnement

Depuis la racine du projet, après avoir configuré l'environnement et la connexion à la base de données, lancer l'API avec :

```powershell
python -m uvicorn src.main:app --reload
```

La documentation interactive de l'API est disponible à l'adresse suivante :

`http://127.0.0.1:8000/docs`

Pour exécuter les tests automatisés, ouvrir un second terminal à la racine du projet et lancer :

```powershell
python -m pytest -v
```

Les tests permettent de vérifier le comportement de l'application et de ses principaux composants.