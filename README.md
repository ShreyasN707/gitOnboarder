# GithubOnboarder

This is a chat agent that helps you understand and search through GitHub repositories. It uses a combination of direct GitHub API calls (via MCP) and local vector search (Qdrant) to pull context and answer questions about codebases.

## Features

- **GitHub Integration**: Connects to GitHub to read files, issues, commits, and PRs.
- **Semantic Search**: Indexes repository files into a local Qdrant vector store so you can actually search the code.
- **Memory**: Remembers what you talked about during a session and saves important repository facts to a local JSON file for future reference.

## Setup

1. **Clone the repo**
   ```bash
   git clone https://github.com/ShreyasN707/gitOnboarder.git
   cd gitOnboarder
   ```

2. **Install dependencies**
   It's recommended to use a virtual environment like Conda or venv.
   ```bash
   pip install -r requirements.txt
   ```

3. **Environment Variables**
   Create a `.env` file in the root directory. You'll need to add your Google API key since this uses Gemini as the model, and a GitHub token to fetch data without getting rate-limited.
   ```
   GOOGLE_API_KEY=your_key_here
   GITHUB_TOKEN=your_token_here
   ```

## Running the Agent

To start the chat interface, just run the main agent file:

```bash
python -m app.agent
```

Wait a few seconds for the agent to load its tools. Once you see "GitHub Repository Intelligence Agent Ready!", you can start asking questions about any repository.
