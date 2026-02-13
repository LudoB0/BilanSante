# Interface d'implementation - questionnaire-catalog

## 1. Reference contractuelle
- PRP de reference : /docs/prp/PRP_CreateQuestionnaireByAgeRange.md
- Version du PRP : V2

## 2. Responsabilite du module
Creer/editer des questionnaires associes a une tranche d'age, imposer 2 questions systeme (`obligatoire1`, `Obligatoire2`) non supprimables, et gerer le caractere obligatoire des reponses via le champ `required`.

## 3. Entrees attendues
- Champ: Tranche d'age (categorielle)
  - Type logique: valeur categorielle
  - Obligatoire: Oui
  - Format/description: Tranche d'age cible du questionnaire
- Champ: Questions structurees (choix simple, choix multiple, texte court)
  - Type logique: donnees structurees
  - Obligatoire: Oui
  - Format/description: Questions editees du questionnaire
- Champ: Champ `required` par question
  - Type logique: booleen
  - Obligatoire: Oui
  - Format/description: valeur issue de la case a cocher `Reponse obligatoire`
- Champ: Questions obligatoires systeme
  - Type logique: donnees structurees
  - Obligatoire: Oui
  - Format/description: `obligatoire1` (poids) et `Obligatoire2` (taille)

## 4. Sorties produites
- Type de sortie :
- JSON structure
- Structure logique / format attendu :
- Questionnaire associe a une tranche d'age
- Champ `required` explicite sur chaque question
- Presence obligatoire de `obligatoire1` et `Obligatoire2`

## 5. Preconditions
- Les entrees principales sont disponibles.
- Les questions obligatoires systeme sont presentes.

## 6. Postconditions
- Le questionnaire est enregistre pour la tranche d'age cible.
- Les questions `obligatoire1` et `Obligatoire2` sont presentes et non supprimables.
- Le caractere obligatoire (`required`) est conserve pour chaque question.

## 7. Erreurs et cas d'echec
- Situation: Questionnaire incomplet ou non associe a une tranche d'age
  - Comportement attendu: Signalement explicite sans extrapolation
- Situation: Entree obligatoire absente
  - Comportement attendu: Blocage
- Situation: Information contradictoire
  - Comportement attendu: Signalement sans arbitrage
- Situation: Tentative de suppression de `obligatoire1` ou `Obligatoire2`
  - Comportement attendu: Blocage
- Situation: Question sans champ `required`
  - Comportement attendu: Blocage

## 8. Invariants
- Aucune information ne doit etre inventee.
- Aucune interpretation medicale, diagnostic ou prescription.
- Les questions systeme `obligatoire1` et `Obligatoire2` restent presentes.
- Le champ `required` est explicite sur chaque question.

## 9. Hors perimetre
- Diagnostic medical.
- Prescription.
- Decision clinique.
- Interpretation medicale avancee.
