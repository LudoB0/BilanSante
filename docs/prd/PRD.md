# PRD – Outil de Bilan de Santé Prévention (V1)

Date : 07/02/2026 Version : V1 (alignée sur le schéma de fonctionnement étape par étape)

---

## 1. Objectif du produit

L’outil a pour objectif de permettre à un pharmacien d’officine de **générer automatiquement un document de bilan de santé prévention**, clair, structuré et directement exploitable, à partir :

- d’un **questionnaire préalable renseigné par le patient sur tablette**,
    
- d’un **entretien officinal conduit par le pharmacien**, enregistré ou saisi sous forme textuelle,
    
- d’un **processus de génération assistée par IA**, strictement encadré et validé par le pharmacien.
    

L’application suit un **schéma de fonctionnement séquentiel**, garantissant :

- la maîtrise humaine à chaque étape,
    
- la traçabilité des informations,
    
- l’absence totale d’informations inventées,
    
- un stockage **local et temporaire** des données patient.
    

---

## 2. Utilisateur cible

- Pharmacien d’officine
    
- Niveau technique : faible à intermédiaire
    
- Contraintes majeures :
    
    - temps limité par entretien (≈ 15–20 minutes),
        
    - responsabilité professionnelle engagée,
        
    - besoin de fiabilité, de lisibilité et de conformité.
        

Le pharmacien **reste décisionnaire et valideur final** du document remis au patient.

---

## 3. Schéma de fonctionnement global (étape par étape)

Le fonctionnement de l’application est organisé en **9 étapes successives**, exécutées dans un ordre strict.

### Étape 1 — Paramétrage initial de l’application

- Configuration de l'identité de la pharmacie (logo, coordonnées, en‑tête/pied de page).

- Informations de contact optionnelles (site web, réseaux sociaux : Instagram, Facebook, X, LinkedIn).

- Choix du fournisseur d'IA. Avec intégration d'une clé API obligatoire.

- Paramétrage réalisé une seule fois, modifiable à tout moment.

- Les données de paramétrage sont persistantes et indépendantes des sessions patient.

Aucune donnée patient n'est impliquée à ce stade.

---

### Étape 2 — Création des questionnaires par tranche d’âge

- Le pharmacien crée ou édite des questionnaires de prévention, chacun associé à une tranche d’âge.
    
- Les questionnaires sont composés de questions structurées (choix simples, multiples, texte court).
    
- Les questionnaires ne produisent aucune interprétation automatique.
    

---

### Étape 3 — Initialisation d'une session d'entretien (PC officine)

- L'écran d'initialisation affiche les informations de la pharmacie issues du paramétrage (logo, nom, adresse, code postal, ville) ainsi que les liens web non vides (site web, réseaux sociaux).

- Le pharmacien sélectionne la tranche d'âge du patient parmi les tranches d'âge disposant d'un questionnaire non vide.

- L'application crée une **session unique** identifiée par un ID (UUID), stockée dans `data/sessions/`.

- Le fichier de session contient l'identifiant, la tranche d'âge, la date/heure de création, le statut et une copie des coordonnées pharmacie (traçabilité).

- Cette session sert de lien entre questionnaire, entretien et génération du bilan.

- **Il n'existe aucune durée de session prédéfinie** : la session reste active tant que l'entretien n'est pas validé et que les documents ne sont pas générés.


Aucune donnée nominative n'est requise pour créer une session.

---

### Étape 4 — Mise à disposition du questionnaire sur tablette

- Après clic sur **"Démarrer l'entretien"** (Étape 3), l’application génère un **QRCode de session** dans la même interface.
- Le payload du QRCode est une URL web locale signée au format :
  `<questionnaire_base_url>?v=1&sid=<session_id>&t=<token>&sig=<signature>`.
- Champs obligatoires du payload :
  - `v` : version du format
  - `sid` : identifiant de session (UUID)
  - `t` : token opaque non devinable
  - `sig` : signature/HMAC anti-falsification
    
- Le pharmacien scanne le QRCode avec la tablette dédiée.
    
- La tablette ouvre automatiquement la page web du **bon questionnaire**, associé à la session en cours.
- Le patient remplit ensuite les questions sur cette page web.
- Sur l'écran PC (à droite du QR code), le statut questionnaire est affiché en taille 20 points :
  - `Disponible` (rouge) dès génération du QR code,
  - `En Cours` (orange) dès que le questionnaire est chargé sur la tablette.
    

Le questionnaire est accessible sans compte et isolé par session.

---

### Étape 5 — Remplissage du questionnaire par le patient

- Le patient complète le questionnaire de manière autonome (ou accompagné si nécessaire).
    
- Les réponses sont enregistrées localement et liées à l’ID de session.
- Dès que le fichier de réponses est disponible, le statut questionnaire sur le PC passe à `Terminé` (vert, 20 points, à droite du QR code).
- À ce moment, l'application génère un fichier markdown `data/session/QuestionnaireComplet_[Num Session].md` (questions + réponses associées).
- La liste des questions/réponses est affichée sur l'écran PC, à la suite du QR code, avec :
  - une zone de texte markdown à droite de chaque question (optionnelle),
  - une zone de texte markdown finale intitulée `Rapport du pharmacien`.
