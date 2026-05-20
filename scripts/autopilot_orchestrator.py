#!/usr/bin/env python3
"""
AutoPilot Orchestrator — Conversational Task Supervisor for AI Workflow Orchestrator
Bridges the cm-autopilot pattern with the multi-agent debate engine.
"""

import sys
import os
import asyncio
import time
from pathlib import Path

# Add project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.prompt import Prompt
    from rich.progress import Progress, SpinnerColumn, TextColumn
    from rich.table import Table
except ImportError:
    print("Please install rich package: pip install rich")
    sys.exit(1)

from core.identity import enforce_identity
from core.types import AgentRole
from orchestrator.engine import WorkflowOrchestrator

console = Console()

def show_welcome():
    console.print(Panel.fit(
        "[bold magenta]🚀 Welcome to AI Workflow Orchestrator AutoPilot[/bold magenta]\n"
        "[dim]An opinionated conversational task supervisor powered by Adversarial Consensus.[/dim]\n\n"
        "Enter your high-level goal, and AutoPilot will plan, split,\n"
        "and route sub-tasks through the Multi-Agent Debate Engine.",
        title="AutoPilot v1.0", border_style="magenta"
    ))

async def run_autopilot_loop():
    # Enforce identity guard
    try:
        enforce_identity()
    except Exception as e:
        console.print(f"[bold red]Security Block:[/bold red] {e}")
        sys.exit(1)

    orchestrator = WorkflowOrchestrator()
    show_welcome()

    while True:
        try:
            user_input = Prompt.ask("\n[bold green]What complex workflow would you like to execute?[/bold green] (type 'exit' to quit)")
            if user_input.lower() in ("exit", "quit", "q"):
                break
            
            if not user_input.strip():
                continue

            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                transient=True
            ) as progress:
                progress.add_task("Analyzing intent and parsing sub-tasks...", total=None)
                await asyncio.sleep(1.5)  # Simulate planning phase
                
                # Simple heuristic sub-task generator for demonstration parity with cm-autopilot
                # In full integration, the Analyst agent decomposes this.
                lower_input = user_input.lower()
                if "deploy" in lower_input or "service" in lower_input:
                    tasks = [
                        "Decompose GCP VPC and firewall boundary setup for secure hosting",
                        "Evaluate Lua-scripted admission validation logic inside Redis engine",
                        "Deploy safe schema definitions with Row-Level Security rules"
                    ]
                elif "security" in lower_input or "audit" in lower_input:
                    tasks = [
                        "Analyze IAM permission model and identify privilege drift risks",
                        "Audit credential rotations and API access logs"
                    ]
                else:
                    tasks = [
                        f"Evaluate implementation details for request: {user_input}",
                        "Audit architectural plan for safety and cost boundaries"
                    ]

            console.print(f"\n[bold blue]AutoPilot:[/bold blue] Decomposed goal into [bold]{len(tasks)}[/bold] specialized sub-tasks:\n")
            for idx, task in enumerate(tasks, 1):
                console.print(f" [bold magenta]{idx}.[/bold magenta] {task}")
            
            confirm = Prompt.ask("\n[bold cyan]Proceed to dispatch these sub-tasks to the Debate Engine?[/bold cyan]", choices=["y", "n"], default="y")
            if confirm.lower() != "y":
                console.print("[yellow]Canceled dispatch.[/yellow]")
                continue

            # Execute tasks
            for idx, task in enumerate(tasks, 1):
                console.print(f"\n[bold magenta]━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━[/bold magenta]")
                console.print(f"[bold cyan]Sub-task {idx}/{len(tasks)}:[/bold cyan] {task}")
                console.print(f"[bold magenta]━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━[/bold magenta]\n")

                with Progress(
                    SpinnerColumn(),
                    TextColumn("[progress.description]{task.description}"),
                    transient=True
                ) as progress:
                    progress.add_task("Running Multi-Agent Debate Engine...", total=None)
                    # Run actual workflow through orchestrator
                    outcome = await orchestrator.process_request(task)

                # Format outcome beautifully
                table = Table(title=f"Debate Outcome: {outcome.debate_id[:8]}", title_style="bold cyan")
                table.add_column("Agent / Role", style="magenta")
                table.add_column("Confidence", style="yellow")
                table.add_column("Consensus / Argument Summary", style="green")

                for arg in outcome.arguments:
                    table.add_row(
                        f"{arg.role.value} ({arg.agent_id})",
                        f"{arg.confidence:.2f}",
                        arg.content[:80] + "..." if len(arg.content) > 80 else arg.content
                    )

                console.print(table)
                console.print(f"\n[bold green]Final Consensus Decision:[/bold green] [bold]{outcome.final_decision}[/bold]")
                console.print(f"[bold yellow]Confidence Score:[/bold yellow] [bold]{outcome.confidence_score:.2f}[/bold]\n")

            console.print("\n[bold green]✅ All autopilot sub-tasks completed and recorded in Atlas memory successfully![/bold green]")

        except KeyboardInterrupt:
            console.print("\n[dim]Shutting down AutoPilot...[/dim]")
            break
        except Exception as e:
            console.print(f"[bold red]Error executing workflow:[/bold red] {e}")

if __name__ == "__main__":
    asyncio.run(run_autopilot_loop())
