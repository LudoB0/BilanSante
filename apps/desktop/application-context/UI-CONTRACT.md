# UI Contract - application-context

## 1. Responsabilite de l'interface
Permettre le parametrage initial de l'application (identite pharmacie, fournisseur IA, cle API obligatoire) avant tout parcours patient.

## 2. Utilisateur concerne
Pharmacien d'officine, en etape 1 du parcours (PRD section 3, Etape 1), avec possibilite de modification ulterieure du parametrage (PRD section 3, Etape 1).

## 3. Actions utilisateur autorisees
- Saisir ou modifier l'identite de la pharmacie: logo, coordonnees, en-tete, pied de page (PRD section 3, Etape 1; PRP_ConfigureApplicationContext.md).
- Selectionner le fournisseur IA (PRD section 3, Etape 1; PRP_ConfigureApplicationContext.md).
- Saisir ou mettre a jour la cle API obligatoire (PRD section 3, Etape 1; PRP_ConfigureApplicationContext.md).
- Enregistrer le parametrage applicatif (deduit de l'intention de parametrage, PRP_ConfigureApplicationContext.md).

## 4. Donnees affichees
- Valeurs actuelles du parametrage applicatif (identite pharmacie, fournisseur IA, etat cle API) (PRP_ConfigureApplicationContext.md).
- Indication d'absence de donnees patient dans ce module (PRD section 3, Etape 1).

## 5. Donnees saisies ou modifiees
- Identite pharmacie: logo, coordonnees, en-tete, pied de page (PRD section 3, Etape 1).
- Fournisseur IA (PRD section 3, Etape 1).
- Cle API obligatoire (PRD section 3, Etape 1).

## 6. Regles de validation UI
- La cle API est obligatoire pour valider le parametrage (PRD section 3, Etape 1; PRP_ConfigureApplicationContext.md).
- Les champs d'identite pharmacie declares obligatoires par le PRP doivent etre presents (PRP_ConfigureApplicationContext.md).
- Aucune donnee patient ne doit etre demandee dans cette interface (PRD section 3, Etape 1).
- Le format exact de validation de chaque champ (longueur, motif) est non specifie dans PRD/PRP.

## 7. Etats de l'interface
- Etat initial (parametrage non renseigne).
- Etat edition (saisie ou modification en cours).
- Etat valide (parametrage enregistre).
- Etat erreur (donnees obligatoires manquantes ou cle API invalide).

## 8. Erreurs et messages
- Cle API manquante ou invalide: signalement explicite et blocage de validation (PRP_ConfigureApplicationContext.md).
- Donnee obligatoire absente: blocage de validation (PRP_ConfigureApplicationContext.md).
- Texte exact des messages non specifie dans PRD/PRP.

## 9. Hors perimetre
- Saisie ou consultation de donnees patient (PRD section 3, Etape 1).
- Diagnostic, prescription, decision clinique, interpretation medicale avancee (PRD section 7; PRP_ConfigureApplicationContext.md).