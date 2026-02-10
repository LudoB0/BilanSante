# UI Contract - session-purge

## 1. Responsabilite de l'interface
Permettre le suivi de cloture de session et de suppression globale des donnees en fin d'etape 9.

## 2. Utilisateur concerne
Pharmacien d'officine en fin de parcours, apres validation finale et generation documentaire (PRD section 3, Etape 9; PRP_PurgeSessionDataAfterExport.md).

## 3. Actions utilisateur autorisees
- Consulter l'etat de cloture de session (deduit de l'etape 9 et du module de purge, PRD section 3, Etape 9).
- Consulter l'etat de suppression des donnees de session (PRP_PurgeSessionDataAfterExport.md).
- Aucun declenchement manuel explicite n'est defini dans PRD/PRP; suppression decrite comme automatique en fin d'etape 9.

## 4. Donnees affichees
- Etat de validation finale et de generation des documents attendus (PRD section 5.3; PRP_PurgeSessionDataAfterExport.md).
- Etat de suppression des donnees de session: questionnaire, transcript, metadonnees, audio (PRD section 3, Etape 9).
- Indication d'absence de duree de retention par defaut (PRD section 6).

## 5. Donnees saisies ou modifiees
- Aucune saisie utilisateur explicitement definie dans PRD/PRP pour ce module.

## 6. Regles de validation UI
- La purge intervient apres validation finale et generation des documents (PRD section 3, Etape 9; PRP_PurgeSessionDataAfterExport.md).
- La purge ne doit pas etre executee de facon prematuree (PRP_PurgeSessionDataAfterExport.md).
- En cas de document attendu non cree, la regle exacte de purge/cloture est non tranchee dans PRD/PRP et doit etre signalee explicitement.

## 7. Etats de l'interface
- Etat attente de conditions de cloture.
- Etat pret a cloturer.
- Etat purge executee.
- Etat bloque (preconditions non atteintes).
- Etat erreur (tentative de purge prematuree).

## 8. Erreurs et messages
- Suppression prematuree avant generation des documents: blocage (PRP_PurgeSessionDataAfterExport.md).
- Document attendu non cree: signalement explicite; consequence exacte sur purge non specifiee dans PRD/PRP (PRD section 5.3).
- Texte exact des messages non specifie dans PRD/PRP.

## 9. Hors perimetre
- Retention longue duree des donnees session (PRD section 6).
- Purge partielle selective non definie dans PRD/PRP.
- Toute action clinique (PRD section 7).
