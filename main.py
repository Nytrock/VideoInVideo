import cv2
import glob
import json
import numpy
import os
import stat

from datetime import timedelta
from math import ceil

from moviepy.audio.io.AudioFileClip import AudioFileClip
from moviepy.video.io.VideoFileClip import VideoFileClip
from moviepy.video.io.ImageSequenceClip import ImageSequenceClip
from PIL import Image


def main():
    # Start message
    if not confirm_working('Welcome to the "Video in video" program! I’ll warn you right away that video processing'
                           ' can take a lot of time, but progress will be saved at certain stages. Continue? '):
        write_to_console("The program has been interrupted.")
        return

    # Check for original video
    if not os.path.isfile("original.mp4"):
        write_to_console('The system cannot detect the original video. Please put in the folder with the program'
                         ' processed video and rename it to "original.mp4"')
        input()
        return

    # Checking for a save
    progress_stage = 0
    custom_fps = 0
    zoom = 0
    visible = -1
    scale = 0
    have_audio = True
    if os.path.isfile("save_file.json"):
        if not os.path.exists("materials"):
            # If there is a save file, but there is no folder with materials, we start all over again
            if not confirm_working('ATTENTION! The folder with the saved progress was not found, so '
                                   'the program will start the entire creation process again. Continue? '):
                write_to_console("The program has been interrupted.")
                input()
                return
        else:
            file = open("save_file.json")
            data = json.load(file)
            # We invite the user to continue progress
            if confirm_working("A save file was found while the program was running. "
                               "Do you want to continue from the saved stage?"):
                progress_stage = data["progress_stage"]
                custom_fps = int(data["fps"])
                zoom = float(data["zoom"])
                visible = float(data["visible"])
                scale = float(data["scale"])
                have_audio = data["have_audio"]
                stable = os.path.exists("materials")
                # Checking if everything is there to continue progress
                if progress_stage == 2 and stable:
                    stable = os.path.isfile("materials/audio.mp3") or not have_audio
                elif progress_stage == 3 and stable:
                    stable = (os.path.isfile("materials/audio.mp3") or not have_audio) and\
                             os.path.exists("materials/clips")
                elif progress_stage == 4 and stable:
                    stable = (os.path.isfile("materials/audio.mp3") or not have_audio) and \
                             os.path.exists("materials/clips") and len(glob.glob("materials/clips/raw**.jpg")) == 0
                # If not, we talk about it.
                if not stable:
                    # dict for next message
                    stages = {
                        1: "Saving audio",
                        2: "Splitting video into frames",
                        3: "Converting frames",
                        4: "Saving video"
                    }
                    write_to_console('When checking the available files in the "materials" folder, '
                                     f'some of the files needed for the "{stages[progress_stage]}" stage were '
                                     'not found, so the program was interrupted. '
                                     '\nPlease either check for the correct files in the "materials" '
                                     'folder, or start over.')
                    input()
                    return
            # If the user wants to start over, first delete the old files
            elif os.path.exists("materials"):
                write_to_console("Removing old materials...")
                clean_trash("materials")
    # If there are no saves, but the folder exists, delete all files from the folder
    elif os.path.exists("materials"):
        if os.listdir("materials"):
            if confirm_working('ATTENTION! Files already exist in the "materials" folder! '
                               'For the correct operation of the program, it will be cleared. Continue? '):
                write_to_console("Removing all unnecessary files...")
                clean_trash("materials")
            else:
                write_to_console("The program has been interrupted.")
                input()
                return
    # If there is nothing, just create a folder
    else:
        os.mkdir("materials")

    # Checking if the folder exists (just in case)
    if not os.path.exists("materials"):
        os.mkdir("materials")

    # If there was no save, then we will find out the desired fps
    if custom_fps == 0:
        write_to_console("Enter the desired fps of the final video.")
        while True:
            try:
                custom_fps = int(input())
                if custom_fps > 0:
                    break
                print("Enter integer GREATER than zero")
            except ValueError:
                print("Enter the correct answer (integer greater than zero)")

    # If there was no save, then we will find out the zoom
    if zoom == 0:
        write_to_console("Enter how much you want to zoom in on the final video (real number, "
                         "1 - default and min, 10 - max)")
        while True:
            try:
                zoom = float(input())
                if 10 >= zoom >= 1:
                    break
                print("Enter real number BETWEEN 1 and 10)")
            except ValueError:
                print("Enter the correct answer (real number between 1 and 10)")

    # If there was no save, then we will find out the visible coefficient
    if visible == -1:
        write_to_console(
            "Enter the degree of 'visibility' of the main video. At 0, the video will not be visible, and at 1 "
            "the video will simply be enlarged by several times. Most optimal value is 0.7.")
        while True:
            try:
                visible = float(input())
                if not 0 <= visible <= 1:
                    print("Enter a real number BETWEEN 0 and 1.")
                else:
                    break
            except ValueError:
                print("Enter the correct answer (real number between 0 and 1)")

    # If there was no save, then we will find out the scale coefficient
    if scale == 0:
        vid = cv2.VideoCapture("original.mp4")
        height = int(vid.get(cv2.CAP_PROP_FRAME_HEIGHT))
        width = int(vid.get(cv2.CAP_PROP_FRAME_WIDTH))
        max_scale = min(height, width)

        write_to_console("This program replaces each pixel in a frame with the frame itself. "
                         "To avoid bad looking pictures, enter how many times you want to reduce the size "
                         f"of the converting video (real number between 1 and {max_scale}). "
                         f"Converting video size now - {width}x{height}."
                         f" Reducing the size does not affect the original video file. ")

        while True:
            try:
                scale = float(input())
                if 1 <= scale <= max_scale:
                    if confirm_working(f"The new size of the converting video is "
                                       f"{int(width // scale)}x{int(height // scale)}. It suits you?"):
                        break
                    else:
                        write_to_console("Enter how many times you want to reduce the size of the converting video "
                                         f"(real number between 1 and {max_scale}")
                else:
                    print(f"Enter a real number BETWEEN 1 and {max_scale}.")
            except ValueError:
                print(f"Enter the correct answer (real number between 1 and {max_scale})")

    # Extract audio to separate file
    if progress_stage <= 1:
        progress_stage = 1
        save_json(progress_stage, custom_fps, have_audio, zoom, visible, scale)
        if not save_audio():
            have_audio = False
            save_json(progress_stage, custom_fps, have_audio, zoom, visible, scale)

    # Extract video frames into separate files
    if progress_stage <= 2:
        progress_stage = 2
        save_json(progress_stage, custom_fps, have_audio, zoom, visible, scale)
        load_clips("original.mp4", custom_fps)
        write_to_console("Original video has been splitted.")

    # Video frame conversion
    if progress_stage <= 3:
        progress_stage = 3
        save_json(progress_stage, custom_fps, have_audio, zoom, visible, scale)
        length = len(glob.glob("materials/clips/raw**.jpg"))
        write_to_console(f"Converting clips to image in image...\n{0}/{length}")
        for count, name in enumerate(glob.glob("materials/clips/raw**.jpg")):
            convert_to_image_in_image(name, zoom, visible, scale)
            write_to_console(f"Converting clips to image in image...\n{count}/{length}")
        write_to_console(f"All clips successfully converted.")

    # Creating the final video
    if progress_stage <= 4:
        progress_stage = 4
        save_json(progress_stage, custom_fps, have_audio, zoom, visible, scale)
        write_to_console("Collecting data for video...")
        save_video("materials/clips", "materials/audio.mp3", get_fps("original.mp4", custom_fps), have_audio)
    write_to_console("Video saved.")
    input()


