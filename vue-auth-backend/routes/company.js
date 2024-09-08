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

// Update company route
router.put('/update-company/:id', async (req, res) => {
  const { id } = req.params;
  const { company_name } = req.body;

  try {
    const result = await pool.query(
      `UPDATE companies 
       SET company_name = $1 
       WHERE company_id = $2 RETURNING *`,
      [company_name, id]
    );

    res.status(200).json({ message: 'Company updated successfully', company: result.rows[0] });
  } catch (error) {
    console.error('Error updating company:', error);
    res.status(500).json({ error: 'Server error' });
  }
});

// "Remove" company route (soft delete)
router.put('/remove-company/:id', async (req, res) => {
  const { id } = req.params;

  try {
    const result = await pool.query(
      'UPDATE companies SET is_active = false WHERE company_id = $1 RETURNING *',
      [id]
    );

    res.status(200).json({ message: 'Company removed successfully', company: result.rows[0] });
  } catch (error) {
    console.error('Error removing company:', error);
    res.status(500).json({ error: 'Server error' });
  }
});

router.get('/active', async (req, res) => {
  try {
    const activeCompaniesQuery = `
      SELECT c.company_id, c.company_name, 
      (SELECT CONCAT(u.first_name, ' ', u.last_name)
       FROM users u 
       WHERE u.company_id = c.company_id AND u.role = 'admin'
       LIMIT 1) AS admin_user
      FROM companies c
      WHERE c.is_active = true
    `;
    const activeCompaniesResult = await pool.query(activeCompaniesQuery);
    res.json(activeCompaniesResult.rows);
  } catch (err) {
    console.error('Error fetching active companies:', err);
    res.status(500).json({ error: 'Internal server error' });
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
