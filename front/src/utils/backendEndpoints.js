import { timestamp } from "@antfu/utils";

const API_BASE_URL = 'http://localhost:3000/api'; // Or your actual base URL
const USERS_ENDPOINT = "/users"
const COMPANIES_ENDPOINT = "/companies"
const AUTH_ENDPOINT = "/auth"
const TIMESTAMP_ENDPOINT = "/timestamps"

export const endpoints = {
    api_base_url: API_BASE_URL,
    users_enpoint: USERS_ENDPOINT,
    companies_endpoint: COMPANIES_ENDPOINT,
    auth_endpoint: AUTH_ENDPOINT,
    timestamp_endpoint: TIMESTAMP_ENDPOINT,
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
        getCompanyUsers:    `${COMPANIES_ENDPOINT}/users`,
        getCompanyDetails:  `${COMPANIES_ENDPOINT}`,
    },
    auth: {
        login:  `${AUTH_ENDPOINT}/login`,
        verify: `${AUTH_ENDPOINT}/verify`,
        refresh: `${AUTH_ENDPOINT}/refresh`,
    },
    timestamps: {
        create:         `${TIMESTAMP_ENDPOINT}/`,
        getAll:         `${TIMESTAMP_ENDPOINT}/`,
        punchOut:       `${TIMESTAMP_ENDPOINT}/punch_out`,
        punchInStatus:  `${TIMESTAMP_ENDPOINT}/punch_in_status`, // New endpoint
        delete:         `${TIMESTAMP_ENDPOINT}/`, // Assuming this is for deleting a timestamp
        workTimeToday:  `${TIMESTAMP_ENDPOINT}/work_time_today`,
    }
};