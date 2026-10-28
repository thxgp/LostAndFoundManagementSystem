"""
========================================================================================
LOST AND FOUND MANAGEMENT SYSTEM — REST API & WEB SERVER (PHASES 1 - 4)
Zero-dependency HTTP server utilizing Python's built-in http.server module.
Provides full REST JSON endpoints for the modern web UI and serves frontend static assets.
========================================================================================
"""

import os
import sys
import json
import sqlite3
import subprocess
import mimetypes
from datetime import datetime
from http.server import HTTPServer, SimpleHTTPRequestHandler
from socketserver import ThreadingMixIn
from urllib.parse import urlparse, parse_qs

class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    daemon_threads = True

# Configure standard streams for UTF-8 on Windows
if sys.platform == "win32":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")

# Ensure parent directory is in sys.path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from src.service import LostAndFoundService
from src.expression_parser import ExpressionParser
from src.models import ItemRecord, ClaimRecord, ItemStatus, ClaimStatus, ItemType
from config.db_config import SQLITE_DB_PATH

UI_DIR = os.path.join(BASE_DIR, "ui")
PORT = 8080

# Global service instance
service = LostAndFoundService(prefer_mysql=False)


class LFMSRequestHandler(SimpleHTTPRequestHandler):
    """Handles both REST API endpoints and UI static file serving."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=UI_DIR, **kwargs)

    def _set_headers(self, status=200, content_type="application/json"):
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, PUT, DELETE, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization")
        self.send_header("Cache-Control", "no-cache, no-store, must-revalidate")
        self.end_headers()

    def do_OPTIONS(self):
        self._set_headers(200)

    def _read_json_body(self):
        try:
            content_length = int(self.headers.get("Content-Length", 0))
            if content_length > 0:
                raw_data = self.rfile.read(content_length).decode("utf-8")
                return json.loads(raw_data)
        except Exception:
            pass
        return {}

    def _send_json(self, data, status=200):
        self._set_headers(status, "application/json")
        self.wfile.write(json.dumps(data, default=str).encode("utf-8"))

    def _get_sqlite_conn(self):
        conn = sqlite3.connect(SQLITE_DB_PATH)
        conn.row_factory = sqlite3.Row
        return conn

    # ---------------------------------------------------------
    # GET Endpoints
    # ---------------------------------------------------------
    def do_GET(self):
        parsed_url = urlparse(self.path)
        path = parsed_url.path
        query_params = parse_qs(parsed_url.query)

        # Static assets routing
        if not path.startswith("/api/"):
            if path == "/" or path == "":
                self.path = "/index.html"
            return super().do_GET()

        # API Routes
        try:
            if path == "/api/status":
                self._handle_get_status()
            elif path == "/api/items":
                self._handle_get_items(query_params)
            elif path.startswith("/api/items/"):
                item_id = int(path.split("/")[3])
                self._handle_get_item_by_id(item_id)
            elif path == "/api/claims":
                self._handle_get_claims(query_params)
            elif path == "/api/lockers":
                self._handle_get_lockers()
            elif path == "/api/audit":
                self._handle_get_audit()
            elif path == "/api/analytics":
                self._handle_get_analytics()
            elif path == "/api/locations":
                self._handle_get_locations()
            elif path == "/api/categories":
                self._handle_get_categories()
            elif path == "/api/views/active-found":
                self._handle_get_view("v_active_found_inventory")
            elif path == "/api/views/claim-queue":
                self._handle_get_view("v_claim_verification_queue")
            elif path == "/api/views/category-analytics":
                self._handle_get_view("v_category_analytics")
            else:
                self._send_json({"error": "Endpoint not found"}, 404)
        except Exception as e:
            self._send_json({"error": str(e)}, 500)

    # ---------------------------------------------------------
    # POST / DELETE Endpoints
    # ---------------------------------------------------------
    def do_POST(self):
        parsed_url = urlparse(self.path)
        path = parsed_url.path

        try:
            if path == "/api/items":
                self._handle_create_item()
            elif path.startswith("/api/items/") and path.endswith("/status"):
                item_id = int(path.split("/")[3])
                self._handle_update_item_status(item_id)
            elif path == "/api/claims":
                self._handle_create_claim()
            elif path == "/api/claims/verify":
                self._handle_verify_next_claim()
            elif path == "/api/claims/settle-atomic":
                self._handle_settle_atomic_claim()
            elif path == "/api/audit/undo":
                self._handle_undo_action()
            elif path == "/api/evaluate-formula":
                self._handle_evaluate_formula()
            elif path.startswith("/api/run-demo/"):
                phase = path.split("/")[-1]
                self._handle_run_demo(phase)
            else:
                self._send_json({"error": "Endpoint not found"}, 404)
        except Exception as e:
            self._send_json({"error": str(e)}, 500)

    def do_DELETE(self):
        parsed_url = urlparse(self.path)
        path = parsed_url.path

        try:
            if path.startswith("/api/items/"):
                item_id = int(path.split("/")[-1])
                self._handle_delete_item(item_id)
            else:
                self._send_json({"error": "Endpoint not found"}, 404)
        except Exception as e:
            self._send_json({"error": str(e)}, 500)

    # ---------------------------------------------------------
    # Handlers Implementation
    # ---------------------------------------------------------

    def _handle_get_status(self):
        conn = self._get_sqlite_conn()
        cur = conn.cursor()
        total_items = cur.execute("SELECT COUNT(*) FROM items").fetchone()[0]
        in_custody = cur.execute("SELECT COUNT(*) FROM items WHERE status = 'IN_CUSTODY'").fetchone()[0]
        pending_claims = cur.execute("SELECT COUNT(*) FROM claims WHERE claim_status = 'PENDING'").fetchone()[0]
        total_val = cur.execute("SELECT COALESCE(SUM(reward_or_value), 0) FROM items").fetchone()[0]
        returned_count = cur.execute("SELECT COUNT(*) FROM items WHERE status = 'VERIFIED_RETURNED'").fetchone()[0]
        conn.close()

        self._send_json({
            "status": "online",
            "db_type": service.db.db_type,
            "phases_completed": [1, 2, 3, 4],
            "metrics": {
                "total_items": total_items,
                "in_custody": in_custody,
                "pending_claims": pending_claims,
                "total_valuation": float(total_val),
                "reunited_count": returned_count,
                "queue_size": len(service.claim_queue),
                "undo_stack_size": len(service.undo_stack)
            }
        })

    def _handle_get_items(self, query_params):
        search_q = query_params.get("search", [""])[0].strip().lower()
        type_filter = query_params.get("type", [""])[0].strip().upper()
        status_filter = query_params.get("status", [""])[0].strip().upper()
        cat_filter = query_params.get("category", [""])[0].strip()

        conn = self._get_sqlite_conn()
        cur = conn.cursor()

        sql = """
            SELECT 
                i.item_id, i.title, i.category, i.description, i.item_type,
                i.location, i.status, i.reporter_name, i.reporter_contact,
                i.reward_or_value, i.reported_date, i.updated_at,
                sl.locker_code, sl.custody_start_date, sl.release_date
            FROM items i
            LEFT JOIN storage_lockers sl ON i.item_id = sl.item_id
            WHERE 1=1
        """
        params = []

        if type_filter:
            sql += " AND i.item_type = ?"
            params.append(type_filter)
        if status_filter:
            sql += " AND i.status = ?"
            params.append(status_filter)
        if cat_filter:
            sql += " AND i.category = ?"
            params.append(cat_filter)
        if search_q:
            sql += " AND (LOWER(i.title) LIKE ? OR LOWER(i.description) LIKE ? OR LOWER(i.location) LIKE ?)"
            term = f"%{search_q}%"
            params.extend([term, term, term])

        sql += " ORDER BY i.item_id DESC"
        cur.execute(sql, params)
        rows = cur.fetchall()

        items = []
        for r in rows:
            items.append({
                "item_id": r["item_id"],
                "title": r["title"],
                "category": r["category"],
                "description": r["description"],
                "item_type": r["item_type"],
                "location": r["location"],
                "status": r["status"],
                "reporter_name": r["reporter_name"],
                "reporter_contact": r["reporter_contact"],
                "reward_or_value": float(r["reward_or_value"]),
                "reported_date": str(r["reported_date"]),
                "updated_at": str(r["updated_at"]),
                "locker_code": r["locker_code"],
                "custody_start_date": str(r["custody_start_date"]) if r["custody_start_date"] else None,
                "release_date": str(r["release_date"]) if r["release_date"] else None
            })

        conn.close()
        self._send_json({"items": items, "count": len(items)})

    def _handle_get_item_by_id(self, item_id):
        conn = self._get_sqlite_conn()
        cur = conn.cursor()

        sql = """
            SELECT 
                i.item_id, i.title, i.category, i.description, i.item_type,
                i.location, i.status, i.reporter_name, i.reporter_contact,
                i.reward_or_value, i.reported_date, i.updated_at,
                sl.locker_code, sl.custody_start_date, sl.release_date, sl.remarks as locker_remarks
            FROM items i
            LEFT JOIN storage_lockers sl ON i.item_id = sl.item_id
            WHERE i.item_id = ?
        """
        cur.execute(sql, (item_id,))
        row = cur.fetchone()
        if not row:
            conn.close()
            self._send_json({"error": f"Item #{item_id} not found"}, 404)
            return

        cur.execute("""
            SELECT claim_id, claimant_name, claimant_contact, proof_description,
                   confidence_score, claim_status, submitted_at
            FROM claims WHERE item_id = ? ORDER BY claim_id DESC
        """, (item_id,))
        claims = [dict(c) for c in cur.fetchall()]

        cur.execute("""
            SELECT action_id, action_type, snapshot_before, snapshot_after, performed_at
            FROM audit_actions WHERE item_id = ? ORDER BY action_id DESC
        """, (item_id,))
        audit = [dict(a) for a in cur.fetchall()]

        conn.close()

        item_data = {
            "item_id": row["item_id"],
            "title": row["title"],
            "category": row["category"],
            "description": row["description"],
            "item_type": row["item_type"],
            "location": row["location"],
            "status": row["status"],
            "reporter_name": row["reporter_name"],
            "reporter_contact": row["reporter_contact"],
            "reward_or_value": float(row["reward_or_value"]),
            "reported_date": str(row["reported_date"]),
            "updated_at": str(row["updated_at"]),
            "locker_code": row["locker_code"],
            "custody_start_date": str(row["custody_start_date"]) if row["custody_start_date"] else None,
            "release_date": str(row["release_date"]) if row["release_date"] else None,
            "locker_remarks": row["locker_remarks"],
            "claims": claims,
            "audit_history": audit
        }
        self._send_json({"item": item_data})

    def _handle_get_claims(self, query_params):
        status_filter = query_params.get("status", [""])[0].strip().upper()
        conn = self._get_sqlite_conn()
        cur = conn.cursor()

        sql = """
            SELECT 
                c.claim_id, c.item_id, c.claimant_name, c.claimant_contact,
                c.proof_description, c.confidence_score, c.claim_status,
                c.submitted_at, i.title AS item_title, i.category AS item_category,
                i.status AS item_status, sl.locker_code
            FROM claims c
            JOIN items i ON c.item_id = i.item_id
            LEFT JOIN storage_lockers sl ON i.item_id = sl.item_id
            WHERE 1=1
        """
        params = []
        if status_filter:
            sql += " AND c.claim_status = ?"
            params.append(status_filter)

        sql += " ORDER BY c.submitted_at ASC"
        cur.execute(sql, params)
        rows = cur.fetchall()

        claims = []
        for r in rows:
            claims.append({
                "claim_id": r["claim_id"],
                "item_id": r["item_id"],
                "claimant_name": r["claimant_name"],
                "claimant_contact": r["claimant_contact"],
                "proof_description": r["proof_description"],
                "confidence_score": float(r["confidence_score"] or 0),
                "claim_status": r["claim_status"],
                "submitted_at": str(r["submitted_at"]),
                "item_title": r["item_title"],
                "item_category": r["item_category"],
                "item_status": r["item_status"],
                "locker_code": r["locker_code"]
            })
        conn.close()
        self._send_json({"claims": claims, "count": len(claims)})

    def _handle_get_lockers(self):
        conn = self._get_sqlite_conn()
        cur = conn.cursor()
        cur.execute("""
            SELECT 
                sl.locker_id, sl.locker_code, sl.item_id, sl.custody_start_date,
                sl.release_date, sl.remarks, i.title, i.category, i.status
            FROM storage_lockers sl
            LEFT JOIN items i ON sl.item_id = i.item_id
            ORDER BY sl.locker_code ASC
        """)
        rows = cur.fetchall()
        lockers = []
        now = datetime.now()

        for r in rows:
            days_held = 0
            if r["custody_start_date"]:
                try:
                    start_dt = datetime.strptime(str(r["custody_start_date"]).split()[0], "%Y-%m-%d")
                    end_dt = datetime.strptime(str(r["release_date"]).split()[0], "%Y-%m-%d") if r["release_date"] else now
                    days_held = max(0, (end_dt - start_dt).days)
                except Exception:
                    days_held = 0

            lockers.append({
                "locker_id": r["locker_id"],
                "locker_code": r["locker_code"],
                "item_id": r["item_id"],
                "item_title": r["title"],
                "category": r["category"],
                "status": r["status"],
                "custody_start_date": str(r["custody_start_date"]),
                "release_date": str(r["release_date"]) if r["release_date"] else None,
                "is_released": r["release_date"] is not None,
                "days_held": days_held,
                "remarks": r["remarks"]
            })

        conn.close()
        self._send_json({"lockers": lockers})

    def _handle_get_audit(self):
        conn = self._get_sqlite_conn()
        cur = conn.cursor()
        cur.execute("""
            SELECT action_id, item_id, action_type, snapshot_before, snapshot_after, performed_at
            FROM audit_actions
            ORDER BY action_id DESC
            LIMIT 50
        """)
        rows = cur.fetchall()
        actions = []
        for r in rows:
            snap_before = None
            snap_after = None
            try:
                snap_before = json.loads(r["snapshot_before"]) if r["snapshot_before"] else None
            except Exception:
                snap_before = r["snapshot_before"]
            try:
                snap_after = json.loads(r["snapshot_after"]) if r["snapshot_after"] else None
            except Exception:
                snap_after = r["snapshot_after"]

            actions.append({
                "action_id": r["action_id"],
                "item_id": r["item_id"],
                "action_type": r["action_type"],
                "snapshot_before": snap_before,
                "snapshot_after": snap_after,
                "performed_at": str(r["performed_at"])
            })

        conn.close()
        self._send_json({
            "history": actions,
            "undo_available": not service.undo_stack.is_empty(),
            "stack_size": len(service.undo_stack)
        })

    def _handle_get_analytics(self):
        conn = self._get_sqlite_conn()
        cur = conn.cursor()

        # Category analytics view
        cur.execute("SELECT * FROM v_category_analytics")
        cat_rows = cur.fetchall()
        cat_stats = [dict(r) for r in cat_rows]

        # Status breakdown
        cur.execute("SELECT status, COUNT(*) AS count FROM items GROUP BY status")
        status_rows = cur.fetchall()
        status_stats = {r["status"]: r["count"] for r in status_rows}

        # Item types
        cur.execute("SELECT item_type, COUNT(*) AS count FROM items GROUP BY item_type")
        type_rows = cur.fetchall()
        type_stats = {r["item_type"]: r["count"] for r in type_rows}

        conn.close()
        self._send_json({
            "categories": cat_stats,
            "status_distribution": status_stats,
            "type_distribution": type_stats
        })

    def _handle_get_locations(self):
        conn = self._get_sqlite_conn()
        cur = conn.cursor()
        cur.execute("SELECT * FROM locations ORDER BY building_name ASC")
        rows = [dict(r) for r in cur.fetchall()]
        conn.close()
        self._send_json({"locations": rows})

    def _handle_get_categories(self):
        conn = self._get_sqlite_conn()
        cur = conn.cursor()
        cur.execute("SELECT * FROM categories ORDER BY category_name ASC")
        rows = [dict(r) for r in cur.fetchall()]
        conn.close()
        self._send_json({"categories": rows})

    def _handle_get_view(self, view_name):
        conn = self._get_sqlite_conn()
        cur = conn.cursor()
        cur.execute(f"SELECT * FROM {view_name}")
        rows = [dict(r) for r in cur.fetchall()]
        conn.close()
        self._send_json({"view": view_name, "rows": rows, "count": len(rows)})

    # --- Mutations ---

    def _handle_create_item(self):
        body = self._read_json_body()
        required = ["title", "category", "description", "item_type", "location", "reporter_name", "reporter_contact"]
        for field in required:
            if not body.get(field):
                self._send_json({"error": f"Missing required field: {field}"}, 400)
                return

        new_record = service.report_item(body)

        # If it's a found item, allocate a locker in storage_lockers
        if new_record.item_type == "FOUND":
            conn = self._get_sqlite_conn()
            cur = conn.cursor()
            locker_code = f"LOCKER-W{new_record.item_id:03d}"
            cur.execute("""
                INSERT INTO storage_lockers (item_id, locker_code, custody_start_date, remarks)
                VALUES (?, ?, date('now'), ?)
            """, (new_record.item_id, locker_code, f"Auto-allocated upon intake of '{new_record.title}'"))
            conn.commit()
            conn.close()

        self._send_json({"success": True, "item": new_record.to_dict()}, 201)

    def _handle_update_item_status(self, item_id):
        body = self._read_json_body()
        new_status = body.get("status")
        if not new_status:
            self._send_json({"error": "status is required"}, 400)
            return

        success = service.update_item_status(item_id, new_status)
        if success:
            self._send_json({"success": True, "item_id": item_id, "status": new_status})
        else:
            self._send_json({"error": f"Item {item_id} not found"}, 404)

    def _handle_delete_item(self, item_id):
        deleted = service.delete_item(item_id)
        if deleted:
            self._send_json({"success": True, "deleted_item": deleted.to_dict()})
        else:
            self._send_json({"error": f"Item {item_id} not found"}, 404)

    def _handle_create_claim(self):
        body = self._read_json_body()
        item_id = body.get("item_id")
        claimant_name = body.get("claimant_name")
        claimant_contact = body.get("claimant_contact")
        proof_desc = body.get("proof_description")

        if not all([item_id, claimant_name, claimant_contact, proof_desc]):
            self._send_json({"error": "item_id, claimant_name, claimant_contact, proof_description are required"}, 400)
            return

        claim = service.submit_claim(int(item_id), claimant_name, claimant_contact, proof_desc)
        self._send_json({"success": True, "claim": claim.to_dict()}, 201)

    def _handle_verify_next_claim(self):
        body = self._read_json_body()
        formula = body.get("formula", "(desc_match * 0.40) + (serial_match * 0.40) + (photo_match * 0.20)")
        variables = body.get("variables", {
            "desc_match": 85.0,
            "serial_match": 95.0,
            "photo_match": 90.0
        })
        threshold = float(body.get("approve_threshold", 75.0))

        claim, score, decision = service.process_next_claim(formula, variables, threshold)
        if not claim:
            self._send_json({"error": decision}, 400)
            return

        self._send_json({
            "success": True,
            "claim": claim.to_dict(),
            "confidence_score": score,
            "decision": decision
        })

    def _handle_settle_atomic_claim(self):
        """
        Phase 4 Demonstration: Atomically settles a claim, updates item status to VERIFIED_RETURNED,
        releases the storage locker, and logs an immutable audit snapshot in a single ACID transaction.
        """
        body = self._read_json_body()
        claim_id = int(body.get("claim_id", 0))
        item_id = int(body.get("item_id", 0))
        confidence_score = float(body.get("confidence_score", 95.0))
        decision = body.get("decision", "APPROVED")  # "APPROVED" or "REJECTED"

        conn = self._get_sqlite_conn()
        cur = conn.cursor()

        try:
            cur.execute("BEGIN TRANSACTION;")

            # 1. Update claim status
            cur.execute("""
                UPDATE claims 
                SET claim_status = ?, confidence_score = ?
                WHERE claim_id = ?
            """, (decision, confidence_score, claim_id))

            if decision == "APPROVED":
                # 2. Update item status to VERIFIED_RETURNED
                cur.execute("""
                    UPDATE items
                    SET status = 'VERIFIED_RETURNED', updated_at = datetime('now')
                    WHERE item_id = ?
                """, (item_id,))

                # 3. Release storage locker
                cur.execute("""
                    UPDATE storage_lockers
                    SET release_date = date('now'), remarks = 'Identity verified and handed over to claimant'
                    WHERE item_id = ? AND release_date IS NULL
                """, (item_id,))

                action_type = "CLAIM_VERIFIED_AND_RELEASED"
            else:
                # Revert item status to IN_CUSTODY
                cur.execute("""
                    UPDATE items
                    SET status = 'IN_CUSTODY', updated_at = datetime('now')
                    WHERE item_id = ?
                """, (item_id,))
                action_type = "CLAIM_REJECTED"

            # 4. Insert audit action
            snap_before = json.dumps({"status": "CLAIM_PENDING", "claim_id": claim_id})
            snap_after = json.dumps({"status": "VERIFIED_RETURNED" if decision == "APPROVED" else "IN_CUSTODY", "confidence_score": confidence_score})
            cur.execute("""
                INSERT INTO audit_actions (item_id, action_type, snapshot_before, snapshot_after, performed_at)
                VALUES (?, ?, ?, ?, datetime('now'))
            """, (item_id, action_type, snap_before, snap_after))

            conn.commit()

            # Synchronize in-memory service
            in_mem_item = service.item_list.search_by_id(item_id)
            if in_mem_item:
                in_mem_item.status = "VERIFIED_RETURNED" if decision == "APPROVED" else "IN_CUSTODY"

            self._send_json({
                "success": True,
                "message": f"ACID Transaction committed: Claim #{claim_id} {decision} for Item #{item_id}",
                "transaction_status": "COMMITTED"
            })
        except Exception as e:
            conn.rollback()
            self._send_json({"error": f"ACID Transaction aborted & rolled back: {str(e)}"}, 500)
        finally:
            conn.close()

    def _handle_undo_action(self):
        result = service.undo_last_action()
        if result:
            self._send_json({"success": True, "message": result})
        else:
            self._send_json({"error": "Undo stack is empty."}, 400)

    def _handle_evaluate_formula(self):
        body = self._read_json_body()
        formula = body.get("formula", "")
        variables = body.get("variables", {})

        if not formula:
            self._send_json({"error": "Formula string is required."}, 400)
            return

        try:
            postfix = ExpressionParser.infix_to_postfix(formula)
            result = ExpressionParser.evaluate(formula, variables)
            self._send_json({
                "formula": formula,
                "variables": variables,
                "postfix": " ".join(postfix),
                "result": result
            })
        except Exception as e:
            self._send_json({"error": str(e)}, 400)

    def _handle_run_demo(self, phase):
        py_bin = r"C:\Users\spsid\AppData\Local\Python\bin\python.exe"
        if not os.path.exists(py_bin):
            py_bin = sys.executable

        script_map = {
            "phase1": os.path.join(BASE_DIR, "main.py"),
            "phase2": os.path.join(BASE_DIR, "phase2_demo.py"),
            "phase3": os.path.join(BASE_DIR, "phase3_demo.py"),
            "phase4": os.path.join(BASE_DIR, "phase4_demo.py")
        }

        if phase not in script_map:
            self._send_json({"error": f"Invalid demo phase: {phase}"}, 400)
            return

        script_path = script_map[phase]
        try:
            if phase == "phase1":
                # Run automated demo function non-interactively
                cmd = [py_bin, "-c", "from src.service import LostAndFoundService; from main import run_automated_demo; run_automated_demo(LostAndFoundService(prefer_mysql=False))"]
            else:
                cmd = [py_bin, script_path]

            res = subprocess.run(
                cmd,
                cwd=BASE_DIR,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                timeout=30
            )

            self._send_json({
                "phase": phase,
                "exit_code": res.returncode,
                "output": res.stdout,
                "error": res.stderr
            })
        except Exception as e:
            self._send_json({"error": f"Failed running {phase}: {str(e)}"}, 500)


def start_server():
    server_address = ("", PORT)
    httpd = ThreadedHTTPServer(server_address, LFMSRequestHandler)
    print("\n=======================================================")
    print("  [+] LOST AND FOUND SYSTEM - WEB SERVER ACTIVE")
    print(f"  Local URL: http://localhost:{PORT}")
    print(f"  Database : {service.db.db_type}")
    print(f"  Web Root : {UI_DIR}")
    print("=======================================================\n")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down server.")
        httpd.server_close()


if __name__ == "__main__":
    start_server()
