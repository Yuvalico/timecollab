const express = require('express');
const pool = require('../config/db');
const bcrypt = require('bcrypt');

const router = express.Router();

// Permission map
const permissionMap = {
  'Net Admin': 0,
  'Employer': 1,
  'Employee': 2,
};

// route to create a user
router.post('/create-user', async (req, res) => {
  const {
    first_name,
    last_name,
    email,
    password,
    company_name,
    role,
    permission,
    salary,
    work_capacity,
  } = req.body;

  try {
    const permissionInt = permissionMap[permission];
    // Handle invalid permission input
    if (permissionInt === undefined) {
      return res.status(400).json({ error: 'Invalid permission type' });
    }
    
    // Check if user already exists
    const userCheck = await pool.query('SELECT * FROM public.users WHERE email = $1', [email]);
    if (userCheck.rows.length > 0) {
      return res.status(400).json({ error: 'User already exists' });
    }

    // Get the company_id for the provided company name
    const companyResult = await pool.query('SELECT company_id FROM companies WHERE company_name = $1', [company_name]);
    if (companyResult.rows.length === 0) {
      return res.status(404).json({ error: 'Company not found' });
    }

    const company_id = companyResult.rows[0].company_id;

    // Hash the password
    const hashedPassword = await bcrypt.hash(password, 10);

    // Insert new user into the database
    const result = await pool.query(
      `INSERT INTO users (email, first_name, last_name, company_id, role, permission, pass_hash, is_active, salary, work_capacity)
       VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10) RETURNING *`,
      [email, first_name, last_name, company_id, role, permissionInt, hashedPassword, true, salary, work_capacity]
    );

    res.status(201).json({ message: 'User registered successfully', user: result.rows[0] });
  } catch (error) {
    console.error('Error creating user:', error);
    res.status(500).json({ error: 'Server error' });
  }
});

// Update user route
router.put('/update-user/:id', async (req, res) => {
  const { id } = req.params;
  const { first_name, last_name, mobile_phone, email, role, permission, salary, work_capacity } = req.body;
  const permissionInt = permissionMap[permission];
  // Handle invalid permission input
  if (permissionInt === undefined) {
    return res.status(400).json({ error: 'Invalid permission type' });
  }

  try {
    const result = await pool.query(
      `UPDATE users 
       SET first_name = $1, last_name = $2, mobile_phone = $3, email = $4, role = $5, permission = $6, salary = $7, work_capacity = $8 
       WHERE id = $9 RETURNING *`,
      [first_name, last_name, mobile_phone, email, role, permissionInt, salary, work_capacity, id]
    );

    res.status(200).json({ message: 'User updated successfully', user: result.rows[0] });
  } catch (error) {
    console.error('Error updating user:', error);
    res.status(500).json({ error: 'Server error' });
  }
});

// "Remove" user route (soft delete)
router.put('/remove-user/:id', async (req, res) => {
  const { id } = req.params;

  try {
    const result = await pool.query(
      'UPDATE users SET is_active = false WHERE id = $1 RETURNING *',
      [id]
    );

    res.status(200).json({ message: 'User removed successfully', user: result.rows[0] });
  } catch (error) {
    console.error('Error removing user:', error);
    res.status(500).json({ error: 'Server error' });
  }
});

router.get('/active', async (req, res) => {
  try {
    const usersQuery = `
      SELECT u.id, u.first_name, u.last_name, u.mobile_phone, u.email, u.company_id, c.company_name, u.role, u.permission, u.pass_hash, u.is_active, u.salary, u.work_capacity
      FROM users u
      JOIN companies c ON u.company_id = c.company_id
      WHERE u.is_active = true
    `;
    const usersResult = await pool.query(usersQuery);
    res.json(usersResult.rows);
  } catch (err) {
    console.error('Error fetching active users:', err);
    res.status(500).json({ error: 'Internal server error' });
  }
});

router.get('/', async (req, res) => {
  try {
    const usersQuery = `
      SELECT u.id, u.first_name, u.last_name, u.mobile_phone, u.email, u.company_id, c.company_name, u.role, u.permission, u.pass_hash, u.is_active, u.salary, u.work_capacity
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
