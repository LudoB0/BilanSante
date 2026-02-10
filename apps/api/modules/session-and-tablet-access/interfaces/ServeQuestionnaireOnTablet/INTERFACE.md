# Interface d'implementation - session-and-tablet-access

## 1. Reference contractuelle
- PRP de reference : /docs/prp/PRP_ServeQuestionnaireOnTablet.md
- Version du PRP : V1

## 2. Responsabilite du module
Charger automatiquement le bon questionnaire sur la tablette via le QRCode.

## 3. Entrees attendues
- Champ: Identifiant de session
  - Type logique: texte
  - Obligatoire: Oui
  - Format/description: Identifiant de session
- Champ: Questionnaire associe a la tranche dage
  - Type logique: valeur categorielle
  - Obligatoire: Oui
  - Format/description: Questionnaire associe a la tranche dage
- Champ: Payload QRCode (`v`, `sid`, `t`, `sig`)
  - Type logique: texte structure
  - Obligatoire: Oui
  - Format/description: Payload signe permettant de charger la session cible.

## 4. Sorties produites
- Type de sortie :
- Autre (a preciser) : bilan structure
- Structure logique / format attendu :
- Permet la saisie des reponses patient pour la synthese du bilan
- Le chargement est autorise uniquement si le payload respecte : `bsp://session?v=1&sid=<session_id>&t=<token>&sig=<signature>`.

## 5. Preconditions
- La session n'est pas active.
- Le questionnaire correspondant n'est pas disponible.
- Le payload QRCode est invalide (version, token ou signature).
- Les entrees principales ne sont pas disponibles.

## 6. Postconditions
- Les donnees produites sont pretes a etre relues, modifiees et validees par le pharmacien.
- Aucune persistance automatique de donnees apres validation finale de la session.

## 7. Erreurs et cas d'echec
- Situation: Questionnaire non disponible pour la tranche dage.
  - Comportement attendu: Signalement explicite sans extrapolation
- Situation: Signature/HMAC invalide dans le payload
  - Comportement attendu: Blocage
- Situation: Token opaque absent ou invalide
  - Comportement attendu: Blocage
- Situation: Entree obligatoire absente
  - Comportement attendu: Blocage

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