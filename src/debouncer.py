"""
Speaker ID debouncing for stable camera tracking.

Removes rapid speaker-ID bounces that cause jarring crop window snaps.
"""


def debounce_speaker_ids(speaker_track_ids, min_hold_frames=15):
    """
    Remove rapid speaker-ID bounces shorter than min_hold_frames.

    Speaker detection sometimes flickers the active-speaker label during
    crosstalk or brief classification uncertainty, producing 1-10 frame
    segments that cause jarring rapid-fire crop snaps. This pre-filter
    replaces those short segments with the surrounding stable speaker ID
    so the downstream dead-zone tracker never sees them.

    Algorithm:
      1. Run-length encode the raw IDs into (track_id, start, length) runs.
      2. For any run shorter than min_hold_frames, replace it with the
         previous stable run's ID (or the next stable run if it's the first).
      3. Expand back to a per-frame list.

    Args:
        speaker_track_ids: Per-frame list of speaker IDs (int or None).
            None means no speaker detected at that frame.
        min_hold_frames: Minimum frames a speaker must hold to be "stable".

    Returns:
        Same-length list with short flicker runs replaced by nearest stable ID.
        None segments are never modified.

    Examples:
        >>> debounce_speaker_ids([0]*50 + [1]*3 + [0]*50, min_hold_frames=10)
        [0]*103  # The 3-frame speaker-1 segment is replaced by speaker 0

        >>> debounce_speaker_ids([None]*10 + [0]*50, min_hold_frames=15)
        [None]*10 + [0]*50  # None segments are untouched
    """
    if not speaker_track_ids:
        return speaker_track_ids

    # Step 1: Run-length encode
    runs = []
    cur_id = speaker_track_ids[0]
    cur_start = 0
    cur_len = 1
    for i in range(1, len(speaker_track_ids)):
        tid = speaker_track_ids[i]
        if tid == cur_id:
            cur_len += 1
        else:
            runs.append((cur_id, cur_start, cur_len))
            cur_id = tid
            cur_start = i
            cur_len = 1
    runs.append((cur_id, cur_start, cur_len))

    # Step 2: Replace short non-None runs with nearest stable ID
    stable_ids = list(runs)
    for i in range(len(stable_ids)):
        tid, start, length = stable_ids[i]
        if tid is None:
            continue
        if length < min_hold_frames:
            prev_id = None
            for j in range(i - 1, -1, -1):
                if stable_ids[j][0] is not None and stable_ids[j][2] >= min_hold_frames:
                    prev_id = stable_ids[j][0]
                    break
            if prev_id is not None:
                stable_ids[i] = (prev_id, start, length)
            else:
                for j in range(i + 1, len(stable_ids)):
                    if stable_ids[j][0] is not None and stable_ids[j][2] >= min_hold_frames:
                        stable_ids[i] = (stable_ids[j][0], start, length)
                        break

    # Step 3: Expand back to per-frame list
    result = []
    for tid, _start, length in stable_ids:
        result.extend([tid] * length)
    return result
