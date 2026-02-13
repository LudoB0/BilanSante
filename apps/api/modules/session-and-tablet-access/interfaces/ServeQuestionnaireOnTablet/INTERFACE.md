# Interface d'implementation - session-and-tablet-access

## 1. Reference contractuelle
- PRP de reference : /docs/prp/PRP_ServeQuestionnaireOnTablet.md
- Version du PRP : V5

## 2. Responsabilite du module
Valider l'URL signee issue du QR code, puis charger la page web du questionnaire correspondant a la session active via un mini serveur web local du PC officine.

## 3. Entrees attendues
- Champ: URL questionnaire signee
  - Type logique: texte
  - Obligatoire: Oui
  - Format/description: `<questionnaire_base_url>?v=1&sid=<session_id>&t=<token>&sig=<signature>`
- Champ: Identifiant de session (`sid`)
  - Type logique: texte
  - Obligatoire: Oui
  - Format/description: Identifiant de session cible present dans l'URL signee
- Champ: Questionnaire associe a la tranche d'age
  - Type logique: donnees structurees
  - Obligatoire: Oui
  - Format/description: Questionnaire determine a partir de la session et du referentiel
- Champ: Payload QRCode (`v`, `sid`, `t`, `sig`)
  - Type logique: texte structure
  - Obligatoire: Oui
  - Format/description: Parametres de securite a valider avant chargement.

## 4. Sorties produites
- Type de sortie :
- Autre (a preciser) : page web questionnaire chargee
- Structure logique / format attendu :
- Questionnaire charge pour la session cible avec contexte de soumission (`sid`).
- Le chargement est autorise uniquement si le payload respecte : `<questionnaire_base_url>?v=1&sid=<session_id>&t=<token>&sig=<signature>`.
- Etat questionnaire UI : `En Cours` (orange, 20pt, a droite du QR code) des que la page questionnaire est chargee sur tablette.

## 4.1 Contrats d'appel (logiques)
- Appel web d'acces questionnaire
  - Methode: `GET`
  - Entree: `<questionnaire_base_url>?v=1&sid=<session_id>&t=<token>&sig=<signature>`
  - Sortie attendue: page web questionnaire de la session cible
- Erreur d'acces (payload invalide ou session invalide)
  - Methode: `GET`
  - Sortie attendue: refus explicite (acces non autorise)

## 5. Preconditions
- Le clic "Demarrer l'entretien" a cree une session active.
- Le questionnaire correspondant est disponible.
- Le payload QRCode est valide (version, token et signature).
- Les entrees principales sont disponibles.

## 6. Postconditions
- Le questionnaire est affiche sur la tablette pour la session cible.
- Le contexte `sid` est pret pour la soumission des reponses vers CaptureQuestionnaireResponses.
- Le statut questionnaire sur le PC est `En Cours` (orange, 20pt, a droite du QR code).

## 7. Erreurs et cas d'echec
- Situation: Acces direct sans parametres de securite
  - Comportement attendu: Blocage
- Situation: Session inconnue ou inactive
  - Comportement attendu: Blocage
- Situation: Questionnaire non disponible pour la tranche d'age.
  - Comportement attendu: Signalement explicite sans extrapolation
- Situation: Signature/HMAC invalide dans le payload
  - Comportement attendu: Blocage
- Situation: Token opaque absent ou invalide
  - Comportement attendu: Blocage
- Situation: Entree obligatoire absente
  - Comportement attendu: Blocage

## 8. Invariants
- Aucune information ne doit etre inventee.
- Validation obligatoire des parametres `v`, `sid`, `t`, `sig`.
- L'acces questionnaire reste isole par session.
- Aucune persistance de reponse dans ce module.

## 9. Hors perimetre
- Capture et persistance des reponses patient (module questionnaire-capture).
