
import sys
import os

assert len(sys.argv)==2, f"Missing simulation index. Usage: {sys.argv[0]} <simulation-index>."

#simulation_number = 1
simulation_number = sys.argv[1]

assert os.path.exists(os.path.join('visualisations', f'sim_{simulation_number}')),\
    f"No visualisations for simulation #{simulation_number}"

files = os.path.join("visualisations", f"sim_{simulation_number}", "frame_%d.png")
output = os.path.join("visualisations", "_movies", f"sim_{simulation_number}.mp4")
fps = 30


cmd = f"ffmpeg -framerate {fps} -i {files} -start_number 0 -c:v libx264 -r {fps} -pix_fmt yuv420p {output}"
print(cmd)
