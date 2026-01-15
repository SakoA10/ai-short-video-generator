import os
import re
import subprocess
import textwrap
import uuid
import re

W = 1080
H = 1920

def _split_sentences(text: str) -> list[str]:
    text = (text or "").strip()
    if not text:
        return []

    parts = re.split(r'(?<=[.!?])\s+', text)
    parts = [p.strip() for p in parts if p and p.strip()]

    if len(parts) < 3:
        words = text.split()
        chunks = []
        chunk = []
        max_words = 10 

        for w in words:
            chunk.append(w)
            if len(chunk) >= max_words:
                chunks.append(" ".join(chunk).strip())
                chunk = []

        if chunk:
            chunks.append(" ".join(chunk).strip())

        parts = [c for c in chunks if c]

    return parts



def _wrap_lines(text: str, width: int = 28, max_lines: int = 3) -> str:

    text = (text or "").strip()
    lines = textwrap.wrap(text, width=width)
    if len(lines) > max_lines:
        lines = lines[:max_lines]
        lines[-1] = lines[-1].rstrip(".") + "..."
    return r"\N".join(lines)


def _ass_escape(s: str) -> str:
    return (s or "").replace("{", r"\{").replace("}", r"\}")


def _ass_time(seconds: float) -> str:
    if seconds < 0:
        seconds = 0
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = seconds % 60
    sec = int(s)
    cs = int(round((s - sec) * 100))
    if cs >= 100:
        cs = 99
    return f"{h}:{m:02d}:{sec:02d}.{cs:02d}"


def _get_audio_duration(audio_path: str) -> float:

    cmd = [
        "ffprobe",
        "-v", "error",
        "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1",
        audio_path
    ]
    out = subprocess.check_output(cmd, text=True).strip()
    try:
        return float(out)
    except:
        return 0.0


def _allocate_timings(total_dur: float, sentences: list[str]) -> list[tuple[float, float]]:
    
    n = len(sentences)
    if n == 0:
        return []

    if total_dur <= 0.1:
        per = 2.0
        t = 0.0
        return [(t + i * per, t + (i + 1) * per) for i in range(n)]

    weights = [max(8, len(s)) for s in sentences]
    wsum = sum(weights)

    min_each = 0.90
    base_needed = min_each * n
    spare = max(0.0, total_dur - base_needed)

    starts_ends = []
    t = 0.0
    for w in weights:
        extra = spare * (w / wsum) if wsum else 0.0
        dur = min_each + extra
        end = min(total_dur, t + dur)
        if end - t < 0.05:
            end = min(total_dur, t + 0.05)
        starts_ends.append((t, end))
        t = end

    if starts_ends:
        starts_ends[-1] = (starts_ends[-1][0], total_dur)

    return starts_ends


def _write_ass_sentence_by_sentence(
    prompt: str,
    audio_path: str,
    ass_path: str,
    fontsize: int = 64,
    y_ratio: float = 0.70
):
    x = W // 2
    y = int(H * y_ratio)

    sentences = _split_sentences(prompt)
    dur = _get_audio_duration(audio_path)
    times = _allocate_timings(dur, sentences)

    outline = 2
    shadow = 0

    header = f"""[Script Info]
ScriptType: v4.00+
PlayResX: {W}
PlayResY: {H}

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Default,Montserrat SemiBold,{fontsize},&H00FFFFFF,&H00000000,&H00000000,0,0,0,0,100,100,0,0,1,{outline},{shadow},2,60,60,60,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""

    lines = [header]
    for (start, end), sent in zip(times, sentences):
        txt = _ass_escape(_wrap_lines(sent, width=28, max_lines=3))
        st = _ass_time(start)
        en = _ass_time(end)
        lines.append(
            f"Dialogue: 0,{st},{en},Default,,0,0,0,,{{\\an5\\pos({x},{y})}}{txt}\n"
        )

    with open(ass_path, "w", encoding="utf-8") as f:
        f.writelines(lines)


def _vf_scale_to_vertical() -> str:

    return f"scale={W}:{H}:force_original_aspect_ratio=decrease,pad={W}:{H}:(ow-iw)/2:(oh-ih)/2"


def make_clip(image_path: str, audio_path: str, subtitle_text: str, output_path: str):
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    ass_path = os.path.abspath(f"temp_subs_{uuid.uuid4().hex}.ass")

    try:
        tlen = len((subtitle_text or "").strip())
        if tlen <= 70:
            fontsize = 104
        elif tlen <= 140:
            fontsize = 92
        elif tlen <= 220:
            fontsize = 80
        else:
            fontsize = 68

        _write_ass_sentence_by_sentence(
            prompt=subtitle_text,
            audio_path=audio_path,
            ass_path=ass_path,
            fontsize=fontsize,
            y_ratio=0.70
        )
        import shutil; os.makedirs("outputs",exist_ok=True);
        shutil.copyfile(ass_path,"outputs/subs_last.ass")

        ass_ff = ass_path.replace("\\", "/").replace(":", r"\:")
        vf = f"{_vf_scale_to_vertical()},subtitles='{ass_ff}'"

        cmd = [
            "ffmpeg",
            "-y",
            "-loop", "1",
            "-i", image_path,
            "-i", audio_path,
            "-vf", vf,
            "-c:v", "libx264",
            "-tune", "stillimage",
            "-pix_fmt", "yuv420p",
            "-c:a", "aac",
            "-b:a", "192k",
            "-ar", "44100",
            "-ac", "2",
            "-shortest",
            "-movflags", "+faststart",
            output_path
        ]

        subprocess.run(cmd, check=True)

    finally:
        try:
            if os.path.exists(ass_path):
                os.remove(ass_path)
        except:
            pass
