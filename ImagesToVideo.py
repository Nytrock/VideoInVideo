import os
import moviepy.video.io.ImageSequenceClip

image_folder = 'D:/videoInVideo/MainVideo'
fps = 30

print("Creating images list...")
image_files = [os.path.join(image_folder, img)
               for img in os.listdir(image_folder)
               if img.endswith(".jpg")]
print("Creating video...")
clip = moviepy.video.io.ImageSequenceClip.ImageSequenceClip(image_files, fps=fps)
print("Saving video...")
clip.write_videofile('full_version.mp4')
