# Interface d'implementation - final-validation-and-export

## 1. Reference contractuelle
- PRP de reference : /docs/prp/PRP_ValidateFinalBilan.md
- Version du PRP : V1

## 2. Responsabilite du module
Permettre la validation finale par le pharmacien avant export.

## 3. Entrees attendues
- Champ: Bilan et plan dactions assembles
  - Type logique: non specifie
  - Obligatoire: Oui
  - Format/description: Bilan et plan dactions assembles

## 4. Sorties produites
- Type de sortie :
- Autre (a preciser) : documents DOCX/PDF
- Structure logique / format attendu :
- Contenu valide pour generation DOCX/PDF
- Documents attendus apres validation :
- `output/BDS_<numero_session>.docx`
- `output/PAC_<numero_session>.docx`
- `output/BDS_<numero_session>.pdf`
- `output/PAC_<numero_session>.pdf`

## 5. Preconditions
- Les entrees principales ne sont pas disponibles.

## 6. Postconditions
- Les donnees produites sont pretes a etre relues, modifiees et validees par le pharmacien.
- Aucune persistance automatique de donnees apres validation finale de la session.

## 7. Erreurs et cas d'echec
- Situation: Validation non realisee.
  - Comportement attendu: Signalement explicite sans extrapolation
- Situation: Echec de generation d'un document attendu
  - Comportement attendu: Document concerne non cree
- Situation: Entree obligatoire absente
  - Comportement attendu: Blocage
- Situation: Information contradictoire
  - Comportement attendu: Signalement sans arbitrage

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