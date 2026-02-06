# Outil de Bilan de Santé Prévention (V0)

> **Objectif de ce document**  
> Ce PRD sert de cadre fonctionnel de référence pour le développement de l’outil.  
> Il est volontairement **court, clair et orienté usage réel**, afin d’être exploitable par une IA (Codex / Claude) et par un humain.

---

## 1. Objectif du produit

Permettre à un pharmacien d’officine de **générer automatiquement un document de bilan de santé prévention**, clair, structuré et directement exploitable, à partir d’un **questionnaire renseigné par le patient en amont**, complété par un **entretien oral conduit par le pharmacien**. L’outil doit produire un bilan de santé et un **plan d’actions personnalisées**, imprimable et destiné à être remis au patient, **sans jamais inventer d’informations** et dans le strict respect du cadre officinal.

---

## 2. Utilisateur cible

- Pharmacien d’officine
    
- Niveau technique : faible à intermédiaire
    
- Contraintes :
    
    - temps limité 15 à 20 mn/ entretien avec le patient (sans compter le remplissage du questionnaire
        
    - besoin de fiabilité
        
    - responsabilité professionnelle engagée
        

> Le pharmacien **reste maître de l’entretien** et du document final.

---

## 3. Contexte d’usage

**Étape 1 – Questionnaire préalable (autonomie du patient)**  
Le patient est accueilli dans un espace garantissant la confidentialité et remplit, sur une tablette mise à disposition par la pharmacie, un **questionnaire de prévention adapté à sa tranche d’âge**.

- Le patient peut compléter le questionnaire seul ou avec une aide minimale si nécessaire.
    
- Les réponses sont enregistrées et constituent une **base factuelle préparatoire** à l’entretien.
    
- Aucune interprétation n’est réalisée à ce stade.
    

**Étape 2 – Entretien officinal guidé**  
Le pharmacien conduit un **entretien oral structuré**, en s’appuyant sur les réponses du questionnaire afin de :

- clarifier certains points,
    
- approfondir les réponses pertinentes,
    
- identifier avec le patient des axes de prévention et de suivi.
    
- L’entretien est conduit **exclusivement par le pharmacien**.
    
- Il s’appuie sur les réponses au **questionnaire ** du patient.
    
- L’échange peut être :
    
    - enregistré sous forme audio (avec information et accord du patient),
        
    - ou retranscrit directement sous forme écrite.
        

**Étape 3 – Génération et validation du bilan**  
À l’issue de l’entretien, l’outil génère un **compte rendu structuré**, comprenant un **bilan de santé prévention** et un **plan d’actions personnalisé**.

- Le pharmacien peut relire, ajuster et compléter le document avant validation finale.
    
- Le document final est **personnalisable aux couleurs et informations de la pharmacie** (nom, coordonnées, site, e-mail).
    
- Le bilan validé est ensuite **imprimable** et destiné à être remis au patient.
    

---

## 4. Problème à résoudre

- Rédaction chronophage des comptes rendus
    
- Hétérogénéité des bilans selon les pharmaciens
    
- Difficulté à :
    
    - synthétiser l’échange
        
    - identifier les actions de prévention pertinentes
        
    - assurer la traçabilité des décisions
        

---

## 5. Entrées du système

Les entrées du système correspondent **exclusivement aux informations réellement collectées lors du parcours patient**, sans inférence ni enrichissement externe.

### 5.1 Données issues du questionnaire préalable

- Tranche d’âge du patient (clé de sélection du questionnaire)
    
- Réponses structurées au questionnaire associé à la tranche d’âge
    
- Horodatage du remplissage du questionnaire
    

> Ces données constituent une **base déclarative**, elles seront utilisées pour la rédaction du bilan de santé.

### 5.2 Données issues de l’entretien officinal

- Transcript textuel complet de l’entretien (source principale)
    
- Ou enregistrement audio de l’entretien (si activé), destiné à être transcrit
    
- Métadonnées de l’entretien :
    
    - date de l’entretien
        
    - durée approximative
        

### 5.3 Règle de priorité des entrées

- Le **transcript de l’entretien** constitue la **source de vérité principale**.
    
- Les réponses au questionnaire servent de **support contextuel** : elles permettent de **préparer et orienter l’analyse de l’entretien**, d’en **structurer la lecture**, et de **renseigner certaines parties descriptives du bilan de santé**, sans jamais se substituer aux informations exprimées lors de l’entretien.
    
- Aucune autre source de données (dossier médical, historique patient externe, suppositions) n’est utilisée.
    

---

## 6. Sorties attendues

### 6.1 Document Bilan

Un document structuré comprenant :

- Contexte de l’entretien
    
- Synthèse des réponses
    
- Points de vigilance identifiés
    
- Actions de prévention proposées
    
- Conseils officinaux
    

### 6.2 Actions à mener

Pour chaque action :

- intitulé clair
    
- justification issue du transcript
    
- priorité (faible / moyenne / élevée)
    
- proposition de suivi
    

---

## 7. Contraintes fonctionnelles majeures

- Aucune information ne doit être inventée
    
- Aucune action ne peut être proposée sans justification explicite dans le transcript
    
- Le langage doit être :
    
    - professionnel
        
    - clair pour le patient
        
    - adapté au contexte officinal
        

---

## 8. Règles IA (anti-hallucination)

Les règles suivantes encadrent strictement l’analyse réalisée par l’IA, en cohérence avec le **contexte d’usage (section 3)** et les **entrées du système (section 5)**.

- Le **transcript de l’entretien officinal** constitue la **source de vérité principale et obligatoire** pour toute analyse, synthèse ou action proposée.
    
- Les réponses issues du questionnaire préalable peuvent être utilisées **uniquement comme éléments de contexte**, jamais comme base décisionnelle autonome.
    
- Toute information, conclusion ou action figurant dans le bilan doit être **explicitement traçable** à un élément exprimé par le patient lors de l’entretien.
    
- En cas d’information absente, ambiguë ou non exprimée lors de l’entretien :
    
    - l’outil le signale explicitement dans le document,
        
    - aucune déduction, interprétation implicite ou supposition n’est réalisée.
        
- L’IA ne complète pas, ne corrige pas et ne reformule pas le discours du patient au-delà de ce qui est strictement nécessaire à la compréhension, sous validation finale du pharmacien.
    

---

## 9. Hors périmètre (ce que l’outil ne fait pas)

- Diagnostic médical
    
- Prescription médicamenteuse
    
- Décision clinique
    
- Interprétation médicale avancée
    

---

## 10. Critères de succès (version initiale)

- Gain de temps perçu par le pharmacien
    
- Document compréhensible sans reformulation
    
- Aucune information non présente dans le transcript
    
- Possibilité de validation manuelle avant export
    

---

## 11. Points ouverts / à préciser

- Format exact du document final (PDF, HTML, autre)
    
- Niveaux de détail selon tranche d’âge
    
- Modalités d’export et d’archivage
    

---

> **Note de co-construction**  
> Les sections ci-dessus sont destinées à être **corrigées, précisées ou simplifiées** lors des prochaines itérations.