/**
 * Envoi d'email de verification a l'inscription.
 *
 * Configuration via variables d'environnement (voir .env.example) :
 *   SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASS, SMTP_FROM
 * Exemple gratuit : compte Gmail + mot de passe d'application
 *   (SMTP_HOST=smtp.gmail.com, SMTP_PORT=587, SMTP_USER=toi@gmail.com,
 *    SMTP_PASS=<mot de passe d'application Google>).
 *
 * Si aucune config SMTP n'est fournie (dev/demo sans compte email), le code
 * est simplement affiche dans les logs serveur au lieu d'etre envoye -
 * pratique pour tester sans rien configurer, mais a eviter en prod.
 */

const nodemailer = require('nodemailer');

const SMTP_HOST = process.env.SMTP_HOST;
const SMTP_PORT = Number(process.env.SMTP_PORT || 587);
const SMTP_USER = process.env.SMTP_USER;
const SMTP_PASS = process.env.SMTP_PASS;
const SMTP_FROM = process.env.SMTP_FROM || SMTP_USER || 'noreply@autoplus.local';

const isConfigured = Boolean(SMTP_HOST && SMTP_USER && SMTP_PASS);

let transporter = null;
if (isConfigured) {
  transporter = nodemailer.createTransport({
    host: SMTP_HOST,
    port: SMTP_PORT,
    secure: SMTP_PORT === 465,
    auth: { user: SMTP_USER, pass: SMTP_PASS },
  });
}

async function sendVerificationEmail(to, code) {
  const subject = 'Verifiez votre compte AUTO+';
  const text = `Votre code de verification AUTO+ est : ${code}\n\nCe code expire dans 15 minutes.`;
  const html = `
    <div style="font-family: sans-serif; padding: 16px;">
      <h2>Verification de compte AUTO+</h2>
      <p>Votre code de verification est :</p>
      <p style="font-size: 28px; font-weight: bold; letter-spacing: 4px;">${code}</p>
      <p>Ce code expire dans 15 minutes.</p>
    </div>`;

  if (!isConfigured) {
    // Fallback dev : pas de SMTP configure, on log au lieu d'envoyer.
    console.log(`[mailer] SMTP non configure - code de verification pour ${to} : ${code}`);
    return { simulated: true };
  }

  return transporter.sendMail({ from: SMTP_FROM, to, subject, text, html });
}

module.exports = { sendVerificationEmail, isConfigured };
