import logging
import os
import shlex
import subprocess
import time

import pykka
from mopidy import core

logger = logging.getLogger(__name__)


class FMFrontend(pykka.ThreadingActor, core.CoreListener):
    def __init__(self, config, core):
        super(FMFrontend, self).__init__()
        self.core = core
        self.config = config

    # Your frontend implementation
    def on_start(self):
        logger.info("FM Addon started...")
        try:
            # delete old contents of the pipe
            os.remove("/tmp/rds_ctl")
        except FileNotFoundError:
            # the file does not exist
            pass
        try:
            os.mkfifo("/tmp/rds_ctl")
        except FileExistsError:
            # the file already exists
            logging.debug("%s already exists while starting", "/tmp/rds_ctl")

        # commandline = "sox -n -r 16000 -c 1 -t wav - |"
        # " sudo pi_fm_adv --ctl /tmp/rds_ctl --audio -"
        commandline = "tail -F /tmp/rds_ctl"
        args = shlex.split(commandline)
        logger.info(args)
        subprocess.Popen(commandline, shell=True)

        with open("/tmp/rds_ctl", "w") as fp:
            try:
                fp.write("RT Pirate started!\n")
            except OSError:
                logger.warning("pifm Pipe has been closed!")
            finally:
                fp.close()

    def on_stop(self):
        logger.info("FM Addon stopped...")
        try:
            # delete old contents of the pipe
            os.remove("/tmp/rds_ctl")
        except FileNotFoundError:
            # the file does not exist
            pass

    def track_playback_started(self, tl_track):
        track = tl_track.track
        artists = ", ".join(sorted([a.name for a in track.artists]))
        duration = track.length and track.length // 1000 or 0
        self.last_start_time = int(time.time())
        logger.info(f"Now playing track: {artists} - {track.name}")
        track = track.name or ""
        # album=((track.album or "") and (track.album.name or ""))
        duration = str(duration)
        with open("/tmp/rds_ctl", "w") as fp:
            try:
                fp.write(f"RT {artists} - {track}\n")
            except OSError:
                logger.warning("pifm Pipe has been closed!")
            finally:
                fp.close()

    def track_playback_ended(self, tl_track, time_position):
        track = tl_track.track
        artists = ", ".join(sorted([a.name for a in track.artists]))
        duration = track.length and track.length // 1000 or 0
        time_position = time_position // 1000
        if duration < 30:
            logger.debug("Track too short to scrobble. (30s)")
            return
        if time_position < duration // 2 and time_position < 240:
            logger.debug(
                "Track not played long enough to scrobble. (50% or 240s)"
            )
            return
        if self.last_start_time is None:
            self.last_start_time = int(time.time()) - duration
        logger.debug(f"Scrobbling track: {artists} - {track.name}")
        with open("/tmp/rds_ctl", "w") as fp:
            try:
                fp.write("RT Pause\n")
            except OSError:
                logger.warning("pifm Pipe has been closed!")
            finally:
                fp.close()
