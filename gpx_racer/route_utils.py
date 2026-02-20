"""Utilities for GPX route parsing and route progress calculations."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable
import math

import gpxpy

Point = tuple[float, float]


@dataclass(frozen=True)
class RouteData:
    """Represent route coordinates and cumulative progress values."""

    points: list[Point]
    cumulative_m: list[float]
    progress: list[float]


def parse_gpx_points(gpx_text: str) -> list[Point]:
    """Parse all track and route points from GPX text."""
    parsed = gpxpy.parse(gpx_text)
    points: list[Point] = []

    for track in parsed.tracks:
        for segment in track.segments:
            for point in segment.points:
                points.append((point.latitude, point.longitude))

    for route in parsed.routes:
        for point in route.points:
            points.append((point.latitude, point.longitude))

    deduped: list[Point] = []
    for point in points:
        if not deduped or point != deduped[-1]:
            deduped.append(point)

    return deduped


def haversine_m(point_a: Point, point_b: Point) -> float:
    """Compute great-circle distance in meters between two lat/lon points."""
    lat1, lon1 = point_a
    lat2, lon2 = point_b
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)
    a = (
        math.sin(delta_phi / 2) ** 2
        + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2) ** 2
    )
    return 2 * 6_371_000 * math.asin(math.sqrt(a))


def build_route_data(points: Iterable[Point]) -> RouteData:
    """Build route data with cumulative meters and normalized progress."""
    point_list = list(points)
    if len(point_list) < 2:
        raise ValueError("A route needs at least 2 points.")

    cumulative = [0.0]
    for index in range(1, len(point_list)):
        step_m = haversine_m(point_list[index - 1], point_list[index])
        cumulative.append(cumulative[-1] + step_m)

    total = cumulative[-1]
    if total <= 0:
        raise ValueError("Route has zero distance.")

    progress = [value / total for value in cumulative]
    return RouteData(points=point_list, cumulative_m=cumulative, progress=progress)


def point_at_progress(route: RouteData, progress: float) -> Point:
    """Return the nearest route point at a normalized progress [0, 1]."""
    target = min(max(progress, 0.0), 1.0)
    best_idx = 0
    best_dist = abs(route.progress[0] - target)

    for index, value in enumerate(route.progress):
        diff = abs(value - target)
        if diff < best_dist:
            best_dist = diff
            best_idx = index

    return route.points[best_idx]


def index_at_progress(route: RouteData, progress: float) -> int:
    """Return the nearest index for a normalized progress [0, 1]."""
    target = min(max(progress, 0.0), 1.0)
    best_idx = 0
    best_dist = abs(route.progress[0] - target)

    for index, value in enumerate(route.progress):
        diff = abs(value - target)
        if diff < best_dist:
            best_dist = diff
            best_idx = index

    return best_idx


def closest_index(target: Point, route: RouteData) -> int:
    """Return the index of the closest route point to target."""
    best_idx = 0
    best_dist = haversine_m(target, route.points[0])
    for index, point in enumerate(route.points):
        distance = haversine_m(target, point)
        if distance < best_dist:
            best_dist = distance
            best_idx = index
    return best_idx


def earliest_alignment(route_a: RouteData, route_b: RouteData) -> tuple[int, int, float]:
    """Find an early pair of route indices that are geographically close."""
    best_i = 0
    best_j = closest_index(route_a.points[0], route_b)
    best_dist = haversine_m(route_a.points[0], route_b.points[best_j])
    best_score = route_a.progress[0] + route_b.progress[best_j]

    for i, point in enumerate(route_a.points):
        j = closest_index(point, route_b)
        dist = haversine_m(point, route_b.points[j])
        score = route_a.progress[i] + route_b.progress[j]

        if score < best_score or (math.isclose(score, best_score) and dist < best_dist):
            best_i, best_j = i, j
            best_dist = dist
            best_score = score

    return best_i, best_j, best_dist
