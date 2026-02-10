# UI Contract - session-and-tablet-access

## 1. Responsabilite de l'interface
Permettre la creation d'une session d'entretien et l'acces tablette via QR code signe pour charger le questionnaire associe.

## 2. Utilisateur concerne
- Pharmacien d'officine pour la creation de session et la generation du QR code (PRD section 3, Etapes 3 et 4).
- Patient pour l'acces au questionnaire via scan du QR code sur tablette (PRD section 3, Etape 4).

## 3. Actions utilisateur autorisees
- Selectionner la tranche d'age du patient avant creation de session (PRD section 3, Etape 3; PRP_InitializeInterviewSession.md).
- Initialiser une session unique et obtenir un identifiant de session (PRD section 3, Etape 3; PRP_InitializeInterviewSession.md).
- Generer un QR code de session (PRD section 3, Etape 4; PRP_GenerateSessionQRCode.md).
- Afficher le payload QR code conforme au format `bsp://session?v=1&sid=<session_id>&t=<token>&sig=<signature>` (PRD section 3, Etape 4; PRD section 4.6).
- Ouvrir le questionnaire sur tablette apres scan du QR code valide (PRD section 3, Etape 4; PRP_ServeQuestionnaireOnTablet.md).

## 4. Donnees affichees
- Tranche d'age selectionnee et questionnaire associe (PRD section 4.1; PRP_ServeQuestionnaireOnTablet.md).
- Identifiant de session (PRD section 4.4; PRP_InitializeInterviewSession.md).
- QR code et payload (`v`, `sid`, `t`, `sig`) (PRD section 4.6; PRP_GenerateSessionQRCode.md).
- Etat d'autorisation ou de blocage d'acces tablette selon validite du payload (PRP_ServeQuestionnaireOnTablet.md).

## 5. Donnees saisies ou modifiees
- Tranche d'age lors de l'initialisation (PRD section 3, Etape 3).
- Donnees de scan/chargement du QR code cote tablette (PRD section 3, Etape 4).

## 6. Regles de validation UI
- La session doit etre active pour autoriser le flux tablette (PRP_InitializeInterviewSession.md; PRP_ServeQuestionnaireOnTablet.md).
- Le payload QR code doit contenir `v`, `sid`, `t`, `sig` conformes (PRD section 4.6; PRP_GenerateSessionQRCode.md; PRP_ServeQuestionnaireOnTablet.md).
- Le questionnaire charge doit correspondre a la tranche d'age de la session (PRD section 3, Etape 4; PRP_ServeQuestionnaireOnTablet.md).
- Le detail du format de validation du token opaque et de la signature est non specifie dans PRD/PRP.

## 7. Etats de l'interface
- Etat initial (session non creee).
- Etat session active.
- Etat QR code genere.
- Etat acces tablette autorise.
- Etat acces tablette bloque.
- Etat erreur (session invalide, payload invalide, questionnaire indisponible).

## 8. Erreurs et messages
- Session non creee, absente ou inconnue: blocage (PRP_InitializeInterviewSession.md; PRP_GenerateSessionQRCode.md).
- QR code invalide: blocage (PRP_GenerateSessionQRCode.md).
- Signature/HMAC invalide: blocage (PRP_GenerateSessionQRCode.md; PRP_ServeQuestionnaireOnTablet.md).
- Token opaque absent ou invalide: blocage (PRP_GenerateSessionQRCode.md; PRP_ServeQuestionnaireOnTablet.md).
- Questionnaire non disponible pour la tranche d'age: signalement explicite (PRP_ServeQuestionnaireOnTablet.md).
- Texte exact des messages non specifie dans PRD/PRP.

## 9. Hors perimetre
- Analyse des reponses questionnaire (PRD section 3, Etape 5).
- Generation du bilan ou du plan d'actions (PRD section 3, Etapes 8 et 9).
- Diagnostic, prescription, decision clinique, interpretation medicale avancee (PRD section 7).