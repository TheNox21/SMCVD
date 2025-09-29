"""
Job model for persisting analysis jobs
"""
import json
import sqlite3
import os
from datetime import datetime
from typing import Dict, Any, Optional

class JobStorage:
    def __init__(self, db_path: str = "smcvd.db"):
        self.db_path = db_path
        self._init_db()
    
    def _init_db(self):
        """Initialize the database schema"""
        conn = sqlite3.connect(self.db_path)
        try:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS analysis_jobs (
                    job_id TEXT PRIMARY KEY,
                    status TEXT NOT NULL,
                    progress INTEGER DEFAULT 0,
                    message TEXT,
                    vulnerabilities TEXT,
                    files_analyzed INTEGER DEFAULT 0,
                    total_files INTEGER DEFAULT 0,
                    program_scope TEXT,
                    overall_assessment TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            conn.commit()
        finally:
            conn.close()
    
    def save_job(self, job_id: str, job_data: Dict[str, Any]):
        """Save or update a job"""
        conn = sqlite3.connect(self.db_path)
        try:
            # Convert complex objects to JSON strings
            vulnerabilities_json = json.dumps(job_data.get('vulnerabilities', []))
            program_scope_json = json.dumps(job_data.get('program_scope', {}))
            overall_assessment_json = json.dumps(job_data.get('overall_assessment', {}))
            
            conn.execute('''
                INSERT OR REPLACE INTO analysis_jobs 
                (job_id, status, progress, message, vulnerabilities, files_analyzed, 
                 total_files, program_scope, overall_assessment, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            ''', (
                job_id,
                job_data.get('status', 'initializing'),
                job_data.get('progress', 0),
                job_data.get('message', ''),
                vulnerabilities_json,
                job_data.get('files_analyzed', 0),
                job_data.get('total_files', 0),
                program_scope_json,
                overall_assessment_json
            ))
            conn.commit()
        finally:
            conn.close()
    
    def get_job(self, job_id: str) -> Optional[Dict[str, Any]]:
        """Get job by ID"""
        conn = sqlite3.connect(self.db_path)
        try:
            cursor = conn.execute(
                'SELECT * FROM analysis_jobs WHERE job_id = ?', 
                (job_id,)
            )
            row = cursor.fetchone()
            
            if not row:
                return None
            
            columns = [desc[0] for desc in cursor.description]
            job_data = dict(zip(columns, row))
            
            # Parse JSON fields
            job_data['vulnerabilities'] = json.loads(job_data['vulnerabilities'] or '[]')
            job_data['program_scope'] = json.loads(job_data['program_scope'] or '{}')
            job_data['overall_assessment'] = json.loads(job_data['overall_assessment'] or '{}')
            
            return job_data
        finally:
            conn.close()
    
    def cleanup_old_jobs(self, days: int = 7):
        """Remove jobs older than specified days"""
        conn = sqlite3.connect(self.db_path)
        try:
            conn.execute('''
                DELETE FROM analysis_jobs 
                WHERE created_at < datetime('now', '-{} days')
            '''.format(days))
            conn.commit()
        finally:
            conn.close()
