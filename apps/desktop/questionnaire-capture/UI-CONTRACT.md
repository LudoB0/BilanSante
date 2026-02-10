# UI Contract - questionnaire-capture

## 1. Responsabilite de l'interface
Permettre la saisie des reponses du questionnaire par le patient et leur rattachement a la session active.

## 2. Utilisateur concerne
Patient, en etape 5 du parcours, sur tablette dediee; assistance possible du pharmacien si necessaire (PRD section 3, Etape 5).

## 3. Actions utilisateur autorisees
- Consulter les questions du questionnaire associe a la session (PRD section 3, Etapes 4 et 5).
- Saisir des reponses structurees: booleen, choix unique, choix multiple, texte court (PRD section 4.2).
- Valider l'enregistrement des reponses dans la session (PRP_CaptureQuestionnaireResponses.md).

## 4. Donnees affichees
- Questions du questionnaire associe a la tranche d'age (PRD section 3, Etapes 2, 4, 5).
- Type de chaque question (booleen, choix unique, choix multiple, texte court) (PRD section 4.2).
- Etat de completion du questionnaire (deduit du cas limite "questionnaire incomplet", PRP_CaptureQuestionnaireResponses.md).

## 5. Donnees saisies ou modifiees
- Valeur de reponse par question (PRD section 4.2).
- Reponses rattachees a l'identifiant de session (PRD section 3, Etape 5; PRD section 4.4).
- Horodatage de saisie (PRD section 4.2; PRP_CaptureQuestionnaireResponses.md).

## 6. Regles de validation UI
- Chaque reponse doit respecter le type de question defini (PRD section 4.2).
- Les reponses doivent etre rattachees a une session active (PRD section 3, Etape 5; PRP_CaptureQuestionnaireResponses.md).
- Le questionnaire incomplet doit etre signale (PRP_CaptureQuestionnaireResponses.md).
- Le caractere obligatoire de chaque question est non specifie dans PRD/PRP.

## 7. Etats de l'interface
- Etat initial (questionnaire charge).
- Etat saisie en cours.
- Etat incomplet.
- Etat enregistre.
- Etat erreur (session invalide ou interruption).

## 8. Erreurs et messages
- Questionnaire incomplet ou interrompu: signalement explicite (PRP_CaptureQuestionnaireResponses.md).
- Donnee obligatoire absente: blocage (PRP_CaptureQuestionnaireResponses.md).
- Texte exact des messages non specifie dans PRD/PRP.

## 9. Hors perimetre
- Interpretation automatique des reponses (PRD section 3, Etapes 2 et 5).
- Production du transcript, du bilan ou des actions (PRD section 3, Etapes 7, 8, 9).