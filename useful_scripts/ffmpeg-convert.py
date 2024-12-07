
import sys
import os
import subprocess

frames_folder = os.path.abspath(sys.argv[1])

assert os.path.exists(frames_folder),\
    f"File not found: {frames_folder}\n"

outfile = os.path.join(
    os.path.dirname(frames_folder), f'{os.path.basename(frames_folder)}.mp4')
files = os.path.join(frames_folder, 'frame_%d.png')

fps = 30
if len(sys.argv) > 2: fps = int(sys.argv[2])


cmd = ["ffmpeg",
    "-y",
    "-framerate", str(fps),
    "-i", str(files),
    "-start_number", str(0),
    "-c:v", "libx264",
    "-r", str(fps),
    "-pix_fmt", "yuv420p",
    outfile]

if subprocess.run(cmd).returncode == 0:
    print("Converted successfully.")
else:
    print(f"Error running command:\n{' '.join(cmd)}.")
