import { apiClient } from './client';

export function listReviews(garageId) {
  return apiClient.get('/reviews', { params: { garage_id: garageId } }).then((res) => res.data.reviews);
}

export function postReview({ garageId, interventionId, note, commentaire }) {
  return apiClient
    .post('/reviews', {
      garage_id: garageId,
      intervention_id: interventionId || undefined,
      note,
      commentaire: commentaire || undefined,
    })
    .then((res) => res.data);
}
