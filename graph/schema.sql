-- GENIUS Home Graph Database Schema (SQLite)
-- Tracks hardware entities, acoustic incidents, action proposals, and warranties.

CREATE TABLE IF NOT EXISTS entities (
    id TEXT PRIMARY KEY,
    type TEXT NOT NULL,
    brand TEXT,
    model TEXT,
    location TEXT NOT NULL,
    lifecycle_state TEXT CHECK(lifecycle_state IN ('unknown', 'healthy', 'aging', 'end_of_life', 'replaced')) DEFAULT 'unknown',
    provenance TEXT NOT NULL,
    confidence REAL DEFAULT 1.0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS incidents (
    id TEXT PRIMARY KEY,
    entity_id TEXT NOT NULL,
    diagnosis TEXT NOT NULL,
    evidence_ref TEXT NOT NULL,
    severity TEXT CHECK(severity IN ('info', 'warning', 'critical')) DEFAULT 'warning',
    confidence REAL NOT NULL,
    provenance TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(entity_id) REFERENCES entities(id)
);

CREATE TABLE IF NOT EXISTS proposals (
    id TEXT PRIMARY KEY,
    incident_id TEXT,
    kind TEXT NOT NULL,
    payload TEXT NOT NULL,
    status TEXT CHECK(status IN ('proposed', 'confirmed', 'dismissed')) DEFAULT 'proposed',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(incident_id) REFERENCES incidents(id)
);

CREATE TABLE IF NOT EXISTS warranties (
    entity_id TEXT PRIMARY KEY,
    provider TEXT NOT NULL,
    start_date TEXT,
    end_date TEXT,
    claim_status TEXT DEFAULT 'none',
    FOREIGN KEY(entity_id) REFERENCES entities(id)
);

-- Seed initial home baseline
INSERT OR IGNORE INTO entities (id, type, brand, model, location, lifecycle_state, provenance, confidence) VALUES
('ent_smoke_kitchen', 'smoke_detector', 'First Alert', 'BRK-9120B', 'kitchen', 'healthy', 'manual_registration:user_input', 0.95),
('ent_furnace_basement', 'hvac_furnace', 'Carrier', 'Infinity 98', 'basement', 'aging', 'inspection_tag:photo_20260901', 0.90),
('ent_refrigerator_kitchen', 'refrigerator', 'Samsung', 'French Door', 'kitchen', 'healthy', 'device_discovery:smart_home_network', 0.95);
