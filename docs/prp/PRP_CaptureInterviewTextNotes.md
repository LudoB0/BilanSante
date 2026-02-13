# PRP - Product / Prompt Requirements Plan

## 0. Metadonnees
- Nom du skill : CaptureInterviewTextNotes
- Reference PRD : PRD V1 PRD 3 Etape 6 / PRD 4.3-4.4 / PRD 6
- Version : V4
- Statut : implemented
- Dependances (autres skills ou donnees) :
  - BuildQuestionnaireSummarySection (zones de saisie pharmacien + bouton `Demander a l'IA`)
  - ConfigureApplicationContext (fournisseur IA selectionne + cle API)
  - IdentifyVigilancePoints (appel IA apres creation du questionnaire complet)

---

## 1. Intention (obligatoire - 1 phrase)
Capturer les saisies texte du pharmacien, regenerer `QuestionnaireComplet_[xxxxxx].md` au clic `Demander a l'IA`, puis ouvrir l'ecran de co-production qui lance `IdentifyVigilancePoints`.

---

## 2. Perimetre fonctionnel

### 2.1 Ce que le skill FAIT
- Utiliser les entrees contractuelles listees en section 3.1.
- Capturer toutes les saisies pharmacien presentes dans l'ecran questionnaire :
  - notes par question,
  - tension du patient (optionnelle),
  - rapport du pharmacien.
- Au clic sur `Demander a l'IA`, ecrire ces donnees dans `data/sessions/QuestionnaireComplet_[xxxxxx].md` (regeneration complete du fichier markdown avec injection des saisies).
- Detruire le `SessionScreen` actuel dans la fenetre racine CTk.
- Creer et afficher un `CoProductionScreen` dans la meme fenetre racine, pour la meme session.
- A la fin de ce skill (apres creation du `QuestionnaireComplet_[xxxxxx].md`), declencher le skill `IdentifyVigilancePoints`.
- Transmettre a `IdentifyVigilancePoints` le contexte necessaire : `session_id`, `md_path`, fournisseur IA configure, cle API, fichier `config/prompts/promptvigilance.txt`.
- Le `CoProductionScreen` affiche :
  - le statut de la requete IA (ex: `Analyse en cours...`),
  - le resultat du prompt des qu'il est disponible.
- Produire les sorties decrites en section 7.
- Appliquer les regles et contraintes du PRD.

### 2.2 Ce que le skill NE FAIT PAS
- Inventer des informations.
- Utiliser des sources externes non prevues par le PRD.
- Produire un diagnostic, une prescription ou une decision clinique.
- Produire lui-meme la synthese de vigilance (delegue a `IdentifyVigilancePoints`).

---

## 3. Entrees autorisees (contractuelles)

### 3.1 Entrees principales
| Champ | Type | Obligatoire | Description |
|------|------|------------|-------------|
| Identifiant de session | texte | Oui | Identifiant de session actif |
| Fichier questionnaire complet | fichier markdown | Oui | `data/sessions/QuestionnaireComplet_[xxxxxx].md` de la session |
| Notes pharmacien par question | texte markdown | Non | Saisies libres associees a chaque question |
| Tension du patient | texte markdown | Non | Saisie libre (ex: `120/80`) |
| Rapport du pharmacien | texte markdown | Non | Saisie libre de synthese |
| Action utilisateur | evenement UI | Oui | Clic bouton `Demander a l'IA` |
| Fournisseur IA configure | enum | Oui | `OpenIA` ou `Anthropic` ou `Mistral` |
| Cle API IA | texte | Oui | Cle API du fournisseur selectionne |
| Prompt vigilance | fichier texte | Oui | Fichier de configuration `config/prompts/promptvigilance.txt` |

### 3.2 Regles de priorite des entrees
- L'identifiant de session et le fichier `QuestionnaireComplet_[xxxxxx].md` sont obligatoires.
- Les donnees ecrites dans le markdown proviennent uniquement des saisies pharmacien effectuees dans l'interface.
- La tension est optionnelle.
- Le declenchement se fait uniquement au clic `Demander a l'IA`.
- Le lancement de `IdentifyVigilancePoints` est conditionne a la creation reussie de `QuestionnaireComplet_[xxxxxx].md`.

Aucune autre source de donnees n'est autorisee.

---

## 4. Pre-conditions d'execution
Le skill ne doit pas s'executer si :
- La session n'est pas active.
- Le fichier `data/sessions/QuestionnaireComplet_[xxxxxx].md` est absent.
- Le fournisseur IA n'est pas configure.
- La cle API IA est absente.
- Le fichier `config/prompts/promptvigilance.txt` est absent ou vide.
- Les entrees principales ne sont pas disponibles.

---

## 5. Regles IA strictes (conformes PRD)

- Aucune reecriture automatique des notes pharmacien.
- Les saisies pharmacien sont enregistrees telles que saisies.
- Aucune interpretation medicale, diagnostic ou prescription.
- La bascule vers l'IA ne modifie pas le contenu saisi par le pharmacien.

Ces regles sont imperatives et prioritaires.

---

