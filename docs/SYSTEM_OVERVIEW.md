# System Overview - Long Form to Shorts v3.0

## 🎯 At a Glance

**What**: Production-grade system for converting Bengali podcasts to viral vertical reels
**How**: Agentic architecture with intelligent orchestration
**Why**: Automation, reliability, observability, and professional quality

---

## 📊 System Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                        USER INTERFACE                            │
│  • Python API (Primary)                                         │
│  • CLI Commands (Future)                                        │
│  • Configuration Files (config.yaml)                            │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│                   PIPELINE ORCHESTRATOR                          │
│                                                                  │
│  Responsibilities:                                              │
│  ├─ Initialize and coordinate agents                            │
│  ├─ Manage pipeline state and checkpoints                       │
│  ├─ Handle errors with retry logic                              │
│  ├─ Collect and export metrics                                  │
│  └─ Generate execution reports                                  │
└──────────────────────────┬──────────────────────────────────────┘
                           │
              ┌────────────┴────────────┐
              │                         │
              ▼                         ▼
┌─────────────────────────┐  ┌──────────────────────────┐
│   PROCESSING AGENTS     │  │   SUPPORT SYSTEMS        │
│                         │  │                          │
│  1. AudioExtraction     │  │  • Configuration Mgmt    │
│  2. Transcription       │  │  • Logging System        │
│  3. Analysis            │  │  • Metrics Collector     │
│  4. VideoProcessing     │  │  • Validation Framework  │
│  5. SubtitleGeneration  │  │  • Error Handling        │
│  6. Finalization        │  │  • State Management      │
└─────────────────────────┘  └──────────────────────────┘
              │                         │
              └────────────┬────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│                    EXTERNAL SERVICES                             │
│                                                                  │
│  • Gemini API (Transcription & Analysis)                        │
│  • FFmpeg (Video/Audio Processing)                              │
│  • File System (Storage)                                        │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🔄 Data Flow

### Complete Pipeline Flow:

```
INPUT: Source Video (podcast.mp4)
   │
   ├─► STAGE 1: Audio Extraction
   │   ├─ Input: Source video
   │   ├─ Tool: FFmpeg
   │   ├─ Output: audio_30min.mp3
   │   └─ Validation: File exists, has content
   │
   ├─► STAGE 2: Transcription
   │   ├─ Input: Audio file
   │   ├─ Tool: Gemini 2.5 Pro API
   │   ├─ Output: audio_30min_transcription.txt
   │   ├─ Format: [HH:MM:SS.mmm] Speaker N: বাংলা টেক্সট
   │   └─ Validation: Timestamps present, UTF-8 encoded
   │
   ├─► STAGE 3: Analysis
   │   ├─ Input: Transcript
   │   ├─ Tool: Gemini 2.5 Pro API
   │   ├─ Output: REEL_CUT_DIRECTIONS.md + ReelConfig[]
   │   ├─ Logic: Identify viral moments, extract metadata
   │   └─ Validation: At least 1 reel identified
   │
   ├─► STAGE 4: Video Processing (per reel)
   │   ├─ Input: Source video, reel timestamps
   │   ├─ Tool: FFmpeg
   │   ├─ Output: reel_N.mp4 (vertical crop), reel_N_words.txt
   │   ├─ Logic: Extract segment, generate word timestamps
   │   └─ Validation: Duration matches, dimensions correct
   │
   ├─► STAGE 5: Subtitle Generation (per reel)
   │   ├─ Input: Word timestamps, reel metadata
   │   ├─ Tool: ASS generator
   │   ├─ Output: reel_N_tiktok.ass
   │   ├─ Logic: TikTok-style formatting, Bengali rendering
   │   └─ Validation: ASS syntax correct, timestamps aligned
   │
   ├─► STAGE 6: Subtitle Hardburn (per reel)
   │   ├─ Input: reel_N.mp4, reel_N_tiktok.ass
   │   ├─ Tool: FFmpeg with libass
   │   ├─ Output: Final_[বাংলা_টাইটেল].mkv
   │   └─ Validation: Subtitles rendered, quality preserved
   │
   └─► STAGE 7: Finalization
       ├─ Input: All reels
       ├─ Logic: Quality checks, metadata generation
       ├─ Output: Project summary, metrics export
       └─ Validation: All reels present, formats correct

OUTPUT: Multiple vertical reels (608x1080 or 1080x1920 .mkv)
        Location: Projects/[ProjectName]/Output/
```

---

## 🧩 Component Details

### 1. Configuration System (`src/config/`)

**Purpose**: Centralized settings management

**Files**:
- `settings.py` - Load and validate config.yaml
- `schemas.py` - Data models (ProjectConfig, ReelConfig, PipelineState)
- `validators.py` - Validation logic (files, dependencies, configurations)

**Key Features**:
- YAML-based configuration
- Environment variable support
- Typed dataclasses
- Validation on load

**Example**:
```python
settings = load_settings()
print(settings.api.gemini_model)  # "gemini-2.5-pro"
print(settings.video.get_dimensions("tiktok"))  # (608, 1080)
```

### 2. Agent System (`src/agents/`)

**Purpose**: Autonomous execution of pipeline stages

**Base Agent** (`base_agent.py`):
```python
class BaseAgent(ABC):
    def validate_preconditions()   # Check inputs
    def execute()                  # Do the work
    def validate_postconditions()  # Check outputs
    def run()                      # Orchestrated execution
```

**Specialized Agents**:
1. **AudioExtractionAgent** - FFmpeg audio extraction
2. **TranscriptionAgent** - Gemini API transcription
3. **AnalysisAgent** - Viral moment detection
4. **VideoProcessingAgent** - Segment extraction + timestamps
5. **SubtitleAgent** - ASS subtitle generation
6. **FinalizationAgent** - Quality validation

**Agent Lifecycle**:
```
Agent.run()
  ├─► validate_preconditions()
  │   └─ Raises PipelineError if not ready
  │
  ├─► execute()
  │   ├─ Do the actual work
  │   └─ Return AgentResult (success/failure + artifacts)
  │
  └─► validate_postconditions(result)
      └─ Raises PipelineError if output invalid
```

### 3. Orchestrator (`src/agents/orchestrator.py`)

**Purpose**: Master coordinator for all agents

**Responsibilities**:
- Initialize all agents
- Execute pipeline stages in order
- Handle errors and retries
- Manage checkpoints
- Collect metrics
- Generate reports

**Key Methods**:
```python
class PipelineOrchestrator:
    def initialize_agents()      # Create agent instances
    def execute_stage(name)       # Run one stage with retry
    def execute_pipeline()        # Run all stages
    def get_status()              # Return current state
```

**State Management**:
```python
PipelineState
  ├─ current_stage: PipelineStage
  ├─ stage_metrics: List[StageMetrics]
  ├─ started_at / completed_at: datetime
  └─ Methods:
      ├─ save_checkpoint()
      └─ load_checkpoint()
```

### 4. Utilities (`src/utils/`)

**Purpose**: Shared functionality

**Components**:

**Logging** (`logging.py`):
- Color-coded console output
- File rotation
- Structured format
- Per-module loggers

**Errors** (`errors.py`):
- Exception hierarchy
- Retry decorators
- Error context managers
- Dependency validation

**Metrics** (`metrics.py`):
- Performance tracking
- API call statistics
- Stage timing
- JSON export

---

## 🔐 Security & Safety

### 1. API Key Management
```yaml
# Never commit API keys!
# Use environment variables:
export GEMINI_API_KEY="your-key"

# Config loads from environment:
api_key = os.environ.get("GEMINI_API_KEY")
```

### 2. Input Validation
- File existence checks
- File size validation
- Format verification (FFprobe)
- UTF-8 encoding validation
- Dependency checks (FFmpeg, libass)

### 3. Error Isolation
```python
# Errors don't crash the system
try:
    result = agent.execute()
except Exception as e:
    # Log error, record metrics, retry if configured
    # Continue or fail based on error_handling.continue_on_error
```

---

## 📈 Performance Characteristics

### Typical Execution Timeline:

```
Pipeline for 30-minute podcast:

Stage 1: Audio Extraction        ~2-3 seconds
Stage 2: Transcription           ~30-60 seconds  (Gemini API)
Stage 3: Analysis                ~10-20 seconds  (Gemini API)
Stage 4: Video Processing        ~5-10 sec/reel  (FFmpeg)
Stage 5: Subtitle Generation     <1 sec/reel     (Python)
Stage 6: Subtitle Hardburn       ~10-15 sec/reel (FFmpeg)
Stage 7: Finalization            ~1-2 seconds

Total (3 reels): ~120-180 seconds  (~2-3 minutes)
```

### Scalability:

**Current** (v3.0):
- Sequential stage execution
- Parallel reel processing (within stages)
- ~2-3 minutes per 30-minute podcast

**Future** (Optimization Opportunities):
- Parallel agent execution (independent stages)
- GPU acceleration (FFmpeg hardware encoding)
- Distributed processing (multiple videos)
- Estimated: ~60-90 seconds per podcast

---

## 🎛️ Configuration Deep Dive

### config.yaml Structure:

```yaml
system:           # Runtime configuration
api:              # External service settings
video:            # Video processing specs
subtitle:         # Subtitle styling
transcription:    # Audio extraction settings
analysis:         # AI analysis parameters
pipeline:         # Workflow stages
error_handling:   # Retry & recovery
monitoring:       # Metrics & logging
```

### Override Priority:

```
1. Environment variables (highest)
2. config.yaml
3. Defaults in code (lowest)
```

Example:
```bash
# Override in environment
export LOG_LEVEL=DEBUG

# Overrides config.yaml:
# system:
#   log_level: "INFO"
```

---

## 🔍 Monitoring & Observability

### Log Files:

```
Projects/[ProjectName]/Logs/
├── pipeline.log          # All logs (DEBUG→CRITICAL)
├── errors.log            # Errors only
├── pipeline_state.json   # Current execution state
└── metrics.json          # Performance data
```

### Metrics Tracked:

**Execution Metrics**:
- Total duration
- Stage durations
- Success/failure rates

**API Metrics**:
- Call count
- Response times
- Token usage
- Estimated cost

**File Metrics**:
- Operations (read/write/delete)
- File sizes
- Total data processed

**Stage Metrics**:
- Per-stage timing
- Retry counts
- Error messages
- Artifacts generated

---

## 🧪 Testing Strategy

### Current State:
- Manual testing
- Validation at each stage
- Error simulation (manual)

### Future Implementation:

```python
# Unit tests
tests/test_config.py           # Configuration loading
tests/test_agents.py           # Individual agents
tests/test_orchestrator.py     # Pipeline flow

# Integration tests
tests/integration/test_pipeline.py  # End-to-end

# Fixtures
tests/fixtures/sample_audio.mp3
tests/fixtures/sample_transcript.txt
```

---

## 🚀 Deployment Options

### Current: Local Execution
```bash
python main.py
```

### Future Options:

**Docker**:
```dockerfile
FROM python:3.11
RUN apt-get install ffmpeg
COPY . /app
RUN pip install -r requirements-new.txt
CMD ["python", "-m", "src.agents.orchestrator"]
```

**AWS Lambda**:
- Trigger on S3 upload
- Process video serverlessly
- Store output in S3

**Kubernetes**:
- Horizontal scaling
- Batch processing
- Resource management

---

## 🔗 Integration Points

### Current Integrations:
- **Gemini API** - Transcription & Analysis
- **FFmpeg** - Video/Audio processing
- **File System** - Project storage

### Future Integrations:
- **Cloud Storage** (S3, GCS)
- **Databases** (PostgreSQL for metadata)
- **Message Queues** (RabbitMQ, Kafka)
- **Monitoring** (Prometheus, Grafana)
- **Notifications** (Email, Slack, Discord)

---

## 📋 Maintenance

### Regular Tasks:
1. **Log Rotation**: Automatic via RotatingFileHandler
2. **Checkpoint Cleanup**: Remove old pipeline_state.json
3. **Metrics Review**: Analyze metrics.json for bottlenecks
4. **Dependency Updates**: `pip list --outdated`

### Troubleshooting Checklist:
- [ ] Check logs/errors.log
- [ ] Verify GEMINI_API_KEY is set
- [ ] Validate FFmpeg has libass
- [ ] Review pipeline_state.json
- [ ] Check metrics.json for timing issues
- [ ] Verify config.yaml syntax

---

## 🎓 Learning Resources

### For Users:
1. **README_V3.md** - Quick start guide
2. **MIGRATION_GUIDE.md** - Upgrade from v2.0
3. **config.yaml** - All configuration options

### For Developers:
1. **TRANSFORMATION_COMPLETE.md** - Architecture overview
2. **src/agents/** - Agent implementations
3. **src/config/** - Configuration system
4. **src/utils/** - Utility modules

### For Operators:
1. **Logs/** - Execution logs
2. **metrics.json** - Performance data
3. **pipeline_state.json** - Current state

---

## 🎯 Success Criteria

A successful pipeline execution should have:
- ✅ All 7 stages completed
- ✅ No errors in errors.log
- ✅ Reels present in Projects/*/Output/
- ✅ Metrics exported to metrics.json
- ✅ Total duration < 5 minutes (for 30-min podcast)
- ✅ Final reels playable and subtitled

---

**System Status**: ✅ Production-Ready
**Version**: 3.0.0
**Last Updated**: 2025-10-20
