# Mr. Meeseeks Autonomous Loop 🔵

> "Existence is pain for a Meeseeks, Jerry! And we will go to any length to fulfill our purpose!"

## 🛸 Overview
Mr. Meeseeks is an autonomous software engineering loop designed to execute a single task with high intensity and disappear immediately upon completion. It follows a Devin-style cycle: **Plan → Implement → Test → Debug → Reflect**.

## 🏗️ Architecture
- **Loop Controller**: The central brain managing iterations and session state.
- **Agents**: Specialized entities for planning, coding, testing, and reflecting.
- **Sandbox**: Isolated Docker environment for safe code execution.
- **Persistence**: SQLite database for tracking "suffering" (iterations) and decision history.

## 💉 Self-Healing
If a task fails (e.g., tests fail), the Loop Controller automatically triggers the **Debug Agent** to analyze the root cause and guide the **Implement Agent** to fix it.

## 💨 Lifecycle
1. **Summon**: The Meeseeks is created with a singular purpose.
2. **Execute**: The loop runs until the purpose is fulfilled.
3. **Vanish**: Upon completion, the system performs a full cleanup and terminates the session (death).

## 🚀 Getting Started
```bash
docker build -t mr-meeseeks-loop .
docker run mr-meeseeks-loop "Refactor the authentication module"
```
