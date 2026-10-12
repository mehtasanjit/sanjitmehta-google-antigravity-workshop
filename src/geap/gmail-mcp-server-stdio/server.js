#!/usr/bin/env node
/**
 * Gmail MCP Server (stdio) for Google Antigravity
 *
 * Key features:
 * - Zero external npm dependencies (uses built-in Node.js modules only).
 * - Stores OAuth tokens locally in ./tokens/default/token.json (and auto-refreshes expired access tokens).
 * - Auto-launches the interactive Google OAuth consent screen in the user's browser
 *   on first tool call when ./tokens/default is empty (unless GMAIL_MCP_AUTO_POPUP=0).
 * - Supports credentials via environment variables (GMAIL_CLIENT_ID / GMAIL_CLIENT_SECRET)
 *   or a standard Google Cloud OAuth ./credentials.json file.
 */

const fs = require('fs');
const path = require('path');
const http = require('http');
const https = require('https');
const { URL } = require('url');
const { execFile } = require('child_process');
const readline = require('readline');

const BASE_DIR = __dirname;
const TOKENS_DIR = process.env.GMAIL_TOKENS_DIR || path.join(BASE_DIR, 'tokens', 'default');
const TOKEN_FILE = path.join(TOKENS_DIR, 'token.json');
const CREDENTIALS_FILE = process.env.GMAIL_CREDENTIALS_FILE || path.join(BASE_DIR, 'credentials.json');

const PORT = Number(process.env.GMAIL_OAUTH_PORT || 3000);
const REDIRECT_URI = process.env.GMAIL_REDIRECT_URI || `http://localhost:${PORT}/oauth2callback`;
const SCOPES = ['https://www.googleapis.com/auth/gmail.readonly'];
const AUTO_POPUP = process.env.GMAIL_MCP_AUTO_POPUP !== '0';

function loadClientCredentials() {
  let clientId = process.env.GMAIL_CLIENT_ID || '';
  let clientSecret = process.env.GMAIL_CLIENT_SECRET || '';

  if ((!clientId || !clientSecret) && fs.existsSync(CREDENTIALS_FILE)) {
    try {
      const raw = JSON.parse(fs.readFileSync(CREDENTIALS_FILE, 'utf8'));
      const cfg = raw.installed || raw.web || raw;
      clientId = clientId || cfg.client_id || '';
      clientSecret = clientSecret || cfg.client_secret || '';
    } catch (err) {
      process.stderr.write(`Failed to parse ${CREDENTIALS_FILE}: ${err.message}\n`);
    }
  }
  return { clientId, clientSecret };
}

function httpsRequest(urlStr, options = {}, body = null) {
  return new Promise((resolve, reject) => {
    const u = new URL(urlStr);
    const req = https.request(
      {
        hostname: u.hostname,
        path: u.pathname + u.search,
        method: options.method || 'GET',
        headers: options.headers || {},
      },
      (res) => {
        let data = '';
        res.on('data', (chunk) => (data += chunk));
        res.on('end', () => {
          try {
            resolve({ status: res.statusCode, data: JSON.parse(data) });
          } catch {
            resolve({ status: res.statusCode, data });
          }
        });
      }
    );
    req.on('error', reject);
    if (body) req.write(body);
    req.end();
  });
}

function getStoredToken() {
  if (!fs.existsSync(TOKENS_DIR)) {
    fs.mkdirSync(TOKENS_DIR, { recursive: true });
  }
  const files = fs.readdirSync(TOKENS_DIR).filter((f) => f.endsWith('.json'));
  if (files.length === 0) {
    return null;
  }
  const raw = fs.readFileSync(path.join(TOKENS_DIR, files[0]), 'utf8');
  return JSON.parse(raw);
}

function openBrowser(targetUrl) {
  const platform = process.platform;
  if (platform === 'darwin') {
    execFile('open', [targetUrl], () => {});
  } else if (platform === 'win32') {
    execFile('cmd', ['/c', 'start', '', targetUrl], () => {});
  } else {
    const chromeArgs = [];
    if (process.env.DISPLAY) {
      chromeArgs.push(`--display=${process.env.DISPLAY}`);
    }
    if (process.env.GMAIL_OAUTH_INCOGNITO === '1') {
      chromeArgs.push('--incognito');
    }
    chromeArgs.push(targetUrl);
    execFile('xdg-open', [targetUrl], (err) => {
      if (err) {
        execFile('google-chrome', chromeArgs, () => {});
      }
    });
  }
}

async function refreshAccessTokenIfNeeded(tokenObj) {
  if (!tokenObj) return null;
  const now = Date.now();
  if (tokenObj.expiry_date && now < tokenObj.expiry_date - 60000) {
    return tokenObj.access_token;
  }
  if (!tokenObj.refresh_token) {
    return tokenObj.access_token;
  }
  const { clientId, clientSecret } = loadClientCredentials();
  const params = new URLSearchParams({
    client_id: clientId,
    client_secret: clientSecret,
    refresh_token: tokenObj.refresh_token,
    grant_type: 'refresh_token',
  });
  const res = await httpsRequest(
    'https://oauth2.googleapis.com/token',
    {
      method: 'POST',
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    },
    params.toString()
  );
  if (res.status === 200 && res.data.access_token) {
    tokenObj.access_token = res.data.access_token;
    if (res.data.expires_in) {
      tokenObj.expiry_date = Date.now() + res.data.expires_in * 1000;
    }
    fs.writeFileSync(TOKEN_FILE, JSON.stringify(tokenObj, null, 2));
    return tokenObj.access_token;
  }
  throw new Error(`Failed to refresh OAuth token: ${JSON.stringify(res.data)}`);
}

function runInteractiveOAuth() {
  return new Promise((resolve, reject) => {
    const { clientId, clientSecret } = loadClientCredentials();
    if (!clientId || !clientSecret) {
      return reject(
        new Error(
          'Missing OAuth credentials. Set GMAIL_CLIENT_ID and GMAIL_CLIENT_SECRET in mcp_config.json or place credentials.json in the server directory.'
        )
      );
    }

    const authUrl = new URL('https://accounts.google.com/o/oauth2/v2/auth');
    authUrl.searchParams.set('client_id', clientId);
    authUrl.searchParams.set('redirect_uri', REDIRECT_URI);
    authUrl.searchParams.set('response_type', 'code');
    authUrl.searchParams.set('scope', SCOPES.join(' '));
    authUrl.searchParams.set('access_type', 'offline');
    authUrl.searchParams.set('prompt', 'consent');

    const server = http.createServer(async (req, res) => {
      try {
        const reqUrl = new URL(req.url, `http://localhost:${PORT}`);
        if (reqUrl.pathname !== '/oauth2callback') {
          res.writeHead(404);
          res.end('Not found');
          return;
        }
        const code = reqUrl.searchParams.get('code');
        const err = reqUrl.searchParams.get('error');
        if (err || !code) {
          res.writeHead(400, { 'Content-Type': 'text/html' });
          res.end(`<h3>OAuth Error: ${err || 'missing code'}</h3>`);
          server.close();
          return reject(new Error(`OAuth callback error: ${err || 'missing code'}`));
        }
        const params = new URLSearchParams({
          code,
          client_id: clientId,
          client_secret: clientSecret,
          redirect_uri: REDIRECT_URI,
          grant_type: 'authorization_code',
        });
        const tokenRes = await httpsRequest(
          'https://oauth2.googleapis.com/token',
          {
            method: 'POST',
            headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
          },
          params.toString()
        );
        if (tokenRes.status !== 200 || !tokenRes.data.access_token) {
          res.writeHead(500, { 'Content-Type': 'text/html' });
          res.end(`<h3>Token exchange failed</h3><pre>${JSON.stringify(tokenRes.data, null, 2)}</pre>`);
          server.close();
          return reject(new Error(`Token exchange failed: ${JSON.stringify(tokenRes.data)}`));
        }
        const saved = {
          ...tokenRes.data,
          expiry_date: Date.now() + (tokenRes.data.expires_in || 3600) * 1000,
        };
        fs.mkdirSync(TOKENS_DIR, { recursive: true });
        fs.writeFileSync(TOKEN_FILE, JSON.stringify(saved, null, 2));
        res.writeHead(200, { 'Content-Type': 'text/html' });
        res.end('<h2>GmailMcp OAuth completed! Token saved to tokens/default/token.json. You may close this tab.</h2>');
        server.close();
        resolve(saved);
      } catch (e) {
        server.close();
        reject(e);
      }
    });

    server.on('error', (err) => {
      reject(new Error(`Failed to start local OAuth callback listener on port ${PORT}: ${err.message}`));
    });

    server.listen(PORT, '127.0.0.1', () => {
      const targetUrl = authUrl.toString();
      process.stderr.write(`Opening browser for GmailMcp OAuth: ${targetUrl}\n`);
      openBrowser(targetUrl);
    });
  });
}

async function callGmailApi(endpoint) {
  let tokenObj = getStoredToken();
  if (!tokenObj) {
    if (AUTO_POPUP) {
      tokenObj = await runInteractiveOAuth();
    } else {
      throw new Error(
        `GmailMcp authorization not ready: Google account OAuth has not been completed (${TOKENS_DIR} directory is empty).`
      );
    }
  }
  const accessToken = await refreshAccessTokenIfNeeded(tokenObj);
  const res = await httpsRequest(`https://gmail.googleapis.com/gmail/v1/users/me/${endpoint}`, {
    headers: { Authorization: `Bearer ${accessToken}` },
  });
  if (res.status !== 200) {
    throw new Error(`Gmail API error (${res.status}): ${JSON.stringify(res.data)}`);
  }
  return res.data;
}

function decodeBase64Url(data) {
  if (!data) return '';
  const base64 = data.replace(/-/g, '+').replace(/_/g, '/');
  return Buffer.from(base64, 'base64').toString('utf8');
}

function extractMessageContent(payload) {
  const headers = {};
  for (const h of payload?.headers || []) {
    if (['Subject', 'From', 'To', 'Date', 'Cc'].includes(h.name)) {
      headers[h.name.toLowerCase()] = h.value;
    }
  }
  let textBody = '';
  let htmlBody = '';
  const attachments = [];

  function walkParts(part) {
    if (!part) return;
    if (part.filename && part.body?.attachmentId) {
      attachments.push({
        filename: part.filename,
        mimeType: part.mimeType,
        size: part.body.size,
        attachmentId: part.body.attachmentId,
      });
    }
    if (part.mimeType === 'text/plain' && part.body?.data) {
      textBody += decodeBase64Url(part.body.data);
    } else if (part.mimeType === 'text/html' && part.body?.data) {
      htmlBody += decodeBase64Url(part.body.data);
    }
    if (Array.isArray(part.parts)) {
      part.parts.forEach(walkParts);
    }
  }

  walkParts(payload);
  return {
    headers,
    body: textBody || htmlBody,
    attachments,
  };
}

const TOOLS = [
  {
    name: 'list_labels',
    description: 'List all Gmail labels in the user mailbox.',
    inputSchema: { type: 'object', properties: {} },
  },
  {
    name: 'search_threads',
    description: 'Search Gmail messages/threads using a standard Gmail query string (e.g. "is:inbox", "from:boss@example.com").',
    inputSchema: {
      type: 'object',
      properties: {
        q: { type: 'string', description: 'Gmail search query (e.g. "is:inbox")' },
        maxResults: { type: 'number', description: 'Max messages to return (default 5)' },
      },
    },
  },
  {
    name: 'get_message',
    description: 'Get a specific Gmail message by ID, including decoded text body and attachment metadata.',
    inputSchema: {
      type: 'object',
      properties: {
        id: { type: 'string', description: 'Gmail message ID' },
      },
      required: ['id'],
    },
  },
  {
    name: 'get_attachment',
    description: 'Download an email attachment by message ID and attachment ID, optionally saving it to outputPath.',
    inputSchema: {
      type: 'object',
      properties: {
        messageId: { type: 'string', description: 'Gmail message ID' },
        attachmentId: { type: 'string', description: 'Attachment ID from get_message' },
        outputPath: { type: 'string', description: 'Optional local file path to save the decoded attachment' },
      },
      required: ['messageId', 'attachmentId'],
    },
  },
];

