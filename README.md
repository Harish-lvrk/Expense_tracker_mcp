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
