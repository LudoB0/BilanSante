# Interface d'implementation - session-and-tablet-access

## 1. Reference contractuelle
- PRP de reference : /docs/prp/PRP_GenerateSessionQRCode.md
- Version du PRP : V4

## 2. Responsabilite du module
Generer le QRCode de session a partir d'une session active deja creee, puis l'afficher dans la meme interface juste apres le clic sur "Demarrer l'entretien".

## 3. Entrees attendues
- Champ: Identifiant de session
  - Type logique: texte
  - Obligatoire: Oui
  - Format/description: Identifiant de session active creee par InitializeInterviewSession
- Champ: URL de base questionnaire web
  - Type logique: texte
  - Obligatoire: Oui
  - Format/description: Point d'entree web local du questionnaire sur tablette
- Champ: Version du format (`v`)
  - Type logique: entier
  - Obligatoire: Oui
  - Format/description: Version du payload QRCode (valeur attendue: `1`).
- Champ: Token opaque (`t`)
  - Type logique: texte
  - Obligatoire: Oui
  - Format/description: Token non devinable associe a la session.
- Champ: Signature (`sig`)
  - Type logique: texte
  - Obligatoire: Oui
  - Format/description: Signature/HMAC anti-falsification.

## 4. Sorties produites
- Type de sortie :
- Autre (a preciser) : QRCode de session
- Structure logique / format attendu :
- Payload QRCode (string) : `<questionnaire_base_url>?v=1&sid=<session_id>&t=<token>&sig=<signature>`.
- Champs du payload : `v`, `sid`, `t`, `sig`.
- Etat UI : QRCode affiche dans le meme ecran que l'initialisation de session.
- Etat questionnaire UI : `Disponible` (rouge, 20pt, a droite du QR code).

## 5. Preconditions
- Le clic "Demarrer l'entretien" a cree une session active.
- Les entrees principales sont disponibles.

## 6. Postconditions
- Le QRCode est visible dans l'ecran session-and-tablet-access sans navigation vers un autre ecran.
- Le pharmacien peut scanner le QRCode sur la tablette pour ouvrir la page web questionnaire de la session.
- Le statut questionnaire sur le PC est initialise a `Disponible` (rouge, 20pt, a droite du QR code).

## 7. Erreurs et cas d'echec
- Situation: Clic "Demarrer l'entretien" non effectue (session absente).
  - Comportement attendu: Blocage
- Situation: Session inconnue ou inactive.
  - Comportement attendu: Blocage
- Situation: URL de base questionnaire absente.
  - Comportement attendu: Blocage
- Situation: QRCode invalide.
  - Comportement attendu: Signalement explicite sans extrapolation
- Situation: Signature/HMAC invalide
  - Comportement attendu: Blocage
- Situation: Token opaque absent
  - Comportement attendu: Blocage
- Situation: Entree obligatoire absente
  - Comportement attendu: Blocage

## 8. Invariants
- Aucune information ne doit etre inventee.
- Le payload contient obligatoirement `v`, `sid`, `t`, `sig`.
- Le payload reste signe et verifiable.
- L'acces questionnaire reste isole par session.

## 9. Hors perimetre
- Chargement de la page web questionnaire sur tablette (ServeQuestionnaireOnTablet).
- Capture des reponses du questionnaire (CaptureQuestionnaireResponses).
