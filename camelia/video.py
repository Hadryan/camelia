from moviepy.editor import *
from moviepy.audio.AudioClip import AudioArrayClip
from .text_assets import TextAssets
import math

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

        self.background_clips = []

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
            self.width,
            self.height,
            self.artist_name,
            self.track_name,
            self.duration,
            self.drop_beats,
        )

    def set_params(self, platform: str = "square_preview") -> None:
        """Set optimized params for platforms.

        :param platform: Platform for the video (instagram, twitter etc.)
        :return: None
        """

        self.width = OPTIMIZED_PARAMS.get(platform).get("width")
        self.height = OPTIMIZED_PARAMS.get(platform).get("height")

    def loop_clip(self, clip, bpm_video: float = None, crossfadein: float = None):
        """Loop main clip.

        So far the clip is looped for the whole video and then starts late

        :param bpm_video: BPM of the video
        :param crossfade: Duration of the crossfadein (in % of loops), if negative then the clip starts before the drop
        :param early_crossfadein:"""

        clip_duration = clip.duration
        start_offset = 0

        # Fadein

        if crossfadein:

            # We only want an offset when it's negative
            start_offset = min(crossfadein * clip_duration, 0)

        # Loop the clip
        nb_loops = (self.audioclip.duration // clip.duration) + 1

        clip = clip.loop(n=nb_loops).crossfadein(abs(crossfadein))

        # Drop

        if self.drop_beats:

            start = max((self.drop_beats) * self.duration - start_offset, 0)

            clip = clip.set_start(start, change_end=False)

        return clip

    def add_background_clip(self, path, sync=False):
        """Add background clips.

        :param path: Path to the background clip
        """

        clip = VideoFileClip(path, fps_source="fps")

        clip = self.transform_squared_size(clip)

        if sync:

            clip = self.sync_bpm_clip(clip)

        # Loop the clip
        nb_loops = (self.audioclip.duration // clip.duration) + 1

        clip = clip.loop(n=nb_loops).set_position("center")

        self.background_clips.append(clip)

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

    def sync_bpm_clip(self, clip, bpm_video=None, exact_loop=False):
        """Sync the video with the music."""

        # If the BPM of the video is known we might have to truncate it
        if bpm_video:
            video_loop_duration = 60 / bpm_video

        # Otherwise we assume it's a perfect loop
        else:
            bpm_video = round(60 / clip.duration, 0)
            video_loop_duration = clip.duration

        limit_duration = (clip.duration // video_loop_duration) * video_loop_duration

        clip = clip.set_duration(limit_duration)

        # Number of loops to fit with the smallest BPM unity of the music

        loops = self.music_bpm // bpm_video

        # Factor to adjust speed
        factor = self.music_bpm / (bpm_video * loops)

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

        # Background clips

        for clip in self.background_clips:

            clips.append(clip)

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