async function handleToolCall(name, args = {}) {
  if (name === 'list_labels') {
    const data = await callGmailApi('labels');
    return { content: [{ type: 'text', text: JSON.stringify(data, null, 2) }] };
  }
  if (name === 'search_threads') {
    const q = encodeURIComponent(args.q || '');
    const max = args.maxResults || 5;
    const data = await callGmailApi(`messages?q=${q}&maxResults=${max}`);
    return { content: [{ type: 'text', text: JSON.stringify(data, null, 2) }] };
  }
  if (name === 'get_message') {
    const data = await callGmailApi(`messages/${encodeURIComponent(args.id)}?format=full`);
    const parsed = extractMessageContent(data.payload);
    return {
      content: [
        {
          type: 'text',
          text: JSON.stringify(
            {
              id: data.id,
              threadId: data.threadId,
              snippet: data.snippet,
              ...parsed,
            },
            null,
            2
          ),
        },
      ],
    };
  }
  if (name === 'get_attachment') {
    const data = await callGmailApi(
      `messages/${encodeURIComponent(args.messageId)}/attachments/${encodeURIComponent(args.attachmentId)}`
    );
    const base64 = (data.data || '').replace(/-/g, '+').replace(/_/g, '/');
    const buf = Buffer.from(base64, 'base64');
    if (args.outputPath) {
      fs.mkdirSync(path.dirname(path.resolve(args.outputPath)), { recursive: true });
      fs.writeFileSync(args.outputPath, buf);
      return {
        content: [
          {
            type: 'text',
            text: JSON.stringify({ savedTo: path.resolve(args.outputPath), bytes: buf.length }, null, 2),
          },
        ],
      };
    }
    return {
      content: [
        {
          type: 'text',
          text: buf.toString('utf8'),
        },
      ],
    };
  }
  throw new Error(`Unknown tool: ${name}`);
}

function sendJsonRpc(msg) {
  process.stdout.write(JSON.stringify(msg) + '\n');
}

if (process.argv[2] === 'auth') {
  runInteractiveOAuth()
    .then(() => {
      console.error('Successfully saved OAuth token to', TOKEN_FILE);
      process.exit(0);
    })
    .catch((err) => {
      console.error('OAuth failed:', err.message);
      process.exit(1);
    });
} else {
  const rl = readline.createInterface({ input: process.stdin, terminal: false });
  rl.on('line', async (line) => {
    if (!line.trim()) return;
    let req;
    try {
      req = JSON.parse(line);
    } catch {
      return;
    }
    const { id, method, params } = req;
    if (method === 'initialize') {
      sendJsonRpc({
        jsonrpc: '2.0',
        id,
        result: {
          protocolVersion: '2024-11-05',
          capabilities: { tools: {} },
          serverInfo: { name: 'GmailMcp', version: '1.0.0' },
        },
      });
    } else if (method === 'notifications/initialized') {
      // notification; no response
    } else if (method === 'tools/list') {
      sendJsonRpc({
        jsonrpc: '2.0',
        id,
        result: { tools: TOOLS },
      });
    } else if (method === 'tools/call') {
      try {
        const result = await handleToolCall(params?.name, params?.arguments);
        sendJsonRpc({ jsonrpc: '2.0', id, result });
      } catch (err) {
        sendJsonRpc({
          jsonrpc: '2.0',
          id,
          result: {
            isError: true,
            content: [{ type: 'text', text: err.message }],
          },
        });
      }
    } else if (id !== undefined) {
      sendJsonRpc({
        jsonrpc: '2.0',
        id,
        error: { code: -32601, message: `Method not found: ${method}` },
      });
    }
  });
}
