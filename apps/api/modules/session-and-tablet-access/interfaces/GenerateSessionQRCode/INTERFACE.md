# Interface d'implementation - session-and-tablet-access

## 1. Reference contractuelle
- PRP de reference : /docs/prp/PRP_GenerateSessionQRCode.md
- Version du PRP : V1

## 2. Responsabilite du module
Generer le QRCode de session pour acceder au questionnaire sur tablette.

## 3. Entrees attendues
- Champ: Identifiant de session
  - Type logique: texte
  - Obligatoire: Oui
  - Format/description: Identifiant de session
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
- Payload QRCode (string) : `bsp://session?v=1&sid=<session_id>&t=<token>&sig=<signature>`.
- Champs du payload : `v`, `sid`, `t`, `sig`.

## 5. Preconditions
- La session n'est pas active.
- Les entrees principales ne sont pas disponibles.

## 6. Postconditions
- Les donnees produites sont pretes a etre relues, modifiees et validees par le pharmacien.
- Aucune persistance automatique de donnees apres validation finale de la session.

## 7. Erreurs et cas d'echec
- Situation: QRCode invalide ou session inconnue.
  - Comportement attendu: Signalement explicite sans extrapolation
- Situation: Signature/HMAC invalide
  - Comportement attendu: Blocage
- Situation: Token opaque absent
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