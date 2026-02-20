"""Tests for GPX route utility functions."""

from gpx_racer.route_utils import build_route_data, earliest_alignment, haversine_m


def test_haversine_is_zero_for_identical_points() -> None:
    assert haversine_m((51.0, -1.0), (51.0, -1.0)) == 0.0


def test_route_progress_reaches_one() -> None:
    route = build_route_data([(51.0, -1.0), (51.0005, -1.0005), (51.001, -1.001)])
    assert route.progress[0] == 0.0
    assert route.progress[-1] == 1.0


def test_earliest_alignment_prefers_start_when_routes_overlap() -> None:
    route_a = build_route_data([(51.0, -1.0), (51.001, -1.001), (51.002, -1.002)])
    route_b = build_route_data([(51.0, -1.0), (51.004, -1.004), (51.005, -1.005)])
    idx_a, idx_b, _distance = earliest_alignment(route_a, route_b)
    assert (idx_a, idx_b) == (0, 0)
