# Turn Detector Language Warning

## Issue

When running the agent in console mode, the following warning appears:

```
14:46:34.098 INFO   livekit.agents     Turn detector does not support language  {"room": "console"}
```

This occurs after the user speaks and the STT produces a transcript with an empty language field:

```
14:46:33.969 DEBUG  livekit.agents     received user transcript
                                     {"user_transcript": "Hello.", "language": "", "transcript_delay":
0.46952295303344727, "room": "console"}
```

## Diagnosis

The warning occurs because:

1. **STT is configured with language**: In `src/adapters/livekit_adapters.py:25-28`, the LiveKit STT adapter is initialized with:
   ```python
   self._stt = inference.STT(
       model=config.stt_model,
       language=config.stt_language,  # Default: "en"
   )
   ```

2. **STT outputs transcript with empty language**: Despite being configured with `language="en"`, the STT produces transcripts with `"language": ""` (empty string)

3. **Turn Detector receives empty language**: In `src/session_handler.py:98-102`, the `MultilingualModel()` turn detector is created without any language parameter:
   ```python
   turn_detection=(
       MultilingualModel()  # ❌ No language specified
       if self.session_config.use_multilingual_turn_detector
       else None
   ),
   ```

4. **Turn Detector cannot process empty language**: When the turn detector receives transcripts with empty language strings, it emits the warning because it doesn't know which language model to use.

## Root Cause

The `SessionHandler` class lacks access to language configuration:

- Language setting is in `PipelineConfig.stt_language`
- `SessionHandler.__init__()` only receives `SessionConfig`
- The `MultilingualModel()` is initialized without language information

**Relevant Code Locations:**

- `src/config.py:38-40` - Language defined in `PipelineConfig`
- `src/session_handler.py:29` - `SessionHandler` receives only `SessionConfig`
- `src/session_handler.py:99` - `MultilingualModel()` created without language
- `src/agent.py:90-95` - `SessionHandler` instantiated without pipeline config

## Recommended Fix

### Option 1: Pass PipelineConfig to SessionHandler (Recommended)

This provides access to all pipeline settings including language.

**Step 1**: Update `SessionHandler.__init__()` signature in `src/session_handler.py`:

```python
def __init__(
    self,
    stt: STTProtocol,
    llm: LLMProtocol,
    tts: TTSProtocol,
    agent: Agent,
    session_config: SessionConfig,
    pipeline_config: PipelineConfig,  # ✓ Add this parameter
):
    """Initialize the session handler.

    Args:
        stt: Speech-to-text adapter
        llm: Large language model adapter
        tts: Text-to-speech adapter
        agent: The agent instance to use for sessions
        session_config: Configuration for session management
        pipeline_config: Configuration for pipeline components (includes language)
    """
    self.stt = stt
    self.llm = llm
    self.tts = tts
    self.agent = agent
    self.session_config = session_config
    self.pipeline_config = pipeline_config  # ✓ Store pipeline config
    logger.info("SessionHandler initialized")
```

**Step 2**: Update `MultilingualModel()` initialization in `src/session_handler.py:98-102`:

```python
turn_detection=(
    MultilingualModel(language=self.pipeline_config.stt_language)  # ✓ Pass language
    if self.session_config.use_multilingual_turn_detector
    else None
),
```

**Step 3**: Update `SessionHandler` instantiation in `src/agent.py:90-96`:

```python
# Create session handler with injected dependencies
self.session_handler = SessionHandler(
    stt=self.stt,
    llm=self.llm,
    tts=self.tts,
    agent=self.agent,
    session_config=self.config.session,
    pipeline_config=self.config.pipeline,  # ✓ Add this argument
)
```

### Option 2: Pass Language Directly

If you don't need other pipeline config in SessionHandler, pass just the language.

**Step 1**: Update `SessionHandler.__init__()` in `src/session_handler.py`:

```python
def __init__(
    self,
    stt: STTProtocol,
    llm: LLMProtocol,
    tts: TTSProtocol,
    agent: Agent,
    session_config: SessionConfig,
    language: str = "en",  # ✓ Add language parameter
):
    # ... existing code ...
    self.language = language
```

**Step 2**: Update `MultilingualModel()` in `src/session_handler.py:99`:

```python
turn_detection=(
    MultilingualModel(language=self.language)  # ✓ Use language
    if self.session_config.use_multilingual_turn_detector
    else None
),
```

**Step 3**: Update instantiation in `src/agent.py:90-96`:

```python
self.session_handler = SessionHandler(
    stt=self.stt,
    llm=self.llm,
    tts=self.tts,
    agent=self.agent,
    session_config=self.config.session,
    language=self.config.pipeline.stt_language,  # ✓ Pass language
)
```

## Verification

After implementing the fix:

1. Check that the warning no longer appears in console mode
2. Verify the turn detector properly detects end-of-turn in conversations
3. Test with different languages if multilingual support is needed

## Additional Notes

- The LiveKit Docs MCP server may have more details on `MultilingualModel` initialization
- Consider whether the language should be configurable via environment variables
- May want to add language to `SessionConfig` if it affects other session behaviors

## Files to Modify

1. `src/session_handler.py` - Add language parameter, update `MultilingualModel()` initialization
2. `src/agent.py` - Pass language/pipeline config to `SessionHandler`
3. Optionally `src/config.py` - Consider moving language to `SessionConfig` if appropriate

## Priority

**Medium** - The agent functions correctly despite this warning, but proper language configuration will:
- Eliminate console noise
- Ensure optimal turn detection performance
- Enable proper multilingual support if needed
