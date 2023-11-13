<a href="https://youtu.be/a0avir3IQL4" align="center"><img src="Logo.jpg" alt="Rickroll made up of rickrolls"></a>
<p align="center"><i>Click on the preview to see an example of how the program works. The preview itself is one of the frames of the video.</i></p>

# Video in video
Have you ever dreamed of creating an image that would not consist of solid pixels, but of smaller images? Well I see your dreams strongly
are limited, because who needs images from images when this application can make videos consisting of videos? Yes, you didn't hear
you can take absolutely any video, put it into the algorithm, wait and voila!

## Principle of operation
The principle of operation is quite simple: all that is required of you is to place the processed video in the folder with the program, calling it "original.mp4", run the application, specify the desired number fps of the final video, the zoom level and the compression ratio of the processed video. The program itself is divided into 5 stages:
1. Preparatory stage. Receiving data from the user, processing the save file (more on that below).
1. Download the sound. The audio from the video is saved to a separate file for later use.
1. Saving frames. The video is split into individual frames and saved as images.
1. Processing of all frames. As a result, all frames become “pictures from pictures”.
1. Video rendering. From the available processed frames and sound, a full-fledged video is created.

## Save system
If you haven't figured it out yet, this whole 5-step program doesn't work that fast, especially in the last two steps. That's what the save system was designed for. At any stage (except for the preparatory stage), you can safely interrupt the program with your intervention, because the progress made will be saved.
It is undesirable to interrupt the program at stages with the preservation of sound and frames, since these stages pass relatively quickly. But in the processing of frames, the frame system will be useful!
This stage itself is the longest, and therefore it can be stopped at any time. The next time you run the program, it will simply continue to work from the frame where it ended. The last stage CANNOT be stopped because it is holistic.

## Technical limitations
Due to the limitations of modern screens (and for optimization, of course), the resolution of the final video is 8k (or lower). Therefore, it is advisable to process video with a resolution of 144p, or reduce the size of the video being reversed in the program itself (by the way, this will not affect the original file in any way, do not be afraid), so that in the end small videos are distinguishable and do not merge into a mess.

# Instructions for use

- Download latest version

- Replace the standard video `original.mp4` with the one you want to process, of course, replacing the new file name with `original`

- Run `main.exe` and follow the application's instructions.

- Wait. And wait. And wait a little more. If at the moment with the processing of frames you are tired of waiting,
you can artificially interrupt the program, the next time you start it, it will simply continue from where it left off

- If there is a problem with splitting video into frames, then just change the settings in the program, reducing the quality of the processed video

- After the program ends, enjoy the result, seeing how the standard Windows player cannot open the resulting video

# Instructions for running the source code
- Clone the repository

```shell
git clone https://github.com/Nytrock/VideoInVideo.git
```

- Install dependencies with requirements.txt
```shell
pip install -r requirements.txt
```

- Do the same thing you would do when working with released application
