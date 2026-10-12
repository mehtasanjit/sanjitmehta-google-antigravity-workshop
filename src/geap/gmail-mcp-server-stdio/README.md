# Gmail MCP Server (`stdio`) for Google Antigravity

A lightweight, zero-dependency Node.js `stdio` Model Context Protocol (MCP) server for Gmail (`GmailMcp`).

Unlike basic local Gmail MCP scripts that fail silently or halt automation when `tokens/default` is empty, this server **automatically launches an interactive Google OAuth consent window in your browser** on the first tool call when no local token is present, saves the token to `tokens/default/token.json`, and automatically refreshes expired access tokens in the background.

---

## 1. Prerequisites (Google Cloud Console Setup)

1. Open [Google Cloud Console](https://console.cloud.google.com/) and select or create a project.
2. Enable the **Gmail API**:
   - Go to **APIs & Services $\rightarrow$ Library**, search for **Gmail API** (`gmail.googleapis.com`), and click **Enable**.
3. Configure the **OAuth Consent Screen**:
   - Go to **APIs & Services $\rightarrow$ OAuth consent screen** (or **Google Auth Platform $\rightarrow$ Audience**).
   - If the app is set to **External / Testing**, add your email address under **Test users**.
4. Create an **OAuth 2.0 Client ID**:
   - Go to **APIs & Services $\rightarrow$ Credentials $\rightarrow$ + Create Credentials $\rightarrow$ OAuth client ID**.
   - Application type: **Web application** (or **Desktop app**).
   - Under **Authorized redirect URIs**, add:
     ```text
     http://localhost:3000/oauth2callback
     ```
   - Copy the **Client ID** and **Client Secret** (or download the JSON as `credentials.json` into this folder).

---

## 2. Configure in Antigravity (`~/.gemini/config/mcp_config.json`)

Add `GmailMcp` to your global `~/.gemini/config/mcp_config.json` (see [`mcp_config.example.json`](mcp_config.example.json)):

```json
{
  "mcpServers": {
    "GmailMcp": {
      "command": "node",
      "args": [
        "/ABSOLUTE/PATH/TO/src/geap/gmail-mcp-server-stdio/server.js"
      ],
      "env": {
        "GMAIL_CLIENT_ID": "YOUR_OAUTH_CLIENT_ID.apps.googleusercontent.com",
        "GMAIL_CLIENT_SECRET": "YOUR_OAUTH_CLIENT_SECRET",
        "GMAIL_MCP_AUTO_POPUP": "1"
      }
    }
  }
}
```

*(Alternatively, instead of setting `GMAIL_CLIENT_ID` and `GMAIL_CLIENT_SECRET` in `env`, you can place your downloaded `credentials.json` directly inside `src/geap/gmail-mcp-server-stdio/credentials.json`.)*

---

## 3. How Authentication & Token Refresh Work

- **First Use (Empty `tokens/default` Directory)**:
  - When an Antigravity agent invokes any `GmailMcp` tool (`list_labels`, `search_threads`, `get_message`, `get_attachment`) and `tokens/default/token.json` does not exist, the server automatically starts a temporary callback listener on `http://localhost:3000/oauth2callback` and pops open the Google OAuth consent screen in your browser.
  - Once you click **Allow**, the token is saved to `tokens/default/token.json` and the tool call completes immediately without interrupting the agent's workflow.
- **Manual Pre-Auth (Optional)**:
  - You can also pre-authorize from a terminal at any time:
    ```bash
    node server.js auth
    ```
- **Token Longevity**:
  - **`access_token` (1 hour)**: Automatically refreshed in the background using the stored `refresh_token`.
  - **`refresh_token`**: Lasts **7 days** if your GCP OAuth Consent Screen is in `Testing` status, or **indefinitely** if set to `In production` or `Internal`.

---

## 4. Available MCP Tools

| Tool | Description |
| :--- | :--- |
| `list_labels` | Lists all Gmail labels in the authenticated mailbox. |
| `search_threads` | Searches Gmail messages using standard Gmail query syntax (`q`, `maxResults`). |
| `get_message` | Fetches a message by ID, automatically decoding the plain-text/HTML body and listing attachment metadata (`attachmentId`, `filename`, `mimeType`, `size`). |
| `get_attachment` | Downloads and decodes an attachment by `messageId` and `attachmentId` (optionally saving it directly to `outputPath`). |
