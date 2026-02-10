# Interface d'implementation - ConvertNotesToTranscript

## 1. Reference contractuelle
- PRP de reference : /docs/prp/PRP_ConvertNotesToTranscript.md
- Version du PRP : V1

## 2. Responsabilite du module
Convertir les notes textuelles du pharmacien en transcript structure lorsque l'entretien est en mode texte seul (sans audio).

## 3. Entrees attendues
- Champ: Notes textuelles du pharmacien
  - Type logique: texte
  - Obligatoire: Oui
  - Format/description: Notes textuelles saisies lors de l'entretien officinal.
- Champ: Identifiant de session
  - Type logique: texte
  - Obligatoire: Oui
  - Format/description: Identifiant unique de la session active.

## 4. Sorties produites
- Type de sortie :
- Texte structure
- Structure logique / format attendu :
- Transcript textuel structure pret pour validation par le pharmacien.
- Meme format de sortie que TranscribeAudioToTranscript.

## 5. Preconditions
- La session doit etre active.
- Les notes textuelles doivent etre disponibles.
- Aucun enregistrement audio ne doit exister pour cette session.

## 6. Postconditions
- Le transcript textuel structure est disponible pour relecture et validation par le pharmacien.
- Le transcript n'est pas encore la source de verite (validation requise).

## 7. Erreurs et cas d'echec
- Situation: Notes textuelles absentes ou vides.
  - Comportement attendu: Blocage
- Situation: Un enregistrement audio existe pour cette session.
  - Comportement attendu: Blocage (utiliser TranscribeAudioToTranscript)
- Situation: Entree obligatoire absente
  - Comportement attendu: Blocage
- Situation: Notes illisibles ou incompletes
  - Comportement attendu: Signalement explicite sans extrapolation

## 8. Invariants
- Fidelite au contenu des notes, sans reformulation ni ajout.
- Aucune interpretation ou analyse du contenu.
- Le transcript produit n'est pas encore valide.

## 9. Hors perimetre
- Transcription audio (couvert par TranscribeAudioToTranscript).
- Diagnostic medical.
- Prescription.
- Decision clinique.
- Interpretation medicale avancee.
