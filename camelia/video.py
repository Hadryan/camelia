from moviepy.audio.AudioClip import AudioArrayClip

OPTIMIZED_PARAMS = {
    'instagram':{
        'width':1080,
        'height':1080,
    }
}

class Video:
    def __init__(self,song,artist_name:str,track_name:str,music_bpm:float):
        """Generic video object.
        This class contains all parameters common to all styles of videos to be generated.

        :param song: Song
        :param artist_name: Artist name
        :param track_name: Track name
        :param music_bpm: BPM of the music
        """

        # Size

        self.width = None
        self.height = None
        self.set_params()

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


class LoopVideo(Video):

    def __init__(self,song,artist_name,track_name,music_bpm,video_bpm):

        super().__init__(song,artist_name,track_name,music_bpm)

        # Rhythm
        
        self.video_bpm = video_bpm




def squared_size(clip):
    """Resize the video.
    """

    # Resize
    clip = clip.crop(x_center=int(clip.w / 2),
                     y_center=int(clip.h / 2),
                     width=min(clip.w, clip.h),
                     height=min(clip.w, clip.h))

    return (clip)