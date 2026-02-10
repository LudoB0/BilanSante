# Interface d'implementation - interview-capture

## 1. Reference contractuelle
- PRP de reference : /docs/prp/PRP_CaptureConsentStatus.md
- Version du PRP : V1

## 2. Responsabilite du module
Tracer le consentement a lenregistrement audio.

## 3. Entrees attendues
- Champ: Consentement audio (oui/non)
  - Type logique: booleen (oui/non)
  - Obligatoire: Oui
  - Format/description: Consentement audio (oui/non)
- Champ: Horodatage du consentement
  - Type logique: booleen (oui/non)
  - Obligatoire: Oui
  - Format/description: Horodatage du consentement
- Champ: Identifiant de session
  - Type logique: texte
  - Obligatoire: Oui
  - Format/description: Identifiant de session

## 4. Sorties produites
- Type de sortie :
- Autre (a preciser)
- Structure logique / format attendu :
- Donnees de consentement associees a la session (tracabilite)
- Format exact non specifie dans le PRD.

## 5. Preconditions
- La session n'est pas active.
- Le consentement audio n'est pas renseigne.
- Les entrees principales ne sont pas disponibles.

## 6. Postconditions
- Les donnees produites sont pretes a etre relues, modifiees et validees par le pharmacien.
- Aucune persistance automatique de donnees apres validation finale de la session.

## 7. Erreurs et cas d'echec
- Situation: Consentement absent alors quun enregistrement audio est present.
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