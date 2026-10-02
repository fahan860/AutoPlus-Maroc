// Libelles et couleurs des categories de panne et niveaux d'urgence (valeurs de base_pannes).

export const CATEGORIES_PANNE = {
  moteur: { label: 'Moteur', icon: '⚙️' },
  entretien_courant: { label: 'Entretien', icon: '🛢️' },
  freins: { label: 'Freinage', icon: '🛑' },
  electrique: { label: 'Électricité', icon: '🔋' },
  climatisation: { label: 'Climatisation', icon: '❄️' },
  carrosserie: { label: 'Carrosserie', icon: '🚗' },
  pneus_suspension: { label: 'Pneus et suspension', icon: '🛞' },
  transmission: { label: 'Boîte et embrayage', icon: '🔧' },
  direction: { label: 'Direction', icon: '🎯' },
  echappement: { label: 'Échappement', icon: '💨' },
};

export const URGENCES = {
  faible: { label: 'Urgence faible', couleur: '#1E8449', fond: '#E9F7EF' },
  moyenne: { label: 'Urgence moyenne', couleur: '#B9770E', fond: '#FEF5E7' },
  elevee: { label: 'Urgence élevée', couleur: '#C0392B', fond: '#FDEDEC' },
  critique: { label: 'Urgent : ne roulez pas', couleur: '#FFFFFF', fond: '#C0392B' },
};

export function categorieLabel(categorie) {
  return CATEGORIES_PANNE[categorie]?.label ?? categorie;
}
