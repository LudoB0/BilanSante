# Skills (PRD V1)

Ce document liste les skills nécessaires, strictement dérivés du PRD. Chaque skill est atomique et couvre le parcours (paramétrage, questionnaire, entretien, génération/validation).

## 1) ConfigureApplicationContext
- **Intention**: Paramétrer l'application pour une pharmacie (identité, habillage, fournisseur IA et clé API obligatoire).
- **Entrées (PRD §3 – Étape 1)**:
  - Identité de la pharmacie (logo, coordonnées, en-tête/pied de page)
  - Informations de contact optionnelles (site web, réseaux sociaux : Instagram, Facebook, X, LinkedIn)
  - Choix du fournisseur IA (`OpenIA`, `Anthropic`, `Mistral`)
  - Clé API obligatoire
- **Sorties (PRD §3 – Étape 1)**:
  - Données de paramétrage applicatif enregistrées (identité pharmacie, fournisseur IA, clé API)
- **Règles/contraintes (PRD §6)**:
  - Aucune donnée patient n'est impliquée.
  - Paramétrage modifiable à tout moment.
  - Les données de paramétrage sont persistantes et indépendantes des sessions patient.
- **Erreurs/edge cases**:
  - Clé API manquante ou invalide.

## 2) CreateQuestionnaireByAgeRange
- **Intention**: Créer/éditer des questionnaires associés à une tranche d’âge.
- **Entrées (PRD §3 – Étape 2 / §4.1-4.2)**:
  - Tranche d’âge (catégorielle)
  - Questions structurées (choix simple, choix multiple, texte court)
- **Sorties (PRD §3 – Étape 2 / §4.2)**:
  - Questionnaire structuré associé à une tranche d'âge, prêt à être utilisé en session
- **Règles/contraintes (PRD §6)**:
  - Aucune interprétation automatique des réponses.
- **Erreurs/edge cases**:
  - Questionnaire incomplet ou non associé à une tranche d'âge.

## 3) InitializeInterviewSession
- **Intention**: Afficher le contexte pharmacie, permettre la sélection d'une tranche d'âge parmi les questionnaires non vides, et créer une session unique stockée dans `data/`.
- **Entrées (PRD §3 – Étape 3 / §4.1)**:
  - Tranche d'âge du patient (sélectionnée parmi les questionnaires non vides)
