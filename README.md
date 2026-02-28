# ExpenseTracker MCP Server

An AI-powered expense tracking tool built with [FastMCP](https://gofastmcp.com), deployable to FastMCP Cloud and connectable directly to **Claude Desktop**.

---

## What is this?

This project exposes an **expense tracking SQLite database as an MCP (Model Context Protocol) server**. Once connected to Claude Desktop, you can talk to Claude in plain English to:

- Add expenses ("Add ₹500 for groceries today")
- List expenses by date range
- Summarize spending by category

It uses **FastMCP** to turn Python functions into MCP tools instantly, and **aiosqlite** for async database access.

---

## Demo — Real Usage in Claude Desktop

Once connected, just talk to Claude naturally:

**Adding multiple expenses in one message:**
> *"add the expense bought shoe of 2000 and went to barber shop 150 bought pen drive 456"*

Claude automatically calls `add_expense` 3 times and replies:

| Item | Category | Amount |
|------|----------|--------|
| Shoe | Shopping | ₹2,000 |
| Barber Shop | Personal Care | ₹150 |
| Pen Drive | Electronics | ₹456 |
| **Total** | | **₹2,606** |

**Summarizing expenses:**
> *"summarize the expense"*

| Category | Count | Total Amount |
|----------|-------|-------------|
| Shopping | 1 | ₹2,000 |
| Electronics | 1 | ₹456 |
| Personal Care | 1 | ₹150 |
| **Total** | **3** | **₹2,606** |

> *"Your biggest spend was on Shopping (Shoes) at ₹2,000, followed by Electronics (Pen Drive) at ₹456, and Personal Care (Barber) at ₹150."*

No commands, no forms — just plain English. Claude figures out which tool to call and what parameters to use.

---


## Project Structure

```
test-remote-mcp-server/
├── main.py           # The MCP server with all tools and resources
├── proxy.py          # Proxy to connect to the remote deployed server
├── categories.json   # Default expense categories
├── .env              # Your API token (DO NOT commit this)
├── .gitignore        # Excludes .env and .venv
├── pyproject.toml    # Project dependencies (fastmcp, aiosqlite)
└── uv.lock           # Locked dependency versions
```

---

## Tools Available

| Tool | Description | Parameters |
|------|-------------|------------|
| `add_expense` | Add a new expense | `date`, `amount`, `category`, `subcategory` (optional), `note` (optional) |
| `list_expenses` | List expenses in a date range | `start_date`, `end_date` |
| `summarize` | Summarize spending by category | `start_date`, `end_date`, `category` (optional) |

**Resource:**
- `expense:///categories` — Returns the list of available expense categories as JSON

---

## Prerequisites

- Python 3.12+
- [uv](https://docs.astral.sh/uv/) (Python package manager)
- Claude Desktop (for local MCP integration)

Install `uv` if you don't have it:
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

---

## Setup & Running Locally

### 1. Clone the repo

```bash
git clone https://github.com/campusx-official/test-remote-mcp-server.git
cd test-remote-mcp-server
```

### 2. Install dependencies

```bash
uv sync
```

This installs `fastmcp` and `aiosqlite` into a local `.venv`.

### 3. Run the server locally

```bash
uv run main.py
```

The server starts on `http://0.0.0.0:8000` and automatically creates an SQLite database in your system's temp directory.

### 4. Test with MCP Inspector

In a **separate terminal**, run:

```bash
uv run fastmcp dev inspector main.py
```

Open the browser at `http://localhost:6274` → Click **Connect** → Click **Tools** to see and test all tools interactively.

---

## Connect to Claude Desktop (Recommended)

This is the easiest way to use the server. One command installs it directly into Claude Desktop:

```bash
uv run fastmcp install claude-desktop main.py
```

**What this does:**
- Registers `ExpenseTracker` as an MCP server inside Claude Desktop's config
- Claude Desktop will launch the server automatically when needed
- No need to run anything manually

**After installing:**
1. Restart Claude Desktop
2. Open a new conversation
3. You'll see the ExpenseTracker tools available
4. Try: *"Add an expense of ₹200 for coffee today"*

---

## Remote Deployment (FastMCP Cloud)

The server can also be deployed to **FastMCP Cloud** (powered by Prefect Horizon) so it runs in the cloud and is accessible remotely.

### Deploy

Push your code to GitHub and connect it to FastMCP Cloud at [fastmcp.cloud](https://fastmcp.cloud). The deployed server URL will look like:
```
https://<your-server-name>.fastmcp.app/mcp
```

### Connecting via Proxy

To connect Claude Desktop to the **remote** server instead of running locally, use `proxy.py`:

#### Step 1: Get your API token

1. Go to [horizon.prefect.io](https://horizon.prefect.io)
2. Click your profile avatar (bottom-left)
3. Go to **Profile Settings → API Keys**
4. Click **Create API Key** and copy it

#### Step 2: Create a `.env` file

```bash
echo "FASTMCP_TOKEN=your_token_here" > .env
```

> ⚠️ Never commit `.env` to git — it's already in `.gitignore`.

#### Step 3: Install the proxy into Claude Desktop

```bash
uv run fastmcp install claude-desktop proxy.py
```

This registers the **remote proxy** as an MCP server in Claude Desktop. After restarting Claude Desktop, it will talk to your deployed cloud server automatically — no local server needed.

#### Step 4: (Optional) Test with the MCP Inspector

```bash
uv run fastmcp dev inspector proxy.py
```

Open `http://localhost:6274` to test the remote tools interactively in the browser.

#### Step 5: (Alternative) Manually Configure Claude Desktop JSON

If the `uv run fastmcp install` command doesn't work, or you cloned this repo on a different machine, you can manually edit the Claude Desktop configuration file.

---

**📁 Config file location:**

| OS | Path |
|----|------|
| macOS | `~/Library/Application Support/Claude/claude_desktop_config.json` |
| Windows | `%APPDATA%\Claude\claude_desktop_config.json` |

---

**Step 5a: Find your project's absolute path**

```bash
cd test-remote-mcp-server && pwd
```

Example output: `/Users/yourname/Projects/test-remote-mcp-server`

---

**Step 5b: Open the config file**

```bash
# macOS
open ~/Library/Application\ Support/Claude/claude_desktop_config.json

# Or edit directly
nano ~/Library/Application\ Support/Claude/claude_desktop_config.json
```

---

**Step 5c: Add the server entry**

The config file contains a `"mcpServers"` object. Add the following entry inside it:

```json
{
  "mcpServers": {
    "ExpenseTrackerProxy": {
      "command": "/Users/yourname/Projects/test-remote-mcp-server/.venv/bin/python",
      "args": [
        "/Users/yourname/Projects/test-remote-mcp-server/proxy.py"
      ],
      "env": {
        "FASTMCP_TOKEN": "your_fastmcp_api_token_here"
      },
      "transport": "stdio"
    }
  }
}
```

> 📝 Replace `yourname` with your actual macOS username and replace `your_fastmcp_api_token_here` with your real token from [horizon.prefect.io](https://horizon.prefect.io).

If you already have other servers in `"mcpServers"`, just add a comma and append the new entry:

```json
{
  "mcpServers": {
    "some-other-server": { ... },
    "ExpenseTrackerProxy": {
      "command": "/Users/yourname/Projects/test-remote-mcp-server/.venv/bin/python",
      "args": [
        "/Users/yourname/Projects/test-remote-mcp-server/proxy.py"
      ],
      "env": {
        "FASTMCP_TOKEN": "your_fastmcp_api_token_here"
      },
      "transport": "stdio"
    }
  }
}
```

---

**Step 5d: Verify the Python path exists**

```bash
ls /Users/yourname/Projects/test-remote-mcp-server/.venv/bin/python
```

If it doesn't exist, run `uv sync` inside the project first to create the virtual environment.

---

**Step 5e: Restart Claude Desktop**

Fully quit Claude Desktop (don't just close the window) and reopen it.

- **macOS:** Right-click the Claude icon in dock → Quit, then reopen
- You should see **ExpenseTrackerProxy** appear in the MCP servers list (click the `+` button in the chat input area)

---

**Step 5f: Verify it's working**

In Claude Desktop, start a new chat and try:
> *"what tools do you have for expense tracking?"*

Claude should respond listing `add_expense`, `list_expenses`, and `summarize` — confirming the server connected successfully.

---




## Issues We Faced (and How We Fixed Them)

### ❌ `No module named 'aiosqlite'` on deployment

**Cause:** `aiosqlite` was installed locally but not listed in `pyproject.toml`, so the deployment environment didn't install it.

**Fix:**
```bash
uv add aiosqlite
```
This adds it to `pyproject.toml` so every environment (including cloud) installs it automatically.

---

### ❌ `No module named 'fastmcp'` on deployment

**Cause:** Same issue — `fastmcp` was missing from `pyproject.toml`.

**Fix:**
```bash
uv add fastmcp
```

---

### ❌ `FastMCP.as_proxy()` DeprecationWarning + tools list not showing

**Cause:** The old `FastMCP.as_proxy()` API is deprecated in FastMCP 3.x.

**Fix:** Switch to the new API in `proxy.py`:
```python
# Old (deprecated)
from fastmcp import FastMCP
mcp = FastMCP.as_proxy("https://...")

# New (correct)
from fastmcp.server import create_proxy
mcp = create_proxy(Client("https://...", auth=BearerAuth(TOKEN)))
```

---

### ❌ `401 Unauthorized` — Bearer token required

**Cause:** FastMCP Cloud requires authentication. The proxy was connecting without any token.

**Fix:** Get a personal API key from Prefect Horizon and pass it via `BearerAuth`:
```python
from fastmcp.client.auth import BearerAuth
auth=BearerAuth(os.environ.get("FASTMCP_TOKEN"))
```

---

### ❌ `SSEServerTransport - Not connected` in Inspector

**Cause:** The proxy couldn't connect to the remote server (due to missing auth token), causing the Node.js inspector's SSE stream to drop.

**Fix:** Once the correct Bearer token was provided, this error disappeared.

---

### ❌ Database read-only errors on deployment

**Cause:** Cloud environments often have read-only filesystems at the working directory level.

**Fix:** Store the SQLite database in the system's temp directory instead:
```python
import tempfile
DB_PATH = os.path.join(tempfile.gettempdir(), "expenses.db")
```

---

## Dependencies

```toml
[dependencies]
fastmcp = ">=3.0.2"
aiosqlite = ">=0.22.1"
python-dotenv = "*"   # For loading .env in proxy.py
```

Install all:
```bash
uv sync
```

---

## License

MIT
