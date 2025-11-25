-- Create schema for warehouse
CREATE SCHEMA IF NOT EXISTS core AUTHORIZATION admin;
CREATE SCHEMA IF NOT EXISTS feature AUTHORIZATION admin;

-- Add comments
COMMENT ON SCHEMA core IS 'Curated schema for data warehouse analytical queries';
COMMENT ON SCHEMA feature IS 'ML-ready schema for feature engineering and embeddings';

