"""
|
------------------------------------------------
         Video Injection PyGame - 0.0.1
------------------------------------------------
|                                   by rdmchik
|
|
|    This file isn't going to be used and
|
|    all of the logic is mainly stored in the
|
|    video.py file. Read README.md file for
|
|    more information about the library and to
|
|    find out how to use it. In this file a test
|
|    is located though
|
|
|                               -- Enjoy!
"""

if __name__ == '__main__':

    from video import VideoSurface

    import pygame


    pygame.init()
    pygame.mixer.init()

    clock = pygame.time.Clock()
    display = pygame.display.set_mode((600, 1000))

    video = VideoSurface('example.mp4', pygame.Vector2(0, 0), (400, 400))

    video.play()

    while True:

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()

        display.blit(video(), video.get_position())
        if not video.playing:
            video.play()

        pygame.display.flip()
        clock.tick(60)
    