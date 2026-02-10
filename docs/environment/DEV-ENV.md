# Environnement de developpement

## 1. Objectifs de l'environnement DEV
- Permettre l'implementation des modules PRP dans l'ordre du parcours sequentiel en 9 etapes.
- Permettre le flux complet officine + tablette, incluant l'acces questionnaire par page web locale via QR code signe.
- Garantir la conformite contractuelle: transcript valide comme source de verite, validation pharmacien obligatoire, aucune donnee inventee.
- Travailler en local sur les donnees de session et les sorties documentaires, conformement au PRD.

## 2. Pre-requis machine
- Poste de developpement (Windows/macOS/Linux) avec droits lecture/ecriture sur le depot.
- Une tablette (ou smartphone de test) avec navigateur moderne et camera pour le scan QR.
- Reseau local partage entre poste de dev et tablette pour exposer la page web questionnaire.
- Microphone fonctionnel sur le poste de dev pour les modules lies a l'audio/transcription.
- Acces Internet uniquement pour les etapes necessitant le fournisseur IA et sa cle API.

## 3. Outils et versions recommandees

### 3.1 Outils de base

| Outil | Version recommandee | Usage DEV |
|---|---|---|
| Git | 2.40+ | Versionner les modules, contrats et docs |
| Python | 3.11.x | Runtime principal pour implementer les modules et tests |
| pip | version liee a Python 3.11 | Installation des dependances de dev |
| venv | stdlib Python | Isolation de l'environnement de dev |
| pytest | derniere stable | Tests contractuels par module (remplace unittest) |
| Navigateur tablette | Stable recente | Validation du flux QR -> page questionnaire |

### 3.2 Architecture applicative retenue

L'application se compose de deux processus distincts:

- **Application desktop native** (CustomTkinter): interface pharmacien officine (stepper 9 etapes, formulaires, validation, visualisation bilan). Lancee sur le poste du pharmacien.
- **Serveur web local** (Flask): sert la page questionnaire sur tablette via le reseau local. Le pharmacien n'utilise pas le navigateur pour l'interface officine.

Communication entre les deux:

- Le desktop et le serveur Flask partagent le meme stockage local (`data/`, `config/`, `output/`).
- Le serveur Flask expose uniquement la page questionnaire (lecture session + ecriture reponses).
- Le desktop pilote le cycle de vie de la session et declenche la logique metier.

### 3.3 Dependances Python externes

