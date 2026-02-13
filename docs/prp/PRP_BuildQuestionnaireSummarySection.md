# PRP - Product / Prompt Requirements Plan

## 0. Metadonnees
- Nom du skill : BuildQuestionnaireSummarySection
- Reference PRD : PRD V1 PRD 3 Etape 5-6 / PRD 4.2 / PRD 4.8 / PRD 5.4 / PRD 6
- Version : V7
- Statut : implemented
- Dependances (autres skills ou donnees) :
  - CaptureQuestionnaireResponses (fichier de reponses disponible)
  - CreateQuestionnaireByAgeRange (questionnaire source)
  - CaptureInterviewTextNotes (enregistrement des saisies pharmacien au clic `Demander a l'IA`)

---

## 1. Intention (obligatoire - 1 phrase)
Afficher systematiquement sur le PC la liste des questions et reponses du patient, calculer l'IMC a partir du poids et de la taille lorsqu'ils sont disponibles, et preparer la transition vers la co-production IA au clic `Demander a l'IA`.

---

## 2. Perimetre fonctionnel

### 2.1 Ce que le skill FAIT
- Demarrer automatiquement apres detection du fichier de reponses de session (polling 1s dans `session_screen.py`, declenchement sur statut `Termine`).
- Charger le fichier de session (`data/sessions/<sid>.json`) pour obtenir la tranche d'age.
- Charger le questionnaire source (`config/questionnaires/<age_range>.json`) et les reponses patient (`data/sessions/<sid>_responses.json`).
- Associer chaque question a sa reponse via `question_id`.
- Formater les valeurs de reponse pour affichage lisible : boolean -> `Oui`/`Non`, multiple_choice -> valeurs jointes par `, `, valeur absente -> `non renseigne`.
- Rechercher les valeurs de poids et taille dans les reponses patient pour calculer l'IMC :
  - priorite 1 : `question_id` dedies (`q12` pour le poids en kg, `q13` pour la taille en m),
  - priorite 2 (fallback) : recherche sur les libelles de question contenant `poids` et `taille`.
- Calculer `IMC = poids_kg / (taille_m ^ 2)` lorsque les deux valeurs sont numeriques et valides.
- Construire le fichier markdown `data/sessions/QuestionnaireComplet_<short_id>.md` (8 premiers caracteres du UUID de session) avec questions, reponses, placeholders `_Notes pharmacien:_`, section `## Mesures patient` (poids, taille, IMC, tension), puis section `## Rapport du pharmacien`.
- Afficher sur le PC, a la suite du QR code, une vue structuree questions/reponses dans le `session_screen.py` existant.
- Afficher a droite de chaque question une zone de texte editable (`CTkTextbox`) par le pharmacien (optionnelle).
- Afficher avant le rapport une zone de saisie `Tension du patient (mmHg)` (`CTkTextbox`, optionnelle).
- Afficher en fin de vue une zone de texte `Rapport du pharmacien` (`CTkTextbox`, optionnelle).
- Afficher un bouton `Demander a l'IA` pour deleguer l'enregistrement des saisies pharmacien et la transition d'interface au skill `CaptureInterviewTextNotes`.
- Produire les sorties decrites en section 7.

### 2.2 Ce que le skill NE FAIT PAS
- Inventer des informations.
- Produire un diagnostic, une prescription ou une decision clinique.
- Appeler directement l'API IA depuis cet ecran.

---

## 3. Entrees autorisees (contractuelles)

### 3.1 Entrees principales
| Champ | Type | Obligatoire | Description |
|------|------|------------|-------------|
| Identifiant de session | texte (UUID v4) | Oui | Session cible, transmise depuis `session_screen.py` |
| Fichier reponses session | fichier JSON | Oui | `data/sessions/<sid>_responses.json` (structure `{session_id, submitted_at, responses_count, responses: [{question_id, type, value}]}`) |
| Questionnaire source | fichier JSON | Oui | `config/questionnaires/<age_range>.json` (questions originales pour associer chaque reponse a son libelle) |
| Saisie tension du pharmacien | texte | Non | Valeur libre de tension (ex: `120/80`) renseignee dans la vue PC |
| Action utilisateur `Demander a l'IA` | evenement UI | Oui | Declenchement de la transition vers la co-production IA |

### 3.2 Regles de priorite des entrees
- Le fichier reponses est obligatoire pour lancer la construction de la vue PC.
- Le contenu de `QuestionnaireComplet_<short_id>.md` est derive uniquement du questionnaire source et des reponses session.
- Le calcul d'IMC utilise uniquement les reponses patient `poids` et `taille` (aucune estimation).
- La tension est une saisie pharmacien optionnelle et n'est pas requise pour afficher le rapport.
- Les zones de texte pharmacien sont optionnelles mais toujours presentes dans la vue.
- Le clic `Demander a l'IA` delegue la persistance des saisies et la transition UI a `CaptureInterviewTextNotes`.

Aucune autre source de donnees n'est autorisee.

---

## 4. Pre-conditions d'execution
Le skill ne doit pas s'executer si :
- Le fichier `data/sessions/<sid>_responses.json` n'existe pas.
- Le questionnaire correspondant n'est pas disponible dans `config/questionnaires/<age_range>.json`.
- Le fichier de session `data/sessions/<sid>.json` n'existe pas ou ne contient pas de `age_range`.
- Les entrees principales ne sont pas disponibles.

---

## 5. Regles IA strictes (conformes PRD)

- Aucune information ne doit etre inventee.
- Aucune interpretation medicale, diagnostic ou prescription.
- Aucun appel API IA n'est autorise dans ce skill.
- Les saisies pharmacien doivent accepter du markdown (texte brut markdown).

Ces regles sont imperatives et prioritaires.

---

## 6. Traitement attendu (logique fonctionnelle)

### 6.1 Implementation : architecture 3 couches

**Service** (`apps/api/modules/bilan-assembly/service.py`) :
1. `build_questionnaire_summary(session_id, base)` :
   - Charge `data/sessions/<sid>.json` -> extrait `age_range`.
   - Charge `data/sessions/<sid>_responses.json` -> construit un map `{question_id: response}`.
   - Charge `config/questionnaires/<age_range>.json` -> itere les questions.
   - Pour chaque question, associe la reponse via `question_id` et formate la valeur avec `format_response_value()`.
   - Extrait les valeurs de poids/taille depuis les items du questionnaire (IDs dedies puis fallback libelle).
   - Parse les nombres en acceptant `.` et `,` comme separateur decimal.
   - Calcule l'IMC quand possible, sinon produit `non calculable`.
   - Genere le fichier markdown `data/sessions/QuestionnaireComplet_<short_id>.md` via `_generate_markdown()`.
   - Retourne `{session_id, short_id, age_range, md_path, items: [{question_id, label, type, options, response_value, response_display}], metrics: {poids_kg, taille_m, imc_display}}`.
2. `format_response_value(value, qtype)` : formate pour affichage humain.

**UI Adapter** (`apps/desktop/bilan-assembly/questionnaire_summary_ui.py`) :
- Etat : `{status, session_id, short_id, age_range, items, metrics, pharmacist_notes, pharmacist_blood_pressure, pharmacist_report, md_path, errors}`.
- Fonctions pures : `create_summary_state()`, `mark_loading()`, `load_summary()`, `mark_summary_error()`, `update_pharmacist_note()`, `update_pharmacist_blood_pressure()`, `update_pharmacist_report()`, `get_summary_items()`, `is_ready()`.

**Screen** (integre dans `apps/desktop/session-and-tablet-access/session_screen.py`) :
- Nouveau frame `_summary_frame` dans le scrollable, apres le QR code.
- Declenchement automatique via `_build_questionnaire_summary(sid)` lorsque le polling detecte le statut `Termine`.
- Pour chaque question : colonne gauche (label + reponse), colonne droite (`CTkTextbox` notes pharmacien).
- Bloc `Mesures patient` en dessous des questions avec `Poids`, `Taille`, `IMC`.
- Zone `Tension du patient (mmHg)` (`CTkTextbox`) entre le bloc mesures et le `Rapport du pharmacien`.
- Zone finale `Rapport du pharmacien` (`CTkTextbox`) en bas.
- Bouton `Demander a l'IA` en dessous de la zone rapport.
- Au clic : delegation a `CaptureInterviewTextNotes` pour enregistrer les saisies pharmacien dans `QuestionnaireComplet_<short_id>.md`, puis **remplacement du contenu de la fenetre** : le `SessionScreen` est detruit et remplace par un `CoProductionScreen` dans la meme fenetre racine CTk.

### 6.2 Etapes logiques
1. Le polling dans `_poll_questionnaire_status()` detecte `data/sessions/<sid>_responses.json`.
2. Statut passe a `Termine` (vert).
3. `_build_questionnaire_summary(sid)` est appele.
4. Le service `build_questionnaire_summary()` verifie les pre-conditions, charge les donnees, genere le markdown.
5. Le service extrait poids/taille, calcule l'IMC si possible et expose les mesures.
6. L'UI adapter passe en status `ready`.
7. Le screen affiche le frame `_summary_frame` avec questions/reponses, bloc mesures, zone tension et zone rapport.
8. Au clic `Demander a l'IA`, le flux est transmis a `CaptureInterviewTextNotes` pour persistance des saisies, destruction du `SessionScreen` et remplacement par le `CoProductionScreen` dans la meme fenetre racine.

