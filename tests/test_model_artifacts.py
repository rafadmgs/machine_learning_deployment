
import pandas as pd
import pytest

from src.main import MODEL_DIR, load_artifacts


def test_real_model_and_preprocessor_produce_valid_prediction():
    # Données représentatives d'un employé
    payload = {
        "age": 35,
        "genre": "M",
        "revenu_mensuel": 5000,
        "statut_marital": "Célibataire",
        "departement": "Consulting",
        "poste": "Consultant",
        "nombre_experiences_precedentes": 2,
        "annee_experience_totale": 10,
        "annees_dans_l_entreprise": 4,
        "satisfaction_employee_environnement": 3,
        "note_evaluation_precedente": 3,
        "niveau_hierarchique_poste": 2,
        "satisfaction_employee_nature_travail": 3,
        "satisfaction_employee_equipe": 3,
        "satisfaction_employee_equilibre_pro_perso": 3,
        "note_evaluation_actuelle": 3,
        "heure_supplementaires": "Non",
        "augementation_salaire_precedente": 15,
        "nombre_participation_pee": 1,
        "nb_formations_suivies": 2,
        "distance_domicile_travail": 10,
        "niveau_education": 3,
        "domaine_etude": "Marketing",
        "frequence_deplacement": "Occasionnel",
        "annees_depuis_la_derniere_promotion": 1,
    }

    # Vérifier la présence des deux artefacts réels
    assert (MODEL_DIR / "lr_optimise.joblib").is_file()
    assert (MODEL_DIR / "preprocessor.joblib").is_file()

    model, preprocessor = load_artifacts()

    # Appliquer le vrai prétraitement
    input_df = pd.DataFrame([payload])
    transformed_data = preprocessor.transform(input_df)

    transformed_df = pd.DataFrame(
        transformed_data,
        columns=preprocessor.get_feature_names_out(),
    )

    # Exécuter le vrai modèle
    prediction = model.predict(transformed_df)
    probabilities = model.predict_proba(transformed_df)

    # Vérifier la cohérence des résultats
    assert len(prediction) == 1
    assert prediction[0] in model.classes_

    assert probabilities.shape == (1, len(model.classes_))
    assert probabilities[0].sum() == pytest.approx(1.0)
    assert all(0.0 <= probability <= 1.0
               for probability in probabilities[0])
