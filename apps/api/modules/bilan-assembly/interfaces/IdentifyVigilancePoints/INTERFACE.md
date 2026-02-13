# Interface d'implementation - bilan-assembly

## 1. Reference contractuelle
- PRP de reference : /docs/prp/PRP_IdentifyVigilancePoints.md
- Version du PRP : V3

## 2. Responsabilite du module
Apres creation de `QuestionnaireComplet_[xxxxxx].md` (fin `CaptureInterviewTextNotes`), appeler l'IA selectionnee (`OpenIA`, `Anthropic`, `Mistral`) avec la cle API configuree, envoyer le questionnaire complet et le prompt charge depuis `config/prompts/promptvigilance.txt`, afficher le resultat dans la fenetre co-production, puis enregistrer le resultat dans `data/sessions/Vigilance_<short_id>.md`.

## 3. Entrees attendues
- Champ: Identifiant de session
  - Type logique: texte
  - Obligatoire: Oui
  - Format/description: session cible
- Champ: Questionnaire complet
  - Type logique: fichier markdown
  - Obligatoire: Oui
  - Format/description: `data/sessions/QuestionnaireComplet_[xxxxxx].md`
- Champ: Fournisseur IA
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
- Champ: 3 points du plan d'action pharmacien
  - Type logique: liste texte
  - Obligatoire: Oui
  - Format/description: trois points saisis dans l'interface
- Champ: Fichier vigilance session
  - Type logique: fichier markdown
  - Obligatoire: Oui
  - Format/description: `data/sessions/Vigilance_<short_id>.md` (`short_id` = 8 premiers caracteres du UUID session)

## 4. Sorties produites
- Type de sortie :
- Fichier markdown + etat UI
- Structure logique / format attendu :
- `data/sessions/Vigilance_<short_id>.md` avec section `Points de vigilance`
- `data/sessions/Vigilance_<short_id>.md` avec section `Plan d'action - 3 points pharmacien`
- resultat du prompt affiche dans la fenetre co-production
- zone de saisie des 3 points disponible dans la vue

## 5. Preconditions
- `QuestionnaireComplet_[xxxxxx].md` a ete cree en fin de `CaptureInterviewTextNotes`.
- Le fichier `QuestionnaireComplet_[xxxxxx].md` existe.
- Le fournisseur IA est supporte.
- La cle API est disponible.
- Le fichier `config/prompts/promptvigilance.txt` existe et est non vide.
- Les entrees principales sont disponibles.

## 6. Postconditions
- `data/sessions/Vigilance_<short_id>.md` est cree/mis a jour avec vigilance + 3 points.
- Le resultat du prompt est affiche dans la fenetre co-production.
- Les donnees sont pretes pour la suite du flux bilan/validation.

## 7. Erreurs et cas d'echec
- Situation: Fichier questionnaire complet absent
  - Comportement attendu: Blocage
- Situation: Fournisseur IA non supporte
  - Comportement attendu: Blocage
- Situation: Cle API absente/invalide
  - Comportement attendu: Blocage
- Situation: Fichier `config/prompts/promptvigilance.txt` absent ou vide
  - Comportement attendu: Blocage
- Situation: Reponse IA vide/inexploitable
  - Comportement attendu: Signalement explicite
- Situation: Nombre de points saisis different de 3
  - Comportement attendu: Blocage

## 8. Invariants
- Aucune information ne doit etre inventee.
- Sortie IA limitee aux points de vigilance, concise.
- Aucune interpretation medicale avancee, diagnostic ou prescription.
- Le pharmacien reste maitre des 3 points du plan d'action.

## 9. Hors perimetre
- Diagnostic medical.
- Prescription.
- Decision clinique.
- Interpretation medicale avancee.
