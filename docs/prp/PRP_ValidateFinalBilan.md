# PRP - Product / Prompt Requirements Plan

## 0. Metadonnees
- Nom du skill : ValidateFinalBilan
- Reference PRD : PRD V1 PRD 5.1-5.2; PRD 5.3; PRD 6
- Version : V1
- Statut : draft
- Dependances (autres skills ou donnees) : Voir /docs/skills/skills.md

---

## 1. Intention (obligatoire - 1 phrase)
Permettre la validation finale par le pharmacien avant export.

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
| Bilan et plan dactions assembles | non specifie | Oui | Bilan et plan dactions assembles |

### 3.2 Regles de priorite des entrees
- Le bilan et le plan d'actions assembles sont la seule entree.
- Le pharmacien relit, ajuste et valide le contenu final.

Aucune autre source de donnees n'est autorisee.

---

## 4. Pre-conditions d'execution
Le skill ne doit pas s'executer si :
- Les entrees principales ne sont pas disponibles.

---

## 5. Regles IA strictes (conformes PRD)

- Le pharmacien valide systematiquement avant export.
- Le pharmacien est maitre du contenu final.
- Aucune modification automatique du contenu apres validation.

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
- Autre (a preciser) : documents DOCX/PDF

### 7.2 Schema de sortie
- Contenu valide pour generation DOCX/PDF
- Documents attendus apres validation :
- `output/BDS_<numero_session>.docx`
- `output/PAC_<numero_session>.docx`
- `output/BDS_<numero_session>.pdf`
- `output/PAC_<numero_session>.pdf`

---

## 8. Cas limites et comportements attendus

| Situation | Comportement attendu |
|---------|----------------------|
| Validation non realisee. | Signalement explicite sans extrapolation |
| Echec de generation d'un document attendu | Document concerne non cree |
| Entree obligatoire absente | Blocage |
| Information contradictoire | Signalement sans arbitrage |

---

## 9. Criteres d'acceptation

Le skill est conforme si :
- Le bilan et le plan d'actions ont ete relus et valides par le pharmacien.
- Le contenu valide est pret pour la generation documentaire.
- Le format de sortie est strictement respecte.

Un seul critere non respecte rend le skill non conforme.

---

## 10. Post-conditions

Apres execution :
- Le contenu est valide et pret pour la generation des 4 documents attendus.
- La generation documentaire peut etre lancee.

---

## 11. Hors perimetre
- Diagnostic medical.
- Prescription.
- Decision clinique.
- Interpretation medicale avancee.