- **Données lues (contexte, lecture seule)**:
  - Informations pharmacie depuis `config/settings.json` : nom_pharmacie, adresse, code_postal, ville (affichage + copie dans métadonnées session)
  - Logo depuis `config/img/logo.png` (affichage)
  - Liens web depuis `config/settings.json` : site_web, instagram, facebook, x, linkedin (affichage si non vide)
  - Liste des questionnaires depuis `config/questionnaires/*.json` (filtrage des tranches d'âge proposées)
- **Sorties (PRD §4.4 / §5)**:
  - Fichier session `data/sessions/<session_id>.json` contenant : identifiant UUID v4, tranche d'âge, date/heure de création, statut `"active"`, métadonnées pharmacie (coordonnées copiées au moment de la création)
- **Règles/contraintes (PRD §6)**:
  - Aucune donnée nominative requise.
  - Pas de durée de session par défaut : la session reste active jusqu'à validation et génération des documents.
  - Seules les tranches d'âge disposant d'un questionnaire contenant au moins une question sont proposées.
  - Les liens web ne sont affichés que s'ils sont non vides dans `settings.json`.
  - Le paramétrage applicatif doit être complet (précondition).
- **Erreurs/edge cases**:
  - Paramétrage applicatif incomplet (bouton désactivé).
  - Aucun questionnaire disponible (bouton désactivé).
  - Session non créée (ID absent) ou dupliquée.

## 4) GenerateSessionQRCode
- **Intention**: Générer et afficher le QRCode de session dans la même interface, juste après le clic sur `Démarrer l'entretien`, puis afficher le statut `Disponible` (rouge, 20pt) à droite du QR code.
- **Entrées (PRD §3 – Étape 4 / §4.4 / §4.6)**:
  - Identifiant de session active (créée par `InitializeInterviewSession`)
  - URL de base auto-détectée via `get_local_ip()` (adresse IP LAN du poste, pas `localhost`)
  - Version du format (`v=1`)
  - Token opaque généré via `secrets.token_urlsafe(32)`
  - Signature HMAC-SHA256 calculée sur `v=1&sid=<session_id>&t=<token>` avec secret stocké dans `config/qr_secret.key`
- **Sorties (PRD §4.6)**:
  - Payload QRCode signé : `http://<ip_locale>:5000/questionnaire?v=1&sid=<session_id>&t=<token>&sig=<signature>`
  - QRCode affiché dans le même écran `session-and-tablet-access`
  - Serveur Flask démarré en thread daemon sur `0.0.0.0:5000`
  - Statut questionnaire UI : `Disponible` (rouge, 20pt, à droite du QR code)
- **Règles/contraintes (PRD §6)**:
  - Questionnaire isolé par session.
  - Le payload QRCode est signé par HMAC-SHA256 pour éviter la falsification.
  - Le module démarre uniquement après création effective de la session.
  - L'URL utilise l'IP LAN locale (jamais `localhost`) pour être accessible depuis la tablette.
- **Erreurs/edge cases**:
  - Clic `Démarrer l'entretien` non effectué (session absente).
  - QRCode invalide ou session inconnue.
  - Signature HMAC-SHA256 invalide.
  - Détection IP échouée : fallback sur `127.0.0.1`.
  - Serveur déjà démarré : pas de second démarrage (idempotent).

## 5) ServeQuestionnaireOnTablet
- **Intention**: Servir le questionnaire en HTML inline responsive sur la tablette via un serveur Flask (`0.0.0.0:5000`, thread daemon) démarré par `GenerateSessionQRCode`.
- **Entrées (PRD §3 – Étape 4 / §4.1-4.2 / §4.6)**:
  - `GET /questionnaire?v=1&sid=<session_id>&t=<token>&sig=<signature>` (scan QR code)
  - `POST /questionnaire/submit` avec JSON `{sid, submitted_at, responses: [{question_id, type, value}]}`
- **Sorties (PRD §3 – Étape 4)**:
  - `GET` : page HTML inline responsive avec formulaire questionnaire (5 types : boolean, single_choice, multiple_choice, short_text, scale) ou page d'erreur (403/404)
  - `POST` : JSON `{session_id, submitted_at, responses_count, responses}` (200) ou `{error}` (400)
  - Statut questionnaire UI : `En Cours` (orange, 20pt, à droite du QR code) dès chargement du questionnaire tablette
- **Règles/contraintes (PRD §6)**:
  - Accès sans compte ; isolation par session.
  - Validation HMAC-SHA256 de la signature avant tout chargement.
  - La soumission est déléguée à `CaptureQuestionnaireResponses.save_responses()`.
  - Le serveur écoute sur `0.0.0.0` (toutes les interfaces) pour être accessible depuis la tablette.
- **Erreurs/edge cases**:
  - Questionnaire non disponible pour la tranche d'âge (404).
  - Payload invalide : version, token ou signature HMAC-SHA256 (403).
  - Session inconnue ou inactive (403).
  - JSON invalide ou réponses mal structurées (400).

## 6) CaptureQuestionnaireResponses
- **Intention**: Enregistrer les réponses du questionnaire soumises depuis la tablette, mettre le statut à `Terminé` (vert, 20pt), puis déclencher l'affichage questions/réponses opérateur.
- **Entrées (PRD §4.2 / §4.4)**:
  - Identifiant de session (`sid`)
  - Réponses structurées : liste de `{question_id, type, value}`
  - Horodatage de soumission (`submitted_at`, auto-généré si absent)
- **Sorties (PRD §4.2 / §3 – Étape 5)**:
  - Record JSON persisté : `{session_id, submitted_at, responses_count, responses}`
  - Fichier : `data/sessions/<sid>_responses.json`
  - Lecture via `load_responses(sid)` (retourne `None` si absent ou corrompu)
  - Statut questionnaire UI : `Terminé` (vert, 20pt, à droite du QR code)
  - Déclenchement de `BuildQuestionnaireSummarySection` (vue questions/réponses sur PC)
- **Règles/contraintes (PRD §6)**:
  - Les réponses sont stockées telles quelles, sans interprétation.
  - Validation : chaque réponse doit contenir `question_id` et `value`.
  - La session doit exister et être active.
  - Données stockées localement et temporairement.
- **Erreurs/edge cases**:
  - Session inconnue ou inactive (`ValueError`).
  - Réponses mal structurées (`ValueError`).
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
- **Intention**: Capturer les saisies pharmacien au clic `Demander a l'IA`, régénérer `QuestionnaireComplet_[xxxxxx].md`, puis ouvrir l'écran co-production et déclencher `IdentifyVigilancePoints`.
- **Entrées (PRD §3 – Étape 6 / §4.3)**:
  - Identifiant de session
  - Saisies pharmacien (notes par question, tension optionnelle, rapport)
  - Fournisseur IA configuré (`OpenIA`, `Anthropic`, `Mistral`)
  - Clé API du fournisseur sélectionné
  - Fichier de configuration `config/prompts/promptvigilance.txt`
- **Sorties (PRD §4.3-4.4)**:
  - `data/sessions/QuestionnaireComplet_[xxxxxx].md` mis à jour
  - Remplacement de l'écran courant par la fenêtre co-production
  - Déclenchement du skill `IdentifyVigilancePoints`
- **Règles/contraintes (PRD §6)**:
  - Aucune réécriture automatique des saisies pharmacien.
  - Le déclenchement IA intervient après création du questionnaire complet.
- **Erreurs/edge cases**:
  - Fichier questionnaire complet absent.
  - Configuration IA absente (fournisseur, clé API, prompt).

## 10) ConvertNotesToTranscript
- **Intention**: Convertir les notes textuelles du pharmacien en transcript structuré lorsque l'entretien est en mode texte seul (sans audio).
- **Entrées (PRD §3 – Étape 7 / §4.3)**:
  - Notes textuelles du pharmacien
  - Identifiant de session
- **Sorties (PRD §4.3)**:
  - Transcript textuel structuré prêt pour validation
- **Règles/contraintes (PRD §6)**:
  - Fidélité au contenu des notes, sans reformulation ni ajout.
  - Applicable uniquement en mode texte seul (pas d'enregistrement audio présent).
- **Erreurs/edge cases**:
  - Notes textuelles absentes ou vides.
  - Un enregistrement audio existe déjà pour cette session (utiliser TranscribeAudioToTranscript à la place).

## 11) TranscribeAudioToTranscript
- **Intention**: Transcrire l’audio en transcript textuel fidèle.
- **Entrées (PRD §3 – Étape 7 / §4.3)**:
  - Enregistrement audio
- **Sorties (PRD §4.3)**:
  - Transcript textuel complet
- **Règles/contraintes (PRD §6)**:
  - Fidélité au propos, sans reformulation.
- **Erreurs/edge cases**:
  - Audio inaudible ou incomplet.

## 12) ValidateTranscript
- **Intention**: Faire relire et valider le transcript par le pharmacien.
- **Entrées (PRD §3 – Étape 7 / §4.3)**:
  - Transcript textuel complet
- **Sorties (PRD §4.3-4.4)**:
  - Transcript validé, source de vérité unique
  - Date de validation de l’entretien
- **Règles/contraintes (PRD §6)**:
  - Validation pharmacien obligatoire avant génération IA.
  - Le transcript validé devient la source de vérité unique.
  - L’audio n’est pas supprimé à cette étape ; suppression globale en Étape 9.
- **Erreurs/edge cases**:
  - Transcript non validé.

## 13) BuildInterviewContextSection
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

## 14) BuildQuestionnaireSummarySection
- **Intention**: Afficher systématiquement la liste questions/réponses du questionnaire sur le PC, avec zones de texte markdown pharmacien par question et zone finale `Rapport du pharmacien`.
- **Entrées (PRD §4.2 / §4.8)**:
  - Fichier réponses session : `data/sessions/<sid>_responses.json`
  - Questionnaire source (questions)
- **Sorties (PRD §5.4)**:
  - Fichier markdown `data/session/QuestionnaireComplet_[Num Session].md` (questions + réponses)
  - Vue opérateur questionnaire affichée sur l'écran PC, à la suite du QR code
  - Zone markdown à droite de chaque question
  - Zone markdown finale `Rapport du pharmacien`
  - Bouton `Envoyer à l'IA` pour déclencher la génération du bilan et du plan d'action
- **Règles/contraintes (PRD §6)**:
  - La vue est basée uniquement sur les questions/réponses de session.
  - Aucune information inventée, aucun diagnostic, aucune décision clinique.
  - Le markdown `QuestionnaireComplet_[Num Session].md` est généré avant affichage.
  - Le bouton `Envoyer à l'IA` délègue aux skills `AssembleBilanForValidation` / `GeneratePreventionActions`.
- **Erreurs/edge cases**:
  - Fichier réponses absent.
  - Questionnaire source absent.

## 15) IdentifyVigilancePoints
- **Intention**: Après création de `QuestionnaireComplet_[xxxxxx].md`, appeler le fournisseur IA choisi pour produire une synthèse vigilance concise, l'afficher en co-production, puis la stocker.
- **Entrées (PRD §4.3)**:
  - `data/sessions/QuestionnaireComplet_[xxxxxx].md`
  - Fournisseur IA (`OpenIA`, `Anthropic`, `Mistral`)
  - Clé API du fournisseur sélectionné
  - Fichier de configuration `config/prompts/promptvigilance.txt`
- **Sorties (PRD §5.1)**:
  - Affichage du résultat du prompt dans la fenêtre co-production
  - Fichier `data/sessions/Vigilance_<short_id>.md` (section vigilance + section 3 points pharmacien)
- **Règles/contraintes (PRD §6)**:
  - Envoi du questionnaire complet + prompt de configuration avant la requête.
  - Résultat limité aux points de vigilance, sans diagnostic ni prescription.
- **Erreurs/edge cases**:
  - Fournisseur IA non supporté.
  - Clé API absente/invalide.
  - Fichier `config/prompts/promptvigilance.txt` absent ou vide.

## 16) GeneratePreventionActions
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

## 17) AssembleBilanForValidation
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

## 18) ValidateFinalBilan
- **Intention**: Permettre la validation finale par le pharmacien avant export.
- **Entrées (PRD §5.1-5.2)**:
  - Bilan et plan d’actions assemblés
- **Sorties (PRD §5.3)**:
  - Contenu validé pour génération :
    - `output/BDS_<numero_session>.docx`
    - `output/PAC_<numero_session>.docx`
    - `output/BDS_<numero_session>.pdf`
    - `output/PAC_<numero_session>.pdf`
- **Règles/contraintes (PRD §6)**:
  - Le pharmacien valide systématiquement avant export.
- **Erreurs/edge cases**:
  - Validation non réalisée.
  - En cas d’échec de génération d’un document attendu : document non créé.

## 19) GenerateDOCXDocument
- **Intention**: Générer le DOCX final modifiable.
- **Entrées (PRD §5.1-5.2 / §3 – Étape 1)**:
  - Contenu validé
  - Identité graphique de la pharmacie
- **Sorties (PRD §5.3)**:
  - `output/BDS_<numero_session>.docx` (bilan)
  - `output/PAC_<numero_session>.docx` (plan d’actions)
- **Règles/contraintes (PRD §6)**:
  - Structure conforme au bilan, aucune information inventée.
- **Erreurs/edge cases**:
  - DOCX non généré ou incomplet.
  - Échec de génération : document non créé.

## 20) GeneratePDFDocument
- **Intention**: Générer le PDF final destiné à l’impression/export.
- **Entrées (PRD §5.1-5.2 / §3 – Étape 1)**:
  - Contenu validé
  - Identité graphique de la pharmacie
- **Sorties (PRD §5.3)**:
  - `output/BDS_<numero_session>.pdf` (bilan)
  - `output/PAC_<numero_session>.pdf` (plan d’actions)
- **Règles/contraintes (PRD §6)**:
  - Structure conforme au bilan, aucune information inventée.
- **Erreurs/edge cases**:
  - PDF non généré ou illisible.
  - Échec de génération : document non créé.

## 21) PurgeSessionDataAfterExport
- **Intention**: Supprimer les données de session une fois les documents générés et validés.
- **Entrées (PRD §4.4 / §5.3)**:
  - Identifiant de session
  - État de validation et génération des documents
- **Sorties (PRD §6)**:
  - Conformité de la suppression (données locales et temporaires)
- **Règles/contraintes (PRD §6)**:
  - Suppression automatique dès que les 4 documents attendus sont générés et validés.
  - Aucune durée de conservation par défaut.
  - Suppression globale en fin d'Étape 9 : questionnaire, transcript, métadonnées et audio.
- **Erreurs/edge cases**:
  - Suppression prématurée avant génération des documents.
  - Si un document attendu n'est pas créé : pas de purge, la session reste active pour permettre une relance de la génération.

---

## Skills deprecated (legacy)
Les skills ci-dessous ne sont plus cohérents avec le PRD V1 actuel.

- **DEPRECATED** `ConfigureBilanSections` → la sélection/organisation des rubriques n’est plus décrite dans le PRD.
- **DEPRECATED** `CaptureInterviewTranscript` → remplacé par `RecordInterviewAudio`, `CaptureInterviewTextNotes`, `ConvertNotesToTranscript`, `TranscribeAudioToTranscript`, `ValidateTranscript`.
- **DEPRECATED** `GenerateOfficinalAdvice` → la section « conseils officinaux » n’est plus dans les sorties PRD.
