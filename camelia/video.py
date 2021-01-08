from moviepy.editor import *
from moviepy.audio.AudioClip import AudioArrayClip
from .text_assets import TextAssets

OPTIMIZED_PARAMS = {
    "square_preview": {
        "width": 400,
        "height": 400,
    },
    "square_instagram": {
        "width": 1080,
        "height": 1080,
    },
}


class MusicVideo:
    def __init__(
        self,
        song,
        path_video: str,
        artist_name: str,
        track_name: str,
        music_bpm: float,
        drop_beats=None,
        square=True,
    ):
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
        self.drop_beats = drop_beats

        if square:

            self.main_clip = self.transform_squared_size(self.main_clip, prop=0.8)

        self.intro = None

        # Song

        self.song = song
        self.audioclip = AudioArrayClip(
            self.song.waveform.reshape(-1, 2), fps=self.song.sr
        )

        # Rhythm

        self.music_bpm = music_bpm
        self.duration = 60 / self.music_bpm

        # Informations to display

        self.artist_name = artist_name
        self.track_name = track_name

        self.text_assets = TextAssets(
            self.width, self.height, self.artist_name, self.track_name, self.duration
        )

    def set_params(self, platform: str = "square_preview") -> None:
        """Set optimized params for platforms.

        :param platform: Platform for the video (instagram, twitter etc.)
        :return: None
        """

        self.width = OPTIMIZED_PARAMS.get(platform).get("width")
        self.height = OPTIMIZED_PARAMS.get(platform).get("height")

    def set_main_clip_as_loop(self, bpm_video: float = None, keep_only_one_loop=False):
        """Set the main clip as a loop video."""

        clip_duration = self.main_clip.duration

        if bpm_video:
            self.bpm_video = bpm_video
            video_loop_duration = 60 / self.bpm_video

        else:

            self.bpm_video = round(60 / clip_duration, 0)
            video_loop_duration = clip_duration

        if keep_only_one_loop:

            limit_duration = video_loop_duration

        else:

            limit_duration = (
                clip_duration // video_loop_duration
            ) * video_loop_duration

        self.main_clip = self.main_clip.set_duration(limit_duration)

        # Loop the clip
        nb_loops = self.audioclip.duration // self.main_clip.duration

        self.main_clip = self.main_clip.loop(n=nb_loops)

    def add_intro(self, path_intro):

        self.intro = VideoFileClip(path_intro, fps_source="fps")

        self.intro = self.transform_squared_size(self.intro)

        # Loop the clip
        nb_loops = self.audioclip.duration // self.intro.duration

        self.intro = self.intro.loop(n=nb_loops).set_position("center")

    def transform_squared_size(self, clip, prop=1):
        """Resize the video."""

        # Resize
        clip = clip.crop(
            x_center=int(clip.w / 2),
            y_center=int(clip.h / 2),
            width=min(clip.w, clip.h),
            height=min(clip.w, clip.h),
        )

        clip = clip.resize((self.width, self.height)).resize(prop)

        return clip

    def sync_bpm_clip(self, clip, exact_loop=False):
        """Sync the video with the music."""

        if exact_loop:
            factor = self.music_bpm / self.bpm_video
        else:
            loops = self.music_bpm // self.bpm_video
            factor = self.music_bpm / (self.bpm_video * loops)

        clip = clip.speedx(factor=factor)

        return clip

    def gen_txt_assets(self, prop_screen=0.4):
        """Generate text assets.
        :param prop_screen: Set the size of the text"""

        textwidth = prop_screen * self.width
        txt_start = 0
        txt_duration = self.duration * 4

        self.txtClip_artist = TextClip(
            self.artist_name,
            color="white",
            font="Helvetica",
            kerning=5,
            size=(textwidth, None),
        )

        self.txtClip_track = TextClip(
            self.track_name,
            color="LightPink",
            font="Helvetica-bold",
            kerning=5,
            size=(textwidth, None),
        )

        txt_artist_pos = (self.width / 2 - self.txtClip_artist.w / 2, 0.1 * self.height)
        txt_track_pos = (self.width / 2 - self.txtClip_track.w / 2, 0.25 * self.height)

        # Position

        self.txtClip_artist = (
            self.txtClip_artist.set_pos(txt_artist_pos)
            .set_start(txt_start)
            .set_duration(txt_duration)
        )

        self.txtClip_track = (
            self.txtClip_track.set_pos(txt_track_pos)
            .set_start(txt_start)
            .set_duration(txt_duration)
        )

    def generate_video(self, cut=None):
        """Generate final video.

        :param cut: Truncate the video (in seconds)
        """

        clips = []

        # Intro

        if self.intro:

            clips.append(self.intro)

        # Drop

        if self.drop_beats:

            self.main_clip = self.main_clip.set_start(
                (self.drop_beats) * self.duration, change_end=False
            )

        # Main clip

        clips.append(self.main_clip.set_position("center"))

        # Text

        if self.text_assets.text_clips:

            for txt_clip in self.text_assets.text_clips:
                clips.append(txt_clip)

        video = CompositeVideoClip(clips)

        video = video.set_audio(self.audioclip)

        # Cut de la video

        if cut:

            video = video.subclip(0, cut)

        return video
