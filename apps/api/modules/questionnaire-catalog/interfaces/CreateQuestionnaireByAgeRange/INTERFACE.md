# Interface d'implementation - questionnaire-catalog

## 1. Reference contractuelle
- PRP de reference : /docs/prp/PRP_CreateQuestionnaireByAgeRange.md
- Version du PRP : V1

## 2. Responsabilite du module
Creer/editer des questionnaires associes a une tranche dage.

## 3. Entrees attendues
- Champ: Tranche dage (categorielle)
  - Type logique: valeur categorielle
  - Obligatoire: Oui
  - Format/description: Tranche dage (categorielle)
- Champ: Questions structurees (choix simple, choix multiple, texte court)
  - Type logique: non specifie
  - Obligatoire: Oui
  - Format/description: Questions structurees (choix simple, choix multiple, texte court)

## 4. Sorties produites
- Type de sortie :
- JSON structure
- Structure logique / format attendu :
- Permet la collecte des reponses qui alimentent le bilan et le plan dactions

## 5. Preconditions
- Les entrees principales ne sont pas disponibles.

## 6. Postconditions
- Les donnees produites sont pretes a etre relues, modifiees et validees par le pharmacien.
- Aucune persistance automatique de donnees apres validation finale de la session.

## 7. Erreurs et cas d'echec
- Situation: Questionnaire incomplet ou non associe a une tranche dage.
  - Comportement attendu: Signalement explicite sans extrapolation
- Situation: Entree obligatoire absente
  - Comportement attendu: Blocage
- Situation: Information contradictoire
  - Comportement attendu: Signalement sans arbitrage
- Situation: Transcript vide ou trop court
  - Comportement attendu: Sortie minimale sans extrapolation

## 8. Invariants
- Aucune information ne doit etre inventee.
- Aucune action ne peut etre proposee sans justification explicite issue du transcript.
- Toute information absente ou ambigue doit etre signalee explicitement.
- Aucune interpretation medicale, diagnostic ou prescription.
- Le langage doit etre professionnel, clair pour le patient et adapte au contexte officinal.
- Le pharmacien reste maitre du contenu final.

## 9. Hors perimetre
- Diagnostic medical.
- Prescription.
- Decision clinique.
- Interpretation medicale avancee.