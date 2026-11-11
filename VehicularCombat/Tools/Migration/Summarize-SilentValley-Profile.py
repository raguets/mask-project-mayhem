"""Summarize real UE CSV timing without copying account metadata into docs."""
import argparse, csv, json, math, statistics, struct
from pathlib import Path

parser = argparse.ArgumentParser()
parser.add_argument('csv_path', type=Path)
parser.add_argument('capture_folder', type=Path)
parser.add_argument('output', type=Path)
parser.add_argument('--skip', type=int, default=300)
args = parser.parse_args()
rows = list(csv.reader(args.csv_path.open(encoding='utf-8-sig')))
if not rows[-1] or rows[-1][0] != '[HasHeaderRowAtEnd]':
    raise RuntimeError('Expected complete UE CSV with final header')
header, initial = rows[-2], rows[0]
if header[:len(initial)] != initial:
    raise RuntimeError('CSV column ordering changed; cannot assume append-only columns')
data = rows[1:-2][args.skip:]
if len(data) < 100:
    raise RuntimeError('Not enough frames after warmup exclusion')

def series(name):
    index = header.index(name)
    return [float(row[index]) for row in data if len(row) > index]

def summary(values):
    ordered = sorted(values)
    return {'mean': statistics.mean(values), 'median': statistics.median(values),
            'p95': ordered[math.ceil(len(ordered)*.95)-1], 'max': max(values)}

images = {}
for image in args.capture_folder.glob('*.png'):
    with image.open('rb') as stream:
        magic = stream.read(24)
    if magic[:8] != b'\x89PNG\r\n\x1a\n':
        raise RuntimeError('Invalid PNG: ' + str(image))
    images[image.name] = list(struct.unpack('>II', magic[16:24]))
frames = series('FrameTime')
result = {
    'source_csv': args.csv_path.as_posix(), 'sample_frames': len(frames),
    'excluded_initial_frames': args.skip, 'sample_seconds': sum(frames)/1000,
    'frame_time_ms': summary(frames), 'mean_frame_rate_fps': 1000/statistics.mean(frames),
    'game_thread_ms': summary(series('GameThreadTime')),
    'render_thread_ms': summary(series('RenderThreadTime')),
    'gpu_ms': summary(series('GPUTime')), 'gpu_local_memory_mb': summary(series('GPUMem/LocalUsedMB')),
    'actual_png_dimensions': images,
    'limitations': ['Development Editor -game, camera gallery, no fixed timestep.',
                    'Camera cuts and screenshots affect the sample; not a complete driving benchmark.',
                    'CSV covers only its recorded interval, not necessarily all five places.',
                    'No claim of final mission performance or 60 FPS at other resolutions.']
}
args.output.parent.mkdir(parents=True, exist_ok=True)
args.output.write_text(json.dumps(result, indent=2), encoding='utf-8')
print(json.dumps({key: result[key] for key in ('sample_frames', 'mean_frame_rate_fps', 'frame_time_ms')}))
