from moviepy.editor import *
from moviepy.audio.AudioClip import AudioArrayClip

OPTIMIZED_PARAMS = {
    "instagram": {
        "width": 1080,
        "height": 1080,
    }
}


class MusicVideo:
    def __init__(
        self,
        song,
        path_video: str,
        artist_name: str,
        track_name: str,
        music_bpm: float,
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

        self.txtClip_artist = None
        self.txtClip_track = None

    def set_params(self, platform: str = "instagram") -> None:
        """Set optimized params for platforms.

        :param platform: Platform for the video (instagram, twitter etc.)
        :return: None
        """

        self.width = OPTIMIZED_PARAMS.get(platform).get("width")
        self.height = OPTIMIZED_PARAMS.get(platform).get("height")

    def set_main_clip_as_loop(self, bpm_video: float, keep_only_one_loop=False):
        """Set the main clip as a loop video."""

        self.bpm_video = bpm_video

        clip_duration = self.main_clip.duration

        video_loop_duration = 60 / self.bpm_video

        if keep_only_one_loop:

            limit_duration = (
                clip_duration // video_loop_duration
            ) * video_loop_duration

        else:

            limit_duration = (
                clip_duration // video_loop_duration
            ) * video_loop_duration

        self.main_clip = self.main_clip.set_duration(limit_duration)

    def set_main_clip_squared_size(self):
        """Resize the video."""

        # Resize
        self.main_clip = self.main_clip.crop(
            x_center=int(self.main_clip.w / 2),
            y_center=int(self.main_clip.h / 2),
            width=min(self.main_clip.w, self.main_clip.h),
            height=min(self.main_clip.w, self.main_clip.h),
        )

        self.main_clip = self.main_clip.resize((self.width, self.height)).resize(1)

    def sync_bpm_clip(self):
        """Sync the video with the music."""
        self.main_clip = self.main_clip.speedx(factor=self.music_bpm / self.bpm_video)

    def gen_txt_assets(self):
        """Generate text assets."""

        textwidth = 0.2 * self.width
        textheight = 0.2 * self.height

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

        # Say that you want it to appear 10s at the center of the screen
        self.txtClip_artist = (
            self.txtClip_artist.set_pos(
                (self.width / 2 - self.txtClip_artist.w / 2, 0.1 * self.height)
            )
            .set_start(self.duration * 2)
            .set_duration(self.duration * 4)
        )

        # Say that you want it to appear 10s at the center of the screen
        self.txtClip_track = (
            self.txtClip_track.set_pos(
                (self.width / 2 - self.txtClip_track.w / 2, 0.25 * self.height)
            )
            .set_start(self.duration * 2)
            .set_duration(self.duration * 4)
        )

    def generate_video(self, cut=None):
        """Generate final video.

        :param cut: Truncate the video (in seconds)
        """

        # Overlay the text clip on the first video clip
        video = CompositeVideoClip(
            [
                self.main_clip.set_position("center"),
                self.txtClip_artist,
                self.txtClip_track,
            ]
        )

        video = video.set_audio(self.audioclip)

        # Cut de la video

        if cut:
            video = video.subclip(0, cut)

        return video
