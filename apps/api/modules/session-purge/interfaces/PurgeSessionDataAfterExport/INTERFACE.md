# Interface d'implementation - session-purge

## 1. Reference contractuelle
- PRP de reference : /docs/prp/PRP_PurgeSessionDataAfterExport.md
- Version du PRP : V1

## 2. Responsabilite du module
Supprimer les donnees de session une fois les documents generes et valides.

## 3. Entrees attendues
- Champ: Identifiant de session
  - Type logique: texte
  - Obligatoire: Oui
  - Format/description: Identifiant de session
- Champ: Etat de validation et generation des documents
  - Type logique: texte
  - Obligatoire: Oui
  - Format/description: Etat de validation et generation des documents

## 4. Sorties produites
- Type de sortie :
- Autre (a preciser)
- Structure logique / format attendu :
- Conformite de la suppression (donnees locales et temporaires)
- Suppression globale en fin d'etape 9 : questionnaire, transcript, metadonnees et audio.

## 5. Preconditions
- La session n'est pas active.
- Tous les documents attendus ne sont pas crees (`BDS_*.docx`, `PAC_*.docx`, `BDS_*.pdf`, `PAC_*.pdf`).
- Les entrees principales ne sont pas disponibles.

## 6. Postconditions
- Les donnees produites sont pretes a etre relues, modifiees et validees par le pharmacien.
- Aucune persistance automatique de donnees apres validation finale de la session.

## 7. Erreurs et cas d'echec
- Situation: Suppression prematuree avant generation des documents.
  - Comportement attendu: Signalement explicite sans extrapolation
- Situation: Echec de generation d'un document attendu
  - Comportement attendu: Pas de purge; document concerne non cree
- Situation: Validation finale non realisee
  - Comportement attendu: Pas de purge
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