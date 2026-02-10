# PRP - Product / Prompt Requirements Plan

## 0. Metadonnees
- Nom du skill : RecordInterviewAudio
- Reference PRD : PRD V1 PRD 3  Etape 6 / 4.5; PRD 4.3-4.4; PRD 6
- Version : V1
- Statut : draft
- Dependances (autres skills ou donnees) : Voir /docs/skills/skills.md

---

## 1. Intention (obligatoire - 1 phrase)
Enregistrer lentretien audio lorsque le consentement est accorde.

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
| Consentement audio | booleen (oui/non) | Oui | Consentement audio |
| Identifiant de session | texte | Oui | Identifiant de session |

### 3.2 Regles de priorite des entrees
- Le consentement audio positif est une precondition obligatoire.
- L'identifiant de session est obligatoire pour le rattachement.

Aucune autre source de donnees n'est autorisee.

---

## 4. Pre-conditions d'execution
Le skill ne doit pas s'executer si :
- La session n'est pas active.
- Le consentement audio n'est pas renseigne.
- Les entrees principales ne sont pas disponibles.

---

## 5. Regles IA strictes (conformes PRD)

- L'enregistrement audio est interdit sans consentement explicite.
- Aucune reecriture ou transformation automatique de l'audio.
- Les metadonnees d'entretien (date, duree, mode de recueil) sont automatiquement associees.

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
- Autre (a preciser) : enregistrement audio

### 7.2 Schema de sortie
- Enregistrement audio et metadonnees dentretien (date, duree, mode de recueil)
- Format exact non specifie dans le PRD.

---

## 8. Cas limites et comportements attendus

| Situation | Comportement attendu |
|---------|----------------------|
| Tentative denregistrement sans consentement. | Blocage |
| Entree obligatoire absente | Blocage |
| Information contradictoire | Signalement sans arbitrage |

---

## 9. Criteres d'acceptation

Le skill est conforme si :
- L'enregistrement audio est realise uniquement avec consentement.
- Les metadonnees d'entretien sont correctement associees.
- L'audio est rattache a la session.

Un seul critere non respecte rend le skill non conforme.

---

## 10. Post-conditions

Apres execution :
- L'enregistrement audio est disponible pour le module de transcription.
- Les metadonnees d'entretien sont enregistrees.

---

## 11. Hors perimetre
- Diagnostic medical.
- Prescription.
- Decision clinique.
- Interpretation medicale avancee.
