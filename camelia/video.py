from moviepy.editor import *
from moviepy.audio.AudioClip import AudioArrayClip
import os

OPTIMIZED_PARAMS = {
    'instagram':{
        'width':1080,
        'height':1080,
    }
}

class MusicVideo:
    def __init__(self,song,path_video:str,artist_name:str,track_name:str,music_bpm:float,square=True):
        """Generic video object.
        This class contains all parameters common to all styles of videos to be generated.

        :param song: Song
        :param artist_name: Artist name
        :param track_name: Track name
        :param music_bpm: BPM of the music
        :param square: Set the size of the clip as "square"
        """

        # Size

        self.width = None
        self.height = None

        self.set_params()

        # Video

        self.main_clip = VideoFileClip(path_video, fps_source="fps")
        self.bpm_video = None

        if square:

            self.set_main_clip_squared_size()

        # Song

        self.song = song
        self.audioclip = AudioArrayClip(self.song.waveform, fps=self.song.sr)

        # Rhythm

        self.music_bpm = music_bpm
        self.duration = 60 / self.music_bpm

        # Informations to display

        self.artist_name = artist_name
        self.track_name = track_name

        self.textwidth = 0.2 * self.width
        self.textheight = 0.2 * self.height

    def set_params(self,platform:str='instagram')-> None:
        """Set optimized params for platforms.

        :param platform: Platform for the video (instagram, twitter etc.)
        :return: None
        """

        self.width = OPTIMIZED_PARAMS.get(platform).get('width')
        self.height = OPTIMIZED_PARAMS.get(platform).get('height')

    def set_main_clip_as_loop(self,bpm_video:float):
        """Set the main clip as a loop video.
        """

        self.bpm_video = bpm_video

        clip_duration = self.main_clip.duration

        limit_duration = (clip_duration // (60 / self.bpm_video)) * (60 / self.bpm_video)

        self.main_clip = self.main_clip.set_duration(limit_duration)

    def set_main_clip_squared_size(self):
        """Resize the video.
        """

        # Resize
        self.main_clip = self.main_clip.crop(x_center=int(self.main_clip.w / 2),
                        y_center=int(self.main_clip.h / 2),
                        width=min(self.main_clip.w, self.main_clip.h),
                        height=min(self.main_clip.w, self.main_clip.h))




    def gen_txt_assets():

        txtClip_artist = TextClip(artist_name,
                          color='white',
                          font="Helvetica",
                          kerning=5,
                          size=(textwidth, None))

        txtClip_track = TextClip(track_name,
                                color='LightPink',
                                font="Helvetica-bold",
                                kerning=5,
                                size=(textwidth, None))
