const express = require('express');
const cors = require('cors');
require('dotenv').config();

const authRoutes = require('./routes/auth');
const companyRoutes = require('./routes/company');
const userRoutes = require('./routes/user');

const app = express();

// Enable CORS for all routes
app.use(cors({
    origin: 'http://localhost:5173',
    methods: 'GET,POST,PUT,DELETE',
    credentials: true
}));

// Middleware to parse JSON
app.use(express.json());

// Routes
app.use('/auth', authRoutes);         // Authentication routes
app.use('/api/companies', companyRoutes); // Company-related routes
app.use('/api/users', userRoutes);     // User-related routes
app.use('/api/companies/create-company', companyRoutes);     // Company-related routes
app.use('/api/users/create-user', userRoutes);     // User-related routes

// Start the server
const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
  console.log(`Server running on port ${PORT}`);
});
