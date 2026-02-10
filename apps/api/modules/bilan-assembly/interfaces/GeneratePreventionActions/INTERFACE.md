# Interface d'implementation - bilan-assembly

## 1. Reference contractuelle
- PRP de reference : /docs/prp/PRP_GeneratePreventionActions.md
- Version du PRP : V1

## 2. Responsabilite du module
Generer le plan dactions avec justification tracable.

## 3. Entrees attendues
- Champ: Transcript valide
  - Type logique: texte
  - Obligatoire: Oui
  - Format/description: Transcript valide

## 4. Sorties produites
- Type de sortie :
- JSON structure
- Structure logique / format attendu :
- Plan dactions avec intitule, justification, priorite, suivi, tracabilite

## 5. Preconditions
- Le transcript n'est pas valide.
- Les entrees principales ne sont pas disponibles.

## 6. Postconditions
- Les donnees produites sont pretes a etre relues, modifiees et validees par le pharmacien.
- Aucune persistance automatique de donnees apres validation finale de la session.

## 7. Erreurs et cas d'echec
- Situation: Action non justifiable par le transcript.
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