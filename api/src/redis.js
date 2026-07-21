const Redis = require('ioredis');

// REDIS_URL : "redis://redis:6379" dans Docker (voir docker-compose.yml),
// "redis://localhost:6379" si l'API tourne hors container.
const redis = new Redis(process.env.REDIS_URL || 'redis://localhost:6379', {
  lazyConnect: false,
  maxRetriesPerRequest: 3,
});

redis.on('error', (err) => {
  console.error('Erreur connexion Redis :', err.message);
});

module.exports = { redis };
