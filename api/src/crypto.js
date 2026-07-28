/**
 * Chiffrement des donnees personnelles sensibles (telephone, email) stockees
 * en base : AES-256-GCM pour la valeur elle-meme (reversible, pour pouvoir
 * l'afficher a l'utilisateur), + un hash HMAC-SHA256 deterministe a cote
 * pour permettre la recherche/unicite (login, doublons) sans jamais
 * comparer ou indexer la valeur en clair.
 */

const crypto = require('crypto');

const ALGORITHM = 'aes-256-gcm';
const IV_LENGTH = 12;
const AUTH_TAG_LENGTH = 16;

// Cle brute prise depuis l'environnement, normalisee en 32 octets via SHA-256
// (accepte n'importe quelle longueur/format en entree). A definir en prod via
// PII_ENCRYPTION_KEY ; valeur de dev de secours sinon (voir JWT_SECRET).
const KEY = crypto
  .createHash('sha256')
  .update(process.env.PII_ENCRYPTION_KEY || 'dev-pii-key-a-changer-en-production')
  .digest();

function encrypt(plaintext) {
  if (plaintext === null || plaintext === undefined) return null;
  const iv = crypto.randomBytes(IV_LENGTH);
  const cipher = crypto.createCipheriv(ALGORITHM, KEY, iv);
  const ciphertext = Buffer.concat([cipher.update(String(plaintext), 'utf8'), cipher.final()]);
  return Buffer.concat([iv, cipher.getAuthTag(), ciphertext]).toString('base64');
}

function decrypt(payload) {
  if (payload === null || payload === undefined) return null;
  const buf = Buffer.from(payload, 'base64');
  const iv = buf.subarray(0, IV_LENGTH);
  const authTag = buf.subarray(IV_LENGTH, IV_LENGTH + AUTH_TAG_LENGTH);
  const ciphertext = buf.subarray(IV_LENGTH + AUTH_TAG_LENGTH);
  const decipher = crypto.createDecipheriv(ALGORITHM, KEY, iv);
  decipher.setAuthTag(authTag);
  return Buffer.concat([decipher.update(ciphertext), decipher.final()]).toString('utf8');
}

// Deterministe : meme entree -> meme hash, ce qui permet WHERE telephone_hash
// = $1 pour la connexion / la detection de doublons.
function hashForLookup(value) {
  if (value === null || value === undefined) return null;
  return crypto.createHmac('sha256', KEY).update(String(value).trim().toLowerCase()).digest('hex');
}

module.exports = { encrypt, decrypt, hashForLookup };
