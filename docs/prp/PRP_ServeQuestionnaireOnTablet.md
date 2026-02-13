# PRP - Product / Prompt Requirements Plan

## 0. Metadonnees
- Nom du skill : ServeQuestionnaireOnTablet
- Reference PRD : PRD V1 PRD 3 Etape 4 / 4.1-4.2 / 4.6; PRD 6
- Version : V6
- Statut : implemented
- Dependances (autres skills ou donnees) :
  - InitializeInterviewSession (session active deja creee avec `sex`)
  - GenerateSessionQRCode (payload QR code signe deja genere, serveur web demarre)
  - CreateQuestionnaireByAgeRange (questionnaire disponible par tranche d'age avec `sex_target`)
  - CaptureQuestionnaireResponses (persistance des reponses soumises)

---

## 1. Intention (obligatoire - 1 phrase)
Exposer un mini serveur web Flask local sur le reseau de la pharmacie (bind `0.0.0.0:5000`, demarre en thread daemon depuis l'application desktop) pour servir le questionnaire en HTML inline sur le navigateur tablette a partir du QR code signe, filtrer les questions selon `sex` et `sex_target`, puis permettre la soumission des reponses vers le module CaptureQuestionnaireResponses.

---

## 2. Perimetre fonctionnel

### 2.1 Ce que le skill FAIT
- Exposer un serveur Flask sur `0.0.0.0:5000` en thread daemon, accessible depuis la tablette sur le reseau local de la pharmacie.
- Route `GET /questionnaire` : valider les parametres `v`, `sid`, `t`, `sig` presents dans l'URL issue du QR code.
- Verifier la signature HMAC-SHA256 avant toute autre validation.
- Verifier que la session cible existe et est active.
- Charger `session.sex` (`H`/`F`) et determiner le questionnaire associe a la tranche d'age de la session.
- Afficher le questionnaire en HTML inline genere cote serveur (pas de template externe) avec les 5 types de questions supportes : `boolean`, `single_choice`, `multiple_choice`, `short_text`, `scale`.
- Filtrer les questions a afficher selon `sex_target` :
  - si `session.sex=H`, afficher seulement les questions `sex_target` `H` ou `M`
  - si `session.sex=F`, afficher seulement les questions `sex_target` `F` ou `M`
- Mettre a jour sur le PC (meme ecran que le QR code) le statut questionnaire a `En Cours` (orange, 20pt, a droite du QR code) des que la page questionnaire est chargee sur la tablette.
- Route `POST /questionnaire/submit` : recevoir les reponses au format JSON depuis la page web.
- Deleguer la persistance des reponses au module `CaptureQuestionnaireResponses` (`save_responses()`).
- Produire les sorties decrites en section 7.
- Appliquer les regles et contraintes du PRD.

### 2.2 Ce que le skill NE FAIT PAS
- Inventer des informations.
- Utiliser des sources externes non prevues par le PRD.
- Produire un diagnostic, une prescription ou une decision clinique.
- Interpretrer les reponses patient.
- Ecrire directement le fichier de reponses (delegue a CaptureQuestionnaireResponses).

---

## 3. Entrees autorisees (contractuelles)

### 3.1 Entrees principales
| Champ | Type | Obligatoire | Description |
|------|------|------------|-------------|
| URL de base questionnaire web locale (`questionnaire_base_url`) | texte | Oui | URL locale du mini serveur web expose sur le reseau de la pharmacie |
| URL de questionnaire signee | texte | Oui | URL du type `<questionnaire_base_url>?v=1&sid=<session_id>&t=<token>&sig=<signature>` |
| Identifiant de session (`sid`) | texte | Oui | Identifiant de la session cible transporte dans l'URL signee |
| Token opaque (`t`) | texte | Oui | Token anti-devinable associe a la session |
| Signature (`sig`) | texte | Oui | Signature/HMAC anti-falsification |
| Sexe de session (`session.sex`) | texte | Oui | Valeur `H` ou `F` stockee par InitializeInterviewSession |
| Questionnaire associe a la tranche d'age | donnees structurees | Oui | Questionnaire determine via la session et le referentiel |
| Ciblage sexe de question (`question.sex_target`) | texte | Oui | Valeur `H`, `F` ou `M` pour filtrer l'affichage tablette |
| Soumission des reponses (`responses`) | donnees structurees | Non (Oui lors de la soumission) | Donnees envoyees par le navigateur tablette vers l'endpoint de soumission |

### 3.2 Regles de priorite des entrees
- `questionnaire_base_url` doit pointer vers un service local atteignable depuis la tablette.
- Le payload QRCode doit etre valide (version, token, signature) pour autoriser l'acces.
- Le `sid` porte par l'URL signee est la source de verite pour cibler la session.
- Le questionnaire est determine exclusivement par la tranche d'age associee a la session.
- Le filtrage des questions est determine par `session.sex` (`H`/`F`) et `question.sex_target` (`H`/`F`/`M`).
- `responses` devient obligatoire uniquement lors de la soumission de la page web.

Aucune autre source de donnees n'est autorisee.

---

## 4. Pre-conditions d'execution
Le skill ne doit pas s'executer si :
- Le clic "Demarrer l'entretien" n'a pas cree de session active.
- Le serveur Flask n'est pas demarre (le demarrage est automatique via `GenerateSessionQRCode`, en thread daemon sur `0.0.0.0:5000`).
- La tablette n'est pas sur le meme reseau local que le poste pharmacien.
- La session n'est pas active.
- `session.sex` est absent ou hors `H`/`F`.
- Le questionnaire correspondant n'est pas disponible.
- Une question du questionnaire n'a pas `sex_target` ou a une valeur hors `H`/`F`/`M`.
- Le payload QRCode est invalide (version, token ou signature HMAC-SHA256).
- Les entrees principales ne sont pas disponibles.

---

## 5. Regles IA strictes (conformes PRD)

- L'acces au questionnaire est sans compte et isole par session.
- Le chargement n'est autorise que si le payload QRCode est valide.
- Aucune interpretation des reponses n'est realisee.
- La soumission des reponses doit etre routee vers CaptureQuestionnaireResponses.
- Le format de soumission doit rester structure et exploitable pour l'affichage questions/reponses sur le PC (question_id, type, value, horodatage).

Ces regles sont imperatives et prioritaires.

---

## 6. Traitement attendu (logique fonctionnelle)

Etapes logiques :
1. Le serveur Flask (demarre en thread daemon par `GenerateSessionQRCode`) recoit la requete `GET /questionnaire` issue du scan QR code sur la tablette.
2. Extraire et verifier `v`, `sid`, `t`, `sig` via `validate_qr_params()`.
3. Verifier la signature HMAC-SHA256 en priorite (avant le chargement de session).
4. Verifier que la session `sid` existe et est active.
5. Charger `session.sex` et valider qu'il vaut `H` ou `F`.
6. Charger le questionnaire associe a la tranche d'age de la session via `load_questionnaire_for_session()`.
7. Filtrer les questions selon `sex_target` :
   - `session.sex=H` -> conserver `sex_target` dans `H`, `M`
   - `session.sex=F` -> conserver `sex_target` dans `F`, `M`
8. Generer et servir la page HTML inline (responsive, CSS inline, JavaScript inline) avec le formulaire du questionnaire filtre. Les 5 types de questions sont rendus : `boolean` (radio Oui/Non), `single_choice` (radio), `multiple_choice` (checkboxes), `short_text` (textarea), `scale` (range slider).
9. Le nom de la pharmacie et l'identifiant de session sont injectes dans la page pour affichage et soumission.
10. A la soumission, le JavaScript envoie un `POST /questionnaire/submit` au format JSON `{sid, submitted_at, responses: [{question_id, type, value}]}`.
11. Le serveur delegue la persistance a `CaptureQuestionnaireResponses.save_responses()` qui ecrit `data/sessions/<sid>_responses.json`.
12. En cas de succes, la page affiche un message de confirmation. En cas d'erreur, le message d'erreur est affiche.

---

## 7. Sorties attendues

### 7.1 Type de sortie
- Autre (a preciser) : page web questionnaire affichee sur tablette

### 7.2 Schema de sortie
- `GET /questionnaire` : page HTML inline responsive avec le formulaire du questionnaire filtre selon `session.sex` et `question.sex_target`, servie uniquement si le payload respecte `http://<ip_locale>:5000/questionnaire?v=1&sid=<session_id>&t=<token>&sig=<signature>`.
- `GET /questionnaire` (erreur) : page HTML d'erreur avec message "Acces non autorise" (status 403) ou "Questionnaire non disponible" (status 404).
- `POST /questionnaire/submit` (succes) : JSON `{session_id, submitted_at, responses_count, responses}` (status 200).
- `POST /questionnaire/submit` (erreur) : JSON `{error: "<message>"}` (status 400).
- Le fichier de reponses est persiste dans `data/sessions/<sid>_responses.json` par CaptureQuestionnaireResponses.
- Etat questionnaire UI (ecran PC QR code) :
  - `status_label` : `En Cours`
  - `status_color` : `Orange`
  - `status_font_size_pt` : `20`
  - `status_position` : `a droite du QR code`

---

## 8. Cas limites et comportements attendus

| Situation | Comportement attendu |
|---------|----------------------|
| Mini serveur local indisponible | Blocage |
| Tablette hors reseau local pharmacie | Blocage |
| Acces direct sans parametres de securite (`v`, `sid`, `t`, `sig`) | Blocage |
| Session inconnue ou inactive | Blocage |
| `sid` de l'URL ne correspond a aucune session active | Blocage |
| `session.sex` absent ou invalide (`H`/`F` attendu) | Blocage |
| Questionnaire non disponible pour la tranche d'age de la session | Signalement explicite sans extrapolation |
| Question sans `sex_target` ou valeur hors `H`/`F`/`M` | Blocage |
| Signature/HMAC invalide dans le payload | Blocage |
| Token opaque absent ou invalide | Blocage |
| Soumission de reponses invalide (format non structure) | Blocage |
| Entree obligatoire absente | Blocage |

---

## 9. Criteres d'acceptation

Le skill est conforme si :
- Le questionnaire correspond a la tranche d'age de la session.
- Le payload QRCode a ete valide avant chargement.
- L'acces est isole par session.
- La page web du questionnaire est ouverte sur la tablette sans authentification compte.
- La page web est servie par le mini serveur local accessible depuis la tablette.
- Les questions affichees sur tablette respectent le filtrage sexe (`H` -> `H/M`, `F` -> `F/M`).
- La soumission est transmise vers CaptureQuestionnaireResponses en format structure exploitable.
- Le statut PC passe a `En Cours` (orange, 20pt, a droite du QR code) quand le questionnaire est charge sur la tablette.

Un seul critere non respecte rend le skill non conforme.

---

## 10. Post-conditions

Apres execution :
- Le questionnaire est affiche sur la tablette en HTML inline responsive et pret a la saisie patient.
- Le statut questionnaire du PC est `En Cours` (orange, 20pt) a droite du QR code.
- Le serveur Flask reste actif en thread daemon pendant toute la duree de l'application desktop.
- Les reponses soumises sont persistees dans `data/sessions/<sid>_responses.json` via CaptureQuestionnaireResponses.
- Le format de persistance est structure : `{session_id, submitted_at, responses_count, responses: [{question_id, type, value}]}`, exploitable pour la suite IA.

---

## 11. Hors perimetre
- Diagnostic medical.
- Prescription.
- Decision clinique.
- Interpretation medicale avancee.
