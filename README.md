# Long Form to Shorts - v3.0 🚀

**Production-Grade Agentic System for Bengali Podcast Reel Generation**

Transform long-form Bengali podcasts into viral-worthy vertical reels with AI-powered automation, intelligent orchestration, and enterprise-level reliability.

---

## ✨ Version 3.0 - Agentic Architecture

This is a complete rebuild featuring:
- 🤖 **Intelligent Agent System** - Autonomous orchestration
- ⚙️ **Centralized Configuration** - Single YAML file controls everything
- 🔄 **Automatic Retry Logic** - Resilient to failures
- 📊 **Performance Monitoring** - Track every metric
- 📝 **Structured Logging** - Professional observability
- ✅ **Multi-Layer Validation** - Catch errors before they happen
- 💾 **Checkpoint System** - Resume from any failure
- 🎯 **Production-Ready** - Enterprise-level quality

---

## 🎯 Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements-new.txt
```

### 2. Set API Key

```bash
export GEMINI_API_KEY="your-gemini-api-key"
```

### 3. Run the Orchestrator

```python
from src.agents.orchestrator import create_orchestrator
from pathlib import Path

# Create and execute pipeline
orchestrator = create_orchestrator(
    project_name="My_Podcast_2025",
    source_video=Path("path/to/podcast.mp4")
)

success = orchestrator.execute_pipeline()

# Check results
print(f"Status: {'✓ Success' if success else '✗ Failed'}")
print(f"Output: Projects/My_Podcast_2025/Output/")
```

**That's it!** The orchestrator handles:
- ✅ Audio extraction
- ✅ Transcription with Gemini API
- ✅ Viral moment analysis
- ✅ Video segment extraction
- ✅ Timestamp generation
- ✅ Subtitle creation & hardburning
- ✅ Quality validation
- ✅ Final reel assembly

### 🎨 Launch the Interactive Studio (Front-End)

Prefer a visual control room? Spin up the Streamlit interface to run the same pipeline with an intuitive two-panel layout (controls on the left, live status & outputs on the right):

```bash
pip install -r requirements.txt
streamlit run frontend/streamlit_app.py
```

Inside the studio you can:
- Upload a long-form video/podcast and fire the pipeline with one click
- Monitor per-stage progress, logs, and Gemini status in real time
- Preview generated reels, transcripts, and metrics without leaving the browser

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────┐
│           Pipeline Orchestrator (Brain)             │
│  • Coordinates all agents                           │
│  • Manages state & checkpoints                      │
│  • Handles errors & retries                         │
└──────────────────┬──────────────────────────────────┘
                   │
      ┌────────────┴────────────┐
      │                         │
┌─────▼──────┐          ┌──────▼──────┐
│  Agents    │          │  Utilities   │
│            │          │              │
│ • Audio    │          │ • Logging    │
│ • Transcript│         │ • Metrics    │
│ • Analysis │          │ • Validation │
│ • Video    │          │ • Errors     │
│ • Subtitles│          └──────────────┘
└────────────┘
      │
      ▼
┌─────────────────────────────────┐
│      Configuration              │
│  • config.yaml                  │
│  • Project-specific configs     │
└─────────────────────────────────┘
```

---

## 📁 Project Structure

```
Long Form to Shorts/
│
├── config.yaml                  # Central configuration
├── requirements-new.txt         # Dependencies
│
├── src/                         # Core application
│   ├── agents/                  # Autonomous agents
│   │   ├── orchestrator.py      # Master coordinator
│   │   ├── audio_extraction_agent.py
│   │   ├── transcription_agent.py
│   │   ├── analysis_agent.py
│   │   ├── video_processing_agent.py
│   │   ├── subtitle_agent.py
│   │   └── finalization_agent.py
│   │
│   ├── config/                  # Configuration management
│   │   ├── settings.py
│   │   ├── schemas.py
│   │   └── validators.py
│   │
│   └── utils/                   # Utilities
│       ├── logging.py
│       ├── errors.py
│       └── metrics.py
│
├── Projects/                    # Your projects
│   └── [Project_Name]/
│       ├── Source/              # Original video
│       ├── Transcripts/         # Audio & transcript
│       ├── Analysis/            # AI analysis results
│       ├── Processing/          # Intermediate files
│       ├── Output/              # ✨ Final reels
│       └── Logs/                # Execution logs & metrics
│
├── Scripts/                     # Legacy scripts (still work!)
└── Templates/                   # Configuration templates
```

---

## ⚙️ Configuration

Edit `config.yaml` to customize everything:

```yaml
system:
  log_level: "INFO"              # DEBUG, INFO, WARNING, ERROR
  max_workers: 4                 # Parallel processing

api:
  gemini:
    model: "gemini-2.5-pro"
    max_retries: 3

video:
  default_format: "tiktok"       # tiktok (608x1080) or instagram (1080x1920)
  quality:
    crf: 23                      # 18-28 (lower = better quality)

subtitle:
  title_font_size: 68
  subtitle_font_size: 68
  max_words_per_line: 4
  title_duration_seconds: 5.0

error_handling:
  max_retries: 3
  exponential_backoff: true
  save_checkpoints: true
```

---

## 🎨 Features

### 🤖 Intelligent Orchestration
- **Autonomous agents** handle each pipeline stage
- **Automatic coordination** between stages
- **Event-driven** execution flow
- **Parallel processing** where possible

### 🔄 Error Recovery
- **Automatic retry** with exponential backoff
- **Checkpoint system** - resume from any failure
- **Graceful degradation** - continue on non-critical errors
- **Error context** tracking for debugging

### 📊 Observability
- **Structured logging** with colors and rotation
- **Performance metrics** for every operation
- **API call tracking** (duration, tokens, cost)
- **Stage timing** and resource usage
- **JSON export** for analysis

### ✅ Validation
- **Dependency checking** (FFmpeg, Python packages)
- **Input validation** (video, audio, transcript)
- **Output validation** (file size, format, quality)
- **Configuration validation** (syntax, values, paths)

### 🎯 Production-Ready
- **Type hints** throughout
- **Comprehensive error handling**
- **Clean architecture** (SOLID principles)
- **Separation of concerns**
- **Easy to test and extend**

---

## 📝 Example Usage

### Basic Usage:

```python
from src.agents.orchestrator import create_orchestrator
from pathlib import Path

# Create orchestrator
orchestrator = create_orchestrator(
    project_name="AI_Podcast_Oct2025",
    source_video=Path("~/Videos/podcast.mp4")
)

# Execute complete pipeline
success = orchestrator.execute_pipeline()

if success:
    print("✓ All reels generated successfully!")
    print(f"Check: Projects/AI_Podcast_Oct2025/Output/")
else:
    print("✗ Pipeline failed. Check logs:")
    print("  logs/pipeline.log")
    print("  logs/errors.log")
```

### Advanced Usage with Custom Settings:

```python
from src.agents.orchestrator import PipelineOrchestrator
from src.config.settings import load_settings
from src.config.schemas import ProjectConfig
from pathlib import Path

# Load custom config
settings = load_settings(Path("custom_config.yaml"))

# Create project config
project_config = ProjectConfig(
    project_name="Premium_Podcast",
    project_root=Path("Projects/Premium_Podcast"),
    source_video=Path("premium_video.mp4")
)

# Create orchestrator with custom settings
orchestrator = PipelineOrchestrator(
    project_config=project_config,
    settings=settings,
    resume_from_checkpoint=True  # Resume if previous run failed
)

# Execute
success = orchestrator.execute_pipeline()

# Get detailed status
status = orchestrator.get_status()
print(f"Duration: {status['duration_seconds']:.1f}s")
print(f"Reels: {status['reels']}")
print(f"Current stage: {status['current_stage']}")
```

---

## 📈 Monitoring & Metrics

### Logs Location:

```
Projects/YourProject/Logs/
├── pipeline.log              # All execution logs
├── errors.log                # Errors only
├── pipeline_state.json       # Checkpoint for resuming
└── metrics.json              # Performance metrics
```

### Metrics Example:

```json
{
  "execution": {
    "total_duration_seconds": 127.45,
    "stages_completed": 8,
    "stages_failed": 0
  },
  "api": {
    "total_calls": 5,
    "total_duration_seconds": 58.32,
    "total_tokens_used": 125430,
    "total_cost_usd": 0.0847
  },
  "files": {
    "total_operations": 42,
    "total_mb": 245.67
  },
  "stages": [
    {
      "name": "audio_extraction",
      "duration_seconds": 2.34,
      "success": true
    },
    {
      "name": "transcription",
      "duration_seconds": 45.72,
      "success": true
    }
  ]
}
```

---

## 🔧 Troubleshooting

### FFmpeg Not Found
```bash
# macOS
brew install ffmpeg

# Ubuntu/Debian
sudo apt install ffmpeg

# Verify
ffmpeg -version | grep libass
```

### API Key Not Set
```bash
export GEMINI_API_KEY="your-key-here"

# Make permanent
echo 'export GEMINI_API_KEY="your-key"' >> ~/.zshrc
```

### Module Import Error
```bash
# Ensure you're in project root
cd "/Users/Adnan/Desktop/Long Form to Shorts"

# Test import
python -c "from src.agents.orchestrator import create_orchestrator; print('OK')"
```

### Resume from Failure
```python
# Orchestrator automatically resumes from last checkpoint
orchestrator = PipelineOrchestrator(
    project_config=project_config,
    resume_from_checkpoint=True
)
```

---

## 🆚 Version Comparison

| Feature | v2.0 (Scripts) | v3.0 (Agents) |
|---------|----------------|---------------|
| Execution | Manual, 8+ steps | Automated, 1 command |
| Configuration | Hardcoded | Central YAML |
| Error Handling | Basic try/catch | Retry + checkpoints |
| Logging | Print statements | Structured logs |
| Monitoring | None | Full metrics |
| Resumability | Manual | Automatic |
| Validation | Manual checks | Multi-layer |
| Scalability | Single-threaded | Parallel-ready |
| Maintainability | Low | High |

---

## 📚 Documentation

- **TRANSFORMATION_COMPLETE.md** - Full system overview
- **MIGRATION_GUIDE.md** - Upgrade from v2.0 to v3.0
- **README.md** - Original documentation
- **AGENT.md** - Technical pipeline details
- **config.yaml** - All configuration options

---

## 🤝 Backward Compatibility

**All v2.0 scripts still work!**

```bash
# Old scripts remain functional:
python Scripts/transcribe_audio_v2.py audio.mp3
python Scripts/analyze_transcript.py transcript.txt
python Scripts/text_to_tiktok_ass.py words.txt --title "টাইটেল"

# Use new orchestrator when ready
python -m src.agents.orchestrator
```

---

## 🎓 Learning Path

1. **Week 1**: Read TRANSFORMATION_COMPLETE.md, test orchestrator
2. **Week 2**: Customize config.yaml, review logs/metrics
3. **Week 3**: Process real projects, compare with old method
4. **Week 4**: Full adoption, advanced workflows

---

## 🚀 What's Next?

Ready to implement:
- **CLI interface** with rich progress bars
- **Web dashboard** for monitoring
- **Batch processing** for multiple videos
- **Docker containerization**
- **Cloud deployment** (AWS Lambda, GCP)
- **Testing suite** (pytest)
- **CI/CD pipeline**

---

## 📄 License

This tool is for creating social media content from Bengali podcasts. Ensure you have rights to the source material.

---

## 🙏 Credits

**Architecture**: Production-grade agentic system
**Quality Level**: Enterprise
**Type**: Autonomous Orchestration Platform
**Status**: ✅ Production-Ready

---

## 🎯 Quick Links

- [Full System Overview](TRANSFORMATION_COMPLETE.md)
- [Migration Guide](MIGRATION_GUIDE.md)
- [Configuration Reference](config.yaml)
- [Legacy Documentation](README.md)

---

**Version**: 3.0.0
**Architecture**: Agentic Microservices
**Status**: Production-Ready
**Quality**: Enterprise-Grade

**Built with world-class engineering principles** 🌟
