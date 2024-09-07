const express = require('express');
const pool = require('../config/db');

const router = express.Router();

// Create company route
router.post('/create-company', async (req, res) => {
  const { company_name } = req.body;

  try {
    const companyCheck = await pool.query('SELECT * FROM companies WHERE company_name = $1', [company_name]);
    if (companyCheck.rows.length > 0) {
      return res.status(400).json({ error: 'Company already exists' });
    }

    const result = await pool.query(
      'INSERT INTO companies (company_name) VALUES ($1) RETURNING *',
      [company_name]
    );
    res.status(201).json({ message: 'Company created successfully', company: result.rows[0] });
  } catch (error) {
    console.error('Error creating company:', error);
    res.status(500).json({ error: 'Server error' });
  }
});

router.get('/', async (req, res) => {
  try {
    const companiesQuery = `
      SELECT c.company_id, c.company_name, 
      (SELECT CONCAT(u.first_name, ' ', u.last_name)
       FROM users u 
       WHERE u.company_id = c.company_id AND u.role = 'admin'
       LIMIT 1) AS admin_user
      FROM companies c
    `;
    const companiesResult = await pool.query(companiesQuery);
    res.json(companiesResult.rows);
  } catch (err) {
    console.error('Error fetching companies:', err);
    res.status(500).json({ error: 'Internal server error' });
  }
});

module.exports = router;
