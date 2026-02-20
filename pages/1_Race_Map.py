"""Race map page for comparing two GPX tracks."""

from __future__ import annotations

import time

import folium
import streamlit as st
from streamlit.runtime.uploaded_file_manager import UploadedFile
from streamlit_folium import st_folium

from gpx_racer.route_utils import (
    RouteData,
    build_route_data,
    closest_index,
    earliest_alignment,
    parse_gpx_points,
)

ROUTE_1_COLOR = "#D1495B"
ROUTE_2_COLOR = "#00798C"


def ensure_state() -> None:
    """Initialize session state values used by the page."""
    defaults = {
        "route_1_progress": 0.0,
        "route_2_progress": 0.0,
        "sync_progress": 0.0,
        "route_1_progress_ui": 0.0,
        "route_2_progress_ui": 0.0,
        "sync_progress_ui": 0.0,
        "sync_progress_prev": 0.0,
        "autoplay": False,
        "autoplay_start_ts": None,
        "autoplay_from_route_1": 0.0,
        "autoplay_from_route_2": 0.0,
    }
    for key, value in defaults.items():
        st.session_state.setdefault(key, value)


def clamp_progress(value: float) -> float:
    """Clamp progress into [0, 1]."""
    return min(max(value, 0.0), 1.0)


def recompute_sync_progress() -> None:
    """Recompute synchronized progress from individual routes."""
    st.session_state.sync_progress = (
        st.session_state.route_1_progress + st.session_state.route_2_progress
    ) / 2.0
    st.session_state.sync_progress_prev = st.session_state.sync_progress


def sync_if_slider_changed() -> None:
    """Apply synchronized slider changes to both routes."""
    current = clamp_progress(st.session_state.sync_progress_ui)
    previous = st.session_state.sync_progress_prev
    if abs(current - previous) > 1e-9:
        st.session_state.route_1_progress = current
        st.session_state.route_2_progress = current
    st.session_state.sync_progress = current
    st.session_state.sync_progress_prev = current


def progress_to_index(route: RouteData, progress: float) -> int:
    """Get nearest route index from normalized progress."""
    target = clamp_progress(progress)
    nearest_idx = 0
    nearest_distance = abs(route.progress[0] - target)
    for idx, route_progress in enumerate(route.progress):
        distance = abs(route_progress - target)
        if distance < nearest_distance:
            nearest_distance = distance
            nearest_idx = idx
    return nearest_idx


def apply_autoplay() -> None:
    """Advance both routes so they reach route end after 60 seconds."""
    if not st.session_state.autoplay:
        return

    started = st.session_state.autoplay_start_ts
    if started is None:
        return

    elapsed = time.time() - started
    ratio = min(elapsed / 60.0, 1.0)
    from_1 = st.session_state.autoplay_from_route_1
    from_2 = st.session_state.autoplay_from_route_2

    st.session_state.route_1_progress = from_1 + (1.0 - from_1) * ratio
    st.session_state.route_2_progress = from_2 + (1.0 - from_2) * ratio
    recompute_sync_progress()

    if ratio >= 1.0:
        st.session_state.autoplay = False


def update_route_1_from_slider() -> None:
    """Update route 1 progress from its slider."""
    st.session_state.route_1_progress = clamp_progress(st.session_state.route_1_progress_ui)
    recompute_sync_progress()


def update_route_2_from_slider() -> None:
    """Update route 2 progress from its slider."""
    st.session_state.route_2_progress = clamp_progress(st.session_state.route_2_progress_ui)
    recompute_sync_progress()


def render_map(route_1: RouteData, route_2: RouteData) -> None:
    """Render map with routes and current markers."""
    idx_1 = progress_to_index(route_1, st.session_state.route_1_progress)
    idx_2 = progress_to_index(route_2, st.session_state.route_2_progress)
    dot_1 = route_1.points[idx_1]
    dot_2 = route_2.points[idx_2]

    all_points = route_1.points + route_2.points
    center_lat = sum(point[0] for point in all_points) / len(all_points)
    center_lon = sum(point[1] for point in all_points) / len(all_points)
    fmap = folium.Map(location=(center_lat, center_lon), zoom_start=12, control_scale=True)

    folium.PolyLine(route_1.points, color=ROUTE_1_COLOR, weight=5, opacity=0.85).add_to(fmap)
    folium.PolyLine(route_2.points, color=ROUTE_2_COLOR, weight=5, opacity=0.85).add_to(fmap)

    folium.CircleMarker(
        location=dot_1,
        radius=9,
        color=ROUTE_1_COLOR,
        fill=True,
        fill_color=ROUTE_1_COLOR,
        fill_opacity=1.0,
        tooltip="Route 1",
    ).add_to(fmap)
    folium.CircleMarker(
        location=dot_2,
        radius=9,
        color=ROUTE_2_COLOR,
        fill=True,
        fill_color=ROUTE_2_COLOR,
        fill_opacity=1.0,
        tooltip="Route 2",
    ).add_to(fmap)

    st_folium(fmap, use_container_width=True, height=560, returned_objects=[])


def try_build_route(uploaded_file: UploadedFile) -> RouteData:
    """Parse uploaded GPX and build route data."""
    gpx_text = uploaded_file.getvalue().decode("utf-8", errors="ignore")
    points = parse_gpx_points(gpx_text)
    return build_route_data(points)


st.set_page_config(page_title="GPX Race Map", layout="wide")
ensure_state()
st.title("GPX Race Map")
st.caption("Upload two GPX files, then compare and race the routes.")

col_upload_1, col_upload_2 = st.columns(2)
with col_upload_1:
    gpx_file_1 = st.file_uploader("Route 1 GPX", type=["gpx"], key="gpx_1")
with col_upload_2:
    gpx_file_2 = st.file_uploader("Route 2 GPX", type=["gpx"], key="gpx_2")

if not gpx_file_1 or not gpx_file_2:
    st.info("Upload both files to start the race view.")
    st.stop()

try:
    route_1 = try_build_route(gpx_file_1)
    route_2 = try_build_route(gpx_file_2)
except ValueError as error:
    st.error(f"Invalid GPX data: {error}")
    st.stop()
except Exception as error:  # pragma: no cover - defensive for malformed files
    st.error(f"Could not parse GPX files: {error}")
    st.stop()

with st.sidebar:
    st.header("Race Controls")
    st.session_state.route_1_progress = clamp_progress(st.session_state.route_1_progress)
    st.session_state.route_2_progress = clamp_progress(st.session_state.route_2_progress)
    st.session_state.sync_progress = clamp_progress(st.session_state.sync_progress)
    st.session_state.route_1_progress_ui = st.session_state.route_1_progress
    st.session_state.route_2_progress_ui = st.session_state.route_2_progress
    st.session_state.sync_progress_ui = st.session_state.sync_progress

    st.slider(
        "Move both dots together",
        min_value=0.0,
        max_value=1.0,
        step=0.001,
        key="sync_progress_ui",
        format="%.3f",
        on_change=sync_if_slider_changed,
    )

    st.slider(
        "Route 1 progress",
        min_value=0.0,
        max_value=1.0,
        step=0.001,
        key="route_1_progress_ui",
        format="%.3f",
        on_change=update_route_1_from_slider,
    )
    st.slider(
        "Route 2 progress",
        min_value=0.0,
        max_value=1.0,
        step=0.001,
        key="route_2_progress_ui",
        format="%.3f",
        on_change=update_route_2_from_slider,
    )

    col_go, col_stop = st.columns(2)
    with col_go:
        if st.button("Go (60s)", use_container_width=True):
            st.session_state.autoplay = True
            st.session_state.autoplay_start_ts = time.time()
            st.session_state.autoplay_from_route_1 = clamp_progress(
                st.session_state.route_1_progress
            )
            st.session_state.autoplay_from_route_2 = clamp_progress(
                st.session_state.route_2_progress
            )
    with col_stop:
        if st.button("Stop", use_container_width=True):
            st.session_state.autoplay = False
            st.session_state.autoplay_start_ts = None

    st.divider()
    if st.button("Align dots as early as possible", use_container_width=True):
        index_1, index_2, distance_m = earliest_alignment(route_1, route_2)
        st.session_state.route_1_progress = route_1.progress[index_1]
        st.session_state.route_2_progress = route_2.progress[index_2]
        recompute_sync_progress()
        st.caption(f"Closest early pairing distance: {distance_m:.1f} m")

    if st.button("Start race from Route 1 position", use_container_width=True):
        source_index = progress_to_index(route_1, st.session_state.route_1_progress)
        source_point = route_1.points[source_index]
        target_index = closest_index(source_point, route_2)
        st.session_state.route_2_progress = route_2.progress[target_index]
        recompute_sync_progress()

    if st.button("Start race from Route 2 position", use_container_width=True):
        source_index = progress_to_index(route_2, st.session_state.route_2_progress)
        source_point = route_2.points[source_index]
        target_index = closest_index(source_point, route_1)
        st.session_state.route_1_progress = route_1.progress[target_index]
        recompute_sync_progress()

    st.divider()
    st.write(f"Route 1: {route_1.cumulative_m[-1] / 1000:.2f} km")
    st.write(f"Route 2: {route_2.cumulative_m[-1] / 1000:.2f} km")

apply_autoplay()

render_map(route_1, route_2)

if st.session_state.autoplay:
    time.sleep(0.10)
    st.rerun()