- Un bouton **« Envoyer à l'IA »** est affiché en dessous de la zone rapport, permettant au pharmacien de lancer la génération du bilan et du plan d'action.

- Aucune analyse clinique ni interprétation médicale n'est réalisée à ce stade.
    

---

### Étape 6 — Entretien officinal guidé

- Le pharmacien conduit l’entretien en s’appuyant sur les réponses du questionnaire et sur l’affichage questions/réponses avec ses notes markdown sur le PC.
    
- L’entretien peut être :
    
    - enregistré sous forme audio (avec consentement explicite),
        
    - saisi sous forme de notes textuelles,
        
    - ou une combinaison des deux.
        

Les métadonnées de l’entretien (date, durée, mode de recueil) sont automatiquement associées à la session.

---

### Étape 7 — Transcription et validation du contenu de l'entretien

- Si un enregistrement audio existe, il est transcrit automatiquement.

- Si l'entretien a été saisi uniquement sous forme de notes textuelles, celles-ci sont converties en transcript structuré avant validation.

- Le pharmacien relit, corrige et **valide le transcript**, qui devient la **source de vérité unique**.

- L'audio n'est pas supprimé à cette étape ; la suppression est globale en Étape 9.
    

---

### Étape 8 — Génération du bilan et du plan d’actions

- L’IA génère un brouillon de bilan structuré à partir :
    
    - du transcript validé (obligatoire),
        
    - des réponses au questionnaire (contexte uniquement).
        
- Chaque information et chaque action proposée sont explicitement traçables au transcript.
    
- Les informations absentes ou ambiguës sont signalées sans être complétées.
    

---

### Étape 9 — Validation finale et export des documents

- Le pharmacien relit, ajuste et valide le document final.
    
- L’application génère :
    
    - un document DOCX modifiable du bilan : `output/BDS_<numero_session>.docx`,
        
    - un document DOCX modifiable du plan d’action : `output/PAC_<numero_session>.docx`,
        
    - un PDF du bilan : `output/BDS_<numero_session>.pdf`,
        
    - un PDF du plan d’action : `output/PAC_<numero_session>.pdf`.
        

Les documents intègrent automatiquement l’identité graphique de la pharmacie.

**Une fois les 4 documents générés et validés, la session est automatiquement clôturée et l'ensemble des données associées à la session est supprimé** (questionnaire, transcript, métadonnées, et audio le cas échéant).

En cas d'échec de génération d'un document attendu, ce document est considéré **non créé**. La session reste active et le pharmacien peut relancer la génération du document en échec. La purge n'intervient que lorsque les 4 documents attendus ont été créés avec succès.

---

## 4. Données d’entrée du système

Les données d’entrée correspondent exclusivement aux informations collectées au cours d’une **session unique et éphémère**, nécessaires au fonctionnement de l’application.

### 4.1 Tranche d’âge du patient

- **Description** : tranche d’âge utilisée comme clé de sélection du questionnaire.
    
- **Format** : valeur catégorielle prédéfinie.
    
    - Exemple : `18–25`, `26–45`, `46–65`, `65+`
        
- **Source** : sélection par le pharmacien lors de l’initialisation de la session.
    

### 4.2 Réponses structurées au questionnaire

- **Description** : réponses déclaratives saisies par le patient sur tablette.
    
- **Format** : données structurées (clé / valeur).
    
    - Types possibles :
        
        - booléen (oui / non),
            
        - choix unique,
            
        - choix multiple (liste),
            
        - texte court libre.
            
- **Structure** :
    
    - identifiant de question,
        
    - type de question,
        
    - valeur saisie,
        
    - horodatage.
        
- **Rôle** : support contextuel pour la lecture de l’entretien, sans valeur décisionnelle autonome.
    

### 4.3 Transcript validé de l’entretien officinal

- **Description** : retranscription textuelle fidèle de l’échange entre le pharmacien et le patient.
    
- **Format** : texte structuré, relisible et éditable.
    
    - Optionnellement segmenté (paragraphes ou blocs horodatés).
        
- **Source** :
    
    - transcription automatique d’un enregistrement audio,
        
    - et/ou saisie manuelle du pharmacien.
        
- **Règle clé** :
    
    - le transcript validé constitue la **source de vérité unique** pour toute génération IA.
        

### 4.4 Métadonnées de session et d’entretien

- **Description** : informations techniques et contextuelles liées à la session.
    
- **Format** : données structurées.
    
    - identifiant de session,
        
    - date et heure de création de la session,
        
    - date de validation de l’entretien,
        
    - durée approximative de l’entretien (en minutes),
        
    - mode de recueil (audio, texte, mixte).
        
- **Rôle** : traçabilité et contexte, sans impact décisionnel.
    

### 4.5 Statut de consentement

- **Description** : information relative à l’accord du patient pour l’enregistrement audio.
    
- **Format** :
    
    - booléen (oui / non),
        
    - horodatage du recueil du consentement.
        
- **Règle** :
    
    - conditionne uniquement l’activation de l’enregistrement audio,
        
    - n’influence ni l’analyse ni les actions proposées.

### 4.6 Payload QRCode de session

- **Description** : charge utile transportée dans le QRCode de session.
    
- **Format** : chaîne de caractères (URL web locale signée) :
  `<questionnaire_base_url>?v=1&sid=<session_id>&t=<token>&sig=<signature>`.
    
- **Champs** :
    
    - `v` : version du format,
        
    - `sid` : identifiant de session (UUID),
        
    - `t` : token opaque non devinable,
        
    - `sig` : signature/HMAC anti-falsification.

### 4.7 Statut questionnaire (UI PC)

- **Description** : état visuel de progression du questionnaire affiché à droite du QR code.
    
- **Format** : énumération métier avec contraintes d'affichage.
    
    - `Disponible` : couleur rouge, taille 20 points (QR code généré),
        
    - `En Cours` : couleur orange, taille 20 points (questionnaire chargé sur tablette),
        
    - `Terminé` : couleur verte, taille 20 points (fichier réponses disponible).

### 4.8 Fichier markdown questionnaire complet

- **Description** : fichier de travail local contenant la liste complète questions/réponses du questionnaire de session.
    
- **Format** : fichier markdown `data/session/QuestionnaireComplet_[Num Session].md`.
    
- **Contenu minimal** :
    
    - identifiant de session,
        
    - liste complète des questions,
        
    - réponse associée pour chaque question,
        
    - emplacement de note markdown pharmacien par question,
        
    - section markdown finale `Rapport du pharmacien`.
        

Aucune donnée externe, aucun historique patient et aucune supposition ne sont utilisés par le système.

---

## 5. Sorties attendues

### 5.1 Bilan de santé prévention

- **Description** : document de synthèse destiné au patient, récapitulant le contexte de l’entretien et les points clés abordés.
    
- **Format logique** : texte structuré en sections.
    
    - Contexte de l’entretien
        
    - Synthèse des réponses
        
    - Points de vigilance identifiés
        
- **Caractéristiques** :
    
    - phrases courtes,
        
    - vocabulaire compréhensible par le patient,
        
    - aucune information non exprimée lors de l’entretien.
        

### 5.2 Plan d’actions personnalisées

- **Description** : liste d’actions de prévention proposées à l’issue de l’entretien.
    
- **Format logique** : données structurées.
    
    - intitulé de l’action,
        
    - justification issue du transcript,
        
    - niveau de priorité (faible / moyenne / élevée),
        
    - proposition de suivi,
        
    - élément de traçabilité (extrait ou repère du transcript).
        
- **Règle** : aucune action ne peut exister sans justification explicite.
    

### 5.3 Documents générés

- **DOCX** :
    
    - document modifiable,
        
    - fichiers attendus :
        
        - `output/BDS_<numero_session>.docx` (bilan),
            
        - `output/PAC_<numero_session>.docx` (plan d’action),
        
    - structure standardisée conforme au bilan,
        
    - intégration automatique de l’identité graphique de la pharmacie,
        
    - destiné à la relecture, l’ajustement et l’archivage local si besoin.
        
- **PDF** :
    
    - document figé,
        
    - fichiers attendus :
        
        - `output/BDS_<numero_session>.pdf` (bilan),
            
        - `output/PAC_<numero_session>.pdf` (plan d’action),
        
    - prêt à l’impression pour remise au patient,
        
    - utilisable pour export ou transmission manuelle (ex. LGO).
        

Les documents sont générés uniquement après validation explicite du pharmacien.

En cas d’échec de génération d’un document attendu, ce document est non créé.

### 5.4 Vue opérateur questionnaire (pré-entretien)

- **Description** : affichage lisible questions/réponses sur le PC après réception des réponses patient.
    
- **Source** : dérivée directement du fichier `data/session/QuestionnaireComplet_[Num Session].md` (sans appel API IA).
    
- **Usage** : support de conduite d'entretien en face à face, avec notes markdown optionnelles par question et zone `Rapport du pharmacien`.

---

## 6. Contraintes fonctionnelles majeures

- Aucune information ne doit être inventée.
    
- Aucune action sans justification explicite dans le transcript.
    
- Le pharmacien valide systématiquement avant export.
    
- Données stockées localement et de façon temporaire.
    
- **Aucune durée de conservation par défaut** : les données d'une session sont supprimées automatiquement dès que les 4 documents finaux ont été générés et validés. En cas d'échec de génération d'un document, la session reste active pour permettre une relance.
    

---

## 7. Hors périmètre

- Diagnostic médical.
    
- Prescription.
    
- Décision clinique.
    
- Interprétation médicale avancée.
    

---

## 8. Critères de succès (V1)

- Gain de temps perçu par le pharmacien.
    
- Document compréhensible sans reformulation.
    
- Traçabilité explicite des actions.
    
- Absence d’hallucinations ou de contenus inventés.