# Removing all files from the "materials" folder
def clean_trash(path: str) -> None:
    dirlist = [f for f in os.listdir(path)]
    for f in dirlist:
        fullname = os.path.join(path, f)
        if os.path.isdir(fullname):
            clean_trash(fullname)
            os.rmdir(fullname)
        else:
            os.chmod(fullname, stat.S_IWRITE)
            os.remove(fullname)


# Create video from individual frames and audio and save it
def save_video(image_folder: str, audio_file: str, fps: int, have_audio: bool) -> None:
    image_files = [os.path.abspath(os.path.join(image_folder, img))
                   for img in os.listdir(image_folder)
                   if img.endswith(".jpg")]
    print("Creating video...")
    clip = ImageSequenceClip(image_files, fps=fps)
    if have_audio:
        print("Adding audio...")
        audio_clip = AudioFileClip(audio_file)
        clip = clip.set_audio(audio_clip)
    print("Write to file...")
    clip.write_videofile("result.mp4")


# Formatting timedelta objects, remove microseconds and keep milliseconds
def format_timedelta(td: timedelta) -> str:
    result = str(td)
    try:
        result, ms = result.split(".")
    except ValueError:
        return result + ".00".replace(":", "-")
    ms = int(ms)
    ms = round(ms / 1e4)
    ms = f"{ms:02}"
    if ms == "100":
        ms = "999"
    return f"{result}.{ms}".replace(":", "-")


# Function that returns a list of durations in which frames should be saved
def get_saving_frames_durations(cap: cv2.VideoCapture, saving_fps: int) -> list:
    s = []
    clip_duration = cap.get(cv2.CAP_PROP_FRAME_COUNT) / cap.get(cv2.CAP_PROP_FPS)
    for i in numpy.arange(0, clip_duration, 1 / saving_fps):
        s.append(i)
    return s


# Split video into separate frames and save these frames to "clips" folder
def load_clips(video_file: str, custom_fps: int) -> None:
    filename = "materials/clips"

    if not os.path.isdir(filename):
        os.mkdir(filename)
    cap = cv2.VideoCapture(video_file)
    length = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    fps = cap.get(cv2.CAP_PROP_FPS)
    saving_frames_per_second = get_fps(video_file, custom_fps)
    saving_frames_durations = get_saving_frames_durations(cap, saving_frames_per_second)
    count = 0
    while True:
        is_read, frame = cap.read()
        if not is_read:
            break
        frame_duration = count / fps
        try:
            closest_duration = saving_frames_durations[0]
        except IndexError:
            break
        if frame_duration >= closest_duration:
            frame_duration_formatted = format_timedelta(timedelta(seconds=frame_duration))
            cv2.imwrite(os.path.join(filename, f"rawframe{frame_duration_formatted}.jpg"), frame)
            try:
                saving_frames_durations.pop(0)
            except IndexError:
                pass
        count += 1
        if count % 257 == 0:
            write_to_console(f"Splitting the original video into frames... \n{count}/{length}")
    write_to_console(f"Splitting the original video into frames... \n {count}/{length}")


# Get video fps
def get_fps(video_file: str, custom_fps: int) -> int:
    cap = cv2.VideoCapture(video_file)
    fps = cap.get(cv2.CAP_PROP_FPS)
    return min(fps, custom_fps)


# Convert an image (frame) to such an image, but already consisting of smaller images
def convert_to_image_in_image(filename: str, zoom: float, visible: float, scale: float) -> None:
    original = Image.open(filename)
    image_for_pixel = Image.open(filename)

    original = crop_center(original, ceil(original.size[0] // zoom), ceil(original.size[1] // zoom))
    original = original.resize((ceil(original.size[0] / scale), ceil(original.size[1] / scale)))
    original_width, original_height = original.size
    pixel_image_width, pixel_image_height = image_for_pixel.size

    smallest_size = min(pixel_image_width, pixel_image_height)
    image_for_pixel = crop_center(image_for_pixel, smallest_size, smallest_size)
    image_for_pixel = image_for_pixel.resize((min(smallest_size, int(6144 / original_height)),
                                              min(smallest_size, int(6144 / original_height))))
    pixel_image_width, pixel_image_height = image_for_pixel.size

    original = original.convert("RGBA")
    data = original.getdata()
    newData = []
    for item in data:
        newData.append(item[:-1] + (int(256 * visible),))
    original.putdata(newData)

    image_for_pixel = image_for_pixel.convert("RGBA")
    data = image_for_pixel.getdata()
    newData = []
    for item in data:
        newData.append(item[:-1] + (int(256 * (1 - visible)),))
    image_for_pixel.putdata(newData)

    original = original.resize((original_width * pixel_image_width, original_height * pixel_image_height))

    for x in range(original_width):
        for y in range(original_height):
            original.paste(image_for_pixel, (pixel_image_width * x, pixel_image_height * y), mask=image_for_pixel)
    original = original.convert('RGB')
    os.remove(filename)
    original.save(filename.replace("raw", "", 1))


# Function for cropping the image in the center
def crop_center(pil_img: Image, crop_width: int, crop_height: int) -> Image:
    img_width, img_height = pil_img.size
    return pil_img.crop(((img_width - crop_width) // 2,
                         (img_height - crop_height) // 2,
                         (img_width + crop_width) // 2,
                         (img_height + crop_height) // 2))


# Save audio from video to separate file
def save_audio() -> bool:
    write_to_console("Audio saving...")
    videoclip = VideoFileClip("original.mp4")
    audioclip = videoclip.audio
    if audioclip.reader is not None:
        audioclip.write_audiofile("materials/audio.mp3")
    else:
        return False
    videoclip.close()
    audioclip.close()
    write_to_console("Audio saved.")
    return True


# Write something to the console
def write_to_console(text: str) -> None:
    if os.name == 'nt':
        os.system('cls')
    else:
        os.system('clear')
    print(text)


# Confirmation of any action
def confirm_working(text: str) -> bool:
    if os.name == 'nt':
        os.system('cls')
    else:
        os.system('clear')

    print(f"{text} (n/y)")
    while True:
        answer = input()
        if answer == "n":
            return False
        elif answer == "y":
            return True
        else:
            print("Enter the correct answer (n - no, y - yes)")


# Overwrite file with save
def save_json(progress_stage: int, custom_fps: int, audio: bool, zoom: float, visible: float, scale: float) -> None:
    data = {
        "progress_stage": progress_stage,
        "fps": custom_fps,
        "have_audio": audio,
        "zoom": zoom,
        "visible": visible,
        "scale": scale
    }
    json.dump(data, open("save_file.json", "w", encoding="utf-8"))


# Start
if __name__ == '__main__':
    main()