## 6. Traitement attendu (logique fonctionnelle)

### 6.1 Implementation : architecture 3 couches

**Service** (`apps/api/modules/bilan-assembly/service.py` - extension du module existant) :
1. `capture_interview_notes(session_id, pharmacist_notes, pharmacist_blood_pressure, pharmacist_report, base)` :
   - Appelle `build_questionnaire_summary()` pour recharger les donnees sources et valider les pre-conditions.
   - Regenere le fichier markdown `QuestionnaireComplet_<short_id>.md` avec les saisies pharmacien injectees via `_generate_markdown()`.
   - Retourne `{session_id, short_id, md_path}`.

**UI Adapter** (`apps/desktop/bilan-assembly/questionnaire_summary_ui.py`) :
- Transitions de capture : `mark_capturing()`, `mark_captured()`, `mark_capture_error()`.
- `get_pharmacist_data(state)` : extrait `{pharmacist_notes, pharmacist_blood_pressure, pharmacist_report}` depuis l'etat.

**Screen** - transition UI dans `session_screen.py` :
- Au clic `Demander a l'IA` :
  1. Collecte des saisies pharmacien depuis les `CTkTextbox`.
  2. Appel `capture_interview_notes()` pour persister dans le markdown.
  3. Destruction du `SessionScreen` (`.destroy()`).
  4. Creation d'un `CoProductionScreen` dans la meme fenetre racine CTk avec le `session_id` et le `md_path`.
  5. Declenchement de `IdentifyVigilancePoints` depuis le `CoProductionScreen`.

### 6.2 Etapes logiques
1. Verifier les pre-conditions (session active, fichier markdown present, configuration IA disponible).
2. Attendre l'action utilisateur `Demander a l'IA`.
3. Collecter toutes les saisies pharmacien de l'interface courante (notes, tension, rapport).
4. Ecrire ces saisies dans `data/sessions/QuestionnaireComplet_[xxxxxx].md` (regeneration complete).
5. Detruire le `SessionScreen` dans la fenetre racine.
6. Creer et afficher le `CoProductionScreen` dans la meme fenetre racine pour la meme session.
7. Declencher `IdentifyVigilancePoints` avec `QuestionnaireComplet_[xxxxxx].md` + `config/prompts/promptvigilance.txt` + fournisseur IA choisi + cle API.
8. Afficher dans le `CoProductionScreen` le statut de la requete puis le resultat du prompt.

---

## 7. Sorties attendues

### 7.1 Type de sortie
- Fichier markdown + remplacement d'ecran

### 7.2 Schema de sortie
- Fichier markdown mis a jour : `data/sessions/QuestionnaireComplet_[xxxxxx].md`
  - Inclut l'ensemble des saisies pharmacien de la session au moment du clic.
- Transition UI :
  - Le `SessionScreen` est detruit.
  - Le `CoProductionScreen` est affiche dans la meme fenetre racine CTk.
  - Le `CoProductionScreen` recoit `session_id` et `md_path` pour poursuivre le flux.
  - Le resultat du prompt de vigilance est affiche dans la fenetre co-production.

---

## 8. Cas limites et comportements attendus

| Situation | Comportement attendu |
|---------|----------------------|
| Fichier `QuestionnaireComplet_[xxxxxx].md` absent | Blocage |
| Entree obligatoire absente | Blocage |
| Aucune saisie pharmacien | Ecriture d'un fichier coherent puis transition vers le `CoProductionScreen` |
| Echec d'ecriture du markdown | Blocage + message d'erreur explicite, le `SessionScreen` reste affiche |
| Echec de creation du `CoProductionScreen` | Signalement explicite |
| Configuration IA absente (`fournisseur`/`cle API`/`config/prompts/promptvigilance.txt`) | Blocage |

---

## 9. Criteres d'acceptation

Le skill est conforme si :
- Le clic `Demander a l'IA` declenche l'enregistrement de toutes les saisies pharmacien dans `QuestionnaireComplet_[xxxxxx].md`.
- Le `SessionScreen` est detruit apres enregistrement reussi.
- Le `CoProductionScreen` est affiche dans la meme fenetre racine pour la meme session.
- `IdentifyVigilancePoints` est lance automatiquement apres creation de `QuestionnaireComplet_[xxxxxx].md`.
- Le `CoProductionScreen` affiche le statut de la requete IA puis le resultat du prompt.
- Aucune donnee saisie par le pharmacien n'est perdue ou modifiee automatiquement.

Un seul critere non respecte rend le skill non conforme.

---

## 10. Post-conditions

Apres execution :
- Le fichier `QuestionnaireComplet_[xxxxxx].md` contient toutes les saisies pharmacien du contexte questionnaire.
- Le `SessionScreen` n'est plus visible.
- Le flux utilisateur est positionne sur le `CoProductionScreen` qui affiche le statut de la requete IA et son resultat.

---

## 11. Hors perimetre
- Production du contenu vigilance sans passer par `IdentifyVigilancePoints`.
- Diagnostic medical.
- Prescription.
- Decision clinique.
- Interpretation medicale avancee.
