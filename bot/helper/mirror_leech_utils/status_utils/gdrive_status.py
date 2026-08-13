# This file is a part of NEO-WZML (github.com/irisXDR/NEO-WZML)

from bot.helper.ext_utils.status_utils import (
    MirrorStatus,
    EngineStatus,
    get_readable_file_size,
    get_readable_time,
)


class GoogleDriveStatus:
    def __init__(self, listener, obj, gid, status):
        self.listener = listener
        self._obj = obj
        self._size = self.listener.size
        self._gid = gid
        self._status = status
        self.engine = EngineStatus().STATUS_GDAPI

    def processed_bytes(self):
        return get_readable_file_size(self._obj.processed_bytes)

    def size(self):
        return get_readable_file_size(self._size)

    def status(self):
        if self._status == "up":
            return MirrorStatus.STATUS_UPLOAD
        elif self._status == "dl":
            return MirrorStatus.STATUS_DOWNLOAD
        else:
            return MirrorStatus.STATUS_CLONE

    def name(self):
        return self.listener.name

    def gid(self) -> str:
        return self._gid

    def progress_raw(self):
        try:
            # Clamp to 100: processed_bytes can momentarily read higher than
            # the counted total size (e.g. a stale progress tick during a
            # multi-file folder transfer, or Drive's reported size differing
            # slightly from actual bytes written). Displaying >100% is never
            # correct, so cap it here as a safety net regardless of cause.
            return min(self._obj.processed_bytes / self._size * 100, 100)
        except ZeroDivisionError:
            return 0

    def progress(self):
        return f"{round(self.progress_raw(), 2)}%"

    def speed(self):
        return f"{get_readable_file_size(self._obj.speed)}/s"

    def eta(self):
        try:
            remaining = self._size - self._obj.processed_bytes
            if remaining <= 0 or self._obj.speed <= 0:
                return "-"
            return get_readable_time(remaining / self._obj.speed)
        except Exception:
            return "-"

    def files_progress(self):
        # Only present for a GDrive-folder streaming leech (see
        # GoogleDriveDownload._download_folder_streaming), which sets these
        # two attributes on the listener as it works through the folder one
        # file at a time. Absent for a normal file/folder task, so
        # get_readable_message()'s hasattr(task, "files_progress") check
        # skips this line for everything else.
        total = getattr(self.listener, "stream_total_files", None)
        if not total:
            return None
        done = getattr(self.listener, "stream_done_files", 0)
        return f"{done}/{total}"

    def task(self):
        return self._obj
