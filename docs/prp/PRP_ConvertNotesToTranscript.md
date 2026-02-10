# PRP - Product / Prompt Requirements Plan

## 0. Metadonnees
- Nom du skill : ConvertNotesToTranscript
- Reference PRD : PRD V1 PRD 3  Etape 7 / 4.3; PRD 6
- Version : V1
- Statut : draft
- Dependances (autres skills ou donnees) : Voir /docs/skills/skills.md

---

## 1. Intention (obligatoire - 1 phrase)
Convertir les notes textuelles du pharmacien en transcript structure lorsque l'entretien est en mode texte seul (sans audio).

---

## 2. Perimetre fonctionnel

### 2.1 Ce que le skill FAIT
- Utiliser les entrees contractuelles listees en section 3.1.
- Produire les sorties decrites en section 7.
- Appliquer les regles et contraintes du PRD.

### 2.2 Ce que le skill NE FAIT PAS
- Inventer des informations.
- Reformuler ou enrichir le contenu des notes.
- S'executer si un enregistrement audio existe pour la session (utiliser TranscribeAudioToTranscript a la place).
- Produire un diagnostic, une prescription ou une decision clinique.

---

## 3. Entrees autorisees (contractuelles)

### 3.1 Entrees principales
Lister uniquement les donnees explicitement decrites dans le PRD.

| Champ | Type | Obligatoire | Description |
|------|------|------------|-------------|
| Notes textuelles du pharmacien | texte | Oui | Notes textuelles saisies lors de l'entretien |
| Identifiant de session | texte | Oui | Identifiant de session |

### 3.2 Regles de priorite des entrees
- Les notes textuelles sont la seule source d'entree.
- La conversion doit etre fidele au contenu des notes, sans reformulation ni ajout.

Aucune autre source de donnees n'est autorisee.

---

## 4. Pre-conditions d'execution
Le skill ne doit pas s'executer si :
- La session n'est pas active.
- Les notes textuelles ne sont pas disponibles.
- Un enregistrement audio existe pour cette session (utiliser TranscribeAudioToTranscript a la place).
- Les entrees principales ne sont pas disponibles.

---

## 5. Regles strictes (conformes PRD)

- Fidelite au contenu des notes, sans reformulation ni ajout.
- Aucune interpretation ou analyse du contenu.
- Le transcript produit n'est pas encore valide ; il doit etre valide par le pharmacien.
- Applicable uniquement en mode texte seul (pas d'enregistrement audio present).

Ces regles sont imperatives et prioritaires.

---

## 6. Traitement attendu (logique fonctionnelle)

Decrire la transformation attendue des entrees vers les sorties, sans mentionner de technologie, de framework ou d'implementation.

Etapes logiques :
1. Verifier les pre-conditions (session active, notes disponibles, pas d'audio).
2. Convertir les notes textuelles en transcript structure.
3. Produire le transcript pret pour validation par le pharmacien.

---

## 7. Sorties attendues

### 7.1 Type de sortie
- Texte structure

### 7.2 Schema de sortie
- Transcript textuel structure pret pour validation par le pharmacien.
- Meme format de sortie que TranscribeAudioToTranscript.

---

## 8. Cas limites et comportements attendus

| Situation | Comportement attendu |
|---------|----------------------|
| Notes textuelles absentes ou vides. | Blocage |
| Un enregistrement audio existe pour cette session. | Blocage (utiliser TranscribeAudioToTranscript) |
| Entree obligatoire absente | Blocage |
| Notes illisibles ou incompletes | Signalement explicite sans extrapolation |

---

## 9. Criteres d'acceptation

Le skill est conforme si :
- Le transcript est fidele au contenu des notes textuelles.
- Aucune information n'a ete ajoutee ou reformulee.
- Le format de sortie est identique a celui de TranscribeAudioToTranscript.

Un seul critere non respecte rend le skill non conforme.

---

## 10. Post-conditions

Apres execution :
- Le transcript textuel structure est disponible pour relecture et validation par le pharmacien.
- Le transcript n'est pas encore la source de verite (validation requise).

---

## 11. Hors perimetre
- Transcription audio (couvert par TranscribeAudioToTranscript).
- Diagnostic medical.
- Prescription.
- Decision clinique.
- Interpretation medicale avancee.
