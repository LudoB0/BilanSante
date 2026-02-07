# Skills (PRD V1)

Ce document liste les skills nécessaires, strictement dérivés du PRD. Chaque skill est atomique et couvre le parcours (paramétrage, questionnaire, entretien, génération/validation).

## 1) ConfigureApplicationContext
- **Intention**: Paramétrer l’application pour une pharmacie (identité, habillage, fournisseur IA et clé API obligatoire).
- **Entrées (PRD §3 – Étape 1)**:
  - Identité de la pharmacie (logo, coordonnées, en-tête/pied de page)
  - Choix du fournisseur IA
  - Clé API obligatoire
- **Sorties (PRD §5.3)**:
  - Documents DOCX/PDF générés avec identité graphique de la pharmacie
- **Règles/contraintes (PRD §6)**:
  - Aucune donnée patient n’est impliquée.
  - Paramétrage modifiable à tout moment.
- **Erreurs/edge cases**:
  - Clé API manquante ou invalide.

## 2) CreateQuestionnaireByAgeRange
- **Intention**: Créer/éditer des questionnaires associés à une tranche d’âge.
- **Entrées (PRD §3 – Étape 2 / §4.1-4.2)**:
  - Tranche d’âge (catégorielle)
  - Questions structurées (choix simple, choix multiple, texte court)
- **Sorties (PRD §5.1-5.2)**:
  - Permet la collecte des réponses qui alimentent le bilan et le plan d’actions
- **Règles/contraintes (PRD §6)**:
  - Aucune interprétation automatique des réponses.
- **Erreurs/edge cases**:
  - Questionnaire incomplet ou non associé à une tranche d’âge.

## 3) InitializeInterviewSession
- **Intention**: Créer une session unique liant questionnaire, entretien et génération du bilan.
- **Entrées (PRD §3 – Étape 3 / §4.1)**:
  - Tranche d’âge du patient
- **Sorties (PRD §4.4 / §5)**:
  - Identifiant de session et métadonnées associées (dont date/heure de création)
  - Permet la production du bilan, du plan d’actions et des documents
- **Règles/contraintes (PRD §6)**:
  - Aucune donnée nominative requise.
  - Pas de durée de session par défaut : la session reste active jusqu’à validation et génération des documents.
- **Erreurs/edge cases**:
  - Session non créée (ID absent) ou dupliquée.

## 4) GenerateSessionQRCode
- **Intention**: Générer le QRCode de session pour accéder au questionnaire sur tablette.
- **Entrées (PRD §3 – Étape 4 / §4.4)**:
  - Identifiant de session
- **Sorties (PRD §5.1-5.2)**:
  - Permet la collecte des réponses pour alimenter le bilan et le plan d’actions
- **Règles/contraintes (PRD §6)**:
  - Questionnaire isolé par session.
- **Erreurs/edge cases**:
  - QRCode invalide ou session inconnue.

## 5) ServeQuestionnaireOnTablet
- **Intention**: Charger automatiquement le bon questionnaire sur la tablette via le QRCode.
- **Entrées (PRD §3 – Étape 4 / §4.1-4.2)**:
  - Identifiant de session
  - Questionnaire associé à la tranche d’âge
- **Sorties (PRD §5.1)**:
  - Permet la saisie des réponses patient pour la synthèse du bilan
- **Règles/contraintes (PRD §6)**:
  - Accès sans compte ; isolation par session.
- **Erreurs/edge cases**:
  - Questionnaire non disponible pour la tranche d’âge.

## 6) CaptureQuestionnaireResponses
- **Intention**: Enregistrer les réponses du questionnaire et l’horodatage.
- **Entrées (PRD §4.2 / §4.4)**:
  - Réponses structurées au questionnaire
  - Horodatage
  - Identifiant de session
- **Sorties (PRD §5.1)**:
  - Section « Synthèse des réponses » du bilan
- **Règles/contraintes (PRD §6)**:
  - Les réponses sont un support contextuel sans valeur décisionnelle.
  - Données stockées localement et temporairement.
- **Erreurs/edge cases**:
  - Questionnaire incomplet ou interrompu.

