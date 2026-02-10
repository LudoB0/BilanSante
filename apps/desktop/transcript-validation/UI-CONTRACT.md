# UI Contract - transcript-validation

## 1. Responsabilite de l'interface
Permettre la transcription de l'audio (si present), la relecture, la correction et la validation du transcript qui devient la source de verite.

## 2. Utilisateur concerne
Pharmacien d'officine, en etape 7 du parcours (PRD section 3, Etape 7).

## 3. Actions utilisateur autorisees
- Lancer la transcription automatique si un enregistrement audio existe (PRD section 3, Etape 7; PRP_TranscribeAudioToTranscript.md).
- Consulter le transcript textuel genere (PRD section 4.3; PRP_TranscribeAudioToTranscript.md).
- Corriger le transcript avant validation (PRD section 3, Etape 7).
- Valider explicitement le transcript (PRD section 3, Etape 7; PRP_ValidateTranscript.md).

## 4. Donnees affichees
- Transcript textuel complet (PRD section 4.3).
- Indication de validation du transcript et date de validation de l'entretien (PRP_ValidateTranscript.md).
- Indication que l'audio n'est pas supprime a cette etape (PRD section 3, Etape 7).

## 5. Donnees saisies ou modifiees
- Corrections textuelles du transcript par le pharmacien (PRD section 3, Etape 7).
- Validation du transcript (PRP_ValidateTranscript.md).

## 6. Regles de validation UI
- Le transcript valide est la source de verite unique pour la generation (PRD section 4.3; PRP_ValidateTranscript.md).
- La validation du transcript est obligatoire avant generation du bilan (PRD section 3, Etapes 7 et 8).
- Toute ambiguite doit etre signalee sans supposition (PRP_ValidateTranscript.md; PRD section 6).
- Le format exact de segmentation du transcript est non specifie dans PRD/PRP.

## 7. Etats de l'interface
- Etat initial (transcript non disponible ou non valide).
- Etat transcription en cours.
- Etat transcript disponible.
- Etat edition/correction.
- Etat transcript valide.
- Etat erreur (audio inexploitable ou transcript invalide).

## 8. Erreurs et messages
- Audio inaudible ou incomplet: signalement explicite (PRP_TranscribeAudioToTranscript.md).
- Transcript non valide: blocage de la suite du parcours (PRP_ValidateTranscript.md).
- Donnee obligatoire absente: blocage (PRP_ValidateTranscript.md).
- Texte exact des messages non specifie dans PRD/PRP.

## 9. Hors perimetre
- Suppression des donnees audio a cette etape (PRD section 3, Etape 7).
- Validation finale et export documentaire (PRD section 3, Etape 9).
- Diagnostic, prescription, decision clinique, interpretation medicale avancee (PRD section 7).