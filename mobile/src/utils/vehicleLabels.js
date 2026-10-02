// Libelles affiches pour les valeurs techniques attendues par l'API d'estimation.

export const BOITES = [
  { value: 'manuelle', label: 'Manuelle' },
  { value: 'automatique', label: 'Automatique' },
];

export const CARBURANTS = [
  { value: 'diesel', label: 'Diesel' },
  { value: 'essence', label: 'Essence' },
  { value: 'hybride', label: 'Hybride' },
  { value: 'electrique', label: 'Électrique' },
  { value: 'gpl', label: 'GPL' },
];

export const ETATS = [
  { value: 'neuf', label: 'Neuf' },
  { value: 'excellent', label: 'Excellent' },
  { value: 'tres_bon', label: 'Très bon' },
  { value: 'bon', label: 'Bon' },
  { value: 'correct', label: 'Correct' },
];

export const ORIGINES = [
  { value: 'ww_maroc', label: 'WW au Maroc' },
  { value: 'dedouanee', label: 'Dédouanée' },
  { value: 'importee_neuve', label: 'Importée neuve' },
  { value: 'non_dedouanee', label: 'Non dédouanée' },
];

export const PREMIERE_MAIN = [
  { value: true, label: 'Oui' },
  { value: false, label: 'Non' },
];

export const EQUIPEMENTS = [
  { value: 'climatisation', label: 'Climatisation' },
  { value: 'gps', label: 'GPS' },
  { value: 'camera_recul', label: 'Caméra de recul' },
  { value: 'radar_recul', label: 'Radar de recul' },
  { value: 'sieges_cuir', label: 'Sièges cuir' },
  { value: 'toit_ouvrant', label: 'Toit ouvrant' },
  { value: 'jantes_alu', label: 'Jantes alu' },
  { value: 'regulateur_vitesse', label: 'Régulateur' },
  { value: 'limiteur_vitesse', label: 'Limiteur' },
  { value: 'bluetooth', label: 'Bluetooth' },
  { value: 'ordinateur_bord', label: 'Ordinateur de bord' },
  { value: 'vitres_electriques', label: 'Vitres électriques' },
  { value: 'verrouillage_central', label: 'Verrouillage central' },
  { value: 'abs', label: 'ABS' },
  { value: 'esp', label: 'ESP' },
  { value: 'airbags', label: 'Airbags' },
];

// Sigles de marques a afficher en majuscules (les donnees du modele sont en minuscules)
const SIGLES = new Set(['bmw', 'ds', 'mg', 'gmc', 'byd', 'dfsk', 'jac', 'baic', 'vw']);

// "mercedes-benz" -> "Mercedes-Benz", "classe c" -> "Classe C", "bmw" -> "BMW"
export function displayName(value) {
  if (!value) return '';
  return value
    .split(' ')
    .map((mot) =>
      SIGLES.has(mot)
        ? mot.toUpperCase()
        : mot
            .split('-')
            .map((partie) => partie.charAt(0).toUpperCase() + partie.slice(1))
            .join('-')
    )
    .join(' ');
}

// 89000 -> "89 000 DH" (espace insecable fine, lisible en francais)
export function formatDh(montant) {
  return `${formatThousands(montant)} DH`;
}

export function formatThousands(nombre) {
  return String(Math.round(nombre)).replace(/\B(?=(\d{3})+(?!\d))/g, ' ');
}

export function labelOf(liste, value) {
  return liste.find((o) => o.value === value)?.label ?? '';
}