| Bibliotheque | Usage | Module(s) concerne(s) |
|---|---|---|
| customtkinter | Interface desktop native officine | apps/desktop/* |
| flask | Serveur web local pour page questionnaire tablette | apps/api (route tablette) |
| python-docx | Generation des documents DOCX | Module H (GenerateDOCXDocument) |
| weasyprint | Generation des documents PDF depuis templates HTML/CSS | Module H (GeneratePDFDocument) |
| qrcode | Generation de QR codes | Module C (GenerateSessionQRCode) |
| Pillow | Manipulation images (QR, logo pharmacie) | Modules A, C |
| sounddevice | Enregistrement audio de l'entretien | Module E (RecordInterviewAudio) |
| requests | Appels HTTP vers le fournisseur IA (transcription, generation) | Modules F, G |

Strategie de generation documentaire retenue:

- Le skill `AssembleBilanForValidation` (Module G) produit un objet de bilan structure (source unique de contenu).
- Le skill `GenerateDOCXDocument` rend cet objet en DOCX via `python-docx`.
- Le skill `GeneratePDFDocument` rend ce meme objet en PDF via `weasyprint` (template HTML/CSS).
- Deux templates distincts (DOCX et HTML/CSS), mais une seule source de donnees. Pas de dependance a LibreOffice ou Word.

### 3.4 Notes de cadrage

- Aucun outil de production (orchestration, observabilite avancee, CI/CD prod) n'est requis pour demarrer.
- Les dependances listees en 3.3 sont le minimum necessaire pour couvrir les exigences du PRD. Ne pas ajouter de dependances supplementaires sans justification contractuelle.

## 4. Structure du projet en DEV
- `apps/api/modules/`: implementation metier par module (A a I), alignee sur les PRP.
- `apps/desktop/`: interfaces de parcours officine et acces tablette.
- `packages/core/`: modeles metier et contraintes transverses.
- `packages/schemas/`: schemas contractuels de donnees.
- `packages/prompts/`: artefacts de prompts contractuels.
- `config/`: donnees de parametrage applicatif persistantes (identite pharmacie, fournisseur IA, cle API). Non purgees avec les sessions.
- `data/`: stockage local temporaire des donnees de session (purgees en fin d'etape 9).
- `output/`: sorties documentaires attendues (`BDS_*` et `PAC_*` en DOCX/PDF).
- `docs/`: PRD, architecture, PRP et contrats de reference.

Regle de structure:
- Conserver strictement l'arborescence validee.
- Implementer les modules sans modifier les contrats existants (`PRD`, `ARCHITECTURE`, `PRP`, `CONTRACT`, `INTERFACE`).

## 5. Lancement et arret de l'application en DEV

Sequence de demarrage DEV:

1. Activer l'environnement Python local (`venv`).
2. Installer les dependances: `pip install -r requirements.txt`.
3. Lancer le serveur Flask (page questionnaire tablette): `python -m apps.api.server` (ecoute sur le reseau local, port configurable).
4. Lancer l'application desktop officine: `python -m apps.desktop.main` (fenetre CustomTkinter).
5. Verifier que la tablette atteint la page questionnaire via le lien local issu du QR signe.

Sequence d'arret DEV:

1. Fermer la fenetre desktop (arrete l'application officine).
2. Arreter le serveur Flask (Ctrl+C ou signal).
3. Conserver/supprimer les donnees de session selon les regles de fin d'etape 9.

Validation minimale au demarrage:

1. Executer les tests: `pytest`.
2. Verifier le scenario QR -> ouverture page tablette -> rattachement session.
3. Verifier le scenario validation finale -> generation `output/` -> purge de session.

## 6. Perimetre DEV (ce qui est inclus / exclu)
Inclus:
- Implementation de tous les modules PRP en environnement local.
- Flux tablette via page web locale et QR signe.
- Stockage local temporaire des sessions.
- Generation locale des documents de sortie.

Exclus:
- Deploiement production.
- Scalabilite, haute disponibilite, tolerance de panne avancee.
- Outillage de securite/operations production.
- Optimisations non justifiees par les contrats actuels.

## 7. Points ouverts

- Support exact de persistance locale (fichiers vs base embarquee), non impose par les contrats.
- Gestion de la cle utilisee pour `sig` (QR/HMAC), cycle de vie non detaille.
- Format de restitution detaille des erreurs d'export documentaire.
- Exigence offline stricte sur l'ensemble du parcours, non tranchee explicitement.

Points resolus:

- Regle de cloture/purge: pas de purge tant que les 4 documents attendus ne sont pas generes. Session active pour relance en cas d'echec.
- Type d'application: desktop natif CustomTkinter + serveur Flask pour la tablette.
- Framework de test: pytest.
- Enregistrement audio: sounddevice.
- Generation PDF: deux renderers independants (python-docx pour DOCX, weasyprint pour PDF) depuis le meme objet de bilan structure. Pas de dependance a LibreOffice/Word.

## 8. Cadrage UI/UX en DEV
Objectif ergonomique:
- Rendre le parcours utilisable rapidement par un pharmacien (temps contraint) et simple pour le patient sur tablette.

Principes UI/UX a appliquer en DEV:
- Respecter l'ordre sequentiel des 9 etapes dans l'interface, sans acces direct aux etapes futures non valides.
- Afficher des actions explicites de validation par le pharmacien aux etapes critiques (validation transcript, validation finale).
- Limiter les champs a ceux imposes par les contrats, sans ajouter de saisies non necessaires.
- Afficher des messages d'erreur bloquants clairs pour les donnees obligatoires manquantes.
- Distinguer visuellement le parcours officine et le parcours tablette pour eviter les confusions d'usage.
- Sur tablette, proposer une page questionnaire epuree, lisible, avec grands controles tactiles.
- Montrer l'etat de session (active, en cours, cloturee) de maniere visible cote officine.
- Rendre visibles les statuts de generation documentaire, incluant le cas "non cree".

Perimetre UX inclus en DEV:
- Navigation de base entre ecrans/modules.
- Feedback utilisateur immediate (succes, erreur, blocage).
- Lisibilite mobile/tablette pour la saisie questionnaire.

Perimetre UX exclu en DEV:
- Design system avance.
- Optimisations graphiques non necessaires au flux contractuel.
- Personnalisation visuelle poussee hors identite pharmacie deja prevue au PRD.

## 9. Structure graphique de l'interface en DEV

### 9.1 Ecran officine - layout global (CustomTkinter)

L'interface officine est une fenetre desktop native (CustomTkinter), organisee comme suit:

- Zone haute fixe (Frame):
  - logo pharmacie (si configure),
  - nom de la pharmacie,
  - session courante (ID + statut).
- Colonne gauche fixe (Frame): menu principal / navigation entre modules.
- Zone centrale (Frame scrollable): contenu de l'ecran actif (formulaires, visualisation bilan, transcript).
- Colonne droite ou bandeau haut (Frame): progression de session en 9 etapes (stepper visuel).
- Barre d'actions basse fixe (Frame): `Enregistrer`, `Valider`, `Etape suivante`, `Annuler`.

Justification:

- Parcours sequentiel obligatoire en 9 etapes (PRD + architecture).
- Validation pharmacien obligatoire sur etapes critiques.
- Besoin de lisibilite et rapidite d'usage en officine.
- CustomTkinter fournit des widgets natifs modernes sans dependance lourde.

### 9.2 Menu de configuration (hors session patient)
Entree principale: `Configuration application` (module ApplicationContext)

- `Identite pharmacie` (nom, adresse, code postal, ville, telephone)
- `Logo et habillage` (logo, en-tete, pied de page)
- `Informations de contact optionnelles` (site web, Instagram, Facebook, X, LinkedIn)
- `Fournisseur IA`
- `Cle API`
- `Apercu des informations configurees`

Regles UX:
- Afficher les champs obligatoires en tete de formulaire.
- Bloquer la validation si champ obligatoire absent.
- Message explicite si cle API manquante/invalide.
- Aucun champ patient dans ce menu.

Justification:
- Etape 1 du PRD: parametrage initial, modifiable a tout moment, sans donnees patient.

### 9.3 Suite d'etapes par session (stepper obligatoire)
Le stepper affiche les 9 etapes avec un statut visuel:
- `A faire`
- `En cours`
- `Validee`
- `Bloquee`

Etapes affichees:
1. Parametrage initial (reference)
2. Questionnaire par tranche d'age
3. Initialisation session
4. QR code et acces tablette
5. Reponses questionnaire
6. Entretien officinal
7. Transcription et validation
8. Generation bilan/plan
9. Validation finale, export, purge

Regles UX:
- L'etape `n+1` est inaccessible tant que `n` n'est pas validee si la regle contractuelle l'impose.
- Les etapes 7 et 9 exigent une action explicite de validation pharmacien.
- Afficher les blocages de facon actionnable (champ manquant, precondition absente, document non cree).

Justification:
- Sequentialite stricte, controle pharmacien et tracabilite imposes par PRD/architecture.

### 9.4 Ecran tablette - page questionnaire web (Flask + HTML/CSS)

- Ecran epure plein format, sans navigation technique.
- Affichage du questionnaire lie a la session active uniquement.
- Gros boutons tactiles, contraste lisible, progression question par question ou par section.
- Confirmation claire de soumission (etat transmis a la session).

Regles UX:
- Pas de menu configuration ni options hors questionnaire.
- Pas d'acces a d'autres sessions.
- Pas de donnees medicales interpretees ou de contenu hors perimetre questionnaire.

Justification:
- Etapes 4 et 5 du PRD: acces isole par session via QR, sans compte patient.

### 9.5 Etats visuels minimum a couvrir en DEV
- `Initial` (aucune session ouverte)
- `Session active`
- `Attente validation pharmacien`
- `Generation en cours`
- `Export termine`
- `Erreur bloquante`
- `Session cloturee/purgee`

Objectif:
- Rendre l'etat courant evident a tout moment pour limiter les erreurs d'usage.
