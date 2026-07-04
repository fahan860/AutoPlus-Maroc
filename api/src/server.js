require('dotenv').config();
const express = require('express');
const { pool } = require('./db');

const app = express();
app.use(express.json());

// Test end-to-end minimal : API up + connexion DB vivante
app.get('/health', async (_req, res) => {
  try {
    const { rows } = await pool.query('SELECT NOW() AS now');
    res.json({ status: 'ok', db_time: rows[0].now });
  } catch (err) {
    res.status(500).json({ status: 'error', message: err.message });
  }
});

const port = process.env.PORT || 3000;
app.listen(port, () => {
  console.log(`AutoPlus API listening on port ${port}`);
});
