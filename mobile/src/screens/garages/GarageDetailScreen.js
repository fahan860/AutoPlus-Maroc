import { useCallback, useEffect, useState } from 'react';
import { View, Text, StyleSheet, ScrollView, ActivityIndicator, Linking, Pressable } from 'react-native';
import { getGarage } from '../../api/garages';
import { listReviews, postReview } from '../../api/reviews';
import { extractErrorMessage } from '../../api/client';
import { useAuth } from '../../context/AuthContext';
import PrimaryButton from '../../components/PrimaryButton';
import FormInput from '../../components/FormInput';
import { colors } from '../../theme/colors';

export default function GarageDetailScreen({ route, navigation }) {
  const { garageId } = route.params;
  const { user } = useAuth();
  const [garage, setGarage] = useState(null);
  const [reviews, setReviews] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  const [noteChoisie, setNoteChoisie] = useState(5);
  const [commentaire, setCommentaire] = useState('');
  const [postingReview, setPostingReview] = useState(false);
  const [reviewError, setReviewError] = useState('');
  // Retour apres publication : publie tout de suite, ou en verification (detection de faux avis)
  const [reviewInfo, setReviewInfo] = useState(null);

  const loadReviews = useCallback(() => {
    listReviews(garageId).then(setReviews).catch(() => {});
  }, [garageId]);

  useEffect(() => {
    Promise.all([getGarage(garageId), listReviews(garageId).catch(() => [])])
      .then(([garageData, reviewsData]) => {
        setGarage(garageData);
        setReviews(reviewsData);
      })
      .catch((err) => setError(extractErrorMessage(err)))
      .finally(() => setLoading(false));
  }, [garageId]);

  async function handlePostReview() {
    setReviewError('');
    setReviewInfo(null);
    setPostingReview(true);
    try {
      const avis = await postReview({ garageId, note: noteChoisie, commentaire: commentaire.trim() || undefined });
      setReviewInfo({ enVerification: avis.moderation_statut === 'en_verification', message: avis.message });
      setCommentaire('');
      loadReviews();
      getGarage(garageId).then(setGarage).catch(() => {});
    } catch (err) {
      setReviewError(extractErrorMessage(err));
    } finally {
      setPostingReview(false);
    }
  }

  if (loading) {
    return <ActivityIndicator style={styles.flex} size="large" color={colors.primary} />;
  }

  if (error || !garage) {
    return <Text style={styles.error}>{error || 'Garage introuvable'}</Text>;
  }

  return (
    <ScrollView style={styles.flex} contentContainerStyle={styles.content}>
      <Text style={styles.title}>{garage.nom}</Text>
      {garage.categorie ? <Text style={styles.tag}>{garage.categorie}</Text> : null}

      <View style={styles.section}>
        <InfoRow label="Adresse" value={garage.adresse || 'Non renseignee'} />
        <InfoRow label="Ville" value={garage.ville} />
        <InfoRow label="Telephone" value={garage.telephone || 'Non renseigne'} />
        <InfoRow label="Note" value={garage.note != null ? `★ ${garage.note} (${garage.nb_avis} avis)` : 'Pas encore note'} />
      </View>

      {garage.telephone ? (
        <PrimaryButton
          title="Appeler le garage"
          variant="outline"
          onPress={() => Linking.openURL(`tel:${garage.telephone}`)}
        />
      ) : null}

      <View style={styles.spacer} />

      <PrimaryButton
        title="Prendre rendez-vous"
        onPress={() => navigation.navigate('BookIntervention', { garageId: garage.id, garageNom: garage.nom })}
      />

      <View style={styles.reviewsSection}>
        <Text style={styles.sectionTitle}>Avis récents</Text>
        {reviews.length === 0 ? (
          <Text style={styles.hint}>Aucun avis pour le moment.</Text>
        ) : (
          reviews.slice(0, 5).map((r) => (
            <View key={r.id} style={styles.reviewRow}>
              <Text style={styles.reviewStars}>{'⭐'.repeat(Math.round(r.note))} {r.auteur}</Text>
              {r.commentaire ? <Text style={styles.reviewComment}>{r.commentaire}</Text> : null}
            </View>
          ))
        )}

        {user?.role === 'automobiliste' ? (
          <View style={styles.reviewForm}>
            <Text style={styles.label}>Laisser un avis</Text>
            <View style={styles.starPicker}>
              {[1, 2, 3, 4, 5].map((n) => (
                <Pressable key={n} onPress={() => setNoteChoisie(n)}>
                  <Text style={styles.starPickerIcon}>{n <= noteChoisie ? '⭐' : '☆'}</Text>
                </Pressable>
              ))}
            </View>
            <FormInput
              placeholder="Votre commentaire (optionnel)"
              value={commentaire}
              onChangeText={setCommentaire}
            />
            {reviewError ? <Text style={styles.error}>{reviewError}</Text> : null}
            {reviewInfo ? (
              <Text style={[styles.reviewInfo, reviewInfo.enVerification ? styles.reviewInfoPending : styles.reviewInfoOk]}>
                {reviewInfo.enVerification ? '⏳ ' : '✓ '}
                {reviewInfo.message}
              </Text>
            ) : null}
            <PrimaryButton title="Publier l'avis" onPress={handlePostReview} loading={postingReview} />
          </View>
        ) : null}
      </View>
    </ScrollView>
  );
}

function InfoRow({ label, value }) {
  return (
    <View style={styles.infoRow}>
      <Text style={styles.infoLabel}>{label}</Text>
      <Text style={styles.infoValue}>{value}</Text>
    </View>
  );
}

const styles = StyleSheet.create({
  reviewInfo: { borderRadius: 10, padding: 12, marginBottom: 12, fontSize: 14, lineHeight: 20, overflow: 'hidden' },
  reviewInfoOk: { backgroundColor: '#E9F7EF', color: '#1E8449' },
  reviewInfoPending: { backgroundColor: '#FEF5E7', color: '#7E5109' },
  flex: { flex: 1, backgroundColor: colors.background },
  content: { padding: 20 },
  title: { fontSize: 24, fontWeight: '800', color: colors.text },
  tag: { color: colors.primary, fontWeight: '600', marginTop: 4 },
  section: {
    backgroundColor: colors.surface,
    borderRadius: 12,
    borderWidth: 1,
    borderColor: colors.border,
    padding: 16,
    marginVertical: 20,
  },
  infoRow: { marginBottom: 12 },
  infoLabel: { fontSize: 12, color: colors.textMuted, fontWeight: '600', textTransform: 'uppercase' },
  infoValue: { fontSize: 16, color: colors.text, marginTop: 2 },
  spacer: { height: 12 },
  error: { color: colors.danger, textAlign: 'center', marginTop: 40 },
  reviewsSection: { marginTop: 28 },
  sectionTitle: { fontSize: 18, fontWeight: '700', color: colors.text, marginBottom: 12 },
  hint: { fontSize: 13, color: colors.textMuted },
  reviewRow: {
    backgroundColor: colors.surface,
    borderRadius: 10,
    borderWidth: 1,
    borderColor: colors.border,
    padding: 12,
    marginBottom: 10,
  },
  reviewStars: { fontSize: 14, color: colors.text, fontWeight: '600' },
  reviewComment: { fontSize: 13, color: colors.textMuted, marginTop: 4 },
  reviewForm: { marginTop: 16 },
  label: { fontSize: 13, fontWeight: '600', color: colors.textMuted, marginBottom: 8 },
  starPicker: { flexDirection: 'row', gap: 6, marginBottom: 12 },
  starPickerIcon: { fontSize: 26 },
});
