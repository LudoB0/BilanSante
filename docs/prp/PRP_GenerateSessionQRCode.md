# PRP - Product / Prompt Requirements Plan

## 0. Metadonnees
- Nom du skill : GenerateSessionQRCode
- Reference PRD : PRD V1 PRD 3 Etape 4 / 4.4-4.6; PRD 6
- Version : V4
- Statut : implemented
- Dependances (autres skills ou donnees) :
  - InitializeInterviewSession (session active creee apres clic sur "Demarrer l'entretien")
  - ServeQuestionnaireOnTablet (consommation du payload QR code)

---

## 1. Intention (obligatoire - 1 phrase)
Generer et afficher le QRCode de session dans le meme ecran, immediatement apres le clic sur "Demarrer l'entretien", puis afficher a sa droite le statut questionnaire "Disponible" en rouge (20pt).

---

## 2. Perimetre fonctionnel

### 2.1 Ce que le skill FAIT
- S'executer uniquement apres la creation d'une session active par InitializeInterviewSession.
- Construire un payload QR code signe pour l'acces web au questionnaire de la session.
- Afficher le QR code dans la meme interface que celle qui a servi a demarrer l'entretien.
- Initialiser et afficher le statut questionnaire a droite du QR code: `Disponible` (couleur rouge, taille 20pt).
- Produire les sorties decrites en section 7.
- Appliquer les regles et contraintes du PRD.

### 2.2 Ce que le skill NE FAIT PAS
- Inventer des informations.
- Utiliser des sources externes non prevues par le PRD.
- Produire un diagnostic, une prescription ou une decision clinique.
- Capturer les reponses du questionnaire (skill separe).

---

## 3. Entrees autorisees (contractuelles)

### 3.1 Entrees principales
| Champ | Type | Obligatoire | Description |
|------|------|------------|-------------|
| Identifiant de session | texte | Oui | Identifiant de session active creee par InitializeInterviewSession |
| URL de base questionnaire web | texte | Auto-detectee | Detectee automatiquement a partir de l'adresse IP locale du poste (pas localhost). Peut etre surchargee si necessaire. |
| Version du format (`v`) | entier | Oui | Version du payload QRCode (valeur attendue: `1`). |
| Token opaque (`t`) | texte | Auto-genere | Token non devinable genere via `secrets.token_urlsafe(32)`. |
| Signature (`sig`) | texte | Auto-generee | Signature HMAC-SHA256 calculee sur les champs du payload. |
| Secret HMAC | texte | Auto-genere | Secret stocke dans `config/qr_secret.key`, cree automatiquement au premier usage via `secrets.token_hex(32)`. |

### 3.2 Regles de priorite des entrees
- L'identifiant de session est la seule entree explicite requise.
- L'URL de base est auto-detectee via `get_local_ip()` (detection UDP de l'IP LAN du poste, pas `localhost`).
- Le token, la signature et le secret sont generes automatiquement par le service.
- Le format du payload doit respecter le schema contractuel.

Aucune autre source de donnees n'est autorisee.

---

## 4. Pre-conditions d'execution
Le skill ne doit pas s'executer si :
- Le clic "Demarrer l'entretien" n'a pas encore cree de session.
- La session n'est pas active.
- Les entrees principales ne sont pas disponibles.

---

## 5. Regles IA strictes (conformes PRD)

- Le payload QRCode doit etre signe par HMAC-SHA256 (`hmac.new` avec `hashlib.sha256`) pour eviter la falsification.
- Le secret HMAC est stocke dans `config/qr_secret.key` et genere automatiquement au premier usage via `secrets.token_hex(32)`.
- Le token doit etre opaque et non devinable, genere via `secrets.token_urlsafe(32)`.
- Le message signe est la concatenation `v=1&sid=<session_id>&t=<token>`.
- Le payload doit cibler une page web de questionnaire et transporter les champs `v`, `sid`, `t`, `sig`.
- Le format du payload est strictement : `<questionnaire_base_url>?v=1&sid=<session_id>&t=<token>&sig=<signature>`.
- L'URL de base utilise l'adresse IP locale du poste (detectee automatiquement), jamais `localhost`, car la tablette est un appareil distant sur le meme reseau local.

