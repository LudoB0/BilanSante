# PRP - Product / Prompt Requirements Plan

## 0. Metadonnees
- Nom du skill : GeneratePDFDocument
- Reference PRD : PRD V1 PRD 5.1-5.2 / 3  Etape 1; PRD 5.3; PRD 6
- Version : V1
- Statut : draft
- Dependances (autres skills ou donnees) : Voir /docs/skills/skills.md

---

## 1. Intention (obligatoire - 1 phrase)
Generer le PDF final destine a limpression/export.

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
| Contenu valide | texte | Oui | Contenu valide |
| Identite graphique de la pharmacie | texte | Oui | Identite graphique de la pharmacie |

### 3.2 Regles de priorite des entrees
- Le contenu valide par le pharmacien est la source principale.
- L'identite graphique de la pharmacie est appliquee au document.

Aucune autre source de donnees n'est autorisee.

---

## 4. Pre-conditions d'execution
Le skill ne doit pas s'executer si :
- Le parametrage initial n'est pas disponible.
- Les entrees principales ne sont pas disponibles.

---

## 5. Regles IA strictes (conformes PRD)

- Aucune information ne doit etre inventee ou ajoutee au contenu valide.
- La structure du document est conforme au bilan.
- L'identite graphique de la pharmacie est integree.

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
- Autre (a preciser) : document PDF

### 7.2 Schema de sortie
- Documents PDF attendus dans `output/` :
- `output/BDS_<numero_session>.pdf` (bilan)
- `output/PAC_<numero_session>.pdf` (plan d'actions)

---

## 8. Cas limites et comportements attendus

| Situation | Comportement attendu |
|---------|----------------------|
| Echec de generation d'un PDF attendu | Document concerne non cree |
| PDF non genere ou illisible. | Signalement explicite sans extrapolation |
| Entree obligatoire absente | Blocage |
| Information contradictoire | Signalement sans arbitrage |

---

## 9. Criteres d'acceptation

Le skill est conforme si :
- Les documents PDF sont generes dans output/ avec le nommage contractuel.
- Le contenu est identique au contenu valide par le pharmacien.
- L'identite graphique est correctement integree.

Un seul critere non respecte rend le skill non conforme.

---

## 10. Post-conditions

Apres execution :
- Les documents PDF sont disponibles dans output/.
- En cas d'echec, le document concerne est marque 'non cree'.

---

## 11. Hors perimetre
- Diagnostic medical.
- Prescription.
- Decision clinique.
- Interpretation medicale avancee.
