# Architecture de l'application

## 1. Principes directeurs
- Contraintes issues du PRD
- Le parcours est strictement sequentiel en 9 etapes (parametrage, questionnaire, session, entretien, generation, export, purge).
- Le pharmacien est decisionnaire a chaque etape de validation (transcript puis bilan final).
- Le transcript valide est la source de verite pour la generation.
- Le questionnaire est contextuel et non decisionnel.
- Aucune information inventee, aucune action sans justification issue du transcript.
- Aucune interpretation medicale, aucun diagnostic, aucune prescription, aucune decision clinique.
- Stockage local et temporaire des donnees de session.
- Les donnees de parametrage applicatif sont persistantes et independantes des sessions patient.
- La session ne possede pas de duree predefinie et se cloture uniquement apres validation et generation finale des 4 documents attendus.
- Regles structurantes (offline, local, responsabilite du pharmacien, tracabilite)
- Local
- Le PRD impose un fonctionnement local pour les donnees de session et les sorties (`output/`), avec deep-link locale pour le QR code.
- Responsabilite du pharmacien
- Le pharmacien valide le transcript et le bilan final avant export.
- Tracabilite
- Toute action du plan doit comporter justification et preuve de passage transcript.
- Offline
- Le besoin de fonctionnement strictement hors reseau n'est pas explicitement tranche par le PRD (point ouvert).

## 2. Architecture logique
Les responsabilites ci-dessous sont fonctionnelles (sans choix technologique) et derivees du PRD/PRP.

1. Parametrage applicatif
- Gere l'identite pharmacie (y compris informations de contact optionnelles : site web, reseaux sociaux), le fournisseur IA et la cle API obligatoire.
- Donnees persistantes, independantes des sessions.
2. Gestion du referentiel questionnaire
- Gere la creation et l'edition des questionnaires par tranche d'age.
3. Gestion de session et acces tablette
- Ouvre une session unique, produit un QR code signe, autorise l'acces tablette uniquement pour la session cible.
4. Collecte du questionnaire patient
- Capture les reponses structurees et les rattache a la session.
5. Collecte de l'entretien officinal
- Gere consentement audio, enregistrement audio et notes textuelles.
6. Transcription et validation de la source de verite
- Produit le transcript (transcription audio si present, ou conversion des notes textuelles en transcript structure si mode texte seul) et bloque toute generation tant qu'il n'est pas valide.
7. Construction du bilan et du plan d'actions
- Construit les sections du bilan et les actions tracees au transcript.
8. Validation finale et export documentaire
- Applique la validation pharmacien puis genere DOCX/PDF attendus avec nommage contractuel.
9. Cloture et suppression de session
- Supprime toutes les donnees session en fin d'etape 9, uniquement si les 4 sorties attendues sont creees et validees. En cas d'echec d'un document, la session reste active pour permettre une relance.

## 3. Architecture applicative
Les modules ci-dessous couvrent chacun un ensemble de PRP. Chaque PRP est affecte a un seul module.

### Module A - ApplicationContext
- Role
- Parametrage initial de l'application (identite pharmacie, informations de contact optionnelles, fournisseur IA, cle API obligatoire).
- PRP couverts
- `PRP_ConfigureApplicationContext.md`
- Frontieres avec les autres modules
- Fournit les parametres de contexte utilises par les modules de generation documentaire.
- Ne traite aucune donnee patient.
- Donnees persistantes stockees dans `config/` (independantes des sessions).

### Module B - QuestionnaireCatalog
- Role
- Gestion des questionnaires par tranche d'age.
- PRP couverts
- `PRP_CreateQuestionnaireByAgeRange.md`
- Frontieres avec les autres modules
- Fournit le questionnaire de reference au module session/tablette.
- Ne capture pas les reponses patient.