Ces regles sont imperatives et prioritaires.

---

## 6. Traitement attendu (logique fonctionnelle)

Etapes logiques :
1. Detecter que la session vient d'etre creee apres clic sur "Demarrer l'entretien".
2. Verifier les pre-conditions (session active).
3. Demarrer le mini serveur web local (Flask) en thread daemon si pas deja demarre (`host="0.0.0.0"`, port 5000). Le serveur ecoute sur toutes les interfaces reseau pour etre accessible depuis la tablette.
4. Detecter l'adresse IP locale du poste via `get_local_ip()` (socket UDP, pas `localhost`).
5. Charger ou creer le secret HMAC depuis `config/qr_secret.key`.
6. Generer le token opaque via `secrets.token_urlsafe(32)`.
7. Calculer la signature HMAC-SHA256 sur `v=1&sid=<session_id>&t=<token>`.
8. Construire l'URL web signee : `http://<ip_locale>:5000/questionnaire?v=1&sid=...&t=...&sig=...`.
9. Generer le QR code a partir du payload (bibliotheque `qrcode`).
10. Afficher le QR code dans le meme ecran (sans changer d'interface).
11. Le serveur web est pret a recevoir le scan depuis la tablette.

---

## 7. Sorties attendues

### 7.1 Type de sortie
- Autre (a preciser) : QRCode de session

### 7.2 Schema de sortie
- Payload QRCode (string) : `<questionnaire_base_url>?v=1&sid=<session_id>&t=<token>&sig=<signature>`.
- Champs du payload : `v`, `sid`, `t`, `sig`.
- Etat d'affichage : QR code visible dans le meme ecran que l'initialisation de session.
- Etat questionnaire UI :
  - `status_label` : `Disponible`
  - `status_color` : `Rouge`
  - `status_font_size_pt` : `20`
  - `status_position` : `a droite du QR code`

---

## 8. Cas limites et comportements attendus

| Situation | Comportement attendu |
|---------|----------------------|
| Clic "Demarrer l'entretien" non effectue | Blocage |
| Session inconnue ou inactive | Blocage |
| Detection IP locale echoue | Fallback sur `127.0.0.1` |
| QRCode invalide | Signalement explicite sans extrapolation |
| Signature/HMAC invalide | Blocage |
| Token opaque absent | Blocage |
| Entree obligatoire absente | Blocage |
| Serveur web deja demarre | Pas de second demarrage (idempotent) |

---

## 9. Criteres d'acceptation

Le skill est conforme si :
- Le payload QRCode respecte le format contractuel.
- La signature est valide et verifiable.
- Le token est opaque et non devinable.
- Le QR code est affiche dans la meme interface, sans ouverture d'un ecran separe.
- Le statut `Disponible` est visible a droite du QR code, en rouge, taille 20pt.
- Le scan depuis la tablette ouvre la page web du questionnaire de la session cible.

Un seul critere non respecte rend le skill non conforme.

---

## 10. Post-conditions

Apres execution :
- Le mini serveur web Flask est demarre en thread daemon sur `0.0.0.0:5000`.
- Le QRCode est genere et affiche dans le meme ecran de session.
- Le statut questionnaire est initialise a `Disponible` (rouge, 20pt) a droite du QR code.
- Le payload contient l'adresse IP locale du poste (pas `localhost`), accessible depuis la tablette sur le reseau local.
- Le payload est verifiable par le module d'acces tablette via HMAC-SHA256.
- Le pharmacien peut scanner le QR code avec sa tablette pour ouvrir la page web questionnaire, puis laisser le patient repondre.

---

## 11. Hors perimetre
- Diagnostic medical.
- Prescription.
- Decision clinique.
- Interpretation medicale avancee.
