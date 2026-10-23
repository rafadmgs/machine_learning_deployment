# Documentation technique — HR Analytics

Bienvenue dans la documentation technique du projet P5 de déploiement d'un modèle de Machine Learning pour la prédiction de l'attrition des employés.

## Objectifs

Le projet transforme un modèle développé et évalué dans le cadre du projet P4 en une solution opérationnelle comprenant :

- une API REST développée avec FastAPI ;
- une base de données PostgreSQL ;
- la validation des données avec Pydantic ;
- la traçabilité des entrées et des prédictions ;
- des tests automatisés avec pytest ;
- une intégration continue avec GitHub Actions.

## Parcours de la documentation

- [Architecture et choix techniques](architecture.md)
- [Traçabilité des prédictions](tracabilite_predictions.md)
- [Documentation technique du modèle](documentation_modele.md)
- [Guide d'utilisation de l'API](guide_api.md)
- [Protocole de maintenance](protocole_maintenance.md)

## Démarrage rapide

1. Installer les dépendances avec `python -m pip install -r requirements.txt`.
2. Configurer `DATABASE_URL` dans un fichier `.env` à la racine.
3. Créer les tables avec `python -m src.create_tables`.
4. Importer les employés avec `python -m src.import_employees`, si la table est vide.
5. Démarrer l'API avec `python -m uvicorn src.main:app --reload`.

Les artefacts du modèle doivent être disponibles dans `output/models/`. Les commandes supposent que PostgreSQL est installé, accessible et que la base de données a été créée.
