# GPX Racer

Compare and race two GPX routes in a Streamlit UI.

## Features

- Upload two GPX files.
- Display both routes on a map with separate colors.
- Show one movable dot per route.
- Move both dots with a synchronized slider.
- Move each dot independently with route-specific sliders.
- Animate both dots so each reaches the route end in 60 seconds.
- Align both dots to the earliest close location.
- Start race from Route 1 or Route 2 current dot position and snap the other route to the nearest location.

## Local run

```bash
pip install -e .
streamlit run app.py
```

or:

```bash
./scripts/run_local.sh
```

## Docker run

```bash
./run.sh
```
