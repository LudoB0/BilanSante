# Interface d'implementation - InitializeInterviewSession

## 1. Reference contractuelle

- PRP de reference : /docs/prp/PRP_InitializeInterviewSession.md
- Version du PRP : V2

## 2. Responsabilite du module

Afficher le contexte pharmacie, permettre la selection d'une tranche d'age parmi les questionnaires disponibles, et creer une session unique stockee dans `data/`.

## 3. Donnees affichees (lecture seule, depuis config/settings.json)

Les informations suivantes sont lues depuis `config/settings.json` et affichees a l'ecran d'initialisation :

| Champ                  | Cle settings.json               | Affichage                        |
|------------------------|----------------------------------|----------------------------------|
| Logo de la pharmacie   | (fichier `config/img/logo.png`)  | Image affichee en en-tete        |
| Nom de la pharmacie    | `nom_pharmacie`                  | Toujours affiche                 |
| Adresse                | `adresse`                        | Toujours affiche                 |
| Code postal            | `code_postal`                    | Toujours affiche                 |
| Ville                  | `ville`                          | Toujours affiche                 |
| Site web               | `site_web`                       | Affiche uniquement si non vide   |
| Instagram              | `instagram`                      | Affiche uniquement si non vide   |
| Facebook               | `facebook`                       | Affiche uniquement si non vide   |
| X                      | `x`                              | Affiche uniquement si non vide   |
| LinkedIn               | `linkedin`                       | Affiche uniquement si non vide   |

**Regle** : les liens web (site_web, instagram, facebook, x, linkedin) ne sont affiches que si leur valeur dans `settings.json` est une chaine non vide.

## 4. Entrees utilisateur

### 4.1 Selection de la tranche d'age

- **Type** : valeur categorielle (selection unique parmi une liste)
- **Obligatoire** : Oui
- **Source des choix** : les tranches d'age pour lesquelles un fichier questionnaire non vide existe dans `config/questionnaires/<age_range>.json`
- **Regle de filtrage** : seules les tranches d'age disposant d'un questionnaire contenant au moins une question sont proposees. Les tranches d'age sans questionnaire ou avec un questionnaire vide (zero questions) sont exclues de la liste.
- **Valeurs possibles** : sous-ensemble de `("18-25", "45-50", "60-65", "70-75")` filtre selon la regle ci-dessus

### 4.2 Action utilisateur

- **Bouton "Demarrer l'entretien"** : declenche la creation de la session
- **Precondition** : une tranche d'age doit etre selectionnee

## 5. Sorties produites

### 5.1 Fichier de session

- **Emplacement** : `data/sessions/<session_id>.json`
- **Cree au clic sur "Demarrer l'entretien"**

### 5.2 Schema de sortie (JSON)

```json
{
  "session_id": "<UUID v4>",
  "age_range": "<tranche d'age selectionnee>",
  "created_at": "<date/heure ISO 8601>",
  "status": "active",
  "metadata": {
    "pharmacie": {
      "nom_pharmacie": "<valeur depuis settings.json>",
      "adresse": "<valeur depuis settings.json>",
      "code_postal": "<valeur depuis settings.json>",
      "ville": "<valeur depuis settings.json>"
    }
  }
}
```

- `session_id` : UUID v4 genere automatiquement, unique
- `age_range` : tranche d'age selectionnee par le pharmacien
- `created_at` : horodatage de creation au format ISO 8601
- `status` : toujours `"active"` a la creation
- `metadata.pharmacie` : copie des coordonnees pharmacie au moment de la creation (tracabilite)

## 6. Preconditions

- Le parametrage applicatif doit etre complet (`config/settings.json` valide avec tous les champs obligatoires et `config/img/logo.png` present).
- Au moins un questionnaire non vide doit exister dans `config/questionnaires/`.
- Si une precondition n'est pas remplie, l'ecran affiche un message explicite et le bouton "Demarrer l'entretien" est desactive.

## 7. Postconditions

- Un fichier `data/sessions/<session_id>.json` est cree sur disque.
- La session est a l'etat `"active"`.
- Les modules suivants (QR code, collecte, entretien) peuvent se rattacher a cette session.

## 8. Erreurs et cas d'echec

| Situation                           | Comportement attendu                     |
|-------------------------------------|------------------------------------------|
| Parametrage applicatif incomplet    | Message explicite, bouton desactive      |
| Aucun questionnaire disponible      | Message explicite, bouton desactive      |
| Tranche d'age non selectionnee      | Bouton desactive                         |
| Echec d'ecriture du fichier session | Message d'erreur explicite               |
| Session ID duplique (collision UUID)| Regeneration automatique                 |

## 9. Invariants

- Aucune donnee nominative du patient n'est collectee.
- L'identifiant de session est unique (UUID v4).
- Les donnees de session sont stockees dans `data/` (temporaire, purgeable).
- Les donnees de parametrage dans `config/` ne sont jamais modifiees par ce module.

## 10. Hors perimetre

- Generation du QR code (skill separee : GenerateSessionQRCode).
- Capture des reponses questionnaire.
- Diagnostic medical, prescription, decision clinique.
