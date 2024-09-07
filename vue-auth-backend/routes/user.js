const express = require('express');
const pool = require('../config/db');

const router = express.Router();

router.get('/', async (req, res) => {
  try {
    const usersQuery = `
      SELECT u.id, u.first_name, u.last_name, u.company_id, c.company_name, u.role, u.permission, u.pass_hash, u.is_active, u.salary
      FROM users u
      JOIN companies c ON u.company_id = c.company_id
    `;
    const usersResult = await pool.query(usersQuery);
    res.json(usersResult.rows);
  } catch (err) {
    console.error('Error fetching users:', err);
    res.status(500).json({ error: 'Internal server error' });
  }
});

module.exports = router;