## 7) CaptureConsentStatus
- **Intention**: Tracer le consentement à l’enregistrement audio.
- **Entrées (PRD §4.5)**:
  - Consentement audio (oui/non)
  - Horodatage du consentement
  - Identifiant de session
- **Sorties (PRD §4.5)**:
  - Données de consentement associées à la session (traçabilité)
- **Règles/contraintes (PRD §6)**:
  - Le consentement sert uniquement à autoriser l’enregistrement audio.
- **Erreurs/edge cases**:
  - Consentement absent alors qu’un enregistrement audio est présent.

## 8) RecordInterviewAudio
- **Intention**: Enregistrer l’entretien audio lorsque le consentement est accordé.
- **Entrées (PRD §3 – Étape 6 / §4.5)**:
  - Consentement audio
  - Identifiant de session
- **Sorties (PRD §4.3-4.4)**:
  - Enregistrement audio et métadonnées d’entretien (date, durée, mode de recueil)
- **Règles/contraintes (PRD §6)**:
  - Enregistrement audio uniquement si consentement oui.
- **Erreurs/edge cases**:
  - Tentative d’enregistrement sans consentement.

## 9) CaptureInterviewTextNotes
- **Intention**: Saisir des notes textuelles lors de l’entretien (texte seul ou complément audio).
- **Entrées (PRD §3 – Étape 6 / §4.3)**:
  - Notes textuelles du pharmacien
  - Identifiant de session
- **Sorties (PRD §4.3-4.4)**:
  - Notes textuelles et métadonnées d’entretien (mode de recueil texte ou mixte)
- **Règles/contraintes (PRD §6)**:
  - Aucune réécriture automatique.
- **Erreurs/edge cases**:
  - Notes illisibles ou incomplètes.

## 10) TranscribeAudioToTranscript
- **Intention**: Transcrire l’audio en transcript textuel fidèle.
- **Entrées (PRD §3 – Étape 7 / §4.3)**:
  - Enregistrement audio
- **Sorties (PRD §4.3)**:
  - Transcript textuel complet
- **Règles/contraintes (PRD §6)**:
  - Fidélité au propos, sans reformulation.
- **Erreurs/edge cases**:
  - Audio inaudible ou incomplet.

## 11) ValidateTranscript
- **Intention**: Faire relire et valider le transcript par le pharmacien.
- **Entrées (PRD §3 – Étape 7 / §4.3)**:
  - Transcript textuel complet
- **Sorties (PRD §4.3-4.4)**:
  - Transcript validé, source de vérité unique
  - Date de validation de l’entretien
- **Règles/contraintes (PRD §6)**:
  - Validation pharmacien obligatoire avant génération IA.
  - Le transcript validé devient la source de vérité unique.
- **Erreurs/edge cases**:
  - Transcript non validé.

## 12) BuildInterviewContextSection
- **Intention**: Produire la section « Contexte de l’entretien ».
- **Entrées (PRD §4.3)**:
  - Transcript validé
- **Sorties (PRD §5.1)**:
  - Section « Contexte de l’entretien » du bilan
- **Règles/contraintes (PRD §6)**:
  - Traçabilité explicite au transcript.
  - Signaler les absences sans supposition.
  - Phrases courtes et vocabulaire compréhensible par le patient.
- **Erreurs/edge cases**:
  - Informations contextuelles non exprimées.

## 13) BuildQuestionnaireSummarySection
- **Intention**: Synthétiser les réponses du questionnaire en respectant la hiérarchie des sources.
- **Entrées (PRD §4.2-4.3)**:
  - Réponses structurées au questionnaire
  - Transcript validé
- **Sorties (PRD §5.1)**:
  - Section « Synthèse des réponses » du bilan
- **Règles/contraintes (PRD §6)**:
  - Le questionnaire est un support contextuel, jamais décisionnel.
  - Toute information doit rester compatible avec le transcript.
  - Phrases courtes et vocabulaire compréhensible par le patient.
- **Erreurs/edge cases**:
  - Contradiction questionnaire / transcript.

## 14) IdentifyVigilancePoints
- **Intention**: Identifier les points de vigilance évoqués lors de l’entretien.
- **Entrées (PRD §4.3)**:
  - Transcript validé
