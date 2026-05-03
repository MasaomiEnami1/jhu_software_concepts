-- MODULE 6: DATABASE INITIALIZATION
-- This order is critical: Tables MUST exist before Views reference them.

-- 1. Drop existing structures for idempotency (clean starts)
DROP VIEW IF EXISTS applicant_summary;
DROP TABLE IF EXISTS applicants;

-- 2. Create the Table (The base object)
CREATE TABLE applicants (
    id SERIAL PRIMARY KEY,
    program VARCHAR(255),
    university VARCHAR(255),
    degree VARCHAR(50),
    status VARCHAR(50),
    gpa NUMERIC(3, 2),
    term VARCHAR(20),
    date_added TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 3. Create the View (Depends on the table above)
CREATE VIEW applicant_summary AS
SELECT 
    university, 
    COUNT(*) as total_apps, 
    AVG(gpa) as average_gpa
FROM applicants
GROUP BY university;