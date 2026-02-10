# UI Contract - questionnaire-catalog

## 1. Responsabilite de l'interface
Permettre la creation et l'edition de questionnaires de prevention associes a des tranches d'age.

## 2. Utilisateur concerne
Pharmacien d'officine, en etape 2 du parcours (PRD section 3, Etape 2).

## 3. Actions utilisateur autorisees
- Creer un questionnaire associe a une tranche d'age (PRD section 3, Etape 2; PRP_CreateQuestionnaireByAgeRange.md).
- Editer un questionnaire existant associe a une tranche d'age (PRD section 3, Etape 2; PRP_CreateQuestionnaireByAgeRange.md).
- Ajouter ou modifier des questions structurees de type choix simple, choix multiple, texte court (PRD section 3, Etape 2).

## 4. Donnees affichees
- Liste des tranches d'age disponibles (PRD section 4.1).
- Definition des questionnaires par tranche d'age (PRD section 3, Etape 2).
- Types de questions autorises (PRD section 3, Etape 2).

## 5. Donnees saisies ou modifiees
- Tranche d'age cible du questionnaire (PRD section 4.1).
- Libelles et structure des questions du questionnaire (PRD section 3, Etape 2).

## 6. Regles de validation UI
- Un questionnaire doit etre rattache a une tranche d'age (PRP_CreateQuestionnaireByAgeRange.md).
- Un questionnaire incomplet ne peut pas etre considere valide (PRP_CreateQuestionnaireByAgeRange.md).
- Aucune interpretation automatique des reponses n'est autorisee dans ce module (PRD section 3, Etape 2).
- Les contraintes de cardinalite (nombre minimal/maximal de questions) sont non specifiees dans PRD/PRP.

## 7. Etats de l'interface
- Etat initial (aucun questionnaire selectionne).
- Etat creation.
- Etat edition.
- Etat valide (questionnaire enregistre).
- Etat erreur (questionnaire incomplet ou tranche d'age non associee).

## 8. Erreurs et messages
- Questionnaire incomplet: signalement explicite (PRP_CreateQuestionnaireByAgeRange.md).
- Questionnaire non associe a une tranche d'age: signalement explicite (PRP_CreateQuestionnaireByAgeRange.md).
- Texte exact des messages non specifie dans PRD/PRP.

## 9. Hors perimetre
- Saisie des reponses patient (PRD section 3, Etape 5).
- Toute interpretation medicale des reponses (PRD section 7; PRD section 3, Etape 2).