- **Sorties (PRD §5.1)**:
  - Section « Points de vigilance identifiés » du bilan
- **Règles/contraintes (PRD §6)**:
  - Aucun point sans trace explicite.
  - Phrases courtes et vocabulaire compréhensible par le patient.
- **Erreurs/edge cases**:
  - Aucun point de vigilance mentionné.

## 15) GeneratePreventionActions
- **Intention**: Générer le plan d’actions avec justification traçable.
- **Entrées (PRD §4.3)**:
  - Transcript validé
- **Sorties (PRD §5.2)**:
  - Plan d’actions avec intitulé, justification, priorité, suivi, traçabilité
- **Règles/contraintes (PRD §6)**:
  - Aucune action sans justification explicite dans le transcript.
  - Pas de diagnostic, prescription ou décision clinique.
- **Erreurs/edge cases**:
  - Action non justifiable par le transcript.

## 16) AssembleBilanForValidation
- **Intention**: Assembler le bilan structuré et le plan d’actions avant validation.
- **Entrées (PRD §4.2-4.5)**:
  - Transcript validé
  - Réponses questionnaire
  - Métadonnées de session et d’entretien (ID, dates, durée, mode de recueil)
  - Consentement audio
- **Sorties (PRD §5.1-5.2)**:
  - Bilan et plan d’actions prêts à validation
- **Règles/contraintes (PRD §6)**:
  - Traçabilité obligatoire.
  - Informations absentes signalées explicitement.
- **Erreurs/edge cases**:
  - Sections incomplètes faute d’informations exprimées.

## 17) ValidateFinalBilan
- **Intention**: Permettre la validation finale par le pharmacien avant export.
- **Entrées (PRD §5.1-5.2)**:
  - Bilan et plan d’actions assemblés
- **Sorties (PRD §5.3)**:
  - Contenu validé pour génération DOCX/PDF
- **Règles/contraintes (PRD §6)**:
  - Le pharmacien valide systématiquement avant export.
- **Erreurs/edge cases**:
  - Validation non réalisée.

## 18) GenerateDOCXDocument
- **Intention**: Générer le DOCX final modifiable.
- **Entrées (PRD §5.1-5.2 / §3 – Étape 1)**:
  - Contenu validé
  - Identité graphique de la pharmacie
- **Sorties (PRD §5.3)**:
  - Document DOCX
- **Règles/contraintes (PRD §6)**:
  - Structure conforme au bilan, aucune information inventée.
- **Erreurs/edge cases**:
  - DOCX non généré ou incomplet.

## 19) GeneratePDFDocument
- **Intention**: Générer le PDF final destiné à l’impression/export.
- **Entrées (PRD §5.1-5.2 / §3 – Étape 1)**:
  - Contenu validé
  - Identité graphique de la pharmacie
- **Sorties (PRD §5.3)**:
  - Document PDF
- **Règles/contraintes (PRD §6)**:
  - Structure conforme au bilan, aucune information inventée.
- **Erreurs/edge cases**:
  - PDF non généré ou illisible.

## 20) PurgeSessionDataAfterExport
- **Intention**: Supprimer les données de session une fois les documents générés et validés.
- **Entrées (PRD §4.4 / §5.3)**:
  - Identifiant de session
  - État de validation et génération des documents
- **Sorties (PRD §6)**:
  - Conformité de la suppression (données locales et temporaires)
- **Règles/contraintes (PRD §6)**:
  - Suppression automatique dès validation et génération des documents.
  - Aucune durée de conservation par défaut.
- **Erreurs/edge cases**:
  - Suppression prématurée avant génération des documents.

---

## Skills deprecated (legacy)
Les skills ci-dessous ne sont plus cohérents avec le PRD V1 actuel.

- **DEPRECATED** `ConfigureBilanSections` → la sélection/organisation des rubriques n’est plus décrite dans le PRD.
- **DEPRECATED** `CaptureInterviewTranscript` → remplacé par `RecordInterviewAudio`, `CaptureInterviewTextNotes`, `TranscribeAudioToTranscript`, `ValidateTranscript`.
- **DEPRECATED** `GenerateOfficinalAdvice` → la section « conseils officinaux » n’est plus dans les sorties PRD.
