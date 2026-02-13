# Interface d'implementation - bilan-assembly

## 1. Reference contractuelle
- PRP de reference : /docs/prp/PRP_BuildQuestionnaireSummarySection.md
- Version du PRP : V6

## 2. Responsabilite du module
Afficher sur le PC la vue questions/reponses du questionnaire, calculer l'IMC, afficher la zone tension et le rapport pharmacien, puis deleguer au clic `Demander a l'IA` la persistance des saisies et la transition vers `IdentifyVigilancePoints`.

## 3. Entrees attendues
- Champ: Identifiant de session
  - Type logique: texte
  - Obligatoire: Oui
  - Format/description: Numero de session cible
- Champ: Fichier de reponses de session
  - Type logique: fichier JSON
  - Obligatoire: Oui
  - Format/description: `data/sessions/<sid>_responses.json`
- Champ: Questionnaire source
  - Type logique: donnees structurees
  - Obligatoire: Oui
  - Format/description: Questions source pour associer chaque reponse a son libelle
- Champ: Saisie tension du pharmacien
  - Type logique: texte
  - Obligatoire: Non
  - Format/description: valeur libre (ex: `120/80`)
- Champ: Action utilisateur `Demander a l'IA`
  - Type logique: evenement UI
  - Obligatoire: Oui
  - Format/description: clic sur le bouton de transition

## 4. Sorties produites
- Type de sortie :
- Fichier markdown + affichage structure + declencheur de transition
- Structure logique / format attendu :
- Fichier markdown `data/sessions/QuestionnaireComplet_[short_id].md`
- Vue PC question/reponse a la suite du QR code
- Zone markdown a droite de chaque question
- Bloc `Mesures patient` (Poids, Taille, IMC) avant le rapport
- Zone markdown `Tension du patient (mmHg)` avant le rapport
- Zone markdown finale `Rapport du pharmacien`
- Bouton `Demander a l'IA` declenchant `CaptureInterviewTextNotes`

## 5. Preconditions
- Le fichier de reponses existe.
- Le questionnaire correspondant est disponible.
- Les entrees principales sont disponibles.

## 6. Postconditions
- Le fichier `data/sessions/QuestionnaireComplet_[short_id].md` est disponible.
- La vue questions/reponses est affichee sur le PC.
- Les zones markdown pharmacien sont disponibles (par question + `Tension du patient` + `Rapport du pharmacien`).
- Les mesures patient (poids, taille, IMC) sont affichees avant le rapport.
- Au clic `Demander a l'IA`, le flux est delegue a `CaptureInterviewTextNotes` puis `IdentifyVigilancePoints`.

## 7. Erreurs et cas d'echec
- Situation: Fichier de reponses absent
  - Comportement attendu: Blocage
- Situation: Questionnaire source absent
  - Comportement attendu: Blocage
- Situation: Entree obligatoire absente
  - Comportement attendu: Blocage
- Situation: Reponse manquante pour une question
  - Comportement attendu: Afficher `non renseigne`
- Situation: Poids ou taille absent/non numerique
  - Comportement attendu: `IMC: non calculable`
- Situation: Tension non saisie
  - Comportement attendu: Aucun blocage

## 8. Invariants
- Aucune information ne doit etre inventee.
- Aucune interpretation medicale, diagnostic ou prescription.
- Aucun appel API IA pour cette fonctionnalite.
- Les zones de saisie pharmacien acceptent du markdown.

## 9. Hors perimetre
- Diagnostic medical.
- Prescription.
- Decision clinique.
- Interpretation medicale avancee.
