# Protocole de maintenance

## 1. Vérifications avant démarrage

- Vérifier que PostgreSQL est disponible.
- Vérifier la variable `DATABASE_URL`.
- Vérifier la présence des fichiers `output/models/lr_optimise.joblib` et `output/models/preprocessor.joblib`.
- Vérifier la présence de `data/processed/df_central.csv` si une importation est nécessaire.
- Vérifier que les versions des dépendances sont compatibles avec les artefacts du modèle.

## 2. Initialisation de la base

Créer les tables déclarées dans les modèles :

```bash
python -m src.create_tables
```

Importer les employés si la table `employees` est vide :

```bash
python -m src.import_employees
```

Le script d'importation vérifie la compatibilité des colonnes, les identifiants en double et les valeurs manquantes. Il annule l'importation si la table contient déjà des enregistrements. Ne pas vider la table pour relancer l'importation sans procédure de sauvegarde et de validation.

## 3. Tests automatisés

Exécuter les tests :

```bash
python -m pytest -v
```

Pour consulter la couverture, si `pytest-cov` est installé :

```bash
python -m pytest --cov=src --cov-report=term-missing
```

Les tests du projet couvrent notamment l'API, la création des tables, la configuration de la base, l'importation des employés, les artefacts du modèle et la structure du projet.

## 4. Contrôle fonctionnel

- Vérifier `GET /`.
- Vérifier `GET /health`.
- Envoyer une requête valide à `POST /predict` via `/docs`.
- Vérifier que la réponse contient `prediction_id`, `prediction`, `probability` et `message`.
- Vérifier que l'entrée et le résultat ont été enregistrés dans PostgreSQL et sont liés par leurs identifiants.

## 5. Suivi du modèle

Lors d'une nouvelle évaluation, comparer les métriques avec les résultats de référence du projet P4. Examiner en particulier la précision, le recall et le F1-score de la classe `Oui`, ainsi que le ROC-AUC.

Toute mise à jour du modèle ou du préprocesseur doit être évaluée et testée avant remplacement des artefacts utilisés par l'API.

## 6. Sécurité et limites opérationnelles

- Ne jamais versionner les secrets ou les mots de passe.
- Restreindre l'accès à la base et aux données personnelles.
- Prévoir des sauvegardes et une politique de conservation des données.
- Ne pas utiliser les prédictions comme seul fondement de décisions concernant les employés.
- Mettre en place une surveillance adaptée avant tout déploiement en production.

Les contrôles de dérive des données, les alertes opérationnelles et le réentraînement automatique ne sont pas implémentés par les fichiers examinés ; ils nécessiteraient des développements complémentaires.
