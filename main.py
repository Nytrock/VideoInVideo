import cv2
import glob
import json
import numpy
import os
import stat

from datetime import timedelta

from moviepy.audio.io.AudioFileClip import AudioFileClip
from moviepy.editor import VideoFileClip
from moviepy.video.io.ImageSequenceClip import ImageSequenceClip
from PIL import Image

stages = {
    1: "Saving audio",
    2: "Splitting video into frames",
    3: "Converting frames",
    4: "Saving video"
}


def main():
    if not confirm_working('Welcome to the "Video in video" program! I’ll warn you right away that video processing'
                           ' can take a lot of time, but progress will be saved at certain stages.'):
        write_to_console("The program has been interrupted.")
        return
    if not os.path.isfile("original.mp4"):
        write_to_console('The system cannot detect the original video. Please put in the folder with the program'
                         ' processed video and rename it to "original.mp4"')
        return

    progress_stage = 0
    custom_fps = 0
    if os.path.isfile("save_file.json"):
        if not os.path.exists("materials"):
            if not confirm_working('ATTENTION! The folder with the saved progress was not found, so '
                                   'the program will start the entire creation process again.'):
                write_to_console("The program has been interrupted.")
                return
        else:
            file = open("save_file.json")
            data = json.load(file)
            if confirm_working("A save file was found while the program was running. "
                               "Do you want to continue from the saved stage?", True):
                progress_stage = data["progress_stage"]
                custom_fps = int(data["fps"])
                stable = os.path.exists("materials")
                if progress_stage == 2 and stable:
                    stable = os.path.isfile("materials/audio.mp3")
                elif progress_stage == 3 and stable:
                    stable = os.path.isfile("materials/audio.mp3") and os.path.exists("materials/clips")
                elif progress_stage == 4 and stable:
                    stable = os.path.isfile("materials/audio.mp3") and os.path.exists("materials/clips") \
                             and len(glob.glob("materials/clips/raw**.jpg")) == 0
                if not stable:
                    write_to_console('When checking the available files in the "materials" folder, '
                                     f'some of the files needed for the "{stages[progress_stage]}" stage were '
                                     'not found, so the program was interrupted. '
                                     '\nPlease either check for the correct files in the "materials" '
                                     'folder, or start over.')
                    return
            elif os.path.exists("materials"):
                write_to_console("Removing old materials...")
                clean_thrash("materials")
    elif os.path.exists("materials"):
        if os.listdir("materials"):
            if confirm_working('ATTENTION! Files already exist in the "materials" folder! '
                               'For the correct operation of the program, it will be cleared.'):
                write_to_console("Removing all unnecessary files...")
                clean_thrash("materials")
            else:
                write_to_console("The program has been interrupted.")
                return
    else:
        os.mkdir("materials")

    if not os.path.exists("materials"):
        os.mkdir("materials")

    if custom_fps == 0:
        write_to_console("Enter the desired fps of the final video.", True)
        while True:
            try:
                custom_fps = int(input())
                if custom_fps > 0:
                    break
                print("Enter the correct answer (integer greater than zero)")
            except ValueError:
                print("Enter the correct answer (integer greater than zero)")

    if progress_stage <= 1:
        progress_stage = 1
        save_json(progress_stage, custom_fps)
        save_audio()

    if progress_stage <= 2:
        progress_stage = 2
        save_json(progress_stage, custom_fps)
        load_clips("original.mp4", custom_fps)
        write_to_console("Original video has been splitted.")

    if progress_stage <= 3:
        progress_stage = 3
        save_json(progress_stage, custom_fps)
        length = len(glob.glob("materials/clips/raw**.jpg"))
        write_to_console(f"Converting clips to image in image...\n{0}/{length}")
        for count, name in enumerate(glob.glob("materials/clips/raw**.jpg")):
            convert_to_image_in_image(name)
            write_to_console(f"Converting clips to image in image...\n{count}/{length}")
        write_to_console(f"All clips successfully converted.")

    if progress_stage <= 4:
        progress_stage = 4
        save_json(progress_stage, custom_fps)
        write_to_console("")
        save_video("materials/clips", "materials/audio.mp3", get_fps("original.mp4", custom_fps))
    write_to_console("Video saved.")



