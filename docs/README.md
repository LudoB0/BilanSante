# Documentation projet

Ce dossier contient les contrats fonctionnels utilises pour guider le developpement du projet BilanSante.

## Structure
- `prd/PRD.md` : source de verite fonctionnelle (besoins, parcours, regles, contraintes)
- `skills/skills.md` : decomposition en skills metiers atomiques derives du PRD
- `prp/` : un PRP par skill (contrats d'implementation)
- `prp/PRP_TEMPLATE.md` : modele obligatoire de redaction des PRP

## Regles de gouvernance
- Le `PRD` est prioritaire sur tous les autres documents.
- Les `PRP` sont des contrats non negociables pour l'implementation.
- Aucun comportement hors PRD ne doit etre ajoute.
- En cas d'ambiguite, documenter explicitement le point ouvert.

## Conventions deja validees
- QRCode session : payload signe `bsp://session?v=1&sid=<session_id>&t=<token>&sig=<signature>`.
- Exports attendus dans `output/` :
  - `BDS_<numero_session>.docx`
  - `PAC_<numero_session>.docx`
  - `BDS_<numero_session>.pdf`
  - `PAC_<numero_session>.pdf`
- En cas d'echec d'export, le document concerne est considere non cree.
- La suppression des donnees est globale en fin d'etape 9 (questionnaire, transcript, metadonnees, audio).

## Processus de mise a jour
1. Mettre a jour `prd/PRD.md`.
2. Synchroniser `skills/skills.md`.
3. Regenerer ou ajuster les PRP dans `prp/`.
4. Verifier la coherence PRD -> Skills -> PRP avant implementation.
