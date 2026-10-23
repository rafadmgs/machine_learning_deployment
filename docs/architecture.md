# Architecture et choix techniques

## Vue d'ensemble

La solution s'appuie sur quatre composants principaux :

1. **API FastAPI** : reçoit les requêtes et expose les endpoints.
2. **Validation Pydantic** : vérifie les données fournies au modèle.
3. **Pipeline Machine Learning** : applique le prétraitement et le modèle entraîné.
4. **PostgreSQL** : conserve les données des employés ainsi que l'historique des entrées et des prédictions.

## Technologies

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

## Organisation du code

- `src/main.py` : configuration de l'API et endpoints.
- `src/database.py` : configuration de la connexion PostgreSQL et sessions SQLAlchemy.
- `src/models.py` : modèles ORM des tables.
- `src/schemas.py` : schéma de validation des requêtes.
- `src/create_tables.py` : création des tables déclarées dans les modèles.
- `src/import_employees.py` : validation et importation du fichier des employés.
- `tests/` : tests automatisés.
- `output/models/` : artefacts nécessaires à la prédiction.
- `data/processed/df_central.csv` : fichier attendu par le script d'importation.

## Flux d'une prédiction

1. Le client envoie une requête à `POST /predict`.
2. Pydantic valide les données.
3. L'API charge le modèle et le préprocesseur.
4. Le préprocesseur transforme les données d'entrée.
5. Le modèle calcule la classe prédite et sa probabilité associée.
6. L'entrée est enregistrée dans `prediction_inputs`.
7. Le résultat est enregistré dans `prediction_outputs`.
8. L'API retourne l'identifiant de prédiction, la classe, la probabilité et un message.

## Configuration de la base de données

La variable `DATABASE_URL` est lue depuis l'environnement après chargement du fichier `.env`. Si elle est absente, le module de configuration lève une erreur.

Exemple de format à adapter à l'environnement :

```dotenv
DATABASE_URL=postgresql+psycopg://utilisateur:mot_de_passe@localhost:5432/nom_base
```

Ne pas publier les identifiants de connexion dans le dépôt Git.
