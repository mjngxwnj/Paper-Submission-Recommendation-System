-- Create role for Backend Application
CREATE ROLE app_backend WITH LOGIN PASSWORD 'backend';

-- Grain permission to connect database
GRANT CONNECT ON DATABASE rcm_papers TO app_backend;

-- Grain rules on the schema
GRANT SELECT ON ALL TABLES IN SCHEMA public TO app_backend;

