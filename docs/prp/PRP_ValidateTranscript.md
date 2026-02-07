# PRP - Product / Prompt Requirements Plan

## 0. Metadonnees
- Nom du skill : ValidateTranscript
- Reference PRD : PRD V1 PRD 3  Etape 7 / 4.3; PRD 4.3-4.4; PRD 6
- Version : V1
- Statut : draft
- Dependances (autres skills ou donnees) : Voir /docs/skills/skills.md

---

## 1. Intention (obligatoire - 1 phrase)
Faire relire et valider le transcript par le pharmacien.

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
| Transcript textuel complet | texte | Oui | Transcript textuel complet |

### 3.2 Regles de priorite des entrees
- Le transcript de l'entretien officinal est la source de verite principale.
- Les reponses au questionnaire sont utilisees uniquement comme contexte.
- Les donnees de consentement et de metadonnees n'ont aucun role decisionnel.

Aucune autre source de donnees n'est autorisee.

---

## 4. Pre-conditions d'execution
Le skill ne doit pas s'executer si :
- Le transcript n'est pas valide.
- Les entrees principales ne sont pas disponibles.

---

## 5. Regles IA strictes (conformes PRD)

- Aucune information ne doit etre inventee.
- Aucune action ne peut etre proposee sans justification explicite issue du transcript.
- Toute information absente ou ambigue doit etre signalee explicitement.
- Aucune interpretation medicale, diagnostic ou prescription.
- Le langage doit etre professionnel, clair pour le patient et adapte au contexte officinal.
- Le pharmacien reste maitre du contenu final.

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
- Transcript valide, source de verite unique
- Date de validation de lentretien

---

## 8. Cas limites et comportements attendus

| Situation | Comportement attendu |
|---------|----------------------|
| Transcript non valide. | Signalement explicite sans extrapolation |
| Entree obligatoire absente | Blocage |
| Information contradictoire | Signalement sans arbitrage |
| Transcript vide ou trop court | Sortie minimale sans extrapolation |

---

## 9. Criteres d'acceptation

Le skill est conforme si :
- Toutes les informations presentes sont tracables au transcript.
- Aucune donnee non exprimee n'apparait.
- Le format de sortie est strictement respecte.
- Le contenu est comprehensible par un patient sans reformulation.

Un seul critere non respecte rend le skill non conforme.

---

## 10. Post-conditions

Apres execution :
- Les donnees produites sont pretes a etre relues, modifiees et validees par le pharmacien.
- Aucune persistance automatique de donnees apres validation finale de la session.

---

## 11. Hors perimetre
- Diagnostic medical.
- Prescription.
- Decision clinique.
- Interpretation medicale avancee.
