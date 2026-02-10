# UI Contract - final-validation-and-export

## 1. Responsabilite de l'interface
Permettre la relecture finale, l'ajustement, la validation par le pharmacien et l'export des documents attendus.

## 2. Utilisateur concerne
Pharmacien d'officine, en etape 9 du parcours (PRD section 3, Etape 9).

## 3. Actions utilisateur autorisees
- Consulter le bilan et le plan d'actions assembles (PRD section 3, Etape 9; PRP_ValidateFinalBilan.md).
- Ajuster le contenu avant validation finale (PRD section 3, Etape 9).
- Valider explicitement le contenu final (PRD section 3, Etape 9; PRP_ValidateFinalBilan.md).
- Lancer la generation des documents attendus (PRP_GenerateDOCXDocument.md; PRP_GeneratePDFDocument.md):
- `output/BDS_<numero_session>.docx`
- `output/PAC_<numero_session>.docx`
- `output/BDS_<numero_session>.pdf`
- `output/PAC_<numero_session>.pdf`

## 4. Donnees affichees
- Contenu final a valider (bilan + plan d'actions) (PRD section 5.1 et 5.2; PRP_ValidateFinalBilan.md).
- Etat de generation de chacun des 4 documents attendus (PRD section 5.3).
- Marquage "non cree" pour tout document en echec de generation (PRD section 3, Etape 9; PRP_ValidateFinalBilan.md).

## 5. Donnees saisies ou modifiees
- Ajustements du contenu final par le pharmacien avant validation (PRD section 3, Etape 9).
- Decision de validation finale (PRP_ValidateFinalBilan.md).

## 6. Regles de validation UI
- Validation pharmacien obligatoire avant export (PRD section 6; PRP_ValidateFinalBilan.md).
- Les noms de documents doivent suivre le nommage contractuel (PRD section 3, Etape 9; PRD section 5.3).
- Toute absence de generation d'un document attendu doit etre reportee "non cree" (PRD section 3, Etape 9; PRD section 5.3).
- Le format exact de saisie des ajustements est non specifie dans PRD/PRP.

## 7. Etats de l'interface
- Etat initial (contenu non valide).
- Etat edition/relecture.
- Etat valide.
- Etat export en cours.
- Etat export termine (complet ou partiel).
- Etat erreur (validation absente ou echec de generation).

## 8. Erreurs et messages
- Validation non realisee: blocage de l'export (PRP_ValidateFinalBilan.md).
- Echec de generation d'un document attendu: document concerne "non cree" (PRP_ValidateFinalBilan.md; PRP_GenerateDOCXDocument.md; PRP_GeneratePDFDocument.md).
- Donnee obligatoire absente: blocage (PRP_ValidateFinalBilan.md).
- Texte exact des messages non specifie dans PRD/PRP.

## 9. Hors perimetre
- Modification du transcript source de verite (PRD section 3, Etape 7).
- Definition de nouvelles actions non justifiees par le transcript (PRD section 5.2).
- Diagnostic, prescription, decision clinique, interpretation medicale avancee (PRD section 7).