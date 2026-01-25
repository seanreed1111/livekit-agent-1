# Web Frontend Deployment Implementation Plan

> **Status:** DRAFT

## Table of Contents

- [Overview](#overview)
- [Current State Analysis](#current-state-analysis)
- [Desired End State](#desired-end-state)
- [What We're NOT Doing](#what-were-not-doing)
- [Implementation Approach](#implementation-approach)
- [Dependencies](#dependencies)
- [Phase 1: Agent Deployment to LiveKit Cloud](#phase-1-agent-deployment-to-livekit-cloud)
- [Phase 2: Frontend Setup (agent-starter-react)](#phase-2-frontend-setup-agent-starter-react)
- [Phase 3: Authentication and Token Generation](#phase-3-authentication-and-token-generation)
- [Phase 4: Connection Testing and Optimization](#phase-4-connection-testing-and-optimization)
- [Phase 5: Frontend Customization](#phase-5-frontend-customization)
- [Phase 6: Production Deployment](#phase-6-production-deployment)
- [Testing Strategy](#testing-strategy)
- [References](#references)

## Overview

This plan enables potential clients to interact with the LiveKit voice AI agent from this repository by clicking a link on a website. The implementation covers:

1. Deploying the Python agent to LiveKit Cloud
2. Setting up a Next.js/React frontend using the agent-starter-react template
3. Implementing JWT token-based authentication
4. Testing the connection flow
5. Customizing the frontend with branding
6. Deploying the frontend to production (Vercel)

The solution uses LiveKit's official starter templates and SDKs to create a production-ready web application with TypeScript/JavaScript.

**IMPORTANT: This is an audio-only application. No video camera or screen sharing permissions should be requested from users. All configuration must disable video/screenshare features.**

## Current State Analysis

### What Exists Now

**Agent Backend:**
- Python voice AI agent in `/Users/seanreed/PythonProjects/voice-ai/lk-agent-1`
- Built with LiveKit Agents SDK
- Uses OpenAI (LLM), AssemblyAI (STT), Cartesia (TTS)
- Configured with `uv` package manager
- Has `Dockerfile` for containerized deployment
- Environment variables in `.env.local` (OpenAI, AssemblyAI, Cartesia API keys)

**Missing:**
- Agent not yet deployed to LiveKit Cloud
- No web frontend for client interaction
- No token generation server for authentication
- No public-facing URL for clients to access

### Key Discoveries

From `docs/DEPLOYMENT.md`:
- LiveKit Cloud deployment uses `lk` CLI
- Agent deployment command: `lk agent create --secrets-file .env.local`
- Multiple frontend options available (React, Flutter, Swift, Embed)
- Connection requires JWT tokens generated server-side
- agent-starter-react provides production-ready Next.js template
- Token generation uses `livekit-server-sdk` npm package

### Constraints

1. **Security:** API secrets (LIVEKIT_API_SECRET) must never be exposed to frontend
2. **Architecture:** Token generation must happen server-side (Next.js API routes)
3. **Dependencies:** Agent must be deployed and running before frontend can connect
4. **Cost:** LiveKit Cloud charges $0.01 per agent session minute

## Desired End State

### Success Criteria

- [ ] Agent deployed and running on LiveKit Cloud
- [ ] Next.js frontend application running locally
- [ ] JWT token generation working via backend API route
- [ ] Users can click a link and connect to voice AI agent
- [ ] Audio conversation works end-to-end (STT → LLM → TTS)
- [ ] Frontend deployed to production URL (Vercel)
- [ ] Customized branding (logo, colors, company name)
- [ ] Light/dark theme support
- [ ] Audio visualization working
- [ ] Mobile-responsive design

### How to Verify

**Agent Deployment:**
```bash
lk agent status
# Expected: Status: Running, Replicas: X/X ready
```

**Frontend Connection:**
1. Visit frontend URL (local: http://localhost:3000, prod: https://your-app.vercel.app)
2. Click "Connect" or "Start Session"
3. Grant microphone permissions when prompted
4. Speak to the agent
5. Verify agent responds with natural voice
6. Check agent logs: `lk agent logs --follow`

**End-to-End Test:**
```bash
# Terminal 1: Monitor agent logs
lk agent logs --follow

# Terminal 2: Run frontend
cd /path/to/frontend
pnpm dev

# Browser: Visit http://localhost:3000, connect, and speak
```

## What We're NOT Doing

**Out of Scope:**
- Multiple agent types or agent selection UI
- User authentication/login system (anonymous users only)
- Database integration or conversation history storage
- Multi-language support (English only initially)
- iOS/Android native apps (web only)
- Custom voice customization UI
- Payment integration or usage metering
- Advanced analytics dashboard
- Server-side rendering (SSR) for the voice interface
- Custom WebRTC infrastructure (using LiveKit Cloud)

**Future Considerations:**
- User accounts and saved conversations
- Analytics and usage tracking
- Custom domain with branding
- A/B testing different agent configurations
- Rate limiting and abuse prevention

## Implementation Approach

### High-Level Strategy

1. **Deploy Agent First:** Ensure the Python agent is running on LiveKit Cloud before building frontend
2. **Use Official Template:** Start with agent-starter-react to avoid reinventing the wheel
3. **Iterative Testing:** Test each phase independently before proceeding
4. **Security-First:** Never expose API secrets; use environment variables and server-side token generation
5. **Quick Validation:** Use LiveKit Agents Playground first to verify agent works before building frontend

### Technology Stack

**Backend (Agent):**
- Python 3.11+
- LiveKit Agents SDK
- OpenAI GPT-4 (LLM)
- AssemblyAI (STT)
- Cartesia (TTS)
- Deployed to: LiveKit Cloud

**Frontend:**
- Next.js 14+ (App Router)
- React 18+
- TypeScript
- Tailwind CSS
- Shadcn/ui components
- `livekit-client` SDK
- `@livekit/components-react`
- Deployed to: Vercel

**Authentication:**
- JWT tokens (livekit-server-sdk)
- Server-side generation (Next.js API routes)
- 2-hour token expiration

## Dependencies

**Execution Order:**

1. Phase 1: Agent Deployment (no dependencies)
2. Phase 2: Frontend Setup (depends on Phase 1 for credentials)
3. Phase 3: Authentication (depends on Phase 2)
4. Phase 4: Connection Testing (depends on Phases 1-3)
5. Phase 5: Frontend Customization (depends on Phase 4)
6. Phase 6: Production Deployment (depends on Phase 5)

**Dependency Graph:**

```
Phase 1 (Agent Deployment)
  └─> Phase 2 (Frontend Setup)
        └─> Phase 3 (Authentication)
              └─> Phase 4 (Testing)
                    └─> Phase 5 (Customization)
                          └─> Phase 6 (Production)
```

**Parallelization:**
- All phases are sequential due to dependencies
- Within each phase, independent tasks can run in parallel

---

## Phase 1: Agent Deployment to LiveKit Cloud

### Overview

Deploy the Python voice AI agent to LiveKit Cloud to make it accessible via WebRTC. This creates a running agent that can be dispatched to rooms when users connect.

### Context

Before starting, ensure you have:
- LiveKit CLI installed: `brew install livekit/livekit/livekit-cli`
- LiveKit Cloud account at https://cloud.livekit.io
- Agent code in `/Users/seanreed/PythonProjects/voice-ai/lk-agent-1`
- API keys in `.env.local` (OpenAI, AssemblyAI, Cartesia)

Files to review:
- `docs/DEPLOYMENT.md` - Complete deployment guide
- `.env.local` - API keys and secrets
- `Dockerfile` - Container build configuration
- `src/app.py` - Agent entry point

### Dependencies

**Depends on:** None (first phase)

**Required by:** Phase 2 (Frontend needs LiveKit credentials), Phase 4 (Testing needs deployed agent)

### Changes Required

#### 1.1: Authenticate with LiveKit Cloud

**What:** Link your CLI to your LiveKit Cloud account

**Command:**
```bash
lk cloud auth
```

**Expected Outcome:**
- Browser opens for authentication
- CLI displays: "Successfully authenticated with LiveKit Cloud"
- Credentials saved in `~/.livekit/credentials`

**Rationale:** Required for all subsequent `lk` CLI commands

---

#### 1.2: Create or Select LiveKit Project

**What:** Create a new project or select an existing one for the agent deployment

**Commands:**
```bash
# List existing projects
lk project list

# Option A: Use existing project
lk project set-default "your-project-name"

# Option B: Create new project via dashboard
# Visit https://cloud.livekit.io and create a new project
# Then set as default: lk project set-default "new-project-name"

# Verify current project
lk project current
```

**Expected Outcome:**
```
NAME                 PROJECT_ID
your-project-name   prj_abc123
```

**Rationale:** Agent deployments are scoped to projects; need a target project first

---

#### 1.3: Verify Secrets File

**What:** Ensure `.env.local` contains all required API keys

**File:** `/Users/seanreed/PythonProjects/voice-ai/lk-agent-1/.env.local`

**Verify contents:**
```bash
cat .env.local
```

**Required secrets:**
```env
OPENAI_API_KEY=sk-...
ASSEMBLYAI_API_KEY=...
CARTESIA_API_KEY=...
```

**Important Notes:**
- Do NOT include `LIVEKIT_URL`, `LIVEKIT_API_KEY`, or `LIVEKIT_API_SECRET` in `.env.local`
- LiveKit Cloud auto-injects these during deployment
- Verify `.env.local` is in `.gitignore`

**Rationale:** Agent needs these API keys to function; LiveKit Cloud encrypts and injects them as environment variables

---

#### 1.4: Download Model Files

**What:** Download required models (Silero VAD, turn detector) before deployment

**Command:**
```bash
cd /Users/seanreed/PythonProjects/voice-ai/lk-agent-1
uv run python src/app.py download-files
```

**Expected Outcome:**
```
Downloading Silero VAD model...
Downloading multilingual turn detector model...
Download complete.
```

**Rationale:** Models are required at runtime; downloading during build ensures faster agent startup

---

#### 1.5: Deploy Agent to LiveKit Cloud

**What:** Create and deploy the agent container to LiveKit Cloud

**Command:**
```bash
cd /Users/seanreed/PythonProjects/voice-ai/lk-agent-1
lk agent create --secrets-file .env.local
```

**Expected Outcome:**
```
Registering agent...
Agent ID: agent_abc123
Building container image...
Uploading code...
Build in progress (this may take 2-5 minutes)...
Build complete.
Deploying agent...
Deployment successful.
Status: Running
Replicas: 2/2 ready
```

**What Happens:**
1. CLI registers new agent with Cloud project
2. Assigns unique agent ID (e.g., `agent_abc123`)
3. Creates/updates `livekit.toml` configuration file
4. Uploads source code to LiveKit build service
5. Builds Docker container from `Dockerfile`
6. Deploys container to Cloud project
7. Encrypts and injects secrets as environment variables
8. Starts 2 replica instances

**Duration:** 2-5 minutes for initial build

**Rationale:** Makes agent accessible via LiveKit's global WebRTC infrastructure

---

#### 1.6: Verify Agent Status

**What:** Confirm agent is running and ready to accept sessions

**Commands:**
```bash
# Check agent status
lk agent status

# View live logs
lk agent logs --tail 50
```

**Expected Status Output:**
```
Agent ID:     agent_abc123
Status:       Running
Replicas:     2/2 ready
Version:      v1
Last Deploy:  2026-01-25 10:30:00 UTC
Region:       us-west-2
```

**Expected Log Output:**
- No error messages
- Successful initialization messages
- "Waiting for room assignment" or similar

**Troubleshooting:**
- If status is `CrashLoop`: Check logs for Python exceptions
- If status is `Build Failed`: Run `lk agent logs --build` to see build errors
- If secrets missing: Run `lk agent secrets` to verify

**Rationale:** Ensures agent is healthy before proceeding to frontend setup

---

#### 1.7: Quick Test with Agents Playground

**What:** Test agent using LiveKit Agents Playground (no code required)

**Steps:**
1. Get project credentials:
   ```bash
   lk project current --json
   ```

2. Visit https://agents-playground.livekit.io/

3. Enter credentials:
   - **LiveKit URL:** `wss://your-project.livekit.cloud` (from JSON output)
   - **API Key:** Your `LIVEKIT_API_KEY` (from JSON output)
   - **API Secret:** Your `LIVEKIT_API_SECRET` (from JSON output)

4. Click "Connect"

5. Allow microphone access when prompted

6. Speak to your agent

7. Monitor agent logs in terminal:
   ```bash
   lk agent logs --follow
   ```

**Expected Outcome:**
- Agent responds to your voice with natural TTS
- Logs show STT transcriptions, LLM responses, TTS generation
- No errors in logs

**Rationale:** Validates agent works end-to-end before investing in frontend development

---

#### 1.8: Save LiveKit Credentials

**What:** Export LiveKit project credentials for frontend configuration

**Command:**
```bash
lk project current --json > livekit-credentials.json
```

**File:** `/Users/seanreed/PythonProjects/voice-ai/lk-agent-1/livekit-credentials.json`

**Expected Contents:**
```json
{
  "name": "your-project-name",
  "url": "wss://your-project.livekit.cloud",
  "api_key": "APIxxxxxxxxxxxx",
  "api_secret": "your-secret-here"
}
```

**Security Note:**
- Add `livekit-credentials.json` to `.gitignore`
- NEVER commit this file to version control
- This file is for local reference only

**Rationale:** Frontend needs these credentials to generate tokens and connect to LiveKit

---

### Success Criteria

#### Automated Verification:

- [ ] CLI authenticated: `lk cloud auth` successful
- [ ] Project selected: `lk project current` shows correct project
- [ ] Agent deployed: `lk agent status` shows `Status: Running`
- [ ] Replicas ready: `lk agent status` shows `X/X ready` (e.g., 2/2)
- [ ] No crash loops: `lk agent logs --tail 50` shows no errors
- [ ] Credentials saved: `livekit-credentials.json` exists and contains valid JSON

#### Manual Verification:

- [ ] Agents Playground connection successful
- [ ] Agent responds to voice input with TTS output
- [ ] Agent logs show successful STT → LLM → TTS pipeline
- [ ] No API key errors in logs
- [ ] Agent state transitions visible (initializing → listening → thinking → speaking)

**Verify:** After completing automated verification, test agent with Agents Playground before proceeding to Phase 2.

---

## Phase 2: Frontend Setup (agent-starter-react)

### Overview

Clone and configure the agent-starter-react template to create a Next.js web application that connects users to your deployed agent.

### Context

Before starting, ensure:
- Phase 1 completed successfully
- Agent is running on LiveKit Cloud
- `livekit-credentials.json` file exists with credentials

Prerequisites:
- Node.js 18+ installed
- pnpm installed: `npm install -g pnpm`
- `lk` CLI authenticated

Files to review:
- `livekit-credentials.json` - LiveKit project credentials
- N/A (frontend doesn't exist yet)

### Dependencies

**Depends on:** Phase 1 (needs LiveKit credentials)

**Required by:** Phase 3 (authentication setup), Phase 4 (connection testing)

### Changes Required

#### 2.1: Create Frontend Project Directory

**What:** Create a directory to house the frontend application

**Commands:**
```bash
cd /Users/seanreed/PythonProjects/voice-ai/lk-agent-1
mkdir -p frontend
cd frontend
```

**Expected Outcome:**
```
Directory created: /Users/seanreed/PythonProjects/voice-ai/lk-agent-1/frontend/
```

**Rationale:** Separates frontend code from agent backend code

---

#### 2.2: Clone agent-starter-react Template

**What:** Use LiveKit CLI to create a new project from the official template

**Command:**
```bash
cd /Users/seanreed/PythonProjects/voice-ai/lk-agent-1/frontend
lk app create --template agent-starter-react
```

**Interactive Prompts:**
- **Project name:** (Press Enter for default or enter custom name like "voice-ai-frontend")
- **Install dependencies?** Yes

**Alternative (Manual Clone):**
```bash
git clone https://github.com/livekit-examples/agent-starter-react.git voice-ai-frontend
cd voice-ai-frontend
pnpm install
```

**Expected Outcome:**
```
✓ Created project: voice-ai-frontend
✓ Installed dependencies
✓ Ready to configure
```

**Directory Structure:**
```
frontend/voice-ai-frontend/
├── app/
│   ├── api/token/route.ts     # Token generation endpoint
│   ├── page.tsx               # Main page
│   └── layout.tsx
├── components/
│   ├── agents-ui/             # Agents UI components
│   ├── app/                   # Business logic
│   └── ui/                    # Shadcn/ui primitives
├── hooks/
├── lib/
├── public/
├── package.json
├── .env.example
└── next.config.js
```

**Rationale:** Official template provides production-ready structure with all necessary LiveKit integrations

---

#### 2.3: Configure Environment Variables

**What:** Set up LiveKit credentials for the frontend

**File:** `/Users/seanreed/PythonProjects/voice-ai/lk-agent-1/frontend/voice-ai-frontend/.env.local`

**Commands:**
```bash
cd /Users/seanreed/PythonProjects/voice-ai/lk-agent-1/frontend/voice-ai-frontend
cp .env.example .env.local
```

**Edit `.env.local`:**
```env
# LiveKit project credentials (from livekit-credentials.json)
LIVEKIT_API_KEY=APIxxxxxxxxxxxx
LIVEKIT_API_SECRET=your-secret-here
LIVEKIT_URL=wss://your-project.livekit.cloud

# Public URL (exposed to browser - same as LIVEKIT_URL)
NEXT_PUBLIC_LIVEKIT_URL=wss://your-project.livekit.cloud

# Agent configuration
AGENT_NAME=
# Leave AGENT_NAME blank for automatic agent dispatch
# Or set to specific agent name if you have multiple agents
```

**How to Get Values:**
```bash
# Copy from livekit-credentials.json
cat /Users/seanreed/PythonProjects/voice-ai/lk-agent-1/livekit-credentials.json
```

**Security Notes:**
- `LIVEKIT_API_SECRET` is server-side only (never exposed to browser)
- `NEXT_PUBLIC_*` variables are exposed to browser
- Only `NEXT_PUBLIC_LIVEKIT_URL` should be public
- Never expose `LIVEKIT_API_KEY` or `LIVEKIT_API_SECRET` to browser

**Rationale:** Frontend needs credentials to generate tokens and connect to LiveKit rooms

---

#### 2.4: Verify Dependencies Installation

**What:** Ensure all npm packages are installed correctly

**Command:**
```bash
cd /Users/seanreed/PythonProjects/voice-ai/lk-agent-1/frontend/voice-ai-frontend
pnpm install
```

**Expected Outcome:**
```
Packages: +XXX
Progress: resolved XXX, reused XXX, downloaded X, added XXX, done
```

**Key Dependencies (verify in `package.json`):**
- `next` (v14+)
- `react` (v18+)
- `livekit-client`
- `@livekit/components-react`
- `livekit-server-sdk`
- `tailwindcss`
- `typescript`

**Troubleshooting:**
- If pnpm not installed: `npm install -g pnpm`
- If peer dependency warnings: Generally safe to ignore
- If install fails: Delete `node_modules` and `pnpm-lock.yaml`, retry

**Rationale:** Ensures all required packages are available for development

---

#### 2.5: Run Development Server

**What:** Start the Next.js development server to verify basic setup

**Command:**
```bash
cd /Users/seanreed/PythonProjects/voice-ai/lk-agent-1/frontend/voice-ai-frontend
pnpm dev
```

**Expected Outcome:**
```
> next dev

  ▲ Next.js 14.x.x
  - Local:        http://localhost:3000
  - Environments: .env.local

 ✓ Ready in X.Xs
```

**Verification:**
1. Open browser to http://localhost:3000
2. Should see agent interface with "Connect" button
3. No console errors in browser DevTools
4. Page loads without 500 errors

**Expected UI:**
- Welcome/landing view
- "Connect" or "Start Session" button
- Logo and branding elements
- Theme toggle (light/dark)

**Troubleshooting:**
- If port 3000 in use: `pnpm dev -- -p 3001`
- If env vars missing: Check `.env.local` exists and has correct values
- If build errors: Check `pnpm install` completed successfully

**Rationale:** Validates Next.js setup before proceeding to authentication

---

#### 2.6: Inspect Token Generation API Route

**What:** Review the built-in token generation endpoint to understand how authentication works

**File:** `/Users/seanreed/PythonProjects/voice-ai/lk-agent-1/frontend/voice-ai-frontend/app/api/token/route.ts`

**Read the file:**
```typescript
// Expected structure (review actual implementation)
import { AccessToken } from 'livekit-server-sdk';

export async function POST(request: Request) {
  const { roomName, participantName } = await request.json();

  const token = new AccessToken(
    process.env.LIVEKIT_API_KEY,
    process.env.LIVEKIT_API_SECRET,
    {
      identity: participantName,
      ttl: '2h', // Token valid for 2 hours
    }
  );

  token.addGrant({
    room: roomName,
    roomJoin: true,
    canPublish: true,
    canSubscribe: true,
  });

  return Response.json({ token: await token.toJwt() });
}
```

**Key Points:**
- Uses `livekit-server-sdk` to generate JWT tokens
- Reads `LIVEKIT_API_KEY` and `LIVEKIT_API_SECRET` from environment
- Grants room join, publish, and subscribe permissions
- Returns JWT token to frontend
- Token expires after 2 hours (LiveKit auto-refreshes for connected clients)

**Security Review:**
- ✓ API key/secret are server-side only (not exposed to browser)
- ✓ Token generation happens on server
- ✓ Appropriate permissions granted
- ⚠ Consider adding rate limiting for production

**Rationale:** Understanding token flow is critical for debugging connection issues

---

#### 2.7: Add Frontend to .gitignore (Backend Repo)

**What:** Prevent frontend from being committed to agent backend repo

**File:** `/Users/seanreed/PythonProjects/voice-ai/lk-agent-1/.gitignore`

**Add to `.gitignore`:**
```bash
echo "frontend/" >> .gitignore
```

**Verify:**
```bash
git status
# frontend/ should not appear in untracked files
```

**Alternative Approach:**
If you want to commit the frontend to the same repo:
- Create a separate `.gitignore` in `frontend/voice-ai-frontend/`
- Add standard Next.js ignores (`.next/`, `node_modules/`, `.env.local`)

**Rationale:** Keep frontend and backend as separate concerns, or manage carefully if in same repo

---

### Success Criteria

#### Automated Verification:

- [ ] Frontend directory created: `ls frontend/voice-ai-frontend`
- [ ] Dependencies installed: `pnpm list --depth=0` shows key packages
- [ ] Environment variables configured: `cat .env.local | grep LIVEKIT_API_KEY`
- [ ] Development server starts: `pnpm dev` runs without errors
- [ ] No TypeScript errors: `pnpm run build` completes successfully

#### Manual Verification:

- [ ] Visit http://localhost:3000 in browser
- [ ] Page loads without 500 errors
- [ ] UI displays welcome screen with "Connect" button
- [ ] No console errors in browser DevTools
- [ ] Theme toggle works (light/dark mode)
- [ ] Responsive design works on mobile viewport

**Verify:** After completing automated verification, open the app in a browser and verify UI loads correctly before proceeding to Phase 3.

---

## Phase 3: Authentication and Token Generation

### Overview

Configure and test the JWT token generation flow to ensure frontend can authenticate users with LiveKit and connect them to agent sessions.

### Context

Before starting, ensure:
- Phase 2 completed successfully
- Development server running at http://localhost:3000
- Environment variables configured in `.env.local`

Files to review:
- `frontend/voice-ai-frontend/app/api/token/route.ts` - Token generation endpoint
- `frontend/voice-ai-frontend/.env.local` - Environment configuration
- `frontend/voice-ai-frontend/components/app/` - Client-side connection logic

### Dependencies

**Depends on:** Phase 2 (frontend setup)

**Required by:** Phase 4 (connection testing)

### Changes Required

#### 3.1: Test Token Generation Endpoint

**What:** Verify the token API endpoint works correctly

**Command:**
```bash
# Start dev server (if not running)
cd /Users/seanreed/PythonProjects/voice-ai/lk-agent-1/frontend/voice-ai-frontend
pnpm dev

# In another terminal, test the endpoint
curl -X POST http://localhost:3000/api/token \
  -H "Content-Type: application/json" \
  -d '{"roomName": "test-room", "participantName": "test-user"}'
```

**Expected Response:**
```json
{
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**Validate Token:**
```bash
# Decode the JWT to inspect claims (copy token from response)
echo "eyJhbGciOiJ..." | cut -d'.' -f2 | base64 -d | jq
```

**Expected Token Payload:**
```json
{
  "exp": 1234567890,
  "iss": "APIxxxxxxxxxxxx",
  "sub": "test-user",
  "nbf": 1234567890,
  "video": {
    "room": "test-room",
    "roomJoin": true,
    "canPublish": true,
    "canSubscribe": true,
    "canPublishData": true
  }
}
```

**Troubleshooting:**
- If 500 error: Check environment variables in `.env.local`
- If "api_key undefined": Verify `LIVEKIT_API_KEY` is set
- If "invalid signature": Check `LIVEKIT_API_SECRET` is correct
- If no response: Verify dev server is running on port 3000

**Rationale:** Token generation must work before attempting to connect to LiveKit

---

#### 3.2: Review Client-Side Connection Logic

**What:** Understand how the frontend connects to LiveKit rooms

**Files to Review:**
```bash
# Main session component
cat frontend/voice-ai-frontend/components/app/session-view.tsx

# View controller
cat frontend/voice-ai-frontend/components/app/view-controller.tsx

# Connection utilities
cat frontend/voice-ai-frontend/lib/connection.ts
```

**Key Flow:**
1. User clicks "Connect" button
2. Frontend generates room name (random or predefined)
3. Frontend fetches token from `/api/token` endpoint
4. Frontend connects to LiveKit room using `livekit-client`
5. Agent is automatically dispatched to room
6. User and agent establish WebRTC connection
7. Audio tracks are exchanged

**Important Variables:**
- `NEXT_PUBLIC_LIVEKIT_URL` - LiveKit server URL (browser-accessible)
- Room name generation logic
- Participant name/identity
- Agent dispatch configuration

**Rationale:** Understanding client-side logic helps debug connection issues

---

#### 3.3: Configure Agent Dispatch

**What:** Ensure frontend triggers automatic agent dispatch when users connect

**File:** Review `frontend/voice-ai-frontend/app/api/connection-details/route.ts` (if exists) or equivalent

**Verify Agent Name Configuration:**

**Option A: Automatic Dispatch (Recommended):**
```env
# In .env.local
AGENT_NAME=
# Blank means "dispatch any available agent"
```

**Option B: Specific Agent:**
```env
# In .env.local
AGENT_NAME=agent_abc123
# Uses specific agent by ID or name
```

**Check Token Grant Configuration (Audio-Only):**
```typescript
// In app/api/token/route.ts or connection-details/route.ts
token.addGrant({
  room: roomName,
  roomJoin: true,
  canPublish: true,      // Allow publishing audio
  canSubscribe: true,    // Allow receiving audio
  canPublishSources: [   // AUDIO-ONLY: restrict to microphone
    'microphone'
    // NOTE: 'camera' and 'screen_share' are NOT included
  ],
});
```

**For agent-starter-react:**
The template typically handles agent dispatch automatically when a participant joins a room. Verify this by checking the token generation code and connection details endpoint.

**Rationale:** Agent won't join room unless dispatch is configured correctly

---

#### 3.4: Test Token Expiration and Refresh

**What:** Verify token expiration is set correctly and LiveKit handles refresh

**Check Current TTL:**
```typescript
// In app/api/token/route.ts
const token = new AccessToken(
  process.env.LIVEKIT_API_KEY,
  process.env.LIVEKIT_API_SECRET,
  {
    identity: participantName,
    ttl: '2h', // Current setting
  }
);
```

**Recommended TTL:**
- Development: `2h` (2 hours)
- Production: `2h` (LiveKit auto-refreshes for connected clients)
- Pre-generated tokens: `1h` (if caching tokens)

**Token Refresh Behavior:**
- LiveKit client SDK automatically refreshes tokens before expiration
- Refresh happens for connected clients only
- Disconnected users must request new tokens

**No changes needed if TTL is already `2h`.**

**Rationale:** Prevents users from being disconnected due to token expiration

---

#### 3.5: Add Security Headers (Optional but Recommended)

**What:** Add security headers to token API route

**File:** `frontend/voice-ai-frontend/middleware.ts` (create if doesn't exist)

**Content:**
```typescript
import { NextResponse } from 'next/server';
import type { NextRequest } from 'next/server';

export function middleware(request: NextRequest) {
  const response = NextResponse.next();

  // Security headers
  response.headers.set('X-Content-Type-Options', 'nosniff');
  response.headers.set('X-Frame-Options', 'DENY');
  response.headers.set('X-XSS-Protection', '1; mode=block');

  return response;
}

export const config = {
  matcher: '/api/:path*',
};
```

**Optional Rate Limiting:**
Consider adding rate limiting to `/api/token` endpoint to prevent abuse.

**Rationale:** Basic security hardening for production deployments

---

### Success Criteria

#### Automated Verification:

- [ ] Token endpoint returns valid JWT: `curl -X POST http://localhost:3000/api/token -H "Content-Type: application/json" -d '{"roomName":"test","participantName":"user"}' | jq .token`
- [ ] Token payload contains correct claims: Decode JWT and verify `video.roomJoin: true`
- [ ] Environment variables loaded: `console.log(process.env.LIVEKIT_API_KEY)` in token route shows value (not undefined)
- [ ] Token has correct expiration: Decoded JWT shows `exp` timestamp 2 hours in future

#### Manual Verification:

- [ ] Token endpoint accessible via browser: Visit http://localhost:3000/api/token (should return 405 Method Not Allowed for GET)
- [ ] No errors in Next.js server logs when generating tokens
- [ ] Token decodes successfully at https://jwt.io
- [ ] Token issuer (`iss`) matches your LiveKit API key
- [ ] Token subject (`sub`) matches requested participant name

**Verify:** After completing automated verification, test token generation with curl and decode the JWT to inspect claims before proceeding to Phase 4.

---

## Phase 4: Connection Testing and Optimization

### Overview

Test the end-to-end connection flow from frontend to agent, verify audio works correctly, and optimize the connection speed.

### Context

Before starting, ensure:
- Phase 3 completed successfully
- Agent running on LiveKit Cloud (`lk agent status` shows Running)
- Frontend running at http://localhost:3000
- Token generation working

Files to review:
- `frontend/voice-ai-frontend/components/app/session-view.tsx` - Session management
- `frontend/voice-ai-frontend/components/agents-ui/` - UI components

Tools needed:
- Browser with microphone access
- Terminal for monitoring agent logs

### Dependencies

**Depends on:** Phases 1-3 (agent deployed, frontend configured, authentication working)

**Required by:** Phase 5 (customization), Phase 6 (production deployment)

### Changes Required

#### 4.1: Monitor Agent Logs

**What:** Start monitoring agent logs before testing connection

**Command:**
```bash
# Open a dedicated terminal window for agent logs
lk agent logs --follow
```

**Keep this terminal open during all testing.**

**What to Look For:**
- Agent initialization messages
- Room join events
- STT transcriptions
- LLM requests/responses
- TTS generation
- WebRTC connection events
- Any error messages

**Rationale:** Real-time logs are essential for debugging connection issues

---

#### 4.2: Test Basic Connection Flow

**What:** Connect to the agent via frontend and verify basic functionality

**Steps:**

1. Open browser to http://localhost:3000
2. Open browser DevTools Console (F12 → Console tab)
3. Click "Connect" or "Start Session" button
4. Grant microphone permissions when prompted
5. Observe connection states in UI:
   - "Initializing..."
   - "Listening" (agent ready for input)
   - "Thinking" (processing speech)
   - "Speaking" (agent responding)

**Expected Behavior:**
- Connection establishes within 3-5 seconds
- Agent state transitions to "Listening"
- No errors in browser console
- Agent logs show room join event

**Troubleshooting:**
- **Connection hangs:** Check token endpoint, verify LIVEKIT_URL is correct
- **"Failed to connect":** Check agent status (`lk agent status`), verify agent is Running
- **Microphone permission denied:** Grant permission in browser settings
- **No audio:** Check browser audio output, verify speakers are enabled
- **WebRTC errors:** Check firewall, ensure WebRTC ports not blocked

**Rationale:** Validates basic connection before testing voice interaction

---

#### 4.3: Test Voice Interaction

**What:** Verify end-to-end voice pipeline (STT → LLM → TTS)

**Steps:**

1. With frontend connected and agent in "Listening" state
2. Speak clearly into your microphone: "Hello, can you hear me?"
3. Observe agent state transition:
   - "Listening" → "Thinking" → "Speaking"
4. Listen for agent's voice response
5. Check agent logs for:
   - STT transcription of your speech
   - LLM request and response
   - TTS generation

**Expected Outcome:**
- Agent responds with natural voice within 2-4 seconds
- Transcription appears in logs (if logging enabled)
- No audio dropouts or distortion
- Agent response is contextually appropriate

**Additional Test Cases:**
- **Interruption:** Speak while agent is speaking (should handle gracefully)
- **Silence:** Wait 10 seconds without speaking (agent should remain connected)
- **Background Noise:** Test with ambient noise (should filter with VAD)
- **Multiple Turns:** Have a multi-turn conversation

**Troubleshooting:**
- **No transcription:** Check AssemblyAI API key in agent secrets
- **No LLM response:** Check OpenAI API key, verify LLM model is available
- **No TTS audio:** Check Cartesia API key, verify TTS voice model
- **Garbled audio:** Check network connection, reduce network congestion
- **High latency:** Check agent logs for slow API calls, consider region optimization

**Rationale:** Validates the complete voice AI pipeline works end-to-end

---

#### 4.4: Verify Audio Visualization

**What:** Test the audio visualizer component works correctly

**Steps:**

1. With frontend connected
2. Speak into microphone
3. Observe audio visualization:
   - Bars should animate when you speak
   - Bars should pulse when agent speaks
   - Different colors/states for listening vs speaking

**Expected Behavior:**
- `BarVisualizer` component shows real-time audio levels
- Smooth animations
- Clear visual feedback of agent state
- No lag between audio and visualization

**Check Component:**
```bash
# Review visualizer component
cat frontend/voice-ai-frontend/components/agents-ui/bar-visualizer.tsx
```

**Troubleshooting:**
- **No visualization:** Check if audio track is being passed to component
- **Choppy animation:** Check browser performance, reduce animation complexity
- **Wrong colors:** Review CSS/Tailwind classes

**Rationale:** Visual feedback improves user experience and debugging

---

#### 4.5: Test Disconnection and Reconnection

**What:** Verify graceful disconnect and ability to reconnect

**Steps:**

**Test Disconnect:**
1. With frontend connected
2. Click "Disconnect" or "End Session" button
3. Observe clean disconnect:
   - Agent logs show participant left
   - No error messages
   - UI returns to welcome screen

**Test Reconnect:**
1. Click "Connect" again
2. Verify new session starts successfully
3. Test voice interaction again

**Test Network Interruption (Optional):**
1. While connected, disable network (Wi-Fi off)
2. Observe reconnection behavior
3. Re-enable network
4. Verify auto-reconnect or error message

**Expected Behavior:**
- Clean disconnect without errors
- Ability to reconnect immediately
- Each session gets unique room/token
- No lingering WebRTC connections

**Rationale:** Ensures robust connection lifecycle management

---

#### 4.6: Optimize Connection Speed

**What:** Reduce connection time from 3-5 seconds to <1 second using optimization techniques

**Current Flow (Sequential):**
```
1. Click Connect (0ms)
2. Fetch token from /api/token (500ms)
3. Connect to LiveKit room (1000ms)
4. Agent dispatched (1000ms)
5. Agent connects and publishes (1500ms)
Total: ~4000ms (4 seconds)
```

**Optimization 1: Pre-generate Tokens**

Create a "warm token" approach for faster connection:

**File:** Create `frontend/voice-ai-frontend/hooks/use-warm-token.ts`

```typescript
'use client';

import { useState, useEffect } from 'react';

export function useWarmToken() {
  const [token, setToken] = useState<string | null>(null);

  useEffect(() => {
    // Pre-generate token on page load
    async function generateToken() {
      const response = await fetch('/api/token', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          roomName: `room-${Date.now()}`,
          participantName: `user-${Math.random().toString(36).substring(7)}`,
        }),
      });
      const data = await response.json();
      setToken(data.token);
    }

    generateToken();
  }, []);

  return token;
}
```

**Usage in Session Component:**
```typescript
// In session-view.tsx or similar
const warmToken = useWarmToken();

// Use warmToken when connecting instead of fetching on-demand
```

**Optimization 2: Concurrent Dispatch**

Modify connection logic to dispatch agent and connect user simultaneously:

```typescript
// Parallel connection
const [roomConnection, agentDispatch] = await Promise.all([
  connectToRoom(token),
  dispatchAgent(roomName) // If manual dispatch required
]);
```

**Expected Improvement:**
- Pre-generated token: -500ms (eliminates token fetch delay)
- Concurrent dispatch: -1000ms (parallel instead of sequential)
- **New total:** ~2500ms → ~1500ms (1.5 seconds)

**Trade-offs:**
- Pre-generated tokens have expiration (ensure 2h TTL)
- Unused tokens waste resources (minimal cost)
- Complexity slightly increases

**Rationale:** Faster connections improve user experience and perceived performance

---

#### 4.7: Test on Multiple Browsers

**What:** Verify cross-browser compatibility

**Browsers to Test:**
- Chrome/Chromium
- Firefox
- Safari (macOS/iOS)
- Edge

**Test Matrix:**

| Browser | Connection | Audio Input | Audio Output | Visualization |
|---------|-----------|-------------|--------------|---------------|
| Chrome  | ✓         | ✓           | ✓            | ✓             |
| Firefox | ?         | ?           | ?            | ?             |
| Safari  | ?         | ?           | ?            | ?             |
| Edge    | ?         | ?           | ?            | ?             |

**Common Issues:**
- **Safari:** May require user interaction before audio playback
- **Firefox:** Different WebRTC implementation, may have quirks
- **Mobile Safari:** Requires specific audio context handling
- **Edge:** Generally compatible with Chrome

**Rationale:** Ensures wide browser support for production deployment

---

### Success Criteria

#### Automated Verification:

- [ ] Connection establishes successfully: Monitor for "Room connected" event in logs
- [ ] Agent joins room: `lk agent logs` shows room join event
- [ ] WebRTC connection: Browser DevTools Network tab shows WebRTC connections
- [ ] No console errors: Browser DevTools Console shows no red errors
- [ ] Audio tracks published: Check LiveKit Cloud dashboard for active tracks

#### Manual Verification:

- [ ] Voice input recognized: Speak and verify agent responds
- [ ] Voice output works: Hear agent's TTS response clearly
- [ ] Audio visualization animates correctly
- [ ] Agent state transitions work (initializing → listening → thinking → speaking)
- [ ] Interruption handling works (speak during agent response)
- [ ] Disconnect and reconnect works cleanly
- [ ] Connection time <3 seconds (before optimization) or <1.5s (after optimization)
- [ ] Works in Chrome, Firefox, and Safari

**Verify:** After completing automated verification, have a multi-turn conversation with the agent and test all edge cases before proceeding to Phase 5.

---

## Phase 5: Frontend Customization

### Overview

Customize the frontend with your branding, colors, logo, and company information to make it production-ready.

### Context

Before starting, ensure:
- Phase 4 completed successfully
- Voice interaction working end-to-end
- Frontend running at http://localhost:3000

Files to customize:
- `frontend/voice-ai-frontend/app-config.ts` - Main configuration
- `frontend/voice-ai-frontend/public/` - Static assets (logo, favicon)
- `frontend/voice-ai-frontend/app/layout.tsx` - Page metadata
- `frontend/voice-ai-frontend/tailwind.config.ts` - Theme colors

### Dependencies

**Depends on:** Phase 4 (connection testing completed)

**Required by:** Phase 6 (production deployment)

### Changes Required

#### 5.1: Update App Configuration

**What:** Customize company name, page title, and feature flags

**File:** `frontend/voice-ai-frontend/app-config.ts`

**Edit:**
```typescript
export const APP_CONFIG_DEFAULTS = {
  // Branding
  companyName: "Your Company Name", // Change this
  pageTitle: "AI Voice Assistant | Your Company", // Change this

  // Logo URLs
  logoUrl: "/logo.svg", // Update after adding logo in 5.2
  logoUrlDark: "/logo-dark.svg", // Optional: separate dark mode logo

  // Accent color
  accentColor: "#4F46E5", // Change to your brand color (hex)

  // Feature toggles - AUDIO-ONLY CONFIGURATION
  supportsChatInput: false, // Disable text chat (audio-only)
  supportsVideoInput: false, // DISABLE camera video (audio-only)
  supportsScreenShare: false, // DISABLE screen sharing (audio-only)
  isPreConnectBufferEnabled: true, // Pre-load for faster connection

  // Optional: Agent configuration
  defaultAgentName: "", // Leave blank for auto-dispatch
};
```

**Example Customization (Audio-Only):**
```typescript
export const APP_CONFIG_DEFAULTS = {
  companyName: "Acme Voice AI",
  pageTitle: "Voice AI Assistant | Acme Corp",
  logoUrl: "/acme-logo.svg",
  accentColor: "#FF6B35", // Orange
  supportsChatInput: false, // Audio-only: no text chat
  supportsVideoInput: false, // Audio-only: no camera
  supportsScreenShare: false, // Audio-only: no screen share
  isPreConnectBufferEnabled: true,
};
```

**Rationale:** Centralizes configuration for easy customization without code changes

---

#### 5.2: Add Custom Logo

**What:** Replace default logo with your company logo

**Steps:**

1. Prepare logo files:
   - **Format:** SVG (preferred) or PNG
   - **Size:**
     - SVG: Any size (scalable)
     - PNG: 200x200px minimum, transparent background
   - **Naming:**
     - Light mode: `logo.svg` or `logo.png`
     - Dark mode (optional): `logo-dark.svg` or `logo-dark.png`

2. Copy to public directory:
   ```bash
   cp /path/to/your/logo.svg frontend/voice-ai-frontend/public/logo.svg
   # Optional: dark mode logo
   cp /path/to/your/logo-dark.svg frontend/voice-ai-frontend/public/logo-dark.svg
   ```

3. Update `app-config.ts`:
   ```typescript
   logoUrl: "/logo.svg",
   logoUrlDark: "/logo-dark.svg", // If you have separate dark logo
   ```

4. Verify logo appears:
   - Restart dev server: `pnpm dev`
   - Visit http://localhost:3000
   - Check logo displays correctly
   - Toggle light/dark mode to test both logos

**Fallback:**
If you don't have a logo ready, the template includes a default placeholder logo.

**Rationale:** Custom logo reinforces brand identity

---

#### 5.3: Customize Theme Colors

**What:** Update color scheme to match your brand

**File:** `frontend/voice-ai-frontend/tailwind.config.ts`

**Edit:**
```typescript
export default {
  theme: {
    extend: {
      colors: {
        // Primary brand color
        primary: {
          50: '#f0f9ff',
          100: '#e0f2fe',
          // ... continue through 950
          500: '#4F46E5', // Main brand color (change this)
          600: '#4338ca',
          // ...
        },
        // Accent color
        accent: {
          DEFAULT: '#FF6B35', // Change to your accent color
          light: '#FF8A5B',
          dark: '#E5501F',
        },
      },
    },
  },
};
```

**Quick Method (Use Accent Color from app-config.ts):**

The template may automatically use `accentColor` from `app-config.ts`. If so, just update that value:

```typescript
// In app-config.ts
accentColor: "#FF6B35", // Your brand color
```

**Generate Full Color Palette:**
Use tools like https://uicolors.app/create to generate a full Tailwind color palette from your brand color.

**Test Theme:**
- Restart dev server
- Visit http://localhost:3000
- Check buttons, links, highlights use new colors
- Toggle light/dark mode to verify both themes

**Rationale:** Consistent color scheme creates professional, branded experience

---

#### 5.4: Update Page Metadata

**What:** Set page title, description, and favicon for SEO and browser display

**File:** `frontend/voice-ai-frontend/app/layout.tsx`

**Edit:**
```typescript
export const metadata: Metadata = {
  title: "AI Voice Assistant | Your Company", // Change this
  description: "Connect with our AI voice assistant for instant help and support.", // Change this
  icons: {
    icon: '/favicon.ico', // Update after adding favicon
  },
  openGraph: {
    title: "AI Voice Assistant | Your Company",
    description: "Connect with our AI voice assistant for instant help and support.",
    images: ['/og-image.png'], // Optional: social share image
  },
};
```

**Add Custom Favicon:**

1. Generate favicon files (use https://realfavicongenerator.net/):
   - `favicon.ico` (16x16, 32x32, 48x48)
   - `apple-touch-icon.png` (180x180)
   - `favicon-16x16.png`
   - `favicon-32x32.png`

2. Copy to `public/`:
   ```bash
   cp /path/to/favicon.ico frontend/voice-ai-frontend/public/
   cp /path/to/apple-touch-icon.png frontend/voice-ai-frontend/public/
   ```

3. Verify in browser:
   - Clear browser cache
   - Visit http://localhost:3000
   - Check browser tab shows your favicon

**Optional: Open Graph Image (Social Sharing):**
Create `og-image.png` (1200x630px) for social media previews.

**Rationale:** Professional metadata improves SEO and user experience

---

#### 5.5: Customize Welcome Message

**What:** Update the welcome screen text and instructions

**File:** `frontend/voice-ai-frontend/components/app/welcome-view.tsx` or similar

**Find and Edit:**
```typescript
<h1>Welcome to [Your Company] Voice AI</h1>
<p>
  Click the button below to start a voice conversation with our AI assistant.
  We can help you with questions, information, and more.
</p>
```

**Example Customization:**
```typescript
<h1>Welcome to Acme Voice Assistant</h1>
<p>
  Our AI assistant is ready to help you 24/7. Click "Connect" to start a
  natural voice conversation. Just speak naturally - no keywords or commands needed.
</p>
<ul>
  <li>Get instant answers to your questions</li>
  <li>Learn about our products and services</li>
  <li>Get personalized recommendations</li>
</ul>
```

**Rationale:** Clear messaging helps users understand what to expect

---

#### 5.6: Configure Audio-Only Mode (REQUIRED)

**What:** Disable video/screen share features for audio-only application

**File:** `frontend/voice-ai-frontend/app-config.ts`

**REQUIRED Configuration for Audio-Only App:**
```typescript
export const APP_CONFIG_DEFAULTS = {
  // ... other settings
  supportsChatInput: false, // Audio-only: disable text chat
  supportsVideoInput: false, // REQUIRED: disable camera
  supportsScreenShare: false, // REQUIRED: disable screen sharing
  isPreConnectBufferEnabled: true, // Keep for faster connection
};
```

**Effect:**
- Video camera icon hidden
- Screen share button removed
- UI simplified to voice-only interface
- No video/screenshare permission requests to users
- Browser only requests microphone permission

**IMPORTANT:** This is a required configuration for this audio-only application. Do NOT enable video or screen sharing features.

**Rationale:** This application is designed for audio-only interaction. No video capabilities should be exposed to users.

---

#### 5.7: Test Customizations

**What:** Verify all customizations display correctly

**Checklist:**
- [ ] Company name displays on welcome screen
- [ ] Custom logo appears (both light and dark modes)
- [ ] Page title shows in browser tab
- [ ] Custom favicon appears in browser tab
- [ ] Brand colors visible on buttons and accents
- [ ] Welcome message updated with custom text
- [ ] Video/screenshare features are hidden (REQUIRED for audio-only)
- [ ] Only microphone permission requested (no camera/screenshare)
- [ ] No broken images or 404s
- [ ] Responsive design maintained on mobile

**Testing Steps:**
1. Restart dev server: `pnpm dev`
2. Clear browser cache (Cmd+Shift+R on Mac, Ctrl+Shift+R on Windows)
3. Visit http://localhost:3000
4. Toggle light/dark theme
5. Resize browser to mobile size (375px width)
6. Check all visual elements

**Rationale:** Ensures professional, branded appearance before production deployment

---

### Success Criteria

#### Automated Verification:

- [ ] Build succeeds: `pnpm run build` completes without errors
- [ ] No TypeScript errors: `pnpm run type-check` (if available)
- [ ] Static assets exist: `ls public/logo.svg public/favicon.ico`
- [ ] Config updated: `cat app-config.ts | grep companyName` shows your company

#### Manual Verification:

- [ ] Custom company name displays on welcome screen
- [ ] Custom logo visible (light and dark modes)
- [ ] Page title correct in browser tab
- [ ] Favicon visible in browser tab
- [ ] Brand colors applied throughout UI
- [ ] Welcome message updated
- [ ] Video/screenshare features are hidden (REQUIRED - verify no camera/screenshare icons)
- [ ] Browser only requests microphone permission (NOT camera)
- [ ] Mobile responsive (test at 375px width)
- [ ] No console errors or warnings
- [ ] All images load correctly (no broken images)

**Verify:** After completing automated verification, thoroughly test the UI on desktop and mobile, in light and dark modes, before proceeding to Phase 6.

---

## Phase 6: Production Deployment

### Overview

Deploy the customized frontend to Vercel (or another hosting provider) to make it publicly accessible via a URL that clients can visit.

### Context

Before starting, ensure:
- Phase 5 completed successfully
- All customizations tested locally
- Frontend builds successfully (`pnpm run build`)
- Agent deployed and running on LiveKit Cloud

Files to review:
- `frontend/voice-ai-frontend/.env.local` - Environment variables (will configure in Vercel)
- `frontend/voice-ai-frontend/next.config.js` - Next.js configuration
- `frontend/voice-ai-frontend/package.json` - Dependencies and scripts

Accounts needed:
- Vercel account (free tier sufficient): https://vercel.com
- GitHub account (for connecting repo)

### Dependencies

**Depends on:** Phases 1-5 (agent deployed, frontend customized and tested)

**Required by:** None (final phase)

### Changes Required

#### 6.1: Create Production Build

**What:** Verify the production build works correctly before deploying

**Commands:**
```bash
cd /Users/seanreed/PythonProjects/voice-ai/lk-agent-1/frontend/voice-ai-frontend

# Create production build
pnpm run build

# Test production build locally
pnpm start
```

**Expected Output:**
```
> next build

✓ Compiled successfully
✓ Linting and checking validity of types
✓ Collecting page data
✓ Generating static pages (X/X)
✓ Finalizing page optimization

Route (app)                              Size     First Load JS
┌ ○ /                                    XXX kB        XXX kB
└ ○ /api/token                          XXX B          XXX kB
```

**Test Production Build:**
1. Visit http://localhost:3000 (pnpm start)
2. Connect to agent
3. Verify voice interaction works
4. Check for any errors in console

**Troubleshooting:**
- If build fails: Check TypeScript errors, fix before proceeding
- If errors about environment variables: Ensure `.env.local` exists
- If runtime errors: Check browser console for specific issues

**Rationale:** Catches production-specific issues before deployment

---

#### 6.2: Push Frontend to GitHub (Optional but Recommended)

**What:** Create a Git repository for the frontend to enable easy Vercel deployment

**Option A: Separate Repository (Recommended):**

```bash
cd /Users/seanreed/PythonProjects/voice-ai/lk-agent-1/frontend/voice-ai-frontend

# Initialize git repository
git init

# Add .gitignore for Next.js
cat > .gitignore << 'EOF'
# Next.js
.next/
out/
build/
dist/

# Dependencies
node_modules/

# Environment variables
.env
.env.local
.env.production.local
.env.development.local
.env.test.local

# Logs
npm-debug.log*
yarn-debug.log*
yarn-error.log*
pnpm-debug.log*

# OS
.DS_Store
*.swp
*.swo

# IDE
.vscode/
.idea/

# Vercel
.vercel
EOF

# Add files
git add .
git commit -m "Initial commit: Voice AI frontend"

# Create GitHub repository (via GitHub UI or CLI)
gh repo create voice-ai-frontend --public --source=. --remote=origin --push
```

**Option B: Same Repository as Agent:**

If you want frontend and agent in the same repo:
```bash
cd /Users/seanreed/PythonProjects/voice-ai/lk-agent-1

# Remove frontend/ from .gitignore
sed -i '' '/^frontend\//d' .gitignore

# Add and commit
git add frontend/
git commit -m "Add voice AI frontend"
git push
```

**Rationale:** Git repository enables continuous deployment and version control

---

#### 6.3: Sign Up for Vercel

**What:** Create a Vercel account for hosting the frontend

**Steps:**

1. Visit https://vercel.com
2. Click "Sign Up"
3. Choose "Continue with GitHub" (recommended)
4. Authorize Vercel to access your GitHub repositories

**Pricing:**
- **Free Tier:** Sufficient for testing and low traffic
  - Unlimited deployments
  - 100 GB bandwidth/month
  - Serverless functions included
- **Pro Tier:** $20/month (for production with higher traffic)

**Rationale:** Vercel provides seamless Next.js hosting with automatic deployments

---

#### 6.4: Deploy Frontend to Vercel

**What:** Deploy the frontend application to Vercel

**Steps:**

1. **From Vercel Dashboard:**
   - Click "Add New..." → "Project"
   - Select "Import Git Repository"
   - Choose your frontend repository
   - Configure project:
     - **Framework Preset:** Next.js (auto-detected)
     - **Root Directory:** `./` (or `frontend/voice-ai-frontend` if in monorepo)
     - **Build Command:** `pnpm run build` (auto-detected)
     - **Output Directory:** `.next` (auto-detected)
     - **Install Command:** `pnpm install` (auto-detected)

2. **Configure Environment Variables:**
   Click "Environment Variables" and add:

   ```
   LIVEKIT_API_KEY=APIxxxxxxxxxxxx
   LIVEKIT_API_SECRET=your-secret-here
   LIVEKIT_URL=wss://your-project.livekit.cloud
   NEXT_PUBLIC_LIVEKIT_URL=wss://your-project.livekit.cloud
   AGENT_NAME=
   ```

   **Important:**
   - Copy values from your local `.env.local`
   - Apply to "Production", "Preview", and "Development" environments

3. **Deploy:**
   - Click "Deploy"
   - Wait for build to complete (2-5 minutes)

**Expected Outcome:**
```
✓ Build successful
✓ Deployment successful
Your project is now live at: https://your-app.vercel.app
```

**Rationale:** Makes frontend publicly accessible via HTTPS URL

---

#### 6.5: Test Production Deployment

**What:** Verify the deployed frontend works correctly

**Steps:**

1. Visit your Vercel URL: `https://your-app.vercel.app`

2. **Test Checklist:**
   - [ ] Page loads without errors
   - [ ] Custom branding displays correctly
   - [ ] Click "Connect" button
   - [ ] Verify ONLY microphone permission requested (no camera/screenshare)
   - [ ] Grant microphone permission
   - [ ] Speak to agent
   - [ ] Verify agent responds with voice
   - [ ] Confirm no video/screenshare UI elements visible
   - [ ] Test on mobile device
   - [ ] Test in different browsers

3. **Monitor Logs:**
   ```bash
   # Monitor agent logs during production test
   lk agent logs --follow
   ```

4. **Check Vercel Deployment Logs:**
   - Go to Vercel dashboard → Your project → Deployments
   - Click on latest deployment → "Functions" tab
   - Check for any errors in `/api/token` function

**Troubleshooting:**
- **"Failed to connect":** Check environment variables in Vercel
- **Token errors:** Verify `LIVEKIT_API_KEY` and `LIVEKIT_API_SECRET` are correct
- **CORS errors:** Ensure `NEXT_PUBLIC_LIVEKIT_URL` is set correctly
- **Agent not joining:** Check agent status, verify agent is Running

**Rationale:** Ensures production environment works correctly

---

#### 6.6: Configure Custom Domain (Optional)

**What:** Use a custom domain instead of `your-app.vercel.app`

**Prerequisites:**
- Own a domain name (e.g., `voiceai.yourcompany.com`)
- Access to domain DNS settings

**Steps:**

1. **In Vercel Dashboard:**
   - Go to your project → Settings → Domains
   - Click "Add Domain"
   - Enter your domain: `voiceai.yourcompany.com`

2. **Configure DNS:**
   Vercel will provide DNS configuration instructions:

   **Option A: CNAME (Subdomain):**
   ```
   Type: CNAME
   Name: voiceai
   Value: cname.vercel-dns.com
   ```

   **Option B: A Record (Root Domain):**
   ```
   Type: A
   Name: @
   Value: 76.76.21.21
   ```

3. **Wait for DNS Propagation:**
   - Usually takes 5-60 minutes
   - Vercel will auto-configure SSL certificate (Let's Encrypt)

4. **Verify:**
   - Visit `https://voiceai.yourcompany.com`
   - Should show your frontend with SSL (green lock icon)

**Rationale:** Custom domain provides professional appearance and brand consistency

---

#### 6.7: Enable Automatic Deployments

**What:** Configure automatic deployments when you push to GitHub

**Vercel Auto-Deploys By Default:**
- **Production:** Deploys on push to `main` branch
- **Preview:** Deploys on push to any other branch or PR

**Customize (Optional):**
1. Go to Vercel dashboard → Your project → Settings → Git
2. Configure:
   - **Production Branch:** `main` (or `master`)
   - **Ignored Build Step:** (leave blank to build on every commit)

**Test Automatic Deployment:**
```bash
cd frontend/voice-ai-frontend

# Make a small change
echo "# Updated" >> README.md

# Commit and push
git add README.md
git commit -m "Test automatic deployment"
git push origin main
```

**Verify:**
- Visit Vercel dashboard
- Should see new deployment triggered automatically
- Wait for build to complete
- Visit production URL to see changes

**Rationale:** Enables continuous deployment for easy updates

---

#### 6.8: Set Up Production Monitoring (Recommended)

**What:** Monitor production errors and usage

**Vercel Analytics (Built-in):**
1. Go to Vercel dashboard → Your project → Analytics
2. View:
   - Page views
   - Geographic distribution
   - Performance metrics (Web Vitals)

**Error Tracking (Optional):**
Consider integrating Sentry or similar:
```bash
pnpm add @sentry/nextjs
npx @sentry/wizard@latest -i nextjs
```

**LiveKit Cloud Monitoring:**
- Visit LiveKit Cloud dashboard
- Monitor:
  - Active sessions
  - Agent usage
  - Costs (session minutes)

**Rationale:** Production monitoring helps identify and resolve issues quickly

---

#### 6.9: Create Shareable Link

**What:** Generate a clean, shareable URL for potential clients

**Your Production URL:**
```
https://your-app.vercel.app
```

**Or with Custom Domain:**
```
https://voiceai.yourcompany.com
```

**Create Marketing Materials:**
- Add link to your website
- Share via email campaigns
- Include in social media bios
- Create QR code for physical materials

**Example QR Code Generation:**
```bash
# Generate QR code (using qrencode)
brew install qrencode
qrencode -o voiceai-qr.png "https://voiceai.yourcompany.com"
```

**Rationale:** Easy sharing enables potential clients to access your voice AI

---

#### 6.10: Document Production URLs and Credentials

**What:** Save all production information for future reference

**Create:** `frontend/voice-ai-frontend/PRODUCTION.md`

**Content:**
```markdown
# Production Deployment Information

## URLs
- **Production Frontend:** https://your-app.vercel.app
- **Custom Domain:** https://voiceai.yourcompany.com (if configured)
- **LiveKit Cloud Dashboard:** https://cloud.livekit.io

## Vercel
- **Project:** voice-ai-frontend
- **Account:** your-email@example.com
- **Git Repository:** https://github.com/yourusername/voice-ai-frontend

## LiveKit Cloud
- **Project:** your-project-name
- **Region:** us-west-2
- **Agent ID:** agent_abc123

## Deployment Commands
```bash
# Deploy agent updates
cd /Users/seanreed/PythonProjects/voice-ai/lk-agent-1
lk agent deploy

# Deploy frontend updates (automatic via Git)
cd frontend/voice-ai-frontend
git add .
git commit -m "Update frontend"
git push origin main
```

## Monitoring
- **Agent Logs:** `lk agent logs --follow`
- **Vercel Logs:** https://vercel.com/your-project/deployments
- **LiveKit Dashboard:** https://cloud.livekit.io/projects/your-project

## Environment Variables (Vercel)
- LIVEKIT_API_KEY=APIxxxxxxxxxxxx
- LIVEKIT_API_SECRET=*** (not shown)
- LIVEKIT_URL=wss://your-project.livekit.cloud
- NEXT_PUBLIC_LIVEKIT_URL=wss://your-project.livekit.cloud

## Costs
- **LiveKit Cloud:** $0.01 per agent session minute
- **Vercel:** Free tier (or $20/month Pro)

## Support
- **LiveKit:** https://livekit.io/discord
- **Vercel:** https://vercel.com/support
```

**Rationale:** Documentation ensures you can manage production deployment long-term

---

### Success Criteria

#### Automated Verification:

- [ ] Production build succeeds: `pnpm run build` completes without errors
- [ ] Vercel deployment successful: Deployment status shows "Ready"
- [ ] HTTPS enabled: Visit production URL with green lock icon
- [ ] Environment variables configured: Check Vercel dashboard
- [ ] Custom domain configured (if applicable): DNS records set

#### Manual Verification:

- [ ] Visit production URL in browser
- [ ] Page loads without errors
- [ ] Custom branding displays correctly
- [ ] Click "Connect" and grant microphone access
- [ ] Speak to agent and verify voice response
- [ ] Test on mobile device (iOS Safari, Android Chrome)
- [ ] Test in incognito/private mode
- [ ] Share URL with colleague and get confirmation it works
- [ ] Agent logs show production sessions: `lk agent logs --follow`
- [ ] No errors in Vercel function logs

**Verify:** After completing automated verification, test the production URL on multiple devices and browsers, then share with a colleague to confirm public accessibility.

---

## Testing Strategy

### Unit Tests

**Not required for this plan.** The agent-starter-react template is a pre-built, production-ready template that doesn't require custom unit tests unless you add significant custom logic.

**Optional:** Add tests if you customize components heavily:
```bash
pnpm add -D @testing-library/react @testing-library/jest-dom jest
```

### Integration Tests

**End-to-End Testing:**

Manually test the complete flow:
1. User visits URL
2. Clicks "Connect"
3. Grants microphone access
4. Speaks to agent
5. Receives voice response
6. Disconnects cleanly

**Test Matrix:**

| Scenario | Steps | Expected Outcome |
|----------|-------|------------------|
| First Connection | Visit URL → Click Connect → Speak | Agent responds with voice |
| Interruption | Speak while agent is speaking | Agent handles gracefully |
| Disconnect/Reconnect | End session → Start new session | New session works |
| Multiple Turns | Have 3-5 turn conversation | All responses relevant |
| Mobile Safari | Test on iPhone/iPad | Full functionality |
| Network Interruption | Disable Wi-Fi during session | Reconnection or error message |

### Manual Testing Steps

**Pre-Deployment Checklist:**
1. [ ] Agent deployed and running: `lk agent status`
2. [ ] Local frontend works: `pnpm dev` at http://localhost:3000
3. [ ] Voice interaction successful
4. [ ] Audio visualization working
5. [ ] Custom branding applied
6. [ ] Production build succeeds: `pnpm run build`

**Post-Deployment Checklist:**
1. [ ] Production URL accessible
2. [ ] HTTPS enabled (green lock)
3. [ ] Voice interaction works on production
4. [ ] Mobile responsive
5. [ ] Cross-browser compatible
6. [ ] Shareable link works for external users

### Performance Considerations

**Metrics to Monitor:**
- **Connection Time:** Should be <3 seconds (or <1.5s with optimization)
- **Response Latency:** STT → LLM → TTS should be 2-4 seconds
- **Page Load Time:** Initial load <2 seconds (Lighthouse score >90)
- **Audio Quality:** No dropouts or distortion

**Optimization:**
- Enable pre-connect buffering in `app-config.ts`
- Use warm token approach (Phase 4.6)
- Minimize bundle size (Next.js handles automatically)
- Use CDN for static assets (Vercel provides automatically)

## References

### Original Ticket/Request
- User request: "I want potential clients to be able to interact with the livekit agent from this repo by clicking a link on a website."

### Documentation
- `docs/DEPLOYMENT.md` - Complete deployment guide for agent and frontend options
- `README.md` - Project overview and setup instructions
- `AGENTS.md` - Project guidelines and standards

### LiveKit Resources
- **Frontend Deployment Guide:** https://docs.livekit.io/agents/start/frontend/
- **agent-starter-react Repository:** https://github.com/livekit-examples/agent-starter-react
- **Token Authentication:** https://docs.livekit.io/home/get-started/authentication/
- **Agents Playground:** https://agents-playground.livekit.io/
- **LiveKit Cloud Dashboard:** https://cloud.livekit.io
- **React Components Docs:** https://docs.livekit.io/reference/components/react/

### NPM Packages
- **livekit-client:** Client SDK for browser WebRTC
- **@livekit/components-react:** React UI components
- **livekit-server-sdk:** Server-side token generation

### Vercel Resources
- **Vercel Platform:** https://vercel.com
- **Next.js Documentation:** https://nextjs.org/docs
- **Deployment Docs:** https://vercel.com/docs

### Related Plans
- None (initial implementation)

---

**End of Implementation Plan**
