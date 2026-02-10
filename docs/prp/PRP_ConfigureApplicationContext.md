# PRP - Product / Prompt Requirements Plan

## 0. Metadonnees
- Nom du skill : ConfigureApplicationContext
- Reference PRD : PRD V1 PRD 3  Etape 1; PRD 5.3; PRD 6
- Version : V1
- Statut : draft
- Dependances (autres skills ou donnees) : Voir /docs/skills/skills.md

---

## 1. Intention (obligatoire - 1 phrase)
Parametrer lapplication pour une pharmacie (identite, habillage, fournisseur IA et cle API obligatoire).

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
| Identite de la pharmacie | texte | Oui | Identite de la pharmacie (logo, coordonnees, en-tete/pied de page) |
| Choix du fournisseur IA | non specifie | Oui | Choix du fournisseur IA |
| Cle API obligatoire | non specifie | Oui | Cle API obligatoire |

### 3.2 Regles de priorite des entrees
- Les entrees de parametrage sont independantes des sessions patient.
- Aucune donnee patient n'est impliquee.

Aucune autre source de donnees n'est autorisee.

---

## 4. Pre-conditions d'execution
Le skill ne doit pas s'executer si :
- Le parametrage initial n'est pas disponible.
- Les entrees principales ne sont pas disponibles.

---

## 5. Regles IA strictes (conformes PRD)

- Aucune donnee patient ne doit etre manipulee.
- La cle API est obligatoire pour valider le parametrage.
- Le parametrage est modifiable a tout moment.
- Les donnees de parametrage sont persistantes et independantes des sessions.

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
- Autre (a preciser) : donnees de parametrage applicatif

### 7.2 Schema de sortie
- Donnees de parametrage applicatif enregistrees (identite pharmacie, informations de contact, fournisseur IA, cle API).
- Stockage persistant dans config/.

---

## 8. Cas limites et comportements attendus

| Situation | Comportement attendu |
|---------|----------------------|
| Cle API manquante ou invalide. | Signalement explicite sans extrapolation |
| Entree obligatoire absente | Blocage |
| Information contradictoire | Signalement sans arbitrage |

---

## 9. Criteres d'acceptation

Le skill est conforme si :
- Toutes les donnees de parametrage obligatoires sont presentes.
- La cle API est valide.
- Le parametrage est enregistre et accessible par les modules de generation documentaire.

Un seul critere non respecte rend le skill non conforme.

---

## 10. Post-conditions

Apres execution :
- Les donnees de parametrage sont enregistrees de facon persistante dans config/.
- Le parametrage est accessible par les modules de generation documentaire.
- Aucune donnee patient n'est creee.

---

## 11. Hors perimetre
- Diagnostic medical.
- Prescription.
- Decision clinique.
- Interpretation medicale avancee.
