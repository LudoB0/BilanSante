# PRP - Product / Prompt Requirements Plan

## 0. Metadonnees
- Nom du skill : CaptureConsentStatus
- Reference PRD : PRD V1 PRD 4.5; PRD 6
- Version : V1
- Statut : draft
- Dependances (autres skills ou donnees) : Voir /docs/skills/skills.md

---

## 1. Intention (obligatoire - 1 phrase)
Tracer le consentement a lenregistrement audio.

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
| Consentement audio (oui/non) | booleen (oui/non) | Oui | Consentement audio (oui/non) |
| Horodatage du consentement | date-heure | Oui | Horodatage du consentement |
| Identifiant de session | texte | Oui | Identifiant de session |

### 3.2 Regles de priorite des entrees
- Le consentement sert uniquement a autoriser l'enregistrement audio.
- Les donnees de consentement n'ont aucun role decisionnel sur le bilan.

Aucune autre source de donnees n'est autorisee.

---

## 4. Pre-conditions d'execution
Le skill ne doit pas s'executer si :
- La session n'est pas active.
- Le consentement audio n'est pas renseigne.
- Les entrees principales ne sont pas disponibles.

---

## 5. Regles IA strictes (conformes PRD)

- Le consentement conditionne uniquement l'activation de l'enregistrement audio.
- Le consentement n'influence ni l'analyse ni les actions proposees.
- L'horodatage du consentement est obligatoire pour la tracabilite.

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
- Donnees de consentement associees a la session (tracabilite)
- Format exact non specifie dans le PRD.

---

## 8. Cas limites et comportements attendus

| Situation | Comportement attendu |
|---------|----------------------|
| Consentement absent alors quun enregistrement audio est present. | Signalement explicite sans extrapolation |
| Entree obligatoire absente | Blocage |
| Information contradictoire | Signalement sans arbitrage |

---

## 9. Criteres d'acceptation

Le skill est conforme si :
- Le statut de consentement (oui/non) est enregistre.
- L'horodatage du consentement est present.
- Les donnees sont rattachees a la session.

Un seul critere non respecte rend le skill non conforme.

---

## 10. Post-conditions

Apres execution :
- Le statut de consentement est enregistre et disponible pour le module d'enregistrement audio.
- La tracabilite du consentement est assuree.

---

## 11. Hors perimetre
- Diagnostic medical.
- Prescription.
- Decision clinique.
- Interpretation medicale avancee.
