#!/usr/bin/env python3
"""
Streamlit front-end for the Long Form to Shorts pipeline.

This UI lets you upload a long-form podcast/video, trigger the agentic
pipeline, and instantly review generated artifacts. The layout follows a
two-column studio workflow:
    • Left panel: project controls and pipeline launch.
    • Right panel: live status, logs, and produced assets.
"""

from __future__ import annotations

import io
import json
import os
import re
import textwrap
from datetime import datetime
from pathlib import Path
from typing import Iterable, List

import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import streamlit as st

from src.agents.orchestrator import create_orchestrator
from src.config.schemas import ProjectConfig
from src.config.validators import ValidationError, validate_video_file

# Workspace constants
PROJECTS_DIR = ROOT / "Projects"
DEFAULT_VIDEO_EXTENSIONS = ("mp4", "mkv", "mov", "m4v", "mp3", "wav")


def slugify_project_name(name: str) -> str:
    """Convert raw user input to a filesystem-friendly project slug."""
    cleaned = re.sub(r"[^A-Za-z0-9]+", "-", name).strip("-").lower()
    if not cleaned:
        cleaned = datetime.now().strftime("project-%Y%m%d-%H%M%S")
    return cleaned


def save_uploaded_video(project_root: Path, file_uploader) -> Path:
    """Persist uploaded file to the project's Source directory."""
    source_dir = project_root / "Source"
    source_dir.mkdir(parents=True, exist_ok=True)

    video_path = source_dir / file_uploader.name
    with open(video_path, "wb") as f:
        f.write(file_uploader.getbuffer())
    return video_path


def list_project_outputs(project_root: Path) -> List[Path]:
    """Collect final outputs sorted by modification time (newest first)."""
    output_dir = project_root / "Output"
    if not output_dir.exists():
        return []
    assets = [p for p in output_dir.glob("*") if p.is_file()]
    return sorted(assets, key=lambda p: p.stat().st_mtime, reverse=True)


def read_log_excerpt(project_root: Path, max_bytes: int = 16_000) -> str:
    """Read the trailing portion of the pipeline log for quick inspection."""
    log_dir_candidates = [
        project_root / "logs" / "pipeline.log",
        project_root / "Logs" / "pipeline.log",
    ]
    for log_path in log_dir_candidates:
        if log_path.exists():
            with open(log_path, "rb") as log_file:
                log_file.seek(0, io.SEEK_END)
                size = log_file.tell()
                log_file.seek(max(0, size - max_bytes), io.SEEK_SET)
                snippet = log_file.read().decode("utf-8", errors="ignore")
                return snippet.strip()
    return "No pipeline logs available yet."


def render_stage_timeline(status_payload: dict) -> None:
    """Pretty-print per-stage timing and completion stats."""
    stages = status_payload.get("stages", [])
    if not stages:
        st.info("No recorded stages yet.")
        return

    for stage in stages:
        status_icon = "✅" if stage["status"] == "completed" else "⏳"
        st.markdown(
            f"{status_icon} **{stage['name'].replace('_', ' ').title()}** "
            f"- {stage['status'].title()} "
            f"({stage['duration']:.2f}s)"
        )


def render_project_summary(config: ProjectConfig) -> None:
    """Display reel metadata captured in the project configuration."""
    if not config.reels:
        st.warning("No reel segments generated yet.")
        return

    for reel in config.reels:
        with st.expander(f"Reel {reel.id}: {reel.title}", expanded=False):
            st.write(f"Hook type: {reel.hook_type or 'n/a'}")
            st.write(f"Timestamps: {reel.start} ➜ {reel.end}")
            st.write(f"Viral potential: {reel.viral_potential}/5 ⭐")
            if reel.final_output:
                st.write(f"Video file: `{reel.final_output}`")


def render_output_gallery(outputs: Iterable[Path]) -> None:
    """Render playable previews for each output file when possible."""
    seen_any = False
    for asset in outputs:
        seen_any = True
        suffix = asset.suffix.lower()
        st.write(f"`{asset}`")
        if suffix in {".mp4", ".mov", ".m4v", ".mkv"}:
            st.video(str(asset))
        elif suffix in {".mp3", ".wav"}:
            st.audio(str(asset))
        elif suffix in {".txt", ".md"}:
            st.code(asset.read_text(encoding="utf-8"), language="markdown")
        else:
            st.download_button(
                label=f"Download {asset.name}",
                data=asset.read_bytes(),
                file_name=asset.name,
                mime="application/octet-stream",
            )
    if not seen_any:
        st.info("Outputs will appear here after a successful pipeline run.")


def ensure_projects_root() -> None:
    """Guarantee the Projects directory exists before we start."""
    PROJECTS_DIR.mkdir(parents=True, exist_ok=True)


def main() -> None:
    """Entry point for the Streamlit UI."""
    st.set_page_config(
        page_title="Long Form to Shorts Studio",
        page_icon="🎬",
        layout="wide",
    )

    ensure_projects_root()

    if "last_status" not in st.session_state:
        st.session_state["last_status"] = None
    if "last_project" not in st.session_state:
        st.session_state["last_project"] = None
    if "last_error" not in st.session_state:
        st.session_state["last_error"] = None
    if "last_config_path" not in st.session_state:
        st.session_state["last_config_path"] = None

    st.title("🎞️ Long Form to Shorts — Interactive Studio")
    st.caption(
        "Upload a long-form podcast or video, orchestrate the agent pipeline, "
        "and review produced reels instantly."
    )

    api_key_status = (
        "✅ Gemini API key detected"
        if os.environ.get("GEMINI_API_KEY")
        else "⚠️ GEMINI_API_KEY is not set — transcription and analysis will fail."
    )
    st.sidebar.header("Environment")
    st.sidebar.info(api_key_status)

    left, right = st.columns([1, 1], gap="large")

    with left:
        st.subheader("Control Panel")
        project_input = st.text_input(
            "Project name",
            value=datetime.now().strftime("podcast-%Y%m%d"),
            help="This will determine where outputs are stored inside the Projects directory.",
        )

        uploaded_video = st.file_uploader(
            "Source video or audio",
            type=DEFAULT_VIDEO_EXTENSIONS,
            help="Upload the long-form asset you want to cut into shorts.",
        )

        launch_clicked = st.button(
            "🚀 Run Pipeline",
            use_container_width=True,
            disabled=uploaded_video is None,
        )

        if launch_clicked:
            project_slug = slugify_project_name(project_input)
            project_root = PROJECTS_DIR / project_slug

            with st.spinner("Validating media and orchestrating agents..."):
                try:
                    video_path = save_uploaded_video(project_root, uploaded_video)

                    # Quick validation feedback before orchestrating
                    metadata = validate_video_file(video_path)
                    st.success(
                        f"Loaded video: {metadata['width']}x{metadata['height']} • "
                        f"{metadata['duration']:.1f}s • codec {metadata['codec']}"
                    )

                    orchestrator = create_orchestrator(
                        project_name=project_slug,
                        source_video=video_path,
                        project_root=project_root,
                    )

                    success = orchestrator.execute_pipeline()
                    status_payload = orchestrator.get_status()

                    st.session_state["last_status"] = status_payload
                    st.session_state["last_project"] = project_slug
                    st.session_state["last_error"] = None if success else status_payload.get("error")
                    st.session_state["last_config_path"] = project_root / "project_config.json"

                    if success:
                        st.toast("Pipeline completed successfully! 🎉", icon="✅")
                    else:
                        st.error("Pipeline failed — see status panel for details.")

                except ValidationError as ve:
                    st.session_state["last_error"] = str(ve)
                    st.error(f"Video validation error: {ve}")
                except Exception as exc:  # pragma: no cover - best effort diagnostics
                    st.session_state["last_error"] = str(exc)
                    st.error(f"Pipeline execution failed: {exc}")

        with st.expander("Existing projects", expanded=False):
            if PROJECTS_DIR.exists():
                project_names = sorted([p.name for p in PROJECTS_DIR.iterdir() if p.is_dir()])
                if project_names:
                    chosen_project = st.selectbox(
                        "Open project",
                        options=["-- Select --"] + project_names,
                        index=0,
                        key="existing_project_select",
                    )
                    if chosen_project and chosen_project != "-- Select --":
                        st.session_state["last_project"] = chosen_project
                        status_path = PROJECTS_DIR / chosen_project / "Logs" / "pipeline_state.json"
                        if status_path.exists():
                            try:
                                payload = json.loads(status_path.read_text(encoding="utf-8"))
                                st.session_state["last_status"] = payload
                            except json.JSONDecodeError:
                                st.warning("Could not parse pipeline_state.json.")
                        st.session_state["last_config_path"] = (
                            PROJECTS_DIR / chosen_project / "project_config.json"
                        )
                else:
                    st.info("No projects found yet.")

    with right:
        st.subheader("Production Monitor")

        if st.session_state["last_project"]:
            st.write(f"**Active project:** `{st.session_state['last_project']}`")

        if st.session_state["last_error"]:
            st.error(f"Last error: {st.session_state['last_error']}")

        status_payload = st.session_state.get("last_status")
        if status_payload:
            status_badge = "🟢 Success" if status_payload.get("success") else "🟡 In Progress/Failed"
            st.markdown(f"**Pipeline status:** {status_badge}")
            render_stage_timeline(status_payload)
        else:
            st.info("Run the pipeline to see live status here.")

        if st.session_state.get("last_config_path"):
            config_path = Path(st.session_state["last_config_path"])
            if config_path.exists():
                try:
                    project_config = ProjectConfig.load(config_path)
                    render_project_summary(project_config)
                except Exception:
                    st.warning("Could not load project configuration.")

        if st.session_state.get("last_project"):
            project_root = PROJECTS_DIR / st.session_state["last_project"]
            st.markdown("---")
            st.markdown("#### Output Assets")
            render_output_gallery(list_project_outputs(project_root))

            st.markdown("#### Latest Logs")
            log_excerpt = read_log_excerpt(project_root)
            st.code(log_excerpt, language="bash")

            metrics_file = project_root / "Logs" / "metrics.json"
            if metrics_file.exists():
                with st.expander("View metrics.json"):
                    st.code(
                        textwrap.indent(metrics_file.read_text(encoding="utf-8"), prefix=""),
                        language="json",
                    )
        else:
            st.markdown("---")
            st.info("Outputs and logs will appear once you select or run a project.")


if __name__ == "__main__":
    main()
