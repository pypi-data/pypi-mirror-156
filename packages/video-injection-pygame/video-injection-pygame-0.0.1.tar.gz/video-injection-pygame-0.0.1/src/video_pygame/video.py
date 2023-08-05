from utils.data_control import DataControl

from moviepy.editor import *

import pygame
import glob
import time
import cv2


class VideoSurface(object):
    """
    video surface class (only mp4)

    video_path example: 'static\\video_example.mp4'
    """

    def __init__(self, video_path: str, position: pygame.Vector2, size: tuple) -> None:

        self._video_path = video_path
        
        self.position = position
        self.size = size

        self._current_frame_index = 0
        self._current_frame = None

        self.sound = None

        self._folder_path = None

        self._total_frames = 0

        self.playing = False

        self.visible = True

        self._FPS = 0
        self._frameGap = 0

        self._frame_times = []

        try:
            self.__init()
        except Exception:
            raise Exception('An uknown error occurred while making video surface initialization')
            

    def play(self) -> None:
        """
        play the video
        """

        self.playing = True
        self.sound.play()

    def stop(self) -> None:
        """
        stop and restart the video
        """

        self.playing = False
        self._current_frame_index = 0
        self.sound.stop()

    def get_position(self) -> list:
        """
        get current video position
        """

        return [self.position.x, self.position.y]

    def __set_total_count(self) -> int:

        if not self._video_path.endswith('.mp4'):
            raise Exception('for a video surface a .mp4 file required, got %s instead' % self._video_path)

        self._folder_path = DataControl.create_folder(self._video_path.split('\\')[-1][:-4])

        vidcap = cv2.VideoCapture(self._video_path)
        self._FPS = int(vidcap.get(cv2.CAP_PROP_FPS))

        success, image = vidcap.read()
        count = 0

        while success:
            
            count += 1

            success, _ = vidcap.read()

        self._total_frames = count

    def __init(self) -> None:
        """
        a setup for the video surface object, first 
        initialization might take some time
        """

        if not self._video_path.endswith('.mp4'):
            raise Exception('for a video surface a .mp4 file required, got %s instead' % self._video_path)

        self.__set_total_count()

        self._folder_path = DataControl.create_folder(self._video_path.split('\\')[-1][:-4])

        create_new = True

        if not DataControl.folder_is_empty(self._folder_path):
            create_new = False 

        sound = AudioFileClip(self._video_path)
        sound.write_audiofile(self._folder_path + '\\audio.wav', 44100, 2, 2000, "pcm_s32le")
        self.sound = pygame.mixer.Sound(self._folder_path + '\\audio.wav')

        vidcap = cv2.VideoCapture(self._video_path)
        success, image = vidcap.read()
        count = 0

        while success:
            
            count += 1

            if create_new:
                cv2.imwrite(self._folder_path + '\\frame%s.jpg' % count, image)

            success, image = vidcap.read()

            if create_new:
                if count < self._total_frames:
                    success = True
            
        if self.__folder_corrupted():
            DataControl.clear_folder(self._folder_path)
            self.__init()

    def __folder_corrupted(self) -> bool:
        """
        check if video surface's folder is corrupted
        """

        last_count = 1
        for path in glob.glob(self._folder_path + '\\*'):
            if not path.endswith('.jpg'):
                continue
            count = int(path.split('\\')[-1][5:][:-4])
            if count > last_count:
                last_count = count

        if last_count != self._total_frames:
            return True

        return False

    def __load_current_frame(self) -> None:
        """
        change current image to correct one
        """
        
        image_path = self._folder_path + '\\frame%s.jpg' % self._current_frame_index
        
        image = pygame.image.load(image_path)
        image = pygame.transform.scale(image, self.size)

        self._current_frame = image

    def __update(self) -> None:
        """
        update this object
        """

        if self._current_frame_index == 0:
            self._frameGap = 1 / self._FPS
            self._current_frame_index += 1

            for i in range(self._total_frames):
                i += 1
                self._frame_times.append(time.time() + i * self._frameGap)

        if self.playing:
            is_bigger = True
            # synchronization of frame and audio
            while is_bigger:
                if len(self._frame_times) == 0:
                    is_bigger = False
                    self.stop()
                    return
                if time.time() < self._frame_times[0]:
                    is_bigger = False
                else:
                    self._current_frame_index += 1
                    self._frame_times.pop(0)
            if self._current_frame_index > self._total_frames:
                self.stop()
                return
        
        self.__load_current_frame()

    def __call__(self) -> pygame.Surface:
        """
        get current frame by calling the object
        """

        self.__update()
        return self._current_frame


        
