const express = require('express');
const bcrypt = require('bcrypt');
const jwt = require('jsonwebtoken');
const pool = require('../config/db');
require('dotenv').config();

const router = express.Router();

// Register route
router.post('/register', async (req, res) => {
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
      [email, first_name, last_name, company_id, role, permission, hashedPassword, true, salary, work_capacity]
    );

    res.status(201).json({ message: 'User registered successfully', user: result.rows[0] });
  } catch (error) {
    console.error('Error creating user:', error);
    res.status(500).json({ error: 'Server error' });
  }
});

// Login route
router.post('/login', async (req, res) => {
  const { email, password } = req.body;

  try {
    const userCheck = await pool.query('SELECT * FROM users WHERE email = $1', [email]);
    const user = userCheck.rows[0];
    if (!user) {
      return res.status(400).json({ error: 'Invalid credentials' });
    }

    if (!user.pass_hash) {
      return res.status(400).json({ error: 'Password not set for this user' });
    }

    const validPassword = await bcrypt.compare(password, user.pass_hash);
    if (!validPassword) {
      return res.status(400).json({ error: 'Invalid credentials' });
    }

    const token = jwt.sign({ email: user.email }, process.env.JWT_SECRET, { expiresIn: '1h' });
    res.json({ token });
  } catch (error) {
    console.error(error);
    res.status(500).json({ error: 'Server error' });
  }
});

// Verify Token route (optional)
router.get('/verify', (req, res) => {
  const token = req.header('Authorization').replace('Bearer ', '');

  if (!token) {
    return res.status(401).json({ error: 'No token provided' });
  }

  try {
    const decoded = jwt.verify(token, process.env.JWT_SECRET);
    res.json({ decoded });
  } catch (error) {
    res.status(401).json({ error: 'Invalid token' });
  }
});

module.exports = router;
