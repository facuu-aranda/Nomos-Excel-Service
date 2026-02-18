-- Migration: Add tables for storing Excel data
-- This approach uses metadata + JSONB rows instead of dynamic tables

-- Table to store metadata about Excel tables
CREATE TABLE IF NOT EXISTS data_tables_metadata (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workspace_id UUID NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,
    table_name TEXT NOT NULL,
    columns JSONB NOT NULL, -- Array of {name, type, nullable}
    row_count INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(workspace_id, table_name)
);

-- Table to store actual data rows
CREATE TABLE IF NOT EXISTS data_table_rows (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    table_id UUID NOT NULL REFERENCES data_tables_metadata(id) ON DELETE CASCADE,
    workspace_id UUID NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,
    row_number INTEGER NOT NULL,
    row_data JSONB NOT NULL, -- The actual row data as JSON
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(table_id, row_number)
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_data_tables_workspace ON data_tables_metadata(workspace_id);
CREATE INDEX IF NOT EXISTS idx_data_rows_table ON data_table_rows(table_id);
CREATE INDEX IF NOT EXISTS idx_data_rows_workspace ON data_table_rows(workspace_id);
CREATE INDEX IF NOT EXISTS idx_data_rows_number ON data_table_rows(table_id, row_number);

-- RLS Policies for data_tables_metadata
ALTER TABLE data_tables_metadata ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view their workspace tables"
    ON data_tables_metadata FOR SELECT
    USING (workspace_id IN (
        SELECT workspace_id FROM users_workspace 
        WHERE auth_user_id = auth.uid()
    ));

CREATE POLICY "Users can insert tables in their workspace"
    ON data_tables_metadata FOR INSERT
    WITH CHECK (workspace_id IN (
        SELECT workspace_id FROM users_workspace 
        WHERE auth_user_id = auth.uid()
    ));

CREATE POLICY "Users can update their workspace tables"
    ON data_tables_metadata FOR UPDATE
    USING (workspace_id IN (
        SELECT workspace_id FROM users_workspace 
        WHERE auth_user_id = auth.uid()
    ));

CREATE POLICY "Users can delete their workspace tables"
    ON data_tables_metadata FOR DELETE
    USING (workspace_id IN (
        SELECT workspace_id FROM users_workspace 
        WHERE auth_user_id = auth.uid()
    ));

-- RLS Policies for data_table_rows
ALTER TABLE data_table_rows ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view their workspace data"
    ON data_table_rows FOR SELECT
    USING (workspace_id IN (
        SELECT workspace_id FROM users_workspace 
        WHERE auth_user_id = auth.uid()
    ));

CREATE POLICY "Users can insert data in their workspace"
    ON data_table_rows FOR INSERT
    WITH CHECK (workspace_id IN (
        SELECT workspace_id FROM users_workspace 
        WHERE auth_user_id = auth.uid()
    ));

CREATE POLICY "Users can update their workspace data"
    ON data_table_rows FOR UPDATE
    USING (workspace_id IN (
        SELECT workspace_id FROM users_workspace 
        WHERE auth_user_id = auth.uid()
    ));

CREATE POLICY "Users can delete their workspace data"
    ON data_table_rows FOR DELETE
    USING (workspace_id IN (
        SELECT workspace_id FROM users_workspace 
        WHERE auth_user_id = auth.uid()
    ));

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_data_tables_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger for updated_at
CREATE TRIGGER data_tables_updated_at
    BEFORE UPDATE ON data_tables_metadata
    FOR EACH ROW
    EXECUTE FUNCTION update_data_tables_updated_at();

-- Comments
COMMENT ON TABLE data_tables_metadata IS 'Stores metadata about Excel tables uploaded by users';
COMMENT ON TABLE data_table_rows IS 'Stores actual data rows from Excel files as JSONB';
COMMENT ON COLUMN data_tables_metadata.columns IS 'Array of column definitions: [{name: string, type: string, nullable: boolean}]';
COMMENT ON COLUMN data_table_rows.row_data IS 'The actual row data as JSON object with column names as keys';
