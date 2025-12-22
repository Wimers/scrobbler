import os
from datetime import datetime

DEFAULT_FILEPATH: str = 'D:\\.scrobbler.log'
HEADER = [
    '#AUDIOSCROBBLER/1.1\n',
    '#TZ/\n',
    '#CLIENT/Rockbox ipodvideo $Revision$\n',
]

# Default parameters
UPDATE_TS_PATH: str = 'D:\\.scrobbler_update.log'
DEFAULT_LOCAL_TZ: str = 'UTC+10'


def verify_log(filename: str) -> None:
    '''
    Verifies file timestamp integrity.

    Example:
        If a track has a timestamp less than that of
        a track logged before, an error has occured.
    '''
    ts = float('-inf')
    with open(filename, 'r') as f:
        for i, line in enumerate(f):
            if i < len(HEADER):
                continue
            prev = ts
            ts = int(line.split('\t')[-2])
            if prev > ts:
                # FIX CLARITY
                print(f"Error detected: Line {i + 1}\n{line}")
                return
        print('No errors detected')


def clear_scrobble_log() -> None:
    ''' Clears .scrobbler.log to original state with Header '''
    with open(DEFAULT_FILEPATH, 'w') as file:
        file.writelines(HEADER)


def global_offset(filename: str) -> int:
    '''
    If iPod goes flat, battery will reset the clock, to scrobble songs
    played during this time each timestamp is adjusted by determining
    the difference between the real time in UTC, and the time of iPod

    time: current time in utc timestamp format
    '''
    with open(filename, 'r') as f:
        last_scrobble = f.readlines()[-1]
        file_timestamp = int(last_scrobble.split('\t')[-2])
        global_offset = int(datetime.now().timestamp()) - timezone_adjust(
            file_timestamp,
            DEFAULT_LOCAL_TZ,
        )
    return global_offset


def update_ts(filename: str, offset: int) -> None:
    ''' Offsets each timestamp by a given contant value '''
    updated_filename = UPDATE_TS_PATH
    if os.path.exists(updated_filename):
        os.remove(updated_filename)

    with open(updated_filename, 'a') as updated:
        with open(filename, 'r') as f:
            for i, line in enumerate(f):
                if (i < len(HEADER)):
                    updated.write(line)
                    continue
                ts = int(line.split('\t')[-2])
                updated_ts = ts + offset
                updated_line = (
                    '\t'.join(line.split('\t')[:-2] + [str(updated_ts), '\n'])
                )
                updated.write(updated_line)


def fix_file(filename: str) -> None:
    '''
    Adjusts each timestamp in a specifed file
    based on the timezone and required offset.
    '''
    offset = global_offset(filename)
    update_ts(filename, offset)


def ts_to_time(timestamp: int) -> None:
    ''' Converts timestamp to human readable time '''
    dt = datetime.fromtimestamp(timestamp)
    return dt


def timezone_adjust(timestamp: str, timezone: str) -> int:
    ''' Adjusts timestamps to UTC from local timezone '''
    delta_ts = int(timezone[3:]) * 3600
    adjusted_ts = int(timestamp) - delta_ts
    return adjusted_ts
