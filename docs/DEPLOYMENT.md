# LiveKit Agent Deployment Guide

This guide provides detailed step-by-step instructions for deploying your voice AI agent to LiveKit Cloud, with specific focus on setting up development, staging, and production environments.

## Table of Contents

- [Prerequisites](#prerequisites)
- [Environment Strategy](#environment-strategy)
- [Initial Setup](#initial-setup)
  - [Step 1: Authenticate with LiveKit Cloud](#step-1-authenticate-with-livekit-cloud)
  - [Step 2: List Your Projects](#step-2-list-your-projects)
  - [Step 3: Set Default Project](#step-3-set-default-project)
  - [Step 4: Verify Project Context](#step-4-verify-project-context)
- [Deploying to Development Environment](#deploying-to-development-environment)
  - [Step 1: Navigate to Your Agent Directory](#step-1-navigate-to-your-agent-directory)
  - [Step 2: Prepare Your Secrets File](#step-2-prepare-your-secrets-file)
  - [Step 3: Create Initial Deployment](#step-3-create-initial-deployment)
  - [Step 4: Verify Deployment](#step-4-verify-deployment)
  - [Step 5: View Live Logs](#step-5-view-live-logs)
  - [Step 6: Test Your Agent](#step-6-test-your-agent)
- [Connecting to Your Deployed Agent](#connecting-to-your-deployed-agent)
  - [Connection Architecture](#connection-architecture)
  - [Option 1: LiveKit Agents Playground (Quick Test)](#option-1-livekit-agents-playground-quick-test)
  - [Option 2: LiveKit Meet (Video Conferencing)](#option-2-livekit-meet-video-conferencing)
  - [Option 3: Web Frontend (React/Next.js)](#option-3-web-frontend-reactnextjs)
  - [Option 4: iOS/macOS (Swift)](#option-4-iosmacOS-swift)
  - [Option 5: Flutter (Cross-Platform)](#option-5-flutter-cross-platform)
  - [Option 6: Web Embed Widget](#option-6-web-embed-widget)
  - [Connection Flow and Optimization](#connection-flow-and-optimization)
- [Managing Secrets](#managing-secrets)
  - [Viewing Current Secrets](#viewing-current-secrets)
  - [Adding or Updating Individual Secrets](#adding-or-updating-individual-secrets)
  - [Replacing All Secrets](#replacing-all-secrets)
  - [Mounting Secret Files](#mounting-secret-files)
  - [Secret Best Practices](#secret-best-practices)
- [Updating Deployments](#updating-deployments)
  - [Deploying Code Changes](#deploying-code-changes)
  - [Updating Secrets Only](#updating-secrets-only)
  - [Restarting Without Changes](#restarting-without-changes)
- [Monitoring and Troubleshooting](#monitoring-and-troubleshooting)
  - [Real-Time Logs](#real-time-logs)
  - [Build Logs](#build-logs)
  - [Agent Status Dashboard](#agent-status-dashboard)
  - [Checking Agent Health](#checking-agent-health)
  - [Common Issues and Solutions](#common-issues-and-solutions)
- [Common Workflows](#common-workflows)
  - [Workflow 1: Dev → Staging → Production](#workflow-1-dev--staging--production)
  - [Workflow 2: Hotfix Deployment](#workflow-2-hotfix-deployment)
  - [Workflow 3: Rolling Back a Bad Deployment](#workflow-3-rolling-back-a-bad-deployment)
  - [Workflow 4: Managing Multiple Environments](#workflow-4-managing-multiple-environments)
- [CLI Command Reference](#cli-command-reference)
  - [Project Management](#project-management)
  - [Agent Deployment](#agent-deployment)
  - [Secrets Management](#secrets-management)
  - [Monitoring](#monitoring)
  - [Version Control](#version-control)
  - [Cleanup](#cleanup)
- [Advanced Configuration](#advanced-configuration)
  - [Custom Dockerfile](#custom-dockerfile)
  - [Region Selection](#region-selection)
  - [Configuration File (livekit.toml)](#configuration-file-livekittoml)
- [Cost Management](#cost-management)
- [Additional Resources](#additional-resources)
- [Getting Help](#getting-help)

## Prerequisites

Before deploying, ensure you have:

1. **LiveKit CLI** installed and up to date
   ```bash
   # Install or update the LiveKit CLI
   brew install livekit/livekit/livekit-cli
   # or
   curl -sSL https://get.livekit.io/cli | bash
   ```

2. **LiveKit Cloud Account**
   - Sign up at [cloud.livekit.io](https://cloud.livekit.io)
   - Create separate projects for dev, staging, and production

3. **Working Agent Code**
   - Ensure your agent runs locally: `uv run python src/app.py`
   - All dependencies listed in `pyproject.toml` and `uv.lock`
   - Valid `Dockerfile` (one is included in this repo)

4. **API Keys for Third-Party Services**
   - OpenAI API key (for LLM)
   - AssemblyAI API key (for STT)
   - Cartesia API key (for TTS)

## Environment Strategy

**IMPORTANT:** Create separate LiveKit Cloud projects for each environment to prevent dev/test traffic from affecting production users.

Recommended setup:
- **Dev Project**: `my-agent-dev` - For active development and testing
- **Staging Project**: `my-agent-staging` - For pre-production validation
- **Production Project**: `my-agent-prod` - For live user traffic

Each project gets its own:
- `LIVEKIT_URL`
- `LIVEKIT_API_KEY`
- `LIVEKIT_API_SECRET`
- Agent deployments
- Secrets configuration

## Initial Setup

### Step 1: Authenticate with LiveKit Cloud

Open a terminal and run:

```bash
lk cloud auth
```

**What happens:**
- Opens your browser to authenticate
- Links your CLI to your LiveKit Cloud account
- Saves credentials for future commands

### Step 2: List Your Projects

View all available projects:

```bash
lk project list
```

**Output example:**
```
NAME                 PROJECT_ID
my-agent-dev        dev_abc123
my-agent-staging    stg_def456
my-agent-prod       prd_ghi789
```

### Step 3: Set Default Project

Set your dev project as the default:

```bash
lk project set-default "my-agent-dev"
```

**Pro tip:** You can switch between projects anytime using this command.

### Step 4: Verify Project Context

Confirm you're working in the correct project:

```bash
lk project current
```

## Deploying to Development Environment

### Step 1: Navigate to Your Agent Directory

```bash
cd /path/to/lk-agent-1
```

### Step 2: Prepare Your Secrets File

Create a `.env.local` file with your API keys:

```bash
# This file should already exist from local development
# Verify it contains all required secrets:
cat .env.local
```

Required secrets:
```env
# Third-party API keys
OPENAI_API_KEY=sk-...
ASSEMBLYAI_API_KEY=...
CARTESIA_API_KEY=...

# Note: LIVEKIT_URL, LIVEKIT_API_KEY, and LIVEKIT_API_SECRET
# are auto-injected by LiveKit Cloud - do NOT include them
```

**CRITICAL:** Ensure `.env.local` is in your `.gitignore` file to prevent committing secrets.

### Step 3: Create Initial Deployment

Run the create command:

```bash
lk agent create --secrets-file .env.local
```

**What happens:**
1. CLI registers a new agent with your Cloud project
2. Assigns a unique agent ID (e.g., `agent_abc123`)
3. Creates/updates `livekit.toml` configuration file
4. Auto-generates a `Dockerfile` if one doesn't exist
5. Uploads your source code to LiveKit's build service
6. Builds a container image from your Dockerfile
7. Deploys the container to your Cloud project
8. Encrypts and injects your secrets as environment variables

**Duration:** Initial builds typically take 2-5 minutes.

### Step 4: Verify Deployment

Check the agent status:

```bash
lk agent status
```

**Output example:**
```
Agent ID:     agent_abc123
Status:       Running
Replicas:     2/2 ready
Version:      v1
Last Deploy:  2026-01-24 10:30:00 UTC
Region:       us-west-2
```

Possible statuses:
- `Building` - Container image is being built
- `Running` - Agent is active and serving traffic
- `Sleeping` - Scaled to zero (no active sessions)
- `CrashLoop` - Agent is failing to start (check logs)
- `Build Failed` - Container build failed (check build logs)

### Step 5: View Live Logs

Stream real-time logs:

```bash
lk agent logs
```

**Pro tip:** Use `lk agent logs --follow` to keep the stream open, or `lk agent logs --tail 100` to see the last 100 lines.

### Step 6: Test Your Agent

1. **Using the web frontend:**
   ```bash
   # In a separate terminal, run your frontend
   cd /path/to/frontend
   npm run dev
   ```

2. **Verify connection:**
   - Open the frontend in your browser
   - Start a voice session
   - Monitor the agent logs in real-time
   - Confirm STT/LLM/TTS are working correctly

## Connecting to Your Deployed Agent

Once your agent is deployed and running on LiveKit Cloud, you need a frontend application to connect users to your voice AI assistant. LiveKit provides multiple options across web, mobile, and embedded platforms.

### Connection Architecture

Your agent communicates with frontends through **LiveKit WebRTC**, which provides fast and reliable real-time connectivity for:
- **Audio tracks** - Microphones and speakers
- **Video feeds** - Camera, screen sharing, virtual avatars
- **Text streams** - Transcriptions and real-time messaging
- **Data exchange** - Custom data packets and byte streams

**Connection sequence:**
1. Frontend fetches an access token from your token server
2. User connects to the LiveKit room
3. Agent is dispatched to the room
4. Agent connects and joins the room
5. User and agent publish/subscribe to each other's media tracks

### Option 1: LiveKit Agents Playground (Quick Test)

**Best for:** Quickly testing your deployed agent without any code

**URL:** [https://agents-playground.livekit.io/](https://agents-playground.livekit.io/)

**Overview:**

The LiveKit Agents Playground is a web-based tool for instantly connecting to and testing your deployed agent. No frontend setup required.

**Quick Start:**

1. **Get your LiveKit project credentials:**
   ```bash
   lk project current --json
   ```

2. **Open the playground:**
   - Navigate to [agents-playground.livekit.io](https://agents-playground.livekit.io/)

3. **Configure connection:**
   - **LiveKit URL:** `wss://your-project.livekit.cloud`
   - **API Key:** Your `LIVEKIT_API_KEY`
   - **API Secret:** Your `LIVEKIT_API_SECRET`

4. **Connect and test:**
   - Click "Connect"
   - Allow microphone access when prompted
   - Start speaking to your agent
   - Monitor the conversation in real-time

**Key Features:**
- Zero setup required
- Instant agent testing
- Audio visualization
- Agent state indicators (`initializing`, `listening`, `thinking`, `speaking`)
- Transcription display
- No code deployment needed

**Use cases:**
- Quick validation after deploying agent changes
- Demo your agent to stakeholders
- Debug agent behavior in real-time
- Test different prompts and interactions

**Monitoring:**
```bash
# Watch agent logs while testing in playground
lk agent logs --follow
```

### Option 2: LiveKit Meet (Video Conferencing)

**Best for:** Testing agents in multi-user conference scenarios, video calls with agents

**URL:** [https://meet.livekit.io/](https://meet.livekit.io/)

**Overview:**

LiveKit Meet is a production-ready video conferencing application that can connect to your agent alongside human participants.

**Quick Start:**

1. **Create a room token:**
   ```bash
   # Generate a token for the room
   lk token create \
     --room my-test-room \
     --identity user-1 \
     --valid-for 2h
   ```

2. **Join the room:**
   - Navigate to [meet.livekit.io](https://meet.livekit.io/)
   - Paste your token
   - Click "Join Room"

3. **Dispatch your agent to the room:**

   **Option A - Via LiveKit Cloud Dashboard:**
   - Go to your LiveKit Cloud project
   - Navigate to Rooms → Select "my-test-room"
   - Click "Dispatch Agent"

   **Option B - Via CLI (if you have agent dispatch configured):**
   ```bash
   # You may need to configure agent dispatch
   # See LiveKit docs for your specific setup
   ```

4. **Interact with your agent:**
   - Your agent joins as a participant
   - Speak naturally - the agent will respond
   - Test multi-party conversations

**Key Features:**
- Full video conferencing interface
- Screen sharing support
- Multiple participants + agent
- Chat messaging
- Recording capabilities
- Production-quality audio/video

**Use cases:**
- Testing agent in multi-user scenarios
- Video calls with AI assistant
- Screen sharing with agent analysis
- Conference moderation bots
- Live demos with multiple stakeholders

**Advanced Configuration:**

Create custom room tokens with specific permissions:
```bash
lk token create \
  --room agent-demo \
  --identity demo-user \
  --valid-for 4h \
  --can-publish \
  --can-subscribe \
  --metadata '{"user_type":"tester"}'
```

### Option 3: Web Frontend (React/Next.js)

**Best for:** Web applications, progressive web apps, browser-based interfaces

**Starter Repository:** [agent-starter-react](https://github.com/livekit-examples/agent-starter-react)

**Quick Start:**

```bash
# Clone the starter template
git clone https://github.com/livekit-examples/agent-starter-react.git
cd agent-starter-react

# Install dependencies
npm install

# Configure environment
cp .env.example .env.local
```

**Required environment variables** (`.env.local`):
```env
# Get these from your LiveKit Cloud project
LIVEKIT_URL=wss://your-project.livekit.cloud
LIVEKIT_API_KEY=APIxxxxxxxxxxxx
LIVEKIT_API_SECRET=your-secret-here

# Public URL (exposed to browser)
NEXT_PUBLIC_LIVEKIT_URL=wss://your-project.livekit.cloud
```

**Run the development server:**
```bash
npm run dev
# Opens at http://localhost:3000
```

**Key Features:**
- Built with Next.js 14+ App Router
- `useVoiceAssistant` React hook for agent state
- Audio visualizer component (`BarVisualizer`)
- Token generation via API route (`/api/token`)
- Automatic agent state tracking (`initializing`, `listening`, `thinking`, `speaking`)

**Testing your deployed agent:**
1. Start the frontend: `npm run dev`
2. Open http://localhost:3000 in your browser
3. Click "Connect" or "Start Session"
4. Speak to your voice assistant
5. Monitor agent logs: `lk agent logs --follow`

### Option 4: iOS/macOS (Swift)

**Best for:** Native iOS, macOS, and visionOS applications

**Starter Repository:** [agent-starter-swift](https://github.com/livekit-examples/agent-starter-swift)

**Quick Start:**

```bash
# Clone the starter template
git clone https://github.com/livekit-examples/agent-starter-swift.git
cd agent-starter-swift

# Open in Xcode
open AgentStarter.xcodeproj
```

**Token Server Setup:**

iOS apps require a hosted token server. You can use LiveKit Cloud's development sandbox:

```bash
# Get your sandbox token endpoint
lk cloud sandbox token-endpoint

# Example output:
# https://your-project.livekit.cloud/sandbox/token
```

**Configure the app:**

In Xcode, update `Config.swift`:
```swift
struct Config {
    static let tokenServerURL = "https://your-project.livekit.cloud/sandbox/token"
}
```

**Key Features:**
- SwiftUI interface
- Native iOS/macOS components
- `AgentBarAudioVisualizer` for audio visualization
- Automatic microphone permission handling
- Background audio support

**Build and run:**
1. Select your target device/simulator
2. Press ⌘+R to build and run
3. Grant microphone permissions
4. Tap "Connect" to start a session
5. Monitor agent logs: `lk agent logs --follow`

### Option 5: Flutter (Cross-Platform)

**Best for:** Cross-platform apps with Dart/Flutter

**Starter Repository:** [agent-starter-flutter](https://github.com/livekit-examples/agent-starter-flutter)

**Quick Start:**

```bash
# Clone the starter template
git clone https://github.com/livekit-examples/agent-starter-flutter.git
cd agent-starter-flutter

# Get dependencies
flutter pub get

# Run on connected device
flutter run
```

**Configure token server:**

Update `lib/config.dart`:
```dart
class Config {
  static const tokenServerUrl = 'https://your-project.livekit.cloud/sandbox/token';
}
```

**Key Features:**
- Single codebase for iOS, Android, web, desktop
- `SoundWaveformWidget` for audio visualization
- Flutter LiveKit SDK
- Hot reload for rapid development

**Platform-specific setup:**
```bash
# iOS
cd ios && pod install && cd ..

# Android (no additional setup needed)

# Web
flutter run -d chrome
```

### Option 6: Web Embed Widget

**Best for:** Embedding voice AI into existing websites

**Starter Repository:** [agent-starter-embed](https://github.com/livekit-examples/agent-starter-embed)

**Quick Start:**

```bash
# Clone the starter template
git clone https://github.com/livekit-examples/agent-starter-embed.git
cd agent-starter-embed

# Install and build
npm install
npm run build
```

**Embed in your website:**

```html
<!-- Add to your HTML -->
<div id="livekit-agent"></div>

<script src="https://your-cdn.com/livekit-agent-widget.js"></script>
<script>
  LiveKitAgent.init({
    container: '#livekit-agent',
    tokenUrl: 'https://your-project.livekit.cloud/sandbox/token',
    // Optional customization
    theme: 'dark',
    position: 'bottom-right'
  });
</script>
```

**Key Features:**
- Minimal integration
- Customizable appearance
- Floating widget or inline
- No build step required for host website

### Connection Flow and Optimization

**Standard Connection Flow (3-5 seconds):**
```
1. User clicks "Connect"
2. Frontend fetches access token → 500ms
3. User connects to room → 1000ms
4. Agent dispatched to room → 1000ms
5. Agent connects and publishes tracks → 1500ms
6. User-agent media flow established
```

**Optimized Connection Flow (<1 second):**

**1. Pre-generate Tokens (Warm Token Approach):**
```javascript
// Generate token at login/page load with extended expiration
const token = await fetch('/api/token').then(r => r.json());

// Store for later use when user clicks "Connect"
// Eliminates 500ms token fetch delay
```

**2. Concurrent Dispatch:**
```javascript
// Dispatch agent and connect user simultaneously
const [room, agent] = await Promise.all([
  connectToRoom(token),
  dispatchAgent(roomName)
]);
// Saves 1000ms by parallelizing operations
```

**3. Monitor Connection States:**

**React example:**
```javascript
import { useVoiceAssistant } from '@livekit/components-react';

function VoiceAgent() {
  const { state, audioTrack } = useVoiceAssistant();

  // state values: 'initializing' | 'listening' | 'thinking' | 'speaking'

  return (
    <div>
      <p>Agent is {state}</p>
      <BarVisualizer state={state} audioTrack={audioTrack} />
    </div>
  );
}
```

**4. Responsiveness Enhancements:**

```javascript
// Play sound effects during agent "thinking" state
if (state === 'thinking') {
  playThinkingSound();
}

// Add visual feedback
<Spinner visible={state === 'thinking'} />

// Haptic feedback on mobile
if (state === 'speaking') {
  triggerHapticFeedback();
}
```

**Getting Connection Credentials:**

For all frontend options, you need your LiveKit project credentials:

```bash
# View your project details
lk project current --json

# Example output:
{
  "name": "my-agent-dev",
  "url": "wss://your-project.livekit.cloud",
  "api_key": "APIxxxxxxxxxxxx",
  "api_secret": "your-secret-here"
}
```

**Production Token Server:**

For production deployments, implement a secure token server:

```javascript
// Example Node.js token server (Next.js API route)
import { AccessToken } from 'livekit-server-sdk';

export default async function handler(req, res) {
  const roomName = req.body.roomName || 'default-room';
  const participantName = req.body.participantName || 'user';

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

  res.json({ token: token.toJwt() });
}
```

**Next Steps:**

After choosing your frontend:
1. Clone the starter repository
2. Configure with your LiveKit project credentials
3. Run the frontend locally
4. Test connection to your deployed agent
5. Customize UI and behavior
6. Deploy frontend to production (Vercel, Netlify, App Store, Play Store, etc.)

## Managing Secrets

### Viewing Current Secrets

List secret keys (values are never displayed):

```bash
lk agent secrets
```

**Output example:**
```
Secret Keys:
- OPENAI_API_KEY
- ASSEMBLYAI_API_KEY
- CARTESIA_API_KEY
```

### Adding or Updating Individual Secrets

Update one or more secrets without affecting others:

```bash
lk agent update-secrets \
  --secrets "OPENAI_API_KEY=sk-new-key-here" \
  --secrets "NEW_API_KEY=value"
```

**What happens:**
- Merges new secrets with existing ones
- Triggers a rolling restart (no downtime)
- Existing sessions continue using old secrets
- New sessions use updated secrets
- Grace period: up to 1 hour for active sessions to complete

### Replacing All Secrets

Completely replace all secrets with a new file:

```bash
lk agent update-secrets --secrets-file .env.production --overwrite
```

**WARNING:** The `--overwrite` flag removes ALL existing secrets and replaces them with the file contents. Use carefully.

### Mounting Secret Files

For authentication files (like Google Cloud JSON credentials):

```bash
lk agent create --secret-mount ./path/to/credentials.json
```

**Result:** File appears at `/etc/secret/credentials.json` in the container.

### Secret Best Practices

1. **Never commit secrets to git**
   ```bash
   # Verify .gitignore includes:
   echo ".env*" >> .gitignore
   echo "!.env.example" >> .gitignore
   ```

2. **Use different secrets per environment**
   - Dev: `OPENAI_API_KEY=sk-dev-...`
   - Prod: `OPENAI_API_KEY=sk-prod-...`

3. **Rotate secrets regularly**
   ```bash
   # Update secrets, old sessions continue for up to 1 hour
   lk agent update-secrets --secrets "API_KEY=new-value"
   ```

4. **Document required secrets**
   Keep `.env.example` updated:
   ```env
   # Example secrets file - copy to .env.local and fill in values
   OPENAI_API_KEY=sk-...
   ASSEMBLYAI_API_KEY=...
   CARTESIA_API_KEY=...
   ```

## Updating Deployments

### Deploying Code Changes

After modifying your agent code:

```bash
# 1. Test locally first
uv run python src/app.py

# 2. Run tests
uv run pytest

# 3. Deploy new version
lk agent deploy
```

**What happens:**
- Builds a new container image with your changes
- Creates a new version (e.g., v2, v3, etc.)
- Performs a rolling deployment:
  - New instances start serving new sessions
  - Old instances continue existing sessions (up to 1 hour grace period)
  - No user interruptions or downtime

**Duration:** Subsequent builds are faster (1-3 minutes) due to layer caching.

### Updating Secrets Only

Update secrets without rebuilding the container:

```bash
lk agent update --secrets-file .env.local
```

**Pro tip:** This is faster than a full deploy when you only need to change API keys.

### Restarting Without Changes

Force a restart of all agent instances:

```bash
lk agent restart
```

**Use cases:**
- Clear cached state
- Recover from transient errors
- Apply infrastructure updates

## Monitoring and Troubleshooting

### Real-Time Logs

Stream live logs from your agent:

```bash
# Follow logs in real-time
lk agent logs --follow

# View last 100 lines
lk agent logs --tail 100

# Filter logs for errors
lk agent logs | grep ERROR
```

### Build Logs

If a deployment fails during build:

```bash
lk agent logs --build
```

**Common build errors:**
- Missing dependencies in `pyproject.toml`
- Dockerfile syntax errors
- Network timeouts during package installation

### Agent Status Dashboard

View detailed status information:

```bash
lk agent status
```

**Key metrics:**
- **Replicas:** Number of running instances (e.g., 2/2 ready)
- **Version:** Current deployed version
- **CPU/Memory:** Resource usage
- **Last Deploy:** Deployment timestamp

### Checking Agent Health

Test if your agent can accept new sessions:

```bash
# List all agents in the project
lk agent list
```

**Healthy agent checklist:**
- Status: `Running` (not `CrashLoop` or `Build Failed`)
- Replicas: All ready (e.g., 2/2, not 0/2)
- Recent logs show successful initialization
- No error messages about missing secrets

### Common Issues and Solutions

#### Issue: "Build Failed"

**Symptoms:**
```bash
lk agent status
# Output: Status: Build Failed
```

**Solutions:**
1. Check build logs: `lk agent logs --build`
2. Verify Dockerfile syntax
3. Ensure all dependencies are in `pyproject.toml`
4. Check for typos in package names
5. Try building locally: `docker build --platform linux/amd64 -t test .`

#### Issue: "CrashLoop"

**Symptoms:**
- Agent status shows `CrashLoop`
- Logs show repeated restarts

**Solutions:**
1. Check runtime logs: `lk agent logs --tail 200`
2. Look for Python exceptions or stack traces
3. Verify all secrets are set: `lk agent secrets`
4. Check for missing environment variables
5. Test locally with same environment: `uv run python src/app.py`

#### Issue: Agent Not Receiving Sessions

**Symptoms:**
- Frontend connects but agent doesn't respond
- No logs appearing when session starts

**Solutions:**
1. Verify project credentials in frontend match backend
2. Check agent status: `lk agent status`
3. Confirm agent is in `Running` state
4. Review LiveKit Cloud dashboard for connection errors
5. Check frontend console for WebSocket errors

#### Issue: High Latency or Timeouts

**Symptoms:**
- Slow responses
- Timeout errors in logs

**Solutions:**
1. Check agent region matches user location
2. Review logs for slow API calls (OpenAI, AssemblyAI, etc.)
3. Monitor CPU/memory usage: `lk agent status`
4. Consider scaling up replicas (if available in your plan)

## Common Workflows

### Workflow 1: Dev → Staging → Production

**1. Deploy to Dev:**
```bash
lk project set-default "my-agent-dev"
lk agent deploy
```

**2. Test thoroughly in dev environment**
- Run automated tests
- Manual QA testing
- Load testing (if applicable)

**3. Deploy to Staging:**
```bash
lk project set-default "my-agent-staging"
lk agent deploy --secrets-file .env.staging
```

**4. Validate in staging:**
- Final pre-production testing
- Stakeholder demos
- Performance validation

**5. Deploy to Production:**
```bash
lk project set-default "my-agent-prod"
lk agent deploy --secrets-file .env.production
```

**6. Monitor production:**
```bash
lk agent logs --follow
lk agent status
```

### Workflow 2: Hotfix Deployment

**1. Create and test fix locally:**
```bash
uv run python src/app.py
uv run pytest
```

**2. Deploy directly to production:**
```bash
lk project set-default "my-agent-prod"
lk agent deploy
```

**3. Monitor for issues:**
```bash
lk agent logs --follow --tail 50
```

**4. Rollback if needed:**
```bash
lk agent rollback
```

### Workflow 3: Rolling Back a Bad Deployment

**1. Check version history:**
```bash
lk agent versions
```

**Output example:**
```
VERSION  DEPLOYED AT              STATUS
v5       2026-01-24 14:00:00     Current (Running)
v4       2026-01-24 12:00:00     Previous
v3       2026-01-23 16:00:00
```

**2. Rollback to previous version:**
```bash
# Rollback to immediately previous version
lk agent rollback

# Or rollback to specific version
lk agent rollback --version v4
```

**3. Verify rollback:**
```bash
lk agent status
lk agent logs --tail 50
```

**Note:** Instant rollback is only available on paid LiveKit Cloud plans.

### Workflow 4: Managing Multiple Environments

**Create project shortcuts in your shell:**

```bash
# Add to ~/.bashrc or ~/.zshrc
alias lk-dev='lk project set-default "my-agent-dev"'
alias lk-staging='lk project set-default "my-agent-staging"'
alias lk-prod='lk project set-default "my-agent-prod"'
```

**Usage:**
```bash
# Switch to dev
lk-dev
lk agent status

# Switch to production
lk-prod
lk agent status
```

## CLI Command Reference

### Project Management

```bash
# Authenticate with LiveKit Cloud
lk cloud auth

# List all projects
lk project list

# Set default project
lk project set-default "project-name"

# Show current project
lk project current
```

### Agent Deployment

```bash
# Create new agent (initial deployment)
lk agent create [--secrets-file .env.local] [--region us-west-2]

# Deploy code changes (creates new version)
lk agent deploy

# Update secrets without redeploying
lk agent update --secrets-file .env.local

# Restart agent servers
lk agent restart
```

### Secrets Management

```bash
# List secret keys
lk agent secrets

# Update individual secrets
lk agent update-secrets --secrets "KEY=value" --secrets "KEY2=value2"

# Update from file
lk agent update-secrets --secrets-file .env.local

# Replace all secrets
lk agent update-secrets --secrets-file .env.local --overwrite

# Mount secret file
lk agent create --secret-mount ./path/to/file.json
```

### Monitoring

```bash
# Check agent status
lk agent status

# Stream live logs
lk agent logs [--follow] [--tail N]

# View build logs
lk agent logs --build

# List all agents
lk agent list

# View version history
lk agent versions
```

### Version Control

```bash
# Rollback to previous version
lk agent rollback

# Rollback to specific version
lk agent rollback --version v4

# Rollback by deployment ID
lk agent rollback --id deploy_abc123
```

### Cleanup

```bash
# Delete agent permanently
lk agent delete

# Alternative command
lk agent destroy
```

**WARNING:** Deletion is permanent and cannot be undone. Active sessions will be terminated.

## Advanced Configuration

### Custom Dockerfile

If you need to customize the build process, edit the `Dockerfile`:

```dockerfile
# Example: Add system dependencies
RUN apt-get update && apt-get install -y \
    ffmpeg \
    libsndfile1 \
  && rm -rf /var/lib/apt/lists/*

# Example: Custom build arguments
ARG PYTHON_VERSION=3.11
FROM ghcr.io/astral-sh/uv:python${PYTHON_VERSION}-bookworm-slim
```

After modifying the Dockerfile:
```bash
lk agent deploy
```

### Region Selection

Deploy to specific regions for lower latency:

```bash
# Create agent in specific region
lk agent create --region us-east-1

# Available regions (check LiveKit docs for latest):
# us-west-2, us-east-1, eu-west-1, ap-southeast-1, etc.
```

### Configuration File (livekit.toml)

The `livekit.toml` file is auto-generated during `lk agent create`:

```toml
# Example livekit.toml
agent_id = "agent_abc123"
region = "us-west-2"
min_replicas = 0
max_replicas = 10
```

**Regenerate configuration:**
```bash
lk agent config --id agent_abc123
```

## Cost Management

LiveKit Cloud charges **$0.01 per agent session minute** (as of 2026-01-24).

**What's included:**
- Hosting across global network
- Unlimited data transfer
- Observability and analytics
- Automatic scaling

**Optimization tips:**
1. Use auto-scaling (scale to zero when idle)
2. Monitor usage in LiveKit Cloud dashboard
3. Use dev environments for testing (separate billing)
4. Implement session timeout logic in your agent

## Additional Resources

### Deployment Documentation
- [LiveKit Cloud Deployment Docs](https://docs.livekit.io/agents/ops/deployment/)
- [Self-Hosted Deployments](https://docs.livekit.io/agents/ops/deployment/custom/)
- [Agent CLI Reference](https://docs.livekit.io/agents/ops/deployment/cli/)
- [Builds and Dockerfiles](https://docs.livekit.io/agents/ops/deployment/builds/)
- [Secrets Management](https://docs.livekit.io/deploy/agents/secrets/)
- [Deployment Examples (GitHub)](https://github.com/livekit-examples/agent-deployment)

### Quick Testing Tools
- [LiveKit Agents Playground](https://agents-playground.livekit.io/) - Instant agent testing (no code)
- [LiveKit Meet](https://meet.livekit.io/) - Video conferencing with agents

### Frontend Connection Resources
- [Frontend Integration Guide](https://docs.livekit.io/agents/start/frontend/)
- [Web Quickstart (React)](https://docs.livekit.io/home/quickstarts/react/)
- [Token Authentication](https://docs.livekit.io/home/get-started/authentication/)

### Frontend Starter Repositories
- [agent-starter-react](https://github.com/livekit-examples/agent-starter-react) - Next.js web app
- [agent-starter-swift](https://github.com/livekit-examples/agent-starter-swift) - iOS/macOS/visionOS
- [agent-starter-flutter](https://github.com/livekit-examples/agent-starter-flutter) - Flutter
- [agent-starter-embed](https://github.com/livekit-examples/agent-starter-embed) - Embeddable widget

## Getting Help

If you encounter issues:

1. **Check the logs:** `lk agent logs --tail 200`
2. **Review agent status:** `lk agent status`
3. **Search LiveKit docs:** [docs.livekit.io](https://docs.livekit.io)
4. **Community support:** [LiveKit Discord](https://livekit.io/discord)
5. **GitHub issues:** [livekit/agents](https://github.com/livekit/agents/issues)
6. **Cloud support:** Available for paid plans at [cloud.livekit.io](https://cloud.livekit.io)

---

**Last Updated:** 2026-01-24
