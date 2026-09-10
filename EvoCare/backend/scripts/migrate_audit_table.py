import sqlite3

def migrate():
    conn = sqlite3.connect('evocare.db')
    cursor = conn.cursor()
    cols = [r[1] for r in cursor.execute('PRAGMA table_info(audit_logs)').fetchall()]
    needed = [
        ('event_id', 'VARCHAR(100)'),
        ('user_id', 'INTEGER'),
        ('username', 'VARCHAR(100)'),
        ('role', 'VARCHAR(50)'),
        ('patient_id', 'VARCHAR(50)'),
        ('resource_type', 'VARCHAR(100) DEFAULT "GENERAL"'),
        ('resource_id', 'VARCHAR(100)'),
        ('ip_address', 'VARCHAR(50)'),
        ('user_agent', 'VARCHAR(255)'),
        ('result', 'VARCHAR(50) DEFAULT "SUCCESS"'),
        ('reason', 'TEXT'),
        ('metadata_json', 'JSON'),
        ('correlation_id', 'VARCHAR(100)')
    ]
    for col_name, col_type in needed:
        if col_name not in cols:
            cursor.execute(f'ALTER TABLE audit_logs ADD COLUMN {col_name} {col_type}')
            print(f'Added column {col_name}')
    conn.commit()
    conn.close()
    print('AuditLog table migration complete!')

if __name__ == '__main__':
    migrate()
