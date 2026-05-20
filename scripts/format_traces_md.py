
import json

with open('audit_traces_last_10_days.json', 'r') as f:
    data = json.load(f)

markdown = "# Audit Traces - Last 10 Days\n\n"

markdown += "## Summary\n"
markdown += f"- **Execution Traces**: {len(data['execution_traces'])}\n"
markdown += f"- **Debates**: {len(data['debates'])}\n"
markdown += f"- **Arguments**: {len(data['arguments'])}\n\n"

markdown += "## Execution Traces\n"
for trace in data['execution_traces']:
    markdown += f"### Trace ID: {trace['id']}\n"
    markdown += f"- **Workflow ID**: {trace['workflow_id']}\n"
    markdown += f"- **Step**: {trace['step_name']}\n"
    markdown += f"- **Agent**: {trace['agent_name']}\n"
    markdown += f"- **Status**: {trace['status']}\n"
    markdown += f"- **Timestamp**: {trace['timestamp']}\n"
    markdown += f"- **Input**: {trace['input_data']}\n"
    markdown += f"- **Output**: {trace['output_data']}\n\n"

markdown += "## Debates\n"
for debate in data['debates']:
    markdown += f"### Debate ID: {debate['id']}\n"
    markdown += f"- **Objective**: {debate['objective']}\n"
    markdown += f"- **Consensus**: {debate['consensus_decision']}\n"
    markdown += f"- **Confidence**: {debate['confidence_score']}\n"
    markdown += f"- **Created At**: {debate['created_at']}\n"
    markdown += f"- **Reasoning**: {debate['reasoning_trace']}\n\n"
    
    # Filter arguments for this debate
    debate_args = [a for a in data['arguments'] if a['debate_id'] == debate['id']]
    if debate_args:
        markdown += "#### Arguments\n"
        for arg in debate_args:
            markdown += f"- **{arg['agent_name']}** ({'Pro' if arg['is_pro'] else 'Con'}, Conf: {arg['confidence_score']}): {arg['argument']}\n"
        markdown += "\n"

with open('docs/audit_traces_last_10_days.md', 'w') as f:
    f.write(markdown)

print("Generated docs/audit_traces_last_10_days.md")
