# PRP - Product / Prompt Requirements Plan

## 0. Metadonnees

- Nom du skill : InitializeInterviewSession
- Reference PRD : PRD V1 PRD 3 Etape 3 / 4.1; PRD 4.4 / 5; PRD 6
- Version : V2
- Statut : draft
- Dependances (autres skills ou donnees) : ConfigureApplicationContext (lecture config/settings.json), CreateQuestionnaireByAgeRange (lecture config/questionnaires/)

---

## 1. Intention (obligatoire - 1 phrase)

Afficher le contexte pharmacie, permettre la selection d'une tranche d'age parmi les questionnaires non vides, et creer une session unique stockee dans `data/`.

---

## 2. Perimetre fonctionnel

### 2.1 Ce que le skill FAIT

- Lire et afficher les informations de la pharmacie depuis `config/settings.json` (nom, adresse, code postal, ville, logo) et les liens web non vides (site_web, instagram, facebook, x, linkedin).
- Lister les tranches d'age disposant d'un questionnaire non vide dans `config/questionnaires/`.
- Permettre au pharmacien de selectionner une tranche d'age parmi celles disponibles.
- Creer une session unique identifiee par un UUID v4 et stocker le fichier session dans `data/sessions/`.
- Enregistrer les metadonnees de session (identifiant, tranche d'age, date/heure de creation, coordonnees pharmacie).

### 2.2 Ce que le skill NE FAIT PAS

- Inventer des informations.
- Modifier les donnees de parametrage (`config/`).
- Utiliser des sources externes non prevues par le PRD.
- Produire un diagnostic, une prescription ou une decision clinique.
- Generer le QR code (skill separee).

---

## 3. Entrees autorisees (contractuelles)

### 3.1 Entrees principales

| Champ | Type | Obligatoire | Description |
|-------|------|-------------|-------------|
| Tranche d'age du patient | valeur categorielle | Oui | Selectionnee par le pharmacien parmi les questionnaires non vides |

### 3.2 Donnees lues (contexte, lecture seule)

| Source | Donnees lues | Usage |
|--------|-------------|-------|
| `config/settings.json` | nom_pharmacie, adresse, code_postal, ville | Affichage + copie dans metadonnees session |
| `config/img/logo.png` | Image logo | Affichage a l'ecran |
| `config/settings.json` | site_web, instagram, facebook, x, linkedin | Affichage si non vide |
| `config/questionnaires/*.json` | Liste des questionnaires existants | Filtrage des tranches d'age proposees |

### 3.3 Regles de priorite des entrees

- La tranche d'age du patient est la seule entree saisie par l'utilisateur.
- Les donnees pharmacie et questionnaires sont lues depuis `config/` (lecture seule).
- Aucune donnee nominative n'est necessaire.

Aucune autre source de donnees n'est autorisee.

---

## 4. Pre-conditions d'execution

Le skill ne doit pas s'executer si :

- Le parametrage applicatif est incomplet (champs obligatoires manquants dans `config/settings.json` ou logo absent).
- Aucun questionnaire non vide n'existe dans `config/questionnaires/`.

---

## 5. Regles IA strictes (conformes PRD)

- Aucune donnee nominative ne doit etre collectee.
- La session n'a pas de duree predefinie.
- L'identifiant de session doit etre unique (UUID v4).
- Les liens web ne sont affiches que s'ils sont non vides dans `settings.json`.
- Seules les tranches d'age avec un questionnaire contenant au moins une question sont proposees.

Ces regles sont imperatives et prioritaires.

---

## 6. Traitement attendu (logique fonctionnelle)

Etapes logiques :

1. Verifier les pre-conditions (parametrage complet, au moins un questionnaire disponible).
2. Charger et afficher les informations pharmacie depuis `config/settings.json` et `config/img/logo.png`.
3. Afficher les liens web non vides (site_web, instagram, facebook, x, linkedin).
4. Lister les tranches d'age disposant d'un questionnaire non vide et les proposer au pharmacien.
5. Attendre la selection d'une tranche d'age par le pharmacien.
6. Au clic sur "Demarrer l'entretien", generer un UUID v4 unique et creer le fichier session dans `data/sessions/<session_id>.json`.

---

## 7. Sorties attendues

### 7.1 Type de sortie

- JSON structure stocke dans `data/sessions/<session_id>.json`

### 7.2 Schema de sortie

- `session_id` : UUID v4 unique
- `age_range` : tranche d'age selectionnee
- `created_at` : date/heure de creation ISO 8601
- `status` : `"active"`
- `metadata.pharmacie` : copie des coordonnees pharmacie (nom_pharmacie, adresse, code_postal, ville) au moment de la creation

---

## 8. Cas limites et comportements attendus

| Situation | Comportement attendu |
|-----------|----------------------|
| Parametrage applicatif incomplet | Message explicite, bouton desactive |
| Aucun questionnaire disponible | Message explicite, bouton desactive |
| Tranche d'age non selectionnee | Bouton "Demarrer l'entretien" desactive |
| Session non creee (echec ecriture) | Signalement explicite sans extrapolation |
| Collision UUID | Regeneration automatique |
| Tous les liens web vides | Section liens non affichee |

---

## 9. Criteres d'acceptation

Le skill est conforme si :

- Les informations pharmacie (logo, nom, adresse, code postal, ville) sont affichees.
- Les liens web non vides sont affiches, les vides sont masques.
- Seules les tranches d'age avec questionnaire non vide sont proposees.
- Un identifiant de session unique (UUID v4) est genere.
- Les metadonnees de session (date/heure de creation, coordonnees pharmacie) sont associees.
- Le fichier session est stocke dans `data/sessions/`.
- Le format de sortie est strictement respecte.

Un seul critere non respecte rend le skill non conforme.

---

## 10. Post-conditions

Apres execution :

- La session est creee et active dans `data/sessions/`.
- Les modules de collecte peuvent s'y rattacher via le session_id.
- Les donnees de parametrage dans `config/` n'ont pas ete modifiees.

---

## 11. Hors perimetre

- Diagnostic medical.
- Prescription.
- Decision clinique.
- Interpretation medicale avancee.
- Generation du QR code (GenerateSessionQRCode).
- Capture des reponses questionnaire.
