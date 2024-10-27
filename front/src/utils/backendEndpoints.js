import { timestamp } from "@antfu/utils";

const API_BASE_URL = 'http://localhost:3000/api'; // Or your actual base URL
const USERS_ENDPOINT = "/users"
const COMPANIES_ENDPOINT = "/companies"
const AUTH_ENDPOINT = "/auth"
const TIMESTAMP_ENDPOINT = "/timestamps"
const REPORT_ENDPOINT = "/reports"

export const endpoints = {
    api_base_url: API_BASE_URL,
    users_enpoint: USERS_ENDPOINT,
    companies_endpoint: COMPANIES_ENDPOINT,
    auth_endpoint: AUTH_ENDPOINT,
    timestamp_endpoint: TIMESTAMP_ENDPOINT,
    reports_endpoint: REPORT_ENDPOINT,
    users: {
        create:     `${USERS_ENDPOINT}/create-user`,
        update:     `${USERS_ENDPOINT}/update-user`,
        remove:     `${USERS_ENDPOINT}/remove-user`,
        getActive:  `${USERS_ENDPOINT}/active`,
        getAll:     `${USERS_ENDPOINT}/`,
        getByEmail: `${USERS_ENDPOINT}/user-by-email`,
    },
    companies: {
        create:             `${COMPANIES_ENDPOINT}/create-company`,
        update:             `${COMPANIES_ENDPOINT}/update-company`,
        remove:             `${COMPANIES_ENDPOINT}/remove-company`,
        getActive:          `${COMPANIES_ENDPOINT}/active`,
        getAll:             `${COMPANIES_ENDPOINT}/`,
        getCompanyUsers:    `${COMPANIES_ENDPOINT}`,   //finish with /users
        getCompanyDetails:  `${COMPANIES_ENDPOINT}`,
        getCompanyAdmins:  `${COMPANIES_ENDPOINT}`,    // finish with /admins
    },
    auth: {
        login:  `${AUTH_ENDPOINT}/login`,
        verify: `${AUTH_ENDPOINT}/verify`,
        refresh: `${AUTH_ENDPOINT}/refresh`,
    },
    timestamps: {
        create:         `${TIMESTAMP_ENDPOINT}/`,                   // POST
        getAll:         `${TIMESTAMP_ENDPOINT}/`,                   // GET
        getRange:       `${TIMESTAMP_ENDPOINT}/getRange`,           // GET
        punchOut:       `${TIMESTAMP_ENDPOINT}/`,                   // PUT
        edit:           `${TIMESTAMP_ENDPOINT}`,                    // PUT - Require UUID
        punchInStatus:  `${TIMESTAMP_ENDPOINT}/punch_in_status`,    // GET
        delete:         `${TIMESTAMP_ENDPOINT}`,                    // DELETE
    },
    reports: {
        generateUser:         `${REPORT_ENDPOINT}/generate-user`,                 
        generateCompany:      `${REPORT_ENDPOINT}/generate_company`,                 
    }
};