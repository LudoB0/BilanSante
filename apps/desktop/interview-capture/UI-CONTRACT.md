# UI Contract - interview-capture

## 1. Responsabilite de l'interface
Permettre la conduite de l'entretien officinal par le pharmacien avec capture du consentement audio, enregistrement audio et/ou notes textuelles.

## 2. Utilisateur concerne
Pharmacien d'officine, en etape 6 du parcours (PRD section 3, Etape 6).

## 3. Actions utilisateur autorisees
- Enregistrer le statut de consentement audio (oui/non) et son horodatage (PRD section 4.5; PRP_CaptureConsentStatus.md).
- Demarrer l'enregistrement audio uniquement si consentement positif (PRD section 3, Etape 6; PRP_RecordInterviewAudio.md).
- Saisir des notes textuelles d'entretien (PRD section 3, Etape 6; PRP_CaptureInterviewTextNotes.md).
- Utiliser un mode audio, texte, ou mixte (PRD section 3, Etape 6).

## 4. Donnees affichees
- Reponses questionnaire en support contextuel d'entretien (PRD section 3, Etape 6).
- Statut de consentement audio et horodatage (PRD section 4.5).
- Etat du mode de recueil (audio, texte, mixte) (PRD section 4.4).

## 5. Donnees saisies ou modifiees
- Consentement audio (oui/non) et horodatage (PRD section 4.5).
- Notes textuelles du pharmacien (PRD section 4.3).
- Commandes de capture audio associees a la session active (PRP_RecordInterviewAudio.md).

## 6. Regles de validation UI
- L'enregistrement audio est interdit sans consentement explicite (PRD section 4.5; PRP_RecordInterviewAudio.md).
- Le consentement est trace uniquement pour l'autorisation d'enregistrement audio (PRD section 4.5).
- Les donnees doivent etre rattachees a une session active (PRD section 3, Etape 6).
- Les regles de qualite de saisie de notes (longueur minimale, syntaxe) sont non specifiees dans PRD/PRP.

## 7. Etats de l'interface
- Etat initial (consentement non renseigne).
- Etat consentement renseigne.
- Etat capture audio en cours.
- Etat saisie texte en cours.
- Etat mode mixte.
- Etat erreur (enregistrement non autorise ou donnees manquantes).

## 8. Erreurs et messages
- Consentement absent alors qu'un enregistrement est present: signalement explicite (PRP_CaptureConsentStatus.md).
- Tentative d'enregistrement sans consentement: blocage (PRP_RecordInterviewAudio.md).
- Notes illisibles ou incompletes: signalement explicite (PRP_CaptureInterviewTextNotes.md).
- Texte exact des messages non specifie dans PRD/PRP.

## 9. Hors perimetre
- Transcription et validation du transcript (PRD section 3, Etape 7).
- Generation du bilan et des actions (PRD section 3, Etape 8).
- Diagnostic, prescription, decision clinique, interpretation medicale avancee (PRD section 7).