# PRP - Product / Prompt Requirements Plan

## 0. Metadonnees
- Nom du skill : CaptureInterviewTextNotes
- Reference PRD : PRD V1 PRD 3  Etape 6 / 4.3; PRD 4.3-4.4; PRD 6
- Version : V1
- Statut : draft
- Dependances (autres skills ou donnees) : Voir /docs/skills/skills.md

---

## 1. Intention (obligatoire - 1 phrase)
Saisir des notes textuelles lors de lentretien (texte seul ou complement audio).

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
| Notes textuelles du pharmacien | non specifie | Oui | Notes textuelles du pharmacien |
| Identifiant de session | texte | Oui | Identifiant de session |

### 3.2 Regles de priorite des entrees
- Les notes textuelles sont saisies par le pharmacien.
- L'identifiant de session est obligatoire pour le rattachement.

Aucune autre source de donnees n'est autorisee.

---

## 4. Pre-conditions d'execution
Le skill ne doit pas s'executer si :
- La session n'est pas active.
- Les entrees principales ne sont pas disponibles.

---

## 5. Regles IA strictes (conformes PRD)

- Aucune reecriture automatique des notes.
- Les notes sont enregistrees telles que saisies par le pharmacien.
- Les metadonnees d'entretien (mode de recueil texte ou mixte) sont automatiquement associees.

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
- Autre (a preciser)

### 7.2 Schema de sortie
- Notes textuelles et metadonnees dentretien (mode de recueil texte ou mixte)
- Format exact non specifie dans le PRD.

---

## 8. Cas limites et comportements attendus

| Situation | Comportement attendu |
|---------|----------------------|
| Notes illisibles ou incompletes. | Signalement explicite sans extrapolation |
| Entree obligatoire absente | Blocage |
| Information contradictoire | Signalement sans arbitrage |

---

## 9. Criteres d'acceptation

Le skill est conforme si :
- Les notes textuelles sont enregistrees sans modification.
- Les metadonnees d'entretien sont correctement associees.
- Les notes sont rattachees a la session.

Un seul critere non respecte rend le skill non conforme.

---

## 10. Post-conditions

Apres execution :
- Les notes textuelles sont disponibles pour le module de transcription/validation.
- Les metadonnees d'entretien sont enregistrees.

---

## 11. Hors perimetre
- Diagnostic medical.
- Prescription.
- Decision clinique.
- Interpretation medicale avancee.