def clean_thrash(path):
    dirlist = [f for f in os.listdir(path)]
    for f in dirlist:
        fullname = os.path.join(path, f)
        if os.path.isdir(fullname):
            clean_thrash(fullname)
            os.rmdir(fullname)
        else:
            os.chmod(fullname, stat.S_IWRITE)
            os.remove(fullname)


def save_video(image_folder, audio_file, fps):
    image_files = [os.path.join(image_folder, img)
                   for img in os.listdir(image_folder)
                   if img.endswith(".jpg")]
    print("Creating video...")
    clip = ImageSequenceClip(image_files, fps=fps)
    print("Adding audio...")
    audio_clip = AudioFileClip(audio_file)
    clip = clip.set_audio(audio_clip)
    print("Write to file...")
    clip.write_videofile("result.mp4")


def format_timedelta(td):
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


def get_saving_frames_durations(cap, saving_fps):
    s = []
    clip_duration = cap.get(cv2.CAP_PROP_FRAME_COUNT) / cap.get(cv2.CAP_PROP_FPS)
    for i in numpy.arange(0, clip_duration, 1 / saving_fps):
        s.append(i)
    return s


def load_clips(video_file, custom_fps):
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


def get_fps(video_file, custom_fps):
    cap = cv2.VideoCapture(video_file)
    fps = cap.get(cv2.CAP_PROP_FPS)
    return min(fps, custom_fps)


def convert_to_image_in_image(filename):
    original = Image.open(filename)
    image_for_pixel = Image.open(filename)

    original_width, original_height = original.size
    pixel_image_width, pixel_image_height = image_for_pixel.size

    image_for_pixel = crop_center(image_for_pixel, min(pixel_image_width, pixel_image_height),
                                  min(pixel_image_width, pixel_image_height))
    image_for_pixel = image_for_pixel.resize((int(6144 / original_height), int(6144 / original_height)))
    pixel_image_width, pixel_image_height = image_for_pixel.size

    original = original.convert("RGBA")
    data = original.getdata()
    newData = []
    for item in data:
        newData.append(item[:-1] + (int(256 * 0.7),))
    original.putdata(newData)

    image_for_pixel = image_for_pixel.convert("RGBA")
    data = image_for_pixel.getdata()
    newData = []
    for item in data:
        newData.append(item[:-1] + (int(256 * 0.3),))
    image_for_pixel.putdata(newData)

    original = original.resize((original_width * pixel_image_width, original_height * pixel_image_height))

    for x in range(original_width):
        for y in range(original_height):
            original.paste(image_for_pixel, (pixel_image_width * x, pixel_image_height * y), mask=image_for_pixel)
    original = original.convert('RGB')
    os.remove(filename)
    original.save(filename.replace("raw", "", 1))


def crop_center(pil_img: Image, crop_width: int, crop_height: int) -> Image:
    img_width, img_height = pil_img.size
    return pil_img.crop(((img_width - crop_width) // 2,
                         (img_height - crop_height) // 2,
                         (img_width + crop_width) // 2,
                         (img_height + crop_height) // 2))


def save_audio():
    write_to_console("Audio saving...", True)
    videoclip = VideoFileClip("original.mp4")
    audioclip = videoclip.audio
    audioclip.write_audiofile("materials/audio.mp3")
    audioclip.close()
    videoclip.close()
    write_to_console("Audio saved.")


def write_to_console(text: str, end=False) -> None:
    os.system('cls')
    if end:
        print(text)
    else:
        print(text, end='')


def confirm_working(text: str, full=False) -> bool:
    os.system('cls')
    if full:
        print(f"{text} (n/y)")
    else:
        print(f"{text} Continue? (n/y)")
    while True:
        answer = input()
        if answer == "n":
            return False
        elif answer == "y":
            return True
        else:
            print("Enter the correct answer (n - no, y - yes)")


def save_json(progress_stage, custom_fps):
    data = {
        "progress_stage": progress_stage,
        "fps": custom_fps
    }
    json.dump(data, open("save_file.json", "w", encoding="utf-8"))


if __name__ == '__main__':
    main()
