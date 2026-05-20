import json
import sys
import argparse
from typing import List, Dict, Any


def monitor_logs(log_file: str, patterns_file: str):
    """
    Implements the Zero Script QA verification logic.
    Reads logs and checks if defined patterns are satisfied.
    """
    with open(patterns_file, "r") as f:
        patterns_data = json.load(f)

    features = patterns_data.get("features", [])
    results = {f["name"]: {"satisfied": False, "found_patterns": []} for f in features}

    print(f"[*] Starting Zero Script QA Monitor...")
    print(f"[*] Patterns loaded from: {patterns_file}")
    print(f"[*] Analyzing logs from: {log_file if log_file != '-' else 'STDIN'}")

    log_stream = sys.stdin if log_file == "-" else open(log_file, "r")

    for line in log_stream:
        try:
            log_entry = json.loads(line)
            
            for feature in features:
                feature_name = feature["name"]
                feature_patterns = feature["patterns"]
                
                # Check if this log entry matches any pattern for this feature
                for pattern in feature_patterns:
                    match = True
                    for key, value in pattern.items():
                        if log_entry.get(key) != value:
                            match = False
                            break
                    
                    if match:
                        if pattern not in results[feature_name]["found_patterns"]:
                            results[feature_name]["found_patterns"].append(pattern)
                        
                        # Check if all patterns for this feature are now found
                        if len(results[feature_name]["found_patterns"]) == len(feature_patterns):
                            if not results[feature_name]["satisfied"]:
                                print(f"[+] Feature '{feature_name}' VERIFIED.")
                                results[feature_name]["satisfied"] = True
        except json.JSONDecodeError:
            continue
        except Exception as e:
            print(f"[!] Error processing log line: {e}")

    # Final Report
    print("\n" + "="*40)
    print("ZERO SCRIPT QA REPORT")
    print("="*40)
    
    all_passed = True
    for feature_name, data in results.items():
        status = "PASSED" if data["satisfied"] else "FAILED"
        if not data["satisfied"]:
            all_passed = False
        
        print(f"Feature: {feature_name} -> {status}")
        if not data["satisfied"]:
            missing = []
            # Find which patterns are missing
            feature = next(f for f in features if f["name"] == feature_name)
            for p in feature["patterns"]:
                if p not in data["found_patterns"]:
                    missing.append(p)
            print(f"  Missing patterns: {missing}")
            
    print("="*40)
    if all_passed:
        print("[SUCCESS] All features verified via log patterns.")
        sys.exit(0)
    else:
        print("[FAILURE] Some features failed verification.")
        sys.exit(1)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Zero Script QA Monitor")
    parser.add_argument("--logs", default="-", help="Path to log file or '-' for STDIN")
    parser.add_argument("--patterns", default="qa/patterns.json", help="Path to patterns file")
    
    args = parser.parse_args()
    monitor_logs(args.logs, args.patterns)