---

## 7. Sorties attendues

### 7.1 Type de sortie
- Fichier markdown + affichage structure PC + declencheur de transition

### 7.2 Schema de sortie
- Fichier markdown : `data/sessions/QuestionnaireComplet_<short_id>.md` (8 premiers caracteres du UUID).
  - Contenu : titre, identifiant session, tranche d'age, questions numerotees avec reponses, `_Notes pharmacien:_` par question, `## Mesures patient` (Poids, Taille, IMC, Tension), puis `## Rapport du pharmacien`.
- Affichage PC (integre dans `session_screen.py`) :
  - Titre `Questionnaire - Reponses patient`.
  - Liste des questions/reponses patient (colonne gauche).
  - Zone de texte markdown (`CTkTextbox`) a droite de chaque question.
  - Bloc `Mesures patient` avec affichage `Poids (kg)`, `Taille (m)`, `IMC`.
  - Zone de saisie markdown `Tension du patient (mmHg)` (optionnelle) avant le rapport.
  - Zone de texte markdown finale `Rapport du pharmacien`.
  - Bouton `Demander a l'IA`.
- Transition UI :
  - Au clic `Demander a l'IA` : le `SessionScreen` est detruit et remplace par le `CoProductionScreen` (meme fenetre racine CTk).
  - Le `CoProductionScreen` affiche le statut de la requete IA puis la synthese de l'entretien.

---

## 8. Cas limites et comportements attendus

| Situation | Comportement attendu |
|---------|----------------------|
| Fichier reponses absent | `ValueError` - blocage |
| Questionnaire source absent | `ValueError` - blocage |
| Reponse manquante pour une question | Afficher `non renseigne` |
| Questionnaire vide (0 questions) | `ValueError` - blocage |
| Session sans tranche d'age | `ValueError` - blocage |
| Session inconnue | `ValueError` - blocage |
| Reponse boolean `true`/`false` | Affiche `Oui`/`Non` |
| Reponse multiple_choice vide `[]` | Affiche `non renseigne` |
| Reponse short_text vide ou whitespace | Affiche `non renseigne` |
| Poids absent/non numerique | `Poids: non renseigne`, `IMC: non calculable` |
| Taille absente/non numerique | `Taille: non renseigne`, `IMC: non calculable` |
| Taille egale a `0` | `IMC: non calculable` |
| Taille saisie avec virgule (ex: `1,75`) | Conversion en `1.75` pour le calcul |
| Tension non renseignee par le pharmacien | Aucun blocage, valeur vide autorisee |
| Clic bouton sans session valide | Blocage |

---

## 9. Criteres d'acceptation

Le skill est conforme si :
- Le fichier `data/sessions/QuestionnaireComplet_<short_id>.md` est cree.
- La liste questions/reponses est affichee sur le PC a la suite du QR code.
- Chaque question possede une zone de texte markdown a droite.
- Le bloc `Mesures patient` affiche `Poids`, `Taille` et `IMC` avant le rapport.
- L'IMC est calcule avec la formule `poids_kg / (taille_m ^ 2)` quand les donnees sont valides, sinon affiche `non calculable`.
- La zone `Tension du patient (mmHg)` est affichee avant le rapport et editable (optionnelle).
- La zone finale `Rapport du pharmacien` est affichee et editable en markdown.
- Le bouton `Demander a l'IA` declenche le skill `CaptureInterviewTextNotes`.
- Les reponses absentes sont affichees comme `non renseigne`.

Un seul critere non respecte rend le skill non conforme.

---

## 10. Post-conditions

Apres execution :
- `data/sessions/QuestionnaireComplet_<short_id>.md` est disponible.
- Le pharmacien dispose des zones de texte markdown (par question + `Tension du patient` + `Rapport du pharmacien`) pour conduire l'entretien.
- Les mesures patient (poids, taille, IMC) sont visibles avant le rapport pharmacien.
- Le clic `Demander a l'IA` enregistre les saisies, detruit le `SessionScreen` et affiche le `CoProductionScreen` dans la meme fenetre.

---

## 11. Hors perimetre
- Appel direct a l'API IA.
- Diagnostic medical.
- Prescription.
- Decision clinique.
- Interpretation medicale avancee.
- Sauvegarde automatique hors action utilisateur (clic bouton).
