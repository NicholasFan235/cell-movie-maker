
import sys

simulation_number = 1

files = f"visualisations/sim_{simulation_number}/frame_%d.png"
output = f"visualisations/sim_{simulation_number}.mp4"
fps = 30


cmd = f"ffmpeg -framerate {fps} -i {files} -start_number 0 -c:v libx264 -r {fps} -pix_fmt yuv420p {output}"
print(cmd)
