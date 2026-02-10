# PRP - Product / Prompt Requirements Plan

## 0. Metadonnees
- Nom du skill : GenerateSessionQRCode
- Reference PRD : PRD V1 PRD 3  Etape 4 / 4.4; PRD 5.1-5.2; PRD 6
- Version : V1
- Statut : draft
- Dependances (autres skills ou donnees) : Voir /docs/skills/skills.md

---

## 1. Intention (obligatoire - 1 phrase)
Generer le QRCode de session pour acceder au questionnaire sur tablette.

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
| Version du format (`v`) | entier | Oui | Version du payload QRCode (valeur attendue: `1`). |
| Token opaque (`t`) | texte | Oui | Token non devinable associe a la session. |
| Signature (`sig`) | texte | Oui | Signature/HMAC anti-falsification. |

### 3.2 Regles de priorite des entrees
- L'identifiant de session, le token et la signature sont tous obligatoires.
- Le format du payload doit respecter le schema contractuel.

Aucune autre source de donnees n'est autorisee.

---

## 4. Pre-conditions d'execution
Le skill ne doit pas s'executer si :
- La session n'est pas active.
- Les entrees principales ne sont pas disponibles.

---

## 5. Regles IA strictes (conformes PRD)

- Le payload QRCode doit etre signe (HMAC/signature) pour eviter la falsification.
- Le token doit etre opaque et non devinable.
- Le format du payload est strictement : bsp://session?v=1&sid=<session_id>&t=<token>&sig=<signature>.

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
- Autre (a preciser) : QRCode de session

### 7.2 Schema de sortie
- Payload QRCode (string) : `bsp://session?v=1&sid=<session_id>&t=<token>&sig=<signature>`.
- Champs du payload : `v`, `sid`, `t`, `sig`.

---

## 8. Cas limites et comportements attendus

| Situation | Comportement attendu |
|---------|----------------------|
| QRCode invalide ou session inconnue. | Signalement explicite sans extrapolation |
| Signature/HMAC invalide | Blocage |
| Token opaque absent | Blocage |
| Entree obligatoire absente | Blocage |

---

## 9. Criteres d'acceptation

Le skill est conforme si :
- Le payload QRCode respecte le format contractuel.
- La signature est valide et verifiable.
- Le token est opaque et non devinable.

Un seul critere non respecte rend le skill non conforme.

---

## 10. Post-conditions

Apres execution :
- Le QRCode est genere et pret a etre affiche.
- Le payload est verifiable par le module d'acces tablette.

---

## 11. Hors perimetre
- Diagnostic medical.
- Prescription.
- Decision clinique.
- Interpretation medicale avancee.
