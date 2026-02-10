# UI Contract - bilan-assembly

## 1. Responsabilite de l'interface
Permettre la generation et l'assemblage du brouillon de bilan et du plan d'actions a partir du transcript valide, avec tracabilite explicite.

## 2. Utilisateur concerne
Pharmacien d'officine, en etape 8 du parcours (PRD section 3, Etape 8).

## 3. Actions utilisateur autorisees
- Lancer la generation du brouillon de bilan a partir du transcript valide (obligatoire) et du questionnaire (contexte) (PRD section 3, Etape 8; PRP_AssembleBilanForValidation.md).
- Consulter la section "Contexte de l'entretien" (PRP_BuildInterviewContextSection.md).
- Consulter la section "Synthese des reponses" (PRP_BuildQuestionnaireSummarySection.md).
- Consulter la section "Points de vigilance identifies" (PRP_IdentifyVigilancePoints.md).
- Consulter le plan d'actions avec justification et preuve de tracabilite (PRD section 5.2; PRP_GeneratePreventionActions.md).
- Marquer les informations absentes ou ambigues comme non renseignees/inconnues sans supposition (PRD section 3, Etape 8; PRP_AssembleBilanForValidation.md).

## 4. Donnees affichees
- Transcript valide (source principale) (PRD section 4.3).
- Reponses questionnaire en contexte (PRD section 4.2; PRD section 3, Etape 8).
- Metadonnees de session et d'entretien (PRD section 4.4).
- Consentement audio a titre de tracabilite (PRD section 4.5).
- Sections du bilan et actions justifiees par passage du transcript (PRD section 5.1 et 5.2).

## 5. Donnees saisies ou modifiees
- Aucune saisie de donnees metier nouvelle n'est explicitement definie dans les PRP de ce module.
- Marquage explicite des informations absentes/ambiguues selon les regles PRD (PRD section 3, Etape 8).

## 6. Regles de validation UI
- Le transcript valide est obligatoire pour lancer la generation (PRD section 3, Etape 8; PRP_AssembleBilanForValidation.md).
- Chaque action doit avoir une justification explicite issue du transcript (PRD section 5.2; PRP_GeneratePreventionActions.md).
- Aucune information inventee n'est autorisee (PRD section 6; PRP du module).
- En cas d'absence d'information, la sortie doit l'indiquer explicitement (PRD section 3, Etape 8).
- Le format exact du marquage de donnee manquante est non specifie dans PRD/PRP.

## 7. Etats de l'interface
- Etat initial (preconditions non atteintes).
- Etat generation en cours.
- Etat brouillon genere.
- Etat brouillon incomplet (informations manquantes/ambigues signalees).
- Etat erreur (action non justifiable ou donnees d'entree manquantes).

## 8. Erreurs et messages
- Action non justifiable par le transcript: signalement explicite (PRP_GeneratePreventionActions.md).
- Contradiction questionnaire/transcript: signalement sans arbitrage (PRP_BuildQuestionnaireSummarySection.md).
- Sections incompletes faute d'informations exprimees: signalement explicite (PRP_AssembleBilanForValidation.md).
- Texte exact des messages non specifie dans PRD/PRP.

## 9. Hors perimetre
- Validation finale du document (PRD section 3, Etape 9).
- Generation de documents DOCX/PDF (PRD section 3, Etape 9).
- Diagnostic, prescription, decision clinique, interpretation medicale avancee (PRD section 7).