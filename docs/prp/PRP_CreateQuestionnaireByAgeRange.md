# PRP - Product / Prompt Requirements Plan

## 0. Metadonnees
- Nom du skill : CreateQuestionnaireByAgeRange
- Reference PRD : PRD V1 PRD 3  Etape 2 / 4.1-4.2; PRD 5.1-5.2; PRD 6
- Version : V1
- Statut : draft
- Dependances (autres skills ou donnees) : Voir /docs/skills/skills.md

---

## 1. Intention (obligatoire - 1 phrase)
Creer/editer des questionnaires associes a une tranche dage.

---

## 2. Perimetre fonctionnel

### 2.1 Ce que le skill FAIT
- Utiliser les entrees contractuelles listees en section 3.1.
- Produire les sorties decrites en section 7.
- Appliquer les regles et contraintes du PRD.

### 2.2 Ce que le skill NE FAIT PAS
- Inventer des informations.
- Utiliser des sources externes non prevues par le PRD.
- Produire un diagnostic, une prescription ou une decision clinique.

---

## 3. Entrees autorisees (contractuelles)

### 3.1 Entrees principales
Lister uniquement les donnees explicitement decrites dans le PRD.

| Champ | Type | Obligatoire | Description |
|------|------|------------|-------------|
| Tranche dage (categorielle) | valeur categorielle | Oui | Tranche dage (categorielle) |
| Questions structurees (choix simple, choix multiple, texte court) | non specifie | Oui | Questions structurees (choix simple, choix multiple, texte court) |

### 3.2 Regles de priorite des entrees
- La tranche d'age est obligatoire pour associer un questionnaire.
- Les questions structurees definissent le format de collecte.

Aucune autre source de donnees n'est autorisee.

---

## 4. Pre-conditions d'execution
Le skill ne doit pas s'executer si :
- Les entrees principales ne sont pas disponibles.

---

## 5. Regles IA strictes (conformes PRD)

- Aucune interpretation automatique des reponses.
- Les questionnaires ne produisent aucune analyse.
- Le pharmacien est maitre du contenu des questionnaires.

Ces regles sont imperatives et prioritaires.

---

## 6. Traitement attendu (logique fonctionnelle)

Decrire la transformation attendue des entrees vers les sorties, sans mentionner de technologie, de framework ou d'implementation.

Etapes logiques :
1. Verifier les pre-conditions.
2. Utiliser les entrees contractuelles et appliquer les regles PRD.
3. Produire les sorties attendues.

---

## 7. Sorties attendues

### 7.1 Type de sortie
- JSON structure

### 7.2 Schema de sortie
- Questionnaire structure associe a une tranche d'age, pret a etre utilise en session.

---

## 8. Cas limites et comportements attendus

| Situation | Comportement attendu |
|---------|----------------------|
| Questionnaire incomplet ou non associe a une tranche dage. | Signalement explicite sans extrapolation |
| Entree obligatoire absente | Blocage |
| Information contradictoire | Signalement sans arbitrage |

---

## 9. Criteres d'acceptation

Le skill est conforme si :
- Le questionnaire est correctement associe a une tranche d'age.
- Toutes les questions sont structurees (choix simple, choix multiple, texte court).
- Le format de sortie est strictement respecte.

Un seul critere non respecte rend le skill non conforme.

---

## 10. Post-conditions

Apres execution :
- Le questionnaire est enregistre et disponible pour utilisation en session.
- Le pharmacien peut le modifier ou le reediter.

---

## 11. Hors perimetre
- Diagnostic medical.
- Prescription.
- Decision clinique.
- Interpretation medicale avancee.
