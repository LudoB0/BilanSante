# PRP - Product / Prompt Requirements Plan

## 0. Metadonnees
- Nom du skill : IdentifyVigilancePoints
- Reference PRD : PRD V1 PRD 4.3 / PRD 5.1 / PRD 6
- Version : V4
- Statut : draft
- Dependances (autres skills ou donnees) :
  - CaptureInterviewTextNotes (declenchement apres creation de `QuestionnaireComplet_[xxxxxx].md`)
  - ConfigureApplicationContext (fournisseur IA selectionne + cle API + modele IA)

---

## 1. Intention (obligatoire - 1 phrase)
Lancer la co-production IA apres creation de `QuestionnaireComplet_[xxxxxx].md`, envoyer ce fichier avec le prompt de configuration `config/prompts/promptvigilance.txt` au fournisseur IA choisi, afficher le resultat dans la fenetre de co-production, puis permettre la saisie des 3 points du plan d'action et la transition vers l'ecran suivant.

---

## 2. Perimetre fonctionnel

### 2.1 Ce que le skill FAIT
- Utiliser les entrees contractuelles listees en section 3.1.
- Se declencher a la fin du flux `CaptureInterviewTextNotes`, apres creation de `data/sessions/QuestionnaireComplet_[xxxxxx].md`.
- Charger `data/sessions/QuestionnaireComplet_[xxxxxx].md` comme source complete de l'entretien.
- Charger la configuration IA depuis `config/settings.json` : `fournisseur_ia`, `cle_api`, `modele_ia`.
- Se connecter au fournisseur IA configure, parmi : `OpenIA`, `Anthropic`, `Mistral`.
- Utiliser la cle API et le modele IA associes au fournisseur IA selectionne.
- Charger le prompt depuis le fichier de configuration `config/prompts/promptvigilance.txt`.
- Construire la requete IA :
  - `promptvigilance.txt` = **system prompt** (instructions pour l'IA),
  - `QuestionnaireComplet_[xxxxxx].md` = **user message** (donnees de l'entretien).
- Executer l'appel IA dans un **thread daemon** pour ne pas bloquer l'interface.
- Recevoir en retour un resultat succinct contenant uniquement les points de vigilance.
- Afficher le resultat du prompt dans la fenetre `co-production avec l'IA`.
- Stocker le resultat dans `data/sessions/Vigilance_<short_id>.md` (ex: `data/sessions/Vigilance_86ab0991.md`).
- Afficher un espace de saisie pharmacien pour definir exactement 3 points a mettre en place dans le plan d'action.
- Persister ces 3 points dans `data/sessions/Vigilance_<short_id>.md`.
- Au clic `Valider`, sauvegarder et transitionner vers l'ecran suivant du flux.
- Produire les sorties decrites en section 7.
- Appliquer les regles et contraintes du PRD.

### 2.2 Ce que le skill NE FAIT PAS
- Inventer des informations.
- Produire un diagnostic, une prescription ou une decision clinique.
- Produire un resume long ou hors perimetre vigilance.
- Appeler l'IA de maniere synchrone (blocage de l'interface interdit).

---

## 3. Entrees autorisees (contractuelles)

### 3.1 Entrees principales
| Champ | Type | Obligatoire | Description |
|------|------|------------|-------------|
| Identifiant de session | texte | Oui | Session cible |
| Questionnaire complet | fichier markdown | Oui | `data/sessions/QuestionnaireComplet_[xxxxxx].md` |
| Fournisseur IA | enum | Oui | `OpenIA` ou `Anthropic` ou `Mistral` (depuis `config/settings.json` champ `fournisseur_ia`) |
| Cle API IA | texte | Oui | Cle API du fournisseur IA selectionne (depuis `config/settings.json` champ `cle_api`) |
| Modele IA | texte | Non | Modele specifique (depuis `config/settings.json` champ `modele_ia`). Defaut par fournisseur si absent. |
| Prompt vigilance | fichier texte | Oui | Fichier de configuration `config/prompts/promptvigilance.txt` |
| 3 points du plan d'action saisis par le pharmacien | liste texte | Oui | Trois points saisis dans l'interface de co-production |
| Fichier vigilance session | fichier markdown | Oui | `data/sessions/Vigilance_<short_id>.md` (`short_id` = 8 premiers caracteres du UUID session) |

### 3.2 Regles de priorite des entrees
- Le fichier `QuestionnaireComplet_[xxxxxx].md` est la source principale transmise a l'IA.
- Le fournisseur IA est obligatoirement l'un des 3 modules autorises (`OpenIA`, `Anthropic`, `Mistral`).
- Le prompt est obligatoirement charge depuis `config/prompts/promptvigilance.txt` et transmis comme **system prompt**.
- Le modele IA est optionnel : si `modele_ia` est absent ou vide dans `config/settings.json`, un modele par defaut est utilise selon le fournisseur.
- Les 3 points du plan d'action sont definis par le pharmacien apres reception des points de vigilance.

Aucune autre source de donnees n'est autorisee.

---

## 4. Pre-conditions d'execution
Le skill ne doit pas s'executer si :
- Le flux `CaptureInterviewTextNotes` n'a pas cree `QuestionnaireComplet_[xxxxxx].md`.
- Le fichier `QuestionnaireComplet_[xxxxxx].md` est absent.
- Le fournisseur IA configure n'est pas dans la liste autorisee.
- La cle API IA n'est pas disponible.
- Le fichier `config/prompts/promptvigilance.txt` est absent ou vide.
- Les entrees principales ne sont pas disponibles.

---

## 5. Regles IA strictes (conformes PRD)

- Aucune information ne doit etre inventee.
- Le resultat IA doit rester succinct et limite aux points de vigilance.
- Aucune interpretation medicale avancee, diagnostic ou prescription.
- Le pharmacien reste maitre du contenu final et du choix des 3 points du plan d'action.
- Toute information absente ou ambigue doit etre signalee explicitement.

Ces regles sont imperatives et prioritaires.

---

## 6. Traitement attendu (logique fonctionnelle)

### 6.1 Implementation : architecture 3 couches

**Service** (`apps/api/modules/bilan-assembly/service.py` - extension du module existant) :

1. `identify_vigilance_points(session_id, base)` :
   - Charge la configuration IA depuis `config/settings.json` (via le service `application-context`) : `fournisseur_ia`, `cle_api`, `modele_ia`.
   - Valide les pre-conditions : fichier `QuestionnaireComplet_<short_id>.md` present, fournisseur autorise, cle API non vide, fichier `config/prompts/promptvigilance.txt` present et non vide.
   - Charge le contenu de `data/sessions/QuestionnaireComplet_<short_id>.md` (user message).
   - Charge le contenu de `config/prompts/promptvigilance.txt` (system prompt).
   - Resout le modele IA : `modele_ia` depuis settings, ou defaut par fournisseur.
   - Appelle `_call_ai_provider(fournisseur, cle_api, modele, system_prompt, user_message)`.
   - Ecrit le resultat dans `data/sessions/Vigilance_<short_id>.md` (section `## Points de vigilance`).
   - Retourne `{session_id, short_id, vigilance_md_path, vigilance_text}`.

2. `_call_ai_provider(fournisseur, cle_api, modele, system_prompt, user_message)` :
   - Dispatche vers le SDK officiel du fournisseur selectionne :
     - `OpenIA` : SDK `openai` (`client.chat.completions.create()`).
     - `Anthropic` : SDK `anthropic` (`client.messages.create()`).
     - `Mistral` : SDK `mistralai` (`client.chat.complete()`).
   - Structure de l'appel : `system_prompt` = prompt systeme, `user_message` = message utilisateur.
   - Retourne le texte de la reponse IA (string).
   - Leve `ValueError` si le fournisseur n'est pas supporte.
   - Leve `RuntimeError` si l'appel IA echoue (timeout, erreur API, reponse vide).

3. `_resolve_ai_model(fournisseur, modele_ia)` :
   - Si `modele_ia` est fourni et non vide, le retourne tel quel.
   - Sinon, retourne le modele par defaut du fournisseur :
     - `OpenIA` : `gpt-4o-mini`
     - `Anthropic` : `claude-sonnet-4-5-20250929`
     - `Mistral` : `mistral-small-latest`

4. `save_action_points(session_id, action_points, base)` :
   - Valide que `action_points` est une liste de exactement 3 chaines non vides.
   - Recharge `data/sessions/Vigilance_<short_id>.md` existant.
   - Ajoute/remplace la section `## Plan d'action - 3 points pharmacien` avec les 3 points numerotes.
   - Retourne `{session_id, short_id, vigilance_md_path}`.

**Fournisseurs IA autorises et defauts** :
| Fournisseur | SDK Python | Modele par defaut |
|------------|-----------|-------------------|
| `OpenIA` | `openai` | `gpt-4o-mini` |
| `Anthropic` | `anthropic` | `claude-sonnet-4-5-20250929` |
| `Mistral` | `mistralai` | `mistral-small-latest` |

Le champ `modele_ia` dans `config/settings.json` est optionnel. S'il est present et non vide, il remplace le modele par defaut du fournisseur selectionne.

**UI Adapter** (`apps/desktop/co-production/co_production_ui.py`) :
- Etat : `{status, session_id, short_id, md_path, vigilance_text, vigilance_md_path, action_points: ["", "", ""], errors}`.
- Statuts : `initial` -> `loading` -> `vigilance_ready` -> `saving` -> `saved` / `erreur`.
- Fonctions pures :
  - `create_co_production_state()` : etat initial.
  - `mark_loading(state)` : status `loading`.
  - `load_vigilance_result(state, result_data)` : status `vigilance_ready`, stocke `vigilance_text`, `vigilance_md_path`, `short_id`.
  - `mark_vigilance_error(state, errors)` : status `erreur`.
  - `update_action_point(state, index, text)` : met a jour le point d'action a l'index 0, 1 ou 2.
  - `mark_saving(state)` : status `saving`.
  - `mark_saved(state)` : status `saved`.
  - `mark_save_error(state, errors)` : status `erreur`.
  - `get_action_points(state)` : retourne une copie de la liste des 3 points.
  - `is_vigilance_ready(state)` : `True` si status == `vigilance_ready`.
  - `can_validate(state)` : `True` si status == `vigilance_ready` et les 3 points sont non vides.

**Screen** (`apps/desktop/co-production/co_production_screen.py`) :
- Recoit `session_id` et `md_path` depuis le `SessionScreen` (via `CaptureInterviewTextNotes`).
- A l'initialisation :
  1. Affiche le statut `Analyse en cours...` (orange).
  2. Lance `identify_vigilance_points()` dans un **thread daemon**.
  3. Utilise `.after()` pour verifier la fin du thread et mettre a jour l'UI.
- A la reception du resultat IA :
  1. Affiche le texte de vigilance dans la zone de reponse (read-only).
  2. Affiche 3 zones de saisie `CTkTextbox` intitulees `Point 1`, `Point 2`, `Point 3`.
  3. Affiche un bouton `Valider` (desactive tant que les 3 points ne sont pas remplis).
- Au clic `Valider` :
  1. Appelle `save_action_points()` pour persister les 3 points dans `Vigilance_<short_id>.md`.
  2. Transition vers l'ecran suivant du flux.
- En cas d'erreur IA :
  1. Affiche le message d'erreur en rouge.
  2. Pas de zone de saisie des 3 points (le pharmacien ne peut pas continuer sans resultat IA).

### 6.2 Etapes logiques
1. Le `CoProductionScreen` est cree avec `session_id` et `md_path` par `CaptureInterviewTextNotes`.
2. Verification des pre-conditions (fichier markdown present, configuration IA disponible, prompt present).
3. Lancement de l'appel IA dans un thread daemon.
4. Affichage `Analyse en cours...` dans la fenetre co-production.
5. Le service charge `promptvigilance.txt` (system prompt) et `QuestionnaireComplet_<short_id>.md` (user message).
6. Le service appelle le fournisseur IA via le SDK officiel.
7. Le resultat est recu et ecrit dans `data/sessions/Vigilance_<short_id>.md`.
8. Le resultat est affiche dans la zone de reponse de la fenetre co-production.
9. Les 3 zones de saisie `Point 1`, `Point 2`, `Point 3` sont affichees.
10. Le pharmacien saisit ses 3 points du plan d'action.
11. Au clic `Valider`, les 3 points sont enregistres dans `Vigilance_<short_id>.md`.
12. Transition vers l'ecran suivant du flux.

---

## 7. Sorties attendues

### 7.1 Type de sortie
- Fichier markdown + etat UI de co-production + transition ecran

### 7.2 Schema de sortie
- Fichier `data/sessions/Vigilance_<short_id>.md` contenant :
  - une section `## Points de vigilance` (issue de l'IA),
  - une section `## Plan d'action - 3 points pharmacien` (saisie pharmacien).
- Etat UI :
  - vue co-production active,
  - resultat du prompt affiche (read-only),
  - 3 zones de saisie pour les points du plan d'action.
- Transition UI :
  - Au clic `Valider` : sauvegarde des 3 points + transition vers l'ecran suivant du flux.

---

## 8. Cas limites et comportements attendus

| Situation | Comportement attendu |
|---------|----------------------|
| Fichier questionnaire complet absent | Blocage + message d'erreur |
| Fournisseur IA non supporte | Blocage + message d'erreur |
| Cle API absente/invalide | Blocage + message d'erreur |
| Fichier `config/prompts/promptvigilance.txt` absent ou vide | Blocage + message d'erreur |
| Modele IA absent dans settings | Utilisation du modele par defaut du fournisseur |
| Reponse IA vide ou inexploitable | Signalement explicite sans extrapolation |
| Timeout ou erreur API IA | `RuntimeError` + message d'erreur dans le `CoProductionScreen` |
| Aucun point de vigilance detecte | Signalement explicite dans `data/sessions/Vigilance_<short_id>.md` |
| Le pharmacien saisit moins de 3 points | Bouton `Valider` desactive |
| Le pharmacien saisit plus de 3 points | Impossible : exactement 3 zones de saisie |

---

## 9. Criteres d'acceptation

Le skill est conforme si :
- L'appel IA est declenche automatiquement a la creation du `CoProductionScreen` dans un thread daemon.
- L'appel IA utilise le fournisseur selectionne (`OpenIA`, `Anthropic`, `Mistral`), sa cle API, et le modele configure (ou le defaut).
- L'appel IA est structure avec `promptvigilance.txt` comme system prompt et `QuestionnaireComplet_[xxxxxx].md` comme user message.
- Le resultat du prompt est affiche dans la fenetre co-production avec l'IA.
- Le fichier `data/sessions/Vigilance_<short_id>.md` est cree avec un contenu succinct limite aux points de vigilance.
- Le pharmacien dispose de 3 zones de saisie pour definir les 3 points du plan d'action.
- Le bouton `Valider` n'est actif que lorsque les 3 points sont renseignes.
- Les 3 points saisis sont enregistres dans `data/sessions/Vigilance_<short_id>.md`.
- Au clic `Valider`, la transition vers l'ecran suivant est effectuee.
- L'interface n'est jamais bloquee pendant l'appel IA.
- Aucune donnee non exprimee n'est ajoutee.

Un seul critere non respecte rend le skill non conforme.

---

## 10. Post-conditions

Apres execution :
- `data/sessions/Vigilance_<short_id>.md` est disponible avec les points de vigilance et les 3 points du plan d'action saisis par le pharmacien.
- Le resultat du prompt est visible dans la fenetre co-production avec l'IA.
- Le flux utilisateur a transitionne vers l'ecran suivant.
- Le contenu est pret pour les etapes de validation/assemblage du bilan.

---

## 11. Hors perimetre
- Diagnostic medical.
- Prescription.
- Decision clinique.
- Interpretation medicale avancee.
- Definition du contenu metier du prompt au-dela du fichier `config/prompts/promptvigilance.txt`.
- Extension du parametre `modele_ia` dans l'ecran de configuration (couvert par `ConfigureApplicationContext`).
