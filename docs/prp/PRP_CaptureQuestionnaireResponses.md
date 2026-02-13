# PRP - Product / Prompt Requirements Plan

## 0. Metadonnees
- Nom du skill : CaptureQuestionnaireResponses
- Reference PRD : PRD V1 PRD 3 Etape 5 / 4.2 / 4.4; PRD 6
- Version : V4
- Statut : implemented
- Dependances (autres skills ou donnees) :
  - ServeQuestionnaireOnTablet (page questionnaire chargee sur tablette, route `POST /questionnaire/submit`)
  - InitializeInterviewSession (session cible active)
  - BuildQuestionnaireSummarySection (affichage questions/reponses sur le PC apres reception des reponses)

---

## 1. Intention (obligatoire - 1 phrase)
Enregistrer les reponses envoyees depuis la page web tablette, avec horodatage, et les rendre disponibles dans l'application officine pour la session cible.

---

## 2. Perimetre fonctionnel

### 2.1 Ce que le skill FAIT
- Recevoir la soumission des reponses depuis la page web questionnaire.
- Verifier la coherence entre `sid`, session active et questionnaire cible.
- Enregistrer localement les reponses structurees avec horodatage dans les donnees de session.
- Rendre les reponses immediatement lisibles par l'application officine pour la session en cours.
- Mettre a jour sur le PC (meme ecran que le QR code) le statut questionnaire a `Termine` (vert, 20pt, a droite du QR code) lorsque le fichier de reponses est disponible.
- Declencher la construction du fichier `data/session/QuestionnaireComplet_[Num Session].md` et l'affichage questions/reponses sur le PC a la suite du QR code.
- Produire les sorties decrites en section 7.
- Appliquer les regles et contraintes du PRD.

### 2.2 Ce que le skill NE FAIT PAS
- Inventer des informations.
- Utiliser des sources externes non prevues par le PRD.
- Produire un diagnostic, une prescription ou une decision clinique.
- Interpreter ou reformuler les reponses patient.

---

## 3. Entrees autorisees (contractuelles)

### 3.1 Entrees principales
| Champ | Type | Obligatoire | Description |
|------|------|------------|-------------|
| Identifiant de session (`sid`) | texte | Oui | Identifiant de la session cible |
| Reponses structurees au questionnaire | donnees structurees | Oui | Reponses structurees soumises depuis la tablette |
| Horodatage de soumission | date-heure | Oui | Horodatage associe a la soumission des reponses |

### 3.2 Regles de priorite des entrees
- Les reponses sont un support contextuel sans valeur decisionnelle autonome.
- L'identifiant de session est obligatoire pour le rattachement.
- Chaque reponse doit etre rattachee a un identifiant de question.

Aucune autre source de donnees n'est autorisee.

---

## 4. Pre-conditions d'execution
Le skill ne doit pas s'executer si :
- La session n'est pas active.
- Le questionnaire de la session n'a pas ete charge via ServeQuestionnaireOnTablet.
- Les entrees principales ne sont pas disponibles.

---

## 5. Regles IA strictes (conformes PRD)

- Les reponses sont enregistrees telles quelles, sans interpretation ni analyse.
- Les donnees sont stockees localement et temporairement.
- Aucune reecriture automatique des reponses.
- Les reponses restent strictement rattachees au `sid` de la session cible.

Ces regles sont imperatives et prioritaires.

---

## 6. Traitement attendu (logique fonctionnelle)

Etapes logiques :
1. Recevoir la soumission des reponses via `POST /questionnaire/submit` (JSON : `{sid, submitted_at, responses}`).
2. Verifier que le `sid` correspond a une session existante et active dans `data/sessions/<sid>.json`.
3. Valider la structure des reponses : chaque reponse doit contenir `question_id` et `value` (`validate_responses()`).
4. Si `submitted_at` est absent, generer l'horodatage courant (`datetime.now().isoformat()`).
5. Construire le record : `{session_id, submitted_at, responses_count, responses}`.
6. Persister le record dans `data/sessions/<sid>_responses.json` (JSON, UTF-8).
7. Mettre a jour le statut questionnaire PC a `Termine` (vert, 20pt, a droite du QR code) car le fichier de reponses est disponible.
8. Declencher `BuildQuestionnaireSummarySection` pour afficher la liste questions/reponses et les zones markdown pharmacien sur le PC.
9. Retourner le record persiste pour confirmation.
10. Les reponses sont immediatement lisibles par l'application officine via `load_responses(sid)`.

---

## 7. Sorties attendues

### 7.1 Type de sortie
- JSON structure

### 7.2 Schema de sortie
- `session_id` : identifiant de session cible
- `submitted_at` : horodatage de soumission
- `responses` : reponses structurees enregistrees et liees a la session
- `responses_count` : nombre de reponses enregistrees
- Etat questionnaire UI (ecran PC QR code) :
  - `status_label` : `Termine`
  - `status_color` : `Vert`
  - `status_font_size_pt` : `20`
  - `status_position` : `a droite du QR code`
- Declencheur d'affichage questionnaire PC :
  - `questionnaire_view_triggered` : `true` apres creation du fichier `data/sessions/<sid>_responses.json`

---

## 8. Cas limites et comportements attendus

| Situation | Comportement attendu |
|---------|----------------------|
| Session inconnue ou inactive | Blocage |
| Questionnaire incomplet ou interrompu | Signalement explicite sans extrapolation |
| Entree obligatoire absente | Blocage |
| Reponse sans identifiant de question | Blocage |
| Information contradictoire | Signalement sans arbitrage |

---

## 9. Criteres d'acceptation

Le skill est conforme si :
- Toutes les reponses sont correctement rattachees a la session.
- L'horodatage est present pour chaque reponse.
- Le format de sortie est strictement respecte.
- Les reponses sont consultables dans l'application officine pour la session en cours.
- Le statut PC passe a `Termine` (vert, 20pt, a droite du QR code) lorsque le fichier reponses existe.
- Le workflow d'affichage questions/reponses sur PC est declenche automatiquement.

Un seul critere non respecte rend le skill non conforme.

---

## 10. Post-conditions

Apres execution :
- Les reponses sont persistees dans `data/sessions/<sid>_responses.json`.
- Les reponses sont lisibles via `load_responses(sid)` pour les modules de construction du bilan.
- En cas de fichier corrompu ou absent, `load_responses()` retourne `None` (pas d'exception).
- Le statut questionnaire sur le PC est `Termine` (vert, 20pt) a droite du QR code.
- L'affichage questions/reponses est declenche sur le PC a la suite du QR code.
- Aucune interpretation n'a ete realisee.

---

## 11. Hors perimetre
- Diagnostic medical.
- Prescription.
- Decision clinique.
- Interpretation medicale avancee.
