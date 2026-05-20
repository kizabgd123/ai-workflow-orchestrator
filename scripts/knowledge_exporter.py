import os
import json
import re
from datetime import datetime, timedelta

def parse_logs(log_path, days=10):
    now = datetime.utcnow()
    limit = now - timedelta(days=days)
    
    events = []
    if os.path.exists(log_path):
        with open(log_path, 'r') as f:
            try:
                data = json.load(f)
                for entry in data:
                    ts_str = entry.get('timestamp')
                    if ts_str:
                        ts = datetime.strptime(ts_str.replace('Z', '+0000'), '%Y-%m-%dT%H:%M:%S.%f%z').replace(tzinfo=None)
                        if ts >= limit:
                            events.append(entry)
            except Exception as e:
                pass
    return events

def parse_sessions(chats_dir, days=10):
    now = datetime.utcnow()
    limit = now - timedelta(days=days)
    
    artifacts = []
    if os.path.exists(chats_dir):
        for filename in os.listdir(chats_dir):
            if filename.endswith('.jsonl'):
                file_path = os.path.join(chats_dir, filename)
                with open(file_path, 'r') as f:
                    for line in f:
                        try:
                            msg = json.loads(line)
                            ts_str = msg.get('timestamp')
                            if ts_str:
                                ts = datetime.strptime(ts_str.replace('Z', '+0000'), '%Y-%m-%dT%H:%M:%S.%f%z').replace(tzinfo=None)
                                if ts < limit:
                                    continue
                            
                            # Extract meaningful content
                            if msg.get('type') == 'gemini':
                                # Check for high-value keywords in thoughts or content
                                content = msg.get('content', '')
                                thoughts = msg.get('thoughts', [])
                                thought_txt = " ".join([t.get('description', '') for t in thoughts])
                                
                                if any(kw in (content + thought_txt) for kw in ["REASONING TRACE", "Final Decision", "Consensus", "Implementation", "Refinement", "Hardening"]):
                                    artifacts.append({
                                        "source": filename,
                                        "timestamp": ts_str,
                                        "type": "assistant_reasoning",
                                        "thoughts": thoughts,
                                        "content": content
                                    })
                            elif msg.get('type') == 'user':
                                content = msg.get('content', '')
                                if len(content) > 10: # Only save substantial user prompts
                                    artifacts.append({
                                        "source": filename,
                                        "timestamp": ts_str,
                                        "type": "user_instruction",
                                        "content": content
                                    })
                        except:
                            continue
    return artifacts

def main():
    temp_dir = "/home/kizabgd/.gemini/tmp/ai-workflow-orchestrator-project"
    logs_path = os.path.join(temp_dir, "logs.json")
    chats_dir = os.path.join(temp_dir, "chats")
    
    logs = parse_logs(logs_path)
    sessions = parse_sessions(chats_dir)
    
    continuity = ""
    if os.path.exists("CONTINUITY.md"):
        with open("CONTINUITY.md", "r") as f:
            continuity = f.read()
            
    export_data = {
        "project": "AI Workflow Orchestrator",
        "export_date": datetime.utcnow().isoformat(),
        "summary": "High-value reasoning and activity from the last 10 days.",
        "working_memory": continuity,
        "session_artifacts": sessions,
        "raw_logs": logs
    }
    
    output_file = "knowledge_export.json"
    with open(output_file, "w") as f:
        json.dump(export_data, f, indent=2)
    
    print(f"Exported {len(logs)} log entries and {len(sessions)} session artifacts to {output_file}")

if __name__ == "__main__":
    main()
