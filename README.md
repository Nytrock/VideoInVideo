<a href="https://youtu.be/a0avir3IQL4" align="center"><img src="Logo.jpg" alt="Rickroll made up of rickrolls"></a>
<p align="center"><i>Click on the preview to see an example of how the program works. The preview itself is one of the frames of the video.</i></p>

# Video in video
Have you ever dreamed of creating an image that would not consist of solid pixels, but of smaller images? Well I see your dreams strongly
are limited, because who needs images from images when this application can make videos consisting of videos? Yes, you didn't hear
you can take absolutely any video, put it into the algorithm, wait and voila!

## Principle of operation
The principle of operation is quite simple: all that is required of you is to place the processed video in the folder with the program, naming it "original.mp4",
run the application and specify the desired number of fps of the final video. The work of the program itself is divided into 5 stages:
1. Preparatory stage. Receiving data from the user, processing the save file (about it below).
1. Upload sound. The audio from the video is saved to a separate file for later use.
1. Saving frames. The video is divided into individual frames and the save them as images.
1. Processing of all frames. As a result, all frames become "pictures from pictures".
1. Video rendering. From the available processed frames and sound, a full-fledged video is created.

## Save system
If you haven't figured it out yet, this whole 5-stage program doesn't work all that fast, especially in the last two stages. That's what it was designed for.
save system. At any stage (except for the preparatory stage), you can safely interrupt the work of the program with your intervention, because the progress made will be preserved.
It is undesirable to interrupt the program at stages with preservation of sound and frames, since, firstly, these stages go through relatively quickly, and secondly, intermediate
there are no saved results in them, so the next time they start, they will simply start over. But in the processing of frames, the frame system can oh, how useful!
This stage itself is the longest, and therefore it can be stopped at any time. At the next start, the program will simply continue from the frame where
finished. The last stage can NOT be stopped, because it is holistic.
## Technical limitations
Due to the limitations of modern screens (and for optimization, of course) the resolution format of the final image is 8k. Therefore, it is desirable to process video with
144p resolution format because even with such seemingly modest dimensions, the final video should essentially have a resolution of 20k. Unfortunately (or fortunately, who cares),
it is impossible to create a video with this resolution format, and it is not necessary, again due to screen limitations. Don't expect every little video to be
have original resolution.

## Startup instructions
- Clone the repository

```shell
git clone https://github.com/Nytrock/Video_In_Video.git
```

- Install dependencies with requirements.txt
```shell
pip install -r requirements.txt
```

- Replace the standard video `original.mp4` with the one you want to process, of cource replacing the name of the new file with `original`

- Run the program `main.py` and follow the instructions given in the program

- Wait. And wait. And wait a little more.  If at the moment with the processing of frames you are tired of waiting, 
you can artificially interrupt the program, the next time it starts, it will simply continue from where it left off

- If there is a problem with splitting the video into frames, then simply reduce the resolution of the original video

- After the program ends, enjoy the result, seeing how the standard Windows player is not able to open the final video
