# Interface d'implementation - questionnaire-capture

## 1. Reference contractuelle
- PRP de reference : /docs/prp/PRP_CaptureQuestionnaireResponses.md
- Version du PRP : V4

## 2. Responsabilite du module
Enregistrer les reponses soumises depuis la page web tablette, les rattacher a la session active, et les rendre disponibles dans l'application officine.

## 3. Entrees attendues
- Champ: Identifiant de session (`sid`)
  - Type logique: texte
  - Obligatoire: Oui
  - Format/description: Identifiant de session cible
- Champ: Reponses structurees au questionnaire (`responses`)
  - Type logique: liste de donnees structurees
  - Obligatoire: Oui
  - Format/description: Liste de reponses comportant au minimum `question_id` et `value`
- Champ: Horodatage de soumission (`submitted_at`)
  - Type logique: date-heure
  - Obligatoire: Oui
  - Format/description: Horodatage de la soumission tablette

## 4. Sorties produites
- Type de sortie :
- JSON structure
- Structure logique / format attendu :
- `session_id`: session cible
- `submitted_at`: horodatage de soumission
- `responses_count`: nombre de reponses enregistrees
- `responses`: reponses enregistrees
- Statut questionnaire UI: `Termine` (vert, 20pt, a droite du QR code)
- Declenchement de la vue questions/reponses PC: `questionnaire_view_triggered=true`

## 5. Preconditions
- La session est active.
- Le questionnaire correspondant est disponible pour la session.
- Les entrees principales sont disponibles.

## 6. Postconditions
- Les reponses sont persistees localement et liees a la session.
- Les reponses sont disponibles pour les ecrans/modules de l'application officine.
- Le statut questionnaire sur le PC est `Termine` (vert, 20pt, a droite du QR code).
- L'affichage questions/reponses est declenche apres disponibilite du fichier de reponses.

## 6.1 Contrat d'appel (logique)
- Soumission des reponses questionnaire
  - Methode: `POST`
  - Entree attendue (JSON):
    - `sid`: `<session_id>`
    - `submitted_at`: `<ISO8601>`
    - `responses`: liste de reponses
  - Sortie attendue (JSON):
    - `session_id`
    - `submitted_at`
    - `responses_count`
    - `responses`

## 7. Erreurs et cas d'echec
- Situation: Session inconnue ou inactive
  - Comportement attendu: Blocage
- Situation: Questionnaire incomplet ou interrompu
  - Comportement attendu: Signalement explicite sans extrapolation
- Situation: Entree obligatoire absente
  - Comportement attendu: Blocage
- Situation: Reponse sans `question_id`
  - Comportement attendu: Blocage
- Situation: Information contradictoire
  - Comportement attendu: Signalement sans arbitrage

## 8. Invariants
- Aucune information ne doit etre inventee.
- Les reponses sont enregistrees telles quelles, sans interpretation ni reecriture.
- Le rattachement des reponses au `sid` est obligatoire.
- Le stockage reste local et temporaire.

## 9. Hors perimetre
- Interpretation clinique ou generation du bilan.
