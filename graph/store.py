"""
Home Graph SQLite Data Store
Maintains the persistent mental model of the home:
- Hardware entities & lifecycle states
- Acoustic incident history with verifiable data provenance
- Non-executing action proposals awaiting user authorization
"""

import sqlite3
import os
import json
import logging
import datetime
from typing import Dict, Any, List, Optional

logger = logging.getLogger("genius.graph.store")
DB_PATH = os.path.join(os.path.dirname(__file__), "..", "home_graph.db")
SCHEMA_PATH = os.path.join(os.path.dirname(__file__), "schema.sql")


class HomeGraphStore:
    def __init__(self, db_path: str = DB_PATH):
        self.db_path = db_path
        self._init_db()

    def _get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self):
        """Initializes database schema and seed baseline if not present."""
        if os.path.exists(SCHEMA_PATH):
            with open(SCHEMA_PATH, "r", encoding="utf-8") as f:
                schema_sql = f.read()
            with self._get_connection() as conn:
                conn.executescript(schema_sql)
                conn.commit()

    def upsert_entity(
        self,
        entity_id: str,
        entity_type: str,
        brand: str,
        model: str,
        location: str,
        lifecycle_state: str,
        provenance: str,
        confidence: float = 1.0
    ) -> Dict[str, Any]:
        """Creates or updates a hardware entity with strict provenance tracking."""
        now = datetime.datetime.now(datetime.timezone.utc).isoformat()
        with self._get_connection() as conn:
            conn.execute("""
                INSERT INTO entities (id, type, brand, model, location, lifecycle_state, provenance, confidence, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(id) DO UPDATE SET
                    type=excluded.type,
                    brand=excluded.brand,
                    model=excluded.model,
                    location=excluded.location,
                    lifecycle_state=excluded.lifecycle_state,
                    provenance=excluded.provenance,
                    confidence=excluded.confidence,
                    updated_at=excluded.updated_at
            """, (entity_id, entity_type, brand, model, location, lifecycle_state, provenance, confidence, now))
            conn.commit()

        return self.get_entity(entity_id)

    def get_entity(self, entity_id: str) -> Optional[Dict[str, Any]]:
        with self._get_connection() as conn:
            cur = conn.execute("SELECT * FROM entities WHERE id = ?", (entity_id,))
            row = cur.fetchone()
            return dict(row) if row else None

    def list_entities(
        self,
        entity_type: Optional[str] = None,
        lifecycle_state: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        query = "SELECT * FROM entities WHERE 1=1"
        params = []
        if entity_type:
            query += " AND type = ?"
            params.append(entity_type)
        if lifecycle_state:
            query += " AND lifecycle_state = ?"
            params.append(lifecycle_state)
        query += " ORDER BY updated_at DESC"

        with self._get_connection() as conn:
            cur = conn.execute(query, params)
            return [dict(row) for row in cur.fetchall()]

    def record_incident(
        self,
        entity_id: str,
        diagnosis: str,
        evidence_ref: str,
        severity: str = "warning",
        confidence: float = 0.95,
        provenance: str = "acoustic_dsp"
    ) -> Dict[str, Any]:
        """Records an incident against an entity in the graph."""
        incident_id = f"inc_{datetime.datetime.now().strftime('%Y%m%d')}_{os.urandom(3).hex()}"
        now = datetime.datetime.now(datetime.timezone.utc).isoformat()
        with self._get_connection() as conn:
            conn.execute("""
                INSERT INTO incidents (id, entity_id, diagnosis, evidence_ref, severity, confidence, provenance, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (incident_id, entity_id, diagnosis, evidence_ref, severity, confidence, provenance, now))
            conn.commit()

        return {
            "incident_id": incident_id,
            "entity_id": entity_id,
            "diagnosis": diagnosis,
            "evidence_ref": evidence_ref,
            "severity": severity,
            "confidence": confidence,
            "provenance": provenance,
            "created_at": now
        }

    def list_incidents(self, entity_id: Optional[str] = None) -> List[Dict[str, Any]]:
        query = "SELECT * FROM incidents"
        params = []
        if entity_id:
            query += " WHERE entity_id = ?"
            params.append(entity_id)
        query += " ORDER BY created_at DESC"

        with self._get_connection() as conn:
            cur = conn.execute(query, params)
            return [dict(row) for row in cur.fetchall()]

    def create_proposal(
        self,
        incident_id: Optional[str],
        kind: str,
        payload: Dict[str, Any],
        proposal_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Creates a non-executing proposal in the graph."""
        prop_id = proposal_id or f"prop_{os.urandom(4).hex()}"
        payload_str = json.dumps(payload)
        now = datetime.datetime.now(datetime.timezone.utc).isoformat()

        with self._get_connection() as conn:
            conn.execute("""
                INSERT INTO proposals (id, incident_id, kind, payload, status, created_at, updated_at)
                VALUES (?, ?, ?, ?, 'proposed', ?, ?)
                ON CONFLICT(id) DO UPDATE SET
                    incident_id=excluded.incident_id,
                    kind=excluded.kind,
                    payload=excluded.payload,
                    status='proposed',
                    updated_at=excluded.updated_at
            """, (prop_id, incident_id, kind, payload_str, now, now))
            conn.commit()

        return {
            "proposal_id": prop_id,
            "incident_id": incident_id,
            "kind": kind,
            "payload": payload,
            "status": "proposed",
            "created_at": now
        }

    def confirm_proposal(self, proposal_id: str, confirmed: bool = True) -> Dict[str, Any]:
        """Transitions proposal to confirmed or dismissed."""
        status = "confirmed" if confirmed else "dismissed"
        now = datetime.datetime.now(datetime.timezone.utc).isoformat()

        with self._get_connection() as conn:
            conn.execute("""
                UPDATE proposals SET status = ?, updated_at = ? WHERE id = ?
            """, (status, now, proposal_id))
            conn.commit()

            cur = conn.execute("SELECT * FROM proposals WHERE id = ?", (proposal_id,))
            row = cur.fetchone()
            if not row:
                return {"error": "Proposal not found", "proposal_id": proposal_id}
            
            prop = dict(row)
            prop["payload"] = json.loads(prop["payload"])
            return prop

    def get_home_health(self) -> Dict[str, Any]:
        """Computes live home health scorecard from current graph state."""
        entities = self.list_entities()
        total = len(entities)
        healthy = sum(1 for e in entities if e["lifecycle_state"] == "healthy")
        aging = sum(1 for e in entities if e["lifecycle_state"] == "aging")
        eol = sum(1 for e in entities if e["lifecycle_state"] == "end_of_life")

        incidents = self.list_incidents()
        critical_incidents = [i for i in incidents if i["severity"] == "critical"]

        # Health score calculation (100 base, -25 for EOL, -10 for aging)
        score = max(0, min(100, 100 - (eol * 25) - (aging * 10)))

        summary = f"{healthy} devices healthy."
        if eol > 0:
            summary = f"{eol} critical device reached end-of-life; {aging} aging system. Attention required."

        return {
            "health_score": score,
            "summary": summary,
            "metrics": {
                "total_monitored_devices": total,
                "healthy_count": healthy,
                "aging_count": aging,
                "end_of_life_count": eol,
                "open_incidents": len(critical_incidents)
            },
            "recent_incidents": [dict(i) for i in incidents[:3]],
            "card_payload": {
                "template": "mcp.apps.card.home_health",
                "title": "Home Health Overview",
                "accent_color": "#FF9900" if score < 90 else "#00C853",
                "score": score,
                "gauges": [
                    {"label": "Healthy", "value": healthy, "color": "#00A86B"},
                    {"label": "Aging", "value": aging, "color": "#F4B400"},
                    {"label": "End of Life", "value": eol, "color": "#DB4437"}
                ]
            }
        }

    def upsert_warranty(
        self,
        entity_id: str,
        provider: str,
        start_date: str,
        end_date: str,
        claim_status: str = "none"
    ) -> Dict[str, Any]:
        """Registers or updates warranty coverage for a hardware entity."""
        with self._get_connection() as conn:
            conn.execute("""
                INSERT INTO warranties (entity_id, provider, start_date, end_date, claim_status)
                VALUES (?, ?, ?, ?, ?)
                ON CONFLICT(entity_id) DO UPDATE SET
                    provider=excluded.provider,
                    start_date=excluded.start_date,
                    end_date=excluded.end_date,
                    claim_status=excluded.claim_status
            """, (entity_id, provider, start_date, end_date, claim_status))
            conn.commit()

        return self.get_warranty(entity_id)

    def get_warranty(self, entity_id: str) -> Optional[Dict[str, Any]]:
        with self._get_connection() as conn:
            cur = conn.execute("SELECT * FROM warranties WHERE entity_id = ?", (entity_id,))
            row = cur.fetchone()
            return dict(row) if row else None

    def list_warranties(self) -> List[Dict[str, Any]]:
        """Returns all registered warranties joined with entity details."""
        query = """
            SELECT w.entity_id, w.provider, w.start_date, w.end_date, w.claim_status,
                   e.type, e.brand, e.model, e.location, e.lifecycle_state
            FROM warranties w
            JOIN entities e ON w.entity_id = e.id
            ORDER BY w.end_date ASC
        """
        with self._get_connection() as conn:
            cur = conn.execute(query)
            return [dict(row) for row in cur.fetchall()]

    def update_warranty_claim(self, entity_id: str, claim_status: str) -> Dict[str, Any]:
        with self._get_connection() as conn:
            conn.execute("UPDATE warranties SET claim_status = ? WHERE entity_id = ?", (claim_status, entity_id))
            conn.commit()
        return self.get_warranty(entity_id)


# Singleton graph store instance
GRAPH_STORE = HomeGraphStore()
