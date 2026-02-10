# Interface d'implementation - bilan-assembly

## 1. Reference contractuelle
- PRP de reference : /docs/prp/PRP_AssembleBilanForValidation.md
- Version du PRP : V1

## 2. Responsabilite du module
Assembler le bilan structure et le plan dactions avant validation.

## 3. Entrees attendues
- Champ: Transcript valide
  - Type logique: texte
  - Obligatoire: Oui
  - Format/description: Transcript valide
- Champ: Reponses questionnaire
  - Type logique: donnees structurees
  - Obligatoire: Oui
  - Format/description: Reponses questionnaire
- Champ: Metadonnees de session et dentretien (ID, dates, duree, mode de recueil)
  - Type logique: date-heure
  - Obligatoire: Oui
  - Format/description: Metadonnees de session et dentretien (ID, dates, duree, mode de recueil)
- Champ: Consentement audio
  - Type logique: booleen (oui/non)
  - Obligatoire: Oui
  - Format/description: Consentement audio

## 4. Sorties produites
- Type de sortie :
- JSON structure
- Structure logique / format attendu :
- Bilan et plan dactions prets a validation

## 5. Preconditions
- La session n'est pas active.
- Le transcript n'est pas valide.
- Le consentement audio n'est pas renseigne.
- Le questionnaire correspondant n'est pas disponible.
- Les entrees principales ne sont pas disponibles.

## 6. Postconditions
- Les donnees produites sont pretes a etre relues, modifiees et validees par le pharmacien.
- Aucune persistance automatique de donnees apres validation finale de la session.

## 7. Erreurs et cas d'echec
- Situation: Sections incompletes faute dinformations exprimees.
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