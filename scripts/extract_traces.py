
import sqlite3
import json
from datetime import datetime, timedelta

db_path = 'memory/orchestrator_memory.db'
conn = sqlite3.connect(db_path)
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

# Calculate date 10 days ago
ten_days_ago = (datetime.now() - timedelta(days=10)).isoformat()

data = {
    "execution_traces": [],
    "debates": [],
    "arguments": []
}

# Fetch execution traces
cursor.execute("SELECT * FROM execution_traces WHERE timestamp >= ?", (ten_days_ago,))
data["execution_traces"] = [dict(row) for row in cursor.fetchall()]

# Fetch debates
cursor.execute("SELECT * FROM debates WHERE created_at >= ?", (ten_days_ago,))
data["debates"] = [dict(row) for row in cursor.fetchall()]

# Fetch arguments (linked to debates or just by date)
cursor.execute("SELECT * FROM arguments WHERE created_at >= ?", (ten_days_ago,))
data["arguments"] = [dict(row) for row in cursor.fetchall()]

with open('audit_traces_last_10_days.json', 'w') as f:
    json.dump(data, f, indent=2)

print(f"Extracted {len(data['execution_traces'])} traces, {len(data['debates'])} debates, and {len(data['arguments'])} arguments.")
conn.close()
