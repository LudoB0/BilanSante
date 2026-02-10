# PRP - Product / Prompt Requirements Plan

## 0. Metadonnees
- Nom du skill : PurgeSessionDataAfterExport
- Reference PRD : PRD V1 PRD 4.4 / 5.3; PRD 6
- Version : V1
- Statut : draft
- Dependances (autres skills ou donnees) : Voir /docs/skills/skills.md

---

## 1. Intention (obligatoire - 1 phrase)
Supprimer les donnees de session une fois les documents generes et valides.

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
| Identifiant de session | texte | Oui | Identifiant de session |
| Etat de validation et generation des documents | texte | Oui | Etat de validation et generation des documents |

### 3.2 Regles de priorite des entrees
- L'identifiant de session et l'etat de generation des documents sont les seules entrees.
- La purge est conditionnee a la creation des 4 documents attendus.

Aucune autre source de donnees n'est autorisee.

---

## 4. Pre-conditions d'execution
Le skill ne doit pas s'executer si :
- La session n'est pas active.
- Tous les documents attendus ne sont pas crees (`BDS_*.docx`, `PAC_*.docx`, `BDS_*.pdf`, `PAC_*.pdf`).
- Les entrees principales ne sont pas disponibles.

---

## 5. Regles IA strictes (conformes PRD)

- La suppression est automatique des que les 4 documents attendus sont generes et valides.
- Aucune duree de conservation par defaut.
- La purge couvre : questionnaire, transcript, metadonnees et audio.
- En cas d'echec d'un document, la session reste active pour relance. Pas de purge.

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
- Conformite de la suppression (donnees locales et temporaires)
- Suppression globale en fin d'etape 9 : questionnaire, transcript, metadonnees et audio.

---

## 8. Cas limites et comportements attendus

| Situation | Comportement attendu |
|---------|----------------------|
| Suppression prematuree avant generation des documents. | Signalement explicite sans extrapolation |
| Echec de generation d'un document attendu | Pas de purge; document concerne non cree |
| Validation finale non realisee | Pas de purge |
| Entree obligatoire absente | Blocage |

---

## 9. Criteres d'acceptation

Le skill est conforme si :
- Toutes les donnees de session sont supprimees (questionnaire, transcript, metadonnees, audio).
- La suppression n'intervient que si les 4 documents attendus sont crees.
- Aucune donnee de session ne persiste apres purge.

Un seul critere non respecte rend le skill non conforme.

---

## 10. Post-conditions

Apres execution :
- Toutes les donnees de la session sont supprimees.
- Seuls les documents finaux dans output/ subsistent.
- Les donnees de parametrage dans config/ ne sont pas affectees.

---

## 11. Hors perimetre
- Diagnostic medical.
- Prescription.
- Decision clinique.
- Interpretation medicale avancee.
