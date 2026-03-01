-- Track incremental ingestion progress
CREATE TABLE IF NOT EXISTS ingestion_watermarks (
    source TEXT PRIMARY KEY,
    last_seen TEXT, -- Can be an ID, Timestamp, or ISO String
    updated_at TIMESTAMPTZ DEFAULT now()
);

-- (Optional) Analytics View for the "Recompute" task
CREATE OR REPLACE VIEW applicant_stats AS
SELECT 
    role, 
    count(*) as total_applicants, 
    avg(experience_years) as avg_experience 
FROM applicants 
GROUP BY role;