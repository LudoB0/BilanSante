# Interface d'implementation - interview-capture

## 1. Reference contractuelle
- PRP de reference : /docs/prp/PRP_CaptureInterviewTextNotes.md
- Version du PRP : V4

## 2. Responsabilite du module
Au clic `Demander a l'IA`, enregistrer toutes les saisies pharmacien dans `data/sessions/QuestionnaireComplet_[xxxxxx].md`, remplacer l'interface courante par la fenetre de co-production, puis declencher `IdentifyVigilancePoints`.

## 3. Entrees attendues
- Champ: Identifiant de session
  - Type logique: texte
  - Obligatoire: Oui
  - Format/description: session active
- Champ: Fichier questionnaire complet
  - Type logique: fichier markdown
  - Obligatoire: Oui
  - Format/description: `data/sessions/QuestionnaireComplet_[xxxxxx].md`
- Champ: Notes pharmacien par question
  - Type logique: texte markdown
  - Obligatoire: Non
  - Format/description: saisies libres dans la vue questionnaire
- Champ: Tension du patient
  - Type logique: texte markdown
  - Obligatoire: Non
  - Format/description: saisie libre (ex: `120/80`)
- Champ: Rapport du pharmacien
  - Type logique: texte markdown
  - Obligatoire: Non
  - Format/description: saisie libre
- Champ: Action utilisateur
  - Type logique: evenement UI
  - Obligatoire: Oui
  - Format/description: clic bouton `Demander a l'IA`
- Champ: Fournisseur IA configure
  - Type logique: enum
  - Obligatoire: Oui
  - Format/description: `OpenIA` ou `Anthropic` ou `Mistral`
- Champ: Cle API IA
  - Type logique: texte
  - Obligatoire: Oui
  - Format/description: cle API du fournisseur selectionne
- Champ: Prompt vigilance
  - Type logique: fichier texte
  - Obligatoire: Oui
  - Format/description: fichier `config/prompts/promptvigilance.txt`

## 4. Sorties produites
- Type de sortie :
- Fichier markdown + transition UI + declenchement IA
- Structure logique / format attendu :
- `data/sessions/QuestionnaireComplet_[xxxxxx].md` mis a jour avec les saisies pharmacien
- `current_interface_closed = true`
- `co_production_interface_opened = true`
- `next_skill = IdentifyVigilancePoints`
- `identify_vigilance_triggered = true`

## 5. Preconditions
- La session est active.
- Le fichier `QuestionnaireComplet_[xxxxxx].md` existe.
- Le fournisseur IA est configure.
- La cle API est disponible.
- Le fichier `config/prompts/promptvigilance.txt` existe et est non vide.
- Les entrees principales sont disponibles.

## 6. Postconditions
- Les donnees pharmacien ont ete persistees dans `QuestionnaireComplet_[xxxxxx].md`.
- L'interface courante est fermee.
- L'interface de co-production IA est ouverte.
- `IdentifyVigilancePoints` est declenche.

## 7. Erreurs et cas d'echec
- Situation: Fichier markdown absent
  - Comportement attendu: Blocage
- Situation: Entree obligatoire absente
  - Comportement attendu: Blocage
- Situation: Echec d'ecriture
  - Comportement attendu: Blocage + message explicite
- Situation: Echec transition UI
  - Comportement attendu: Signalement explicite
- Situation: Configuration IA absente
  - Comportement attendu: Blocage

## 8. Invariants
- Aucune information ne doit etre inventee.
- Les saisies pharmacien sont enregistrees telles que saisies.
- Aucune interpretation medicale, diagnostic ou prescription.

## 9. Hors perimetre
- Production du resultat vigilance sans `IdentifyVigilancePoints`.
- Diagnostic medical.
- Prescription.
- Decision clinique.
- Interpretation medicale avancee.
