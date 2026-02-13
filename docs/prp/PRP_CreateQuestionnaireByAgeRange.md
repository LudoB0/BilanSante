# PRP - Product / Prompt Requirements Plan

## 0. Metadonnees
- Nom du skill : CreateQuestionnaireByAgeRange
- Reference PRD : PRD V1 PRD 3 Etape 2 / 4.1-4.2; PRD 5.1-5.2; PRD 6
- Version : V3
- Statut : draft
- Dependances (autres skills ou donnees) : Voir /docs/skills/skills.md

---

## 1. Intention (obligatoire - 1 phrase)
Creer/editer des questionnaires associes a une tranche d'age, en imposant les questions `poids` et `taille`, en gerant le caractere obligatoire de chaque reponse via une case a cocher et en gerant le ciblage sexe de chaque question via `sex_target` (`H`, `F`, `M`).

---

## 2. Perimetre fonctionnel

### 2.1 Ce que le skill FAIT
- Utiliser les entrees contractuelles listees en section 3.1.
- Creer/editer un questionnaire associe a une tranche d'age.
- Imposer la presence de 2 questions obligatoires dans chaque questionnaire :
  - `obligatoire1` (ordre `11`) : `Indiquer votre poids (en Kg)`
  - `Obligatoire2` (ordre `12`) : `Indiquer votre taille (en m)`
- Interdire la suppression de ces 2 questions obligatoires lors de la creation et de la modification d'un questionnaire.
- Exposer, pour chaque question, une case a cocher permettant de definir si la reponse est obligatoire (`required=true`) ou non (`required=false`).
- Exposer, pour chaque question, un champ `sex_target` avec 3 choix possibles (`H`, `F`, `M`).
- Produire les sorties decrites en section 7.
- Appliquer les regles et contraintes du PRD.

### 2.2 Ce que le skill NE FAIT PAS
- Inventer des informations.
- Utiliser des sources externes non prevues par le PRD.
- Produire un diagnostic, une prescription ou une decision clinique.

---

## 3. Entrees autorisees (contractuelles)

### 3.1 Entrees principales
| Champ | Type | Obligatoire | Description |
|------|------|------------|-------------|
| Tranche d'age (categorielle) | valeur categorielle | Oui | Tranche d'age cible du questionnaire |
| Questions structurees (`boolean`, `single_choice`, `multiple_choice`, `short_text`, `scale`) | donnees structurees | Oui | Liste des questions editees |
| Champ `required` par question | booleen | Oui | Etat de la case a cocher `Reponse obligatoire` |
| Champ `sex_target` par question | texte | Oui | Ciblage sexe de la question : `H` (Homme), `F` (Femme), `M` (Mixte) |
| Questions obligatoires systeme | donnees structurees | Oui | Bloc fixe `obligatoire1` + `Obligatoire2` present dans tous les questionnaires |

### 3.2 Regles de priorite des entrees
- La tranche d'age est obligatoire pour associer un questionnaire.
- Les questions structurees definissent le format de collecte.
- Les 2 questions obligatoires systeme sont toujours presentes et non supprimables.
- Le caractere obligatoire de chaque question est determine par la case a cocher (`required`).
- Le ciblage sexe de chaque question est determine par `sex_target` (`H`, `F`, `M`).

Aucune autre source de donnees n'est autorisee.

---

## 4. Pre-conditions d'execution
Le skill ne doit pas s'executer si :
- Les entrees principales ne sont pas disponibles.
- Le questionnaire ne contient pas les 2 questions obligatoires systeme.

---

## 5. Regles IA strictes (conformes PRD)

- Aucune interpretation automatique des reponses.
- Les questionnaires ne produisent aucune analyse.
- Le pharmacien est maitre du contenu des questionnaires, hors suppression des 2 questions obligatoires systeme.

Ces regles sont imperatives et prioritaires.

---

## 6. Traitement attendu (logique fonctionnelle)

Etapes logiques :
1. Verifier les pre-conditions.
2. Charger ou initialiser le questionnaire pour la tranche d'age cible.
3. Garantir la presence des 2 questions obligatoires systeme, avec la structure suivante :

```json
{
  "id": "obligatoire1",
  "order": 11,
  "type": "short_text",
  "label": "Indiquer votre poids (en Kg)",
  "required": true,
  "sex_target": "M",
  "options": [],
  "scale_config": null
}
```

```json
{
  "id": "Obligatoire2",
  "order": 12,
  "type": "short_text",
  "label": "Indiquer votre taille (en m)",
  "required": true,
  "sex_target": "M",
  "options": [],
  "scale_config": null
}
```

4. Autoriser l'ajout/modification des autres questions du questionnaire.
5. Exposer pour chaque question une case a cocher `Reponse obligatoire` pour definir `required`.
6. Exposer pour chaque question un select `sex_target` (`H`, `F`, `M`), avec `M` affichable pour tous les sexes.
7. Interdire toute suppression des questions `obligatoire1` et `Obligatoire2`.
8. Produire les sorties attendues.

---

## 7. Sorties attendues

### 7.1 Type de sortie
- JSON structure

### 7.2 Schema de sortie
- Questionnaire structure associe a une tranche d'age, pret a etre utilise en session.
- Chaque question contient explicitement le champ `required` (booleen).
- Chaque question contient explicitement le champ `sex_target` (`H`, `F`, `M`).
- Le questionnaire final contient obligatoirement les questions `obligatoire1` et `Obligatoire2`.

---

## 8. Cas limites et comportements attendus

| Situation | Comportement attendu |
|---------|----------------------|
| Questionnaire incomplet ou non associe a une tranche d'age | Signalement explicite sans extrapolation |
| Entree obligatoire absente | Blocage |
| Information contradictoire | Signalement sans arbitrage |
| Tentative de suppression de `obligatoire1` ou `Obligatoire2` | Blocage |
| Question sans champ `required` | Blocage |
| Question sans champ `sex_target` | Blocage |
| Valeur `sex_target` hors `H`, `F`, `M` | Blocage |

---

## 9. Criteres d'acceptation

Le skill est conforme si :
- Le questionnaire est correctement associe a une tranche d'age.
- Toutes les questions sont structurees (`boolean`, `single_choice`, `multiple_choice`, `short_text`, `scale`).
- Le format de sortie est strictement respecte.
- Les 2 questions obligatoires systeme (`obligatoire1`, `Obligatoire2`) sont presentes dans chaque questionnaire.
- Les 2 questions obligatoires systeme ne peuvent pas etre supprimees en creation/modification.
- Une case a cocher permet de definir `required` pour chaque question (hors questions systeme qui restent `required=true`).
- Un champ `sex_target` est renseigne pour chaque question avec une valeur valide (`H`, `F` ou `M`).

Un seul critere non respecte rend le skill non conforme.

---

## 10. Post-conditions

Apres execution :
- Le questionnaire est enregistre et disponible pour utilisation en session.
- Le pharmacien peut modifier ou reediter le questionnaire sans pouvoir supprimer `obligatoire1` et `Obligatoire2`.
- Le caractere obligatoire de chaque question est conserve dans le champ `required`.
- Le ciblage sexe de chaque question est conserve dans le champ `sex_target`.

---

## 11. Hors perimetre
- Diagnostic medical.
- Prescription.
- Decision clinique.
- Interpretation medicale avancee.