### Module C - SessionAndTabletAccess
- Role
- Initialisation session (affichage contexte pharmacie, selection tranche d'age parmi questionnaires non vides, creation session dans `data/sessions/`), generation QR signe, ouverture questionnaire sur tablette.
- PRP couverts
- `PRP_InitializeInterviewSession.md`
- `PRP_GenerateSessionQRCode.md`
- `PRP_ServeQuestionnaireOnTablet.md`
- Frontieres avec les autres modules
- Lit les donnees de parametrage pharmacie depuis `config/settings.json` et `config/img/logo.png` (lecture seule, ne modifie jamais `config/`).
- Lit la liste des questionnaires non vides depuis `config/questionnaires/` pour filtrer les tranches d'age proposees.
- Stocke les sessions dans `data/sessions/` (donnees temporaires purgees en fin d'etape 9).
- Expose les informations de session aux modules de collecte.
- N'assemble pas le bilan.

### Module D - QuestionnaireCapture
- Role
- Capture et rattachement des reponses patient a la session.
- PRP couverts
- `PRP_CaptureQuestionnaireResponses.md`
- Frontieres avec les autres modules
- Recoit session + questionnaire actif.
- Produit uniquement des donnees de questionnaire pour les modules de construction du bilan.

### Module E - InterviewCapture
- Role
- Capture consentement, audio et notes textuelles d'entretien.
- PRP couverts
- `PRP_CaptureConsentStatus.md`
- `PRP_RecordInterviewAudio.md`
- `PRP_CaptureInterviewTextNotes.md`
- Frontieres avec les autres modules
- Depend de la session active.
- Alimente le module transcription/validation.
- N'effectue aucune generation IA.

### Module F - TranscriptValidation
- Role
- Transcription audio, conversion des notes textuelles en transcript structure (mode texte seul), et validation pharmacien du transcript source de verite.
- PRP couverts
- `PRP_ConvertNotesToTranscript.md`
- `PRP_TranscribeAudioToTranscript.md`
- `PRP_ValidateTranscript.md`
- Frontieres avec les autres modules
- Consomme audio et/ou notes textuelles.
- En mode audio : transcription automatique puis validation.
- En mode texte seul : conversion des notes en transcript structure puis validation.
- Debloque la construction du bilan uniquement apres validation.

### Module G - BilanAssembly
- Role
- Production des sections de bilan et du plan d'actions trace.
- PRP couverts
- `PRP_BuildInterviewContextSection.md`
- `PRP_BuildQuestionnaireSummarySection.md`
- `PRP_IdentifyVigilancePoints.md`
- `PRP_GeneratePreventionActions.md`
- `PRP_AssembleBilanForValidation.md`
- Frontieres avec les autres modules
- Recoit transcript valide (source principale), questionnaire (contexte), metadonnees session, consentement.
- Produit un objet de bilan pret pour validation finale.

### Module H - FinalValidationAndExport
- Role
- Validation pharmacien du bilan assemble puis generation des sorties DOCX/PDF.
- PRP couverts
- `PRP_ValidateFinalBilan.md`
- `PRP_GenerateDOCXDocument.md`
- `PRP_GeneratePDFDocument.md`
- Frontieres avec les autres modules
- Recoit l'objet de bilan assemble.
- Ecrit dans `output/` avec nommage contractuel:
- `BDS_<numero_session>.docx`
- `PAC_<numero_session>.docx`
- `BDS_<numero_session>.pdf`
- `PAC_<numero_session>.pdf`
- Signale "non cree" en cas d'echec d'un document attendu.
- En cas d'echec, la session reste active pour permettre une relance de generation.

### Module I - SessionPurge
- Role
- Purge globale des donnees de session en fin d'etape 9.
- PRP couverts
- `PRP_PurgeSessionDataAfterExport.md`
- Frontieres avec les autres modules
- Depend de l'etat de validation finale et de generation documentaire.
- La purge n'intervient que lorsque les 4 documents attendus sont crees avec succes.
- En cas d'echec d'un document, pas de purge : la session reste active pour relance.
- Supprime questionnaire, transcript, metadonnees et audio.

## 4. Organisation du code (arborescence)
Arborescence textuelle proposee, alignee sur la structure du depot et les PRP.

```text
.
|-- apps/
|   |-- desktop/
|   |   |-- application-context/             # UI/flux de parametrage (Module A)
|   |   |-- questionnaire-catalog/           # UI/flux de gestion questionnaires (Module B)
|   |   |-- session-and-tablet-access/       # UI session + QR + ouverture tablette (Module C)
|   |   |-- questionnaire-capture/           # UI collecte questionnaire (Module D)
|   |   |-- interview-capture/               # UI consentement/audio/notes (Module E)
|   |   |-- transcript-validation/           # UI transcription + validation transcript (Module F)
|   |   |-- bilan-assembly/                  # UI relecture bilan assemble (Module G)
|   |   |-- final-validation-and-export/     # UI validation finale + export (Module H)
|   |   `-- session-purge/                   # UI etat cloture/purge (Module I)
|   `-- api/
|       `-- modules/
|           |-- application-context/         # Logique metier Module A
|           |-- questionnaire-catalog/       # Logique metier Module B
|           |-- session-and-tablet-access/   # Logique metier Module C
|           |-- questionnaire-capture/       # Logique metier Module D
|           |-- interview-capture/           # Logique metier Module E
|           |-- transcript-validation/       # Logique metier Module F
|           |-- bilan-assembly/              # Logique metier Module G
|           |-- final-validation-and-export/ # Logique metier Module H
|           `-- session-purge/               # Logique metier Module I
|-- config/                                  # Donnees de parametrage persistantes (identite pharmacie, fournisseur IA, cle API)
|-- packages/
|   |-- core/                                # Modeles metier et contrats transverses derives PRD/PRP
|   |-- schemas/                             # Schemas de donnees contractuels (ex: bilan output)
|   `-- prompts/                             # Prompts contractuels deja derives du PRD
|-- data/                                    # Donnees locales temporaires de session (purgees en fin d'etape 9)
|-- output/                                  # Documents finaux generes (BDS_*/PAC_*.docx|pdf)
`-- docs/                                    # Contrats (PRD, skills, PRP, architecture)
```

Pour chaque dossier:
- `apps/desktop`
- Parcours operateur (pharmacien) et parcours tablette patient.
- `apps/api/modules`
- Services metier alignes module par module sur les PRP.
- `config`
- Donnees de parametrage applicatif persistantes (identite pharmacie, fournisseur IA, cle API). Non purgees avec les sessions.
- `packages/core`
- Definitions metier partagees et contraintes de validation.
- `packages/schemas`
- Schemas contractuels des objets (dont bilan final).
- `packages/prompts`
- Artefacts prompts contractuels existants.
- `data`
- Stockage local temporaire de session avant cloture. Purge en fin d'etape 9.
- `output`
- Sorties DOCX/PDF finales.
- `docs`
- Source de verite documentaire et contrats de conception.

## 5. Organisation des donnees
Types de donnees manipulees (PRD section 4 + sorties section 5):
1. Donnees de parametrage applicatif
- Identite pharmacie (logo, coordonnees, en-tete/pied de page), informations de contact optionnelles (site web, reseaux sociaux), fournisseur IA, cle API.
- Persistance: permanente, dans `config/`. Non liee aux sessions.
2. Donnees session
- ID session, date/heure creation, date validation entretien, duree approximative, mode recueil.
3. Donnees questionnaire
- Tranche d'age, reponses structurees (question id, type, valeur, horodatage).
4. Donnees entretien
- Consentement audio (oui/non + horodatage), enregistrement audio (si consentement), notes textuelles.
5. Donnees transcript
- Transcript textuel (eventuellement segmente), issu de la transcription audio ou de la conversion des notes textuelles, puis transcript valide (source de verite).
6. Donnees de bilan assemble
- Sections bilan (contexte, synthese des reponses, points de vigilance), plan d'actions justifie et trace.
7. Donnees de sortie
- `output/BDS_<numero_session>.docx`
- `output/PAC_<numero_session>.docx`
- `output/BDS_<numero_session>.pdf`
- `output/PAC_<numero_session>.pdf`
- Statut "non cree" pour tout document attendu en echec de generation.

Cycle de vie:
1. Creation session (etape 3), rattachement des donnees questionnaire et entretien.
2. Validation transcript (etape 7), puis generation bilan/plan (etape 8).
3. Validation finale + generation DOCX/PDF (etape 9).
4. Cloture session et purge globale des donnees de session (questionnaire, transcript, metadonnees, audio) en fin d'etape 9, uniquement si les 4 documents attendus sont crees. En cas d'echec d'un document, la session reste active pour relance.

Regles de persistance et de suppression:
- Donnees de parametrage: persistance permanente dans `config/`, non liee aux sessions.
- Donnees de session (types 2 a 6): persistance locale et temporaire uniquement, dans `data/`.
- Aucune duree de retention par defaut.
- Suppression conditionnee a la fin de l'etape 9 (validation + generation des 4 documents attendus).
- Si un document attendu n'est pas cree, ce document est marque "non cree" et la session reste active pour relance. Pas de purge tant que les 4 documents ne sont pas generes.

Liens avec les PRP:
- La correspondance contractuelle PRP -> module est definie en section 3.
- Les modules C, D, E couvrent la capture et le stockage temporaire de session.
- Le module F couvre la source de verite (transcription audio, conversion notes en transcript, validation transcript).
- Le module G couvre la construction du bilan et du plan d'actions.
- Les modules H et I couvrent export documentaire puis purge finale.

## 6. Flux principaux
1. Flux session, QR code et questionnaire
- Parametrage applique.
- Selection tranche d'age.
- Creation session.
- Generation QR signe.
- Ouverture tablette sur la session.
- Saisie des reponses patient.

2. Flux entretien officinal
- Capture consentement audio.
- Enregistrement audio si consentement oui.
- Saisie notes textuelles (optionnelle ou complementaire).
- Association metadonnees entretien a la session.

3. Flux transcription et validation
- Si audio present: transcription automatique de l'audio.
- Si mode texte seul (pas d'audio): conversion des notes textuelles en transcript structure.
- Relecture et correction par pharmacien.
- Validation explicite du transcript (source unique).

4. Flux generation bilan et plan d'actions
- Construction des sections de bilan.
- Generation des actions avec justification et preuve transcript.
- Assemblage de l'objet final pour validation.

5. Flux validation finale, export et cloture
- Validation explicite du bilan par pharmacien.
- Generation des 4 documents attendus dans `output/`.
- Marquage "non cree" pour chaque document en echec.
- Si les 4 documents sont generes: purge globale de session.
- Si un document est en echec: session active, relance possible par le pharmacien.

## 7. Choix d'infrastructure
Lister uniquement les decisions deduites du PRD.

1. Execution et stockage locaux pour les donnees de session
- Justification
- PRD: stockage local et temporaire, pas d'historique externe.
- Consequences connues
- Les donnees session sont gerables sans dependance a un stockage externe impose.

2. Separation parametrage / donnees session
- Justification
- PRD: le parametrage est persistant et independant des sessions. Les donnees session sont temporaires et purgees.
- Consequences connues
- Deux espaces de stockage distincts: `config/` (persistant) et `data/` (temporaire, purge).

3. QR payload signe pour acces tablette
- Justification
- PRD: format `bsp://session?v=1&sid=<session_id>&t=<token>&sig=<signature>` avec signature/HMAC anti-falsification.
- Consequences connues
- Validation obligatoire de `v`, `sid`, `t`, `sig` avant acces questionnaire.

4. Generation documentaire locale en sortie
- Justification
- PRD: sortie DOCX/PDF attendue dans `output/` avec nommage contractuel.
- Consequences connues
- Le statut "non cree" doit etre trace pour tout document attendu en echec.

5. Cle API obligatoire pour fournisseur IA
- Justification
- PRD etape 1: integration d'une cle API obligatoire.
- Consequences connues
- Le parametrage est incomplet tant que la cle API n'est pas fournie ou valide.

6. Purge globale en fin d'etape 9
- Justification
- PRD: suppression des donnees session (questionnaire, transcript, metadonnees, audio) apres generation et validation finale des 4 documents.
- Consequences connues
- Pas de retention par defaut.
- La purge ne peut pas etre declenchee au stade validation transcript (etape 7).
- En cas d'echec d'un document, la session reste active pour permettre une relance. La purge n'intervient que lorsque les 4 documents sont generes.

## 8. Points ouverts
1. Mode exact de persistance locale
- Le PRD impose "local et temporaire" mais ne specifie pas le support (fichiers, base embarquee, autre).

2. Gestion de cle/signature pour `sig` (QR)
- Le PRD impose signature/HMAC mais ne specifie pas le cycle de vie de la cle de signature.

3. Niveau de detail du statut d'echec export
- Le PRD impose l'etat "non cree" mais ne specifie pas le format de restitution (journal, champ de session, autre).

4. Exigence reseau operationnelle
- Le PRD impose un deep-link local et une cle API fournisseur IA, sans preciser si un mode strictement offline doit etre garanti pour toutes les etapes.
