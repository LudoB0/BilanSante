# PRP — Product / Prompt Requirements Plan

## 0. Métadonnées
- Nom du skill :
- Référence PRD :
- Version :
- Statut : draft / validé
- Dépendances (autres skills ou données) :

---

## 1. Intention (obligatoire – 1 phrase)
Décrire précisément ce que fait le skill, sans formulation vague, sans notion d’aide, d’intelligence ou d’interprétation.

---

## 2. Périmètre fonctionnel

### 2.1 Ce que le skill FAIT
- 
- 
- 

### 2.2 Ce que le skill NE FAIT PAS
- 
- 
- 

---

## 3. Entrées autorisées (contractuelles)

### 3.1 Entrées principales
Lister uniquement les données explicitement décrites dans le PRD.

| Champ | Type | Obligatoire | Description |
|------|------|------------|-------------|
| | | | |

### 3.2 Règles de priorité des entrées
- Le transcript de l’entretien officinal est la source de vérité principale.
- Les réponses au questionnaire sont utilisées uniquement comme contexte.
- Les données de consentement et de métadonnées n’ont aucun rôle décisionnel.

Aucune autre source de données n’est autorisée.

---

## 4. Pré-conditions d’exécution
Le skill ne doit pas s’exécuter si :
- 
- 
- 

---

## 5. Règles IA strictes (conformes PRD)

- Aucune information ne doit être inventée.
- Aucune action ne peut être proposée sans justification explicite issue du transcript.
- Toute information absente ou ambiguë doit être signalée explicitement.
- Aucune interprétation médicale, diagnostic ou prescription.
- Le langage doit être professionnel, clair pour le patient et adapté au contexte officinal.
- Le pharmacien reste maître du contenu final.

Ces règles sont impératives et prioritaires.

---

## 6. Traitement attendu (logique fonctionnelle)

Décrire la transformation attendue des entrées vers les sorties, sans mentionner de technologie, de framework ou d’implémentation.

Étapes logiques :
1. 
2. 
3. 
4. 

---

## 7. Sorties attendues

### 7.1 Type de sortie
- Texte structuré
- JSON structuré
- Autre (à préciser)

### 7.2 Schéma de sortie
Décrire précisément la structure attendue (champs, sections, ordre).

---

## 8. Cas limites et comportements attendus

| Situation | Comportement attendu |
|---------|----------------------|
| Information absente | Mention explicite dans la sortie |
| Information contradictoire | Signalement sans arbitrage |
| Transcript vide ou trop court | Sortie minimale sans extrapolation |
| Aucun point identifié | Section vide avec mention |

---

## 9. Critères d’acceptation

Le skill est conforme si :
- Toutes les informations présentes sont traçables au transcript.
- Aucune donnée non exprimée n’apparaît.
- Le format de sortie est strictement respecté.
- Le contenu est compréhensible par un patient sans reformulation.

Un seul critère non respecté rend le skill non conforme.

---

## 10. Post-conditions

Après exécution :
- Les données produites sont prêtes à être relues, modifiées et validées par le pharmacien.
- Aucune persistance automatique de données après validation finale de la session.

---

## 11. Hors périmètre
Lister explicitement tout ce que le skill ne fait pas, conformément au PRD.
