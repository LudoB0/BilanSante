# PRP - Product / Prompt Requirements Plan

## 0. Metadonnees
- Nom du skill : CaptureQuestionnaireResponses
- Reference PRD : PRD V1 PRD 4.2 / 4.4; PRD 5.1; PRD 6
- Version : V1
- Statut : draft
- Dependances (autres skills ou donnees) : Voir /docs/skills/skills.md

---

## 1. Intention (obligatoire - 1 phrase)
Enregistrer les reponses du questionnaire et lhorodatage.

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
| Reponses structurees au questionnaire | donnees structurees | Oui | Reponses structurees au questionnaire |
| Horodatage | date-heure | Oui | Horodatage |
| Identifiant de session | texte | Oui | Identifiant de session |

### 3.2 Regles de priorite des entrees
- Les reponses sont un support contextuel sans valeur decisionnelle autonome.
- L'identifiant de session est obligatoire pour le rattachement.

Aucune autre source de donnees n'est autorisee.

---

## 4. Pre-conditions d'execution
Le skill ne doit pas s'executer si :
- La session n'est pas active.
- Le questionnaire correspondant n'est pas disponible.
- Les entrees principales ne sont pas disponibles.

---

## 5. Regles IA strictes (conformes PRD)

- Les reponses sont enregistrees telles quelles, sans interpretation ni analyse.
- Les donnees sont stockees localement et temporairement.
- Aucune reecriture automatique des reponses.

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
- Reponses structurees enregistrees et liees a la session.

---

## 8. Cas limites et comportements attendus

| Situation | Comportement attendu |
|---------|----------------------|
| Questionnaire incomplet ou interrompu. | Signalement explicite sans extrapolation |
| Entree obligatoire absente | Blocage |
| Information contradictoire | Signalement sans arbitrage |

---

## 9. Criteres d'acceptation

Le skill est conforme si :
- Toutes les reponses sont correctement rattachees a la session.
- L'horodatage est present pour chaque reponse.
- Le format de sortie est strictement respecte.

Un seul critere non respecte rend le skill non conforme.

---

## 10. Post-conditions

Apres execution :
- Les reponses sont enregistrees et disponibles pour les modules de construction du bilan.
- Aucune interpretation n'a ete realisee.

---

## 11. Hors perimetre
- Diagnostic medical.
- Prescription.
- Decision clinique.
- Interpretation medicale avancee.
