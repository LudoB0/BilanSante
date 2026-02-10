# PRP - Product / Prompt Requirements Plan

## 0. Metadonnees
- Nom du skill : ServeQuestionnaireOnTablet
- Reference PRD : PRD V1 PRD 3  Etape 4 / 4.1-4.2; PRD 5.1; PRD 6
- Version : V1
- Statut : draft
- Dependances (autres skills ou donnees) : Voir /docs/skills/skills.md

---

## 1. Intention (obligatoire - 1 phrase)
Charger automatiquement le bon questionnaire sur la tablette via le QRCode.

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
| Questionnaire associe a la tranche dage | valeur categorielle | Oui | Questionnaire associe a la tranche dage |
| Payload QRCode (`v`, `sid`, `t`, `sig`) | texte structure | Oui | Payload signe permettant de charger la session cible. |

### 3.2 Regles de priorite des entrees
- Le payload QRCode doit etre valide (version, token, signature) pour autoriser l'acces.
- Le questionnaire est determine par la tranche d'age associee a la session.

Aucune autre source de donnees n'est autorisee.

---

## 4. Pre-conditions d'execution
Le skill ne doit pas s'executer si :
- La session n'est pas active.
- Le questionnaire correspondant n'est pas disponible.
- Le payload QRCode est invalide (version, token ou signature).
- Les entrees principales ne sont pas disponibles.

---

## 5. Regles IA strictes (conformes PRD)

- L'acces au questionnaire est sans compte et isole par session.
- Le chargement n'est autorise que si le payload QRCode est valide.
- Aucune interpretation des reponses n'est realisee.

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
- Autre (a preciser) : questionnaire affiche sur tablette

### 7.2 Schema de sortie
- Questionnaire charge et accessible sur la tablette pour la session cible.
- Le chargement est autorise uniquement si le payload respecte : `bsp://session?v=1&sid=<session_id>&t=<token>&sig=<signature>`.

---

## 8. Cas limites et comportements attendus

| Situation | Comportement attendu |
|---------|----------------------|
| Questionnaire non disponible pour la tranche dage. | Signalement explicite sans extrapolation |
| Signature/HMAC invalide dans le payload | Blocage |
| Token opaque absent ou invalide | Blocage |
| Entree obligatoire absente | Blocage |

---

## 9. Criteres d'acceptation

Le skill est conforme si :
- Le questionnaire correspond a la tranche d'age de la session.
- Le payload QRCode a ete valide avant chargement.
- L'acces est isole par session.

Un seul critere non respecte rend le skill non conforme.

---

## 10. Post-conditions

Apres execution :
- Le questionnaire est affiche sur la tablette et pret a la saisie patient.
- Les reponses seront rattachees a la session via le module de capture.

---

## 11. Hors perimetre
- Diagnostic medical.
- Prescription.
- Decision clinique.
- Interpretation medicale avancee.
