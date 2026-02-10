# PRP - Product / Prompt Requirements Plan

## 0. Metadonnees
- Nom du skill : TranscribeAudioToTranscript
- Reference PRD : PRD V1 PRD 3  Etape 7 / 4.3; PRD 4.3; PRD 6
- Version : V1
- Statut : draft
- Dependances (autres skills ou donnees) : Voir /docs/skills/skills.md

---

## 1. Intention (obligatoire - 1 phrase)
Transcrire laudio en transcript textuel fidele.

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
| Enregistrement audio | audio | Oui | Enregistrement audio |

### 3.2 Regles de priorite des entrees
- L'enregistrement audio est la seule source d'entree.
- La transcription doit etre fidele au propos, sans reformulation.

Aucune autre source de donnees n'est autorisee.

---

## 4. Pre-conditions d'execution
Le skill ne doit pas s'executer si :
- Les entrees principales ne sont pas disponibles.

---

## 5. Regles IA strictes (conformes PRD)

- Fidelite au propos, sans reformulation ni ajout.
- Aucune interpretation ou analyse du contenu.
- Le transcript produit n'est pas encore valide ; il doit etre valide par le pharmacien.

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
- Texte structure

### 7.2 Schema de sortie
- Transcript textuel complet

---

## 8. Cas limites et comportements attendus

| Situation | Comportement attendu |
|---------|----------------------|
| Audio inaudible ou incomplet. | Signalement explicite sans extrapolation |
| Entree obligatoire absente | Blocage |
| Information contradictoire | Signalement sans arbitrage |

---

## 9. Criteres d'acceptation

Le skill est conforme si :
- Le transcript est fidele au contenu audio.
- Aucune information n'a ete ajoutee ou reformulee.
- Le format de sortie est strictement respecte.

Un seul critere non respecte rend le skill non conforme.

---

## 10. Post-conditions

Apres execution :
- Le transcript textuel est disponible pour relecture et validation par le pharmacien.
- Le transcript n'est pas encore la source de verite (validation requise).

---

## 11. Hors perimetre
- Diagnostic medical.
- Prescription.
- Decision clinique.
- Interpretation medicale avancee.
