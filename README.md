# Camera Tracking API — Live Coding Session (Track B: Backend)

## Context

You've already worked with this camera tracking module in the take-home. Now we're building a backend API service on top of it — exposing the tracker via REST endpoints with comparison, batch processing, and streaming capabilities.

The repo has:
- Fixed tracker code in `src/` (both bugs fixed, debouncer implemented)
- A Flask starter in `server/app.py` (no routes — you build them)
- Sample data in `sample_data/`

## Getting Started

```bash
cd server
pip install -r requirements.txt
python app.py
# Runs on http://localhost:5000
```

---

## Tier 1 — Basic API (~10 min)

Build a `POST /api/track` endpoint in `server/app.py` that:

1. Accepts JSON in the same format as `sample_data/clip_a.json`
2. Runs `track_face_crop()` with the provided data
3. Returns the tracking results as JSON

Test it:
```bash
curl -X POST http://localhost:5000/api/track \
  -H "Content-Type: application/json" \
  -d @sample_data/clip_a.json
```

Think about:
- What shape should the response be? What fields does a consumer need?
- Error handling — what if the JSON is malformed or missing required fields?

---

## Tier 2 — Compare & Batch (~20 min)

### 2a — Parameter Comparison

Build a `POST /api/compare` endpoint that:

1. Accepts the same clip JSON, plus two sets of tracker parameters
2. Runs the tracker twice with different parameters
3. Returns both results side-by-side with a diff summary

Example request body:
```json
{
  "clip": { ...clip_a.json contents... },
  "params_a": { "deadzone_ratio": 0.05, "smoothing": 0.1 },
  "params_b": { "deadzone_ratio": 0.20, "smoothing": 0.5 }
}
```

Think about what a useful diff summary looks like — segment count differences, total scene cuts, average segment length.

### 2b — Batch Processing

Build a batch processing system:

- `POST /api/batch` — accepts a list of clips, returns a job ID immediately
- `GET /api/batch/<job_id>` — returns job status and results

The batch endpoint should process clips concurrently (threading or multiprocessing). Think about:
- How to track job progress (how many clips done vs total)
- How to handle partial failures (one clip fails, others succeed)
- What the status response looks like while processing vs when complete

Test it:
```bash
# Submit batch job
curl -X POST http://localhost:5000/api/batch \
  -H "Content-Type: application/json" \
  -d "{\"clips\": [$(cat sample_data/clip_a.json), $(cat sample_data/clip_b.json)]}"

# Poll for results
curl http://localhost:5000/api/batch/<job_id>
```

---

## Tier 3 — Streaming Progress (stretch, ~10 min)

Replace the polling model with Server-Sent Events (SSE):

- `GET /api/batch/<job_id>/stream` — streams progress events as clips complete

Each event should include:
- Which clip just finished (index)
- Running totals (clips_done / clips_total)
- The result for that clip

Think about:
- What happens if the client connects after some clips already finished?
- How to signal that all clips are done (close the stream)

---

## Quick Reference

| Value | Number |
|-------|--------|
| Video dimensions | 640 x 360 |
| Crop aspect ratio | 9:16 (portrait) |
| Crop size | 202.5 x 360 px |
| Default dead zone ratio | 0.10 |
| Default smoothing | 0.25 |
| clip_a.json | 500 frames, single speaker |
| clip_b.json | 400 frames, multi-speaker with scene cuts |

### Tracker parameters you can vary

| Parameter | Range | Default | Effect |
|-----------|-------|---------|--------|
| `deadzone_ratio` | 0.0 – 0.5 | 0.10 | Larger = more stable, less responsive |
| `smoothing` | 0.0 – 1.0 | 0.25 | Higher = faster crop movement |
| `pixel_tolerance` | 0 – 20 | 3 | RLE compression tolerance |
| `min_speaker_hold_frames` | 0 – 60 | 15 | Debouncer threshold |
