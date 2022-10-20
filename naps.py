import sys
import yaml
import requests
import pathlib
import getopt
from urllib.parse import urljoin


class SrvPlaylist:

    def __init__(self, playlist_id, name):
        self.playlist_id = playlist_id
        self.name = name
        filename = name + '.m3u8'
        if custom_filenames is not None and name in custom_filenames.keys():
            self.file = pl_path / custom_filenames[name]
        else:
            self.file = pl_path / filename
        self.song_paths = []


class LocalPlaylist:

    def __init__(self, file):
        self.file = file
        self.song_paths = []


def test_connection(link, parameters):
    try:
        test_ping = requests.get(link + "ping", params=parameters)
    except Exception:
        raise Exception('Test connection failed, check the config')

    if test_ping.json()['subsonic-response']['status'] == 'failed':
        raise Exception(test_ping.json()['subsonic-response']['error']
                        ['message'])


def fetch_included_playlists(include_file):
    with open(include_file, 'r', encoding='utf-8') as f:
        included = [x.rstrip() for x in f.read().splitlines()]
    return included


def fetch_excluded_playlists(exclude_file):
    with open(exclude_file, 'r', encoding='utf-8') as f:
        excluded = [x.rstrip() for x in f.read().splitlines()]
    return excluded


def fetch_srv_playlists(link, parameters, srv_system, musicfolder,
                        nd_musicfolder, included, excluded):
    '''Fetches all playlists available on the server and, if they are included
    or not excluded, stores them as objects, then appends the song_paths with
    a full local path of the song.'''

    getPlaylists = requests.get(link + "getPlaylists", params=parameters)
    srv_playlists = []
    print("Fetching server playlists...")
    for pl in (getPlaylists.json()['subsonic-response']['playlists']
               ['playlist']):
        if included is not None and pl['name'] in included:
            srv_playlists.append(SrvPlaylist(pl['id'], pl['name']))
        elif excluded is not None and pl['name'] not in excluded:
            srv_playlists.append(SrvPlaylist(pl['id'], pl['name']))
        elif included is None and excluded is None:
            srv_playlists.append(SrvPlaylist(pl['id'], pl['name']))

    for pl in srv_playlists:
        parameters['id'] = pl.playlist_id
        getPlaylist = requests.get(link + "getPlaylist", params=parameters)
        for song in (getPlaylist.json()['subsonic-response']['playlist']
                     ['entry']):
            if srv_system == 'posix':
                relative_song_path = (pathlib.PurePosixPath(song['path'])
                                      .relative_to(nd_musicfolder))
            elif srv_system == 'dos':
                relative_song_path = (pathlib.PureWindowsPath(song['path'])
                                      .relative_to(nd_musicfolder))
            pl.song_paths.append(str(musicfolder / relative_song_path))
    return srv_playlists


def fetch_local_playlists(pl_path):
    '''Makes a list of all local playlists as objects.'''

    local_playlists = []
    local_files = list(pathlib.Path(pl_path).glob('*.m3u8'))
    print("Loading local playlists...\n")

    for path in local_files:
        local_playlists.append(LocalPlaylist(path))

    for pl in local_playlists:
        with open(pl.file, 'r', encoding='utf-8') as f:
            pl.song_paths = [x for x in f.read().splitlines()
                             if not x.startswith('#')]
    return local_playlists


def pl_to_make_and_update(srv_playlists, local_playlists):
    '''Determines which playlists are to be created or updated and which ones
    are to be left alone, since they're identical to the server's equivalent.
    Playlists are compared literally, which leaves room for omptimization such
    as comparing just the number of elements.'''

    local_files = [x.file for x in local_playlists]
    to_make = []
    to_update = []
    for pl in srv_playlists:
        if pl.file not in local_files:
            to_make.append(pl)
        else:
            with open(pl.file, 'r', encoding='utf-8') as f:
                if f.read().splitlines() != pl.song_paths:
                    to_update.append(pl)
    print(f"Playlists to be made: {len(to_make)}")
    print(f"Playlist to be updated: {len(to_update)}\n")
    return to_make, to_update


def make_new_local(to_make):
    for pl in to_make:
        with open(pl.file, 'w', encoding='utf-8') as f:
            f.write('\n'.join(pl.song_paths))
    print("All new playlists made!")


def update_local(to_update):
    for pl in to_update:
        with open(pl.file, 'w', encoding='utf-8') as f:
            f.write('\n'.join(pl.song_paths))
    print("All existing playlists updated!")


def main():
    initial = False
    config_file = 'config.yaml'
    include_file = None
    exclude_file = None
    opts, args = getopt.getopt(sys.argv[1:], "hic:", ["help", "config=",
                                                      "include-from=",
                                                      "exclude-from="])

    for opt, arg in opts:
        if opt in ['-h', '--help']:
            print("\nnaps - [Na]vidrome [P]laylist [S]yncer",
                  "\nUsage: naps.py (-i for initial connection)",
                  "\n[-h, --help] - open this prompt",
                  "\n[-i] - initial connection",
                  "\n[--include-from] - provide a text file with names of all",
                  "playlists that should be included",
                  "\n[--exclude-from] - provide a text file with names of all",
                  "playlists that should be excluded",
                  "\nDocs: https://github.com/PokerFacowaty/naps\n")
            return
        elif opt in ['-i']:
            initial = True
        elif opt in ['-c', '--config']:
            config_file = arg
            print(f"Custom config file {arg} loaded.")
        elif opt in ['--include-from']:
            include_file = arg
        elif opt in ['--exclude-from']:
            exclude_file = arg

    config = yaml.safe_load(open(config_file))

    global custom_filenames
    global pl_path
    custom_filenames = config["custom_filenames"]
    pl_path = pathlib.Path(config["playlist_dir"])

    parameters = {
        "u": config["user"],
        "t": config["encoded_password"],
        "s": config["salt"],
        "v": config["api_version"],
        "c": config["device_id"],
        "f": "json"
    }

    link = urljoin(config["link"], 'rest/')
    musicfolder = pathlib.Path(config["local_musicfolder"])

    # This is done so that .relative_to works properly in fetch_srv_playlists
    if config["musicfolder_name"].startswith('/'):
        nd_musicfolder = pathlib.PurePosixPath(config["musicfolder_name"])
        srv_system = 'posix'
    elif config["musicfolder_name"].startswith('\\'):
        nd_musicfolder = pathlib.PureWindowsPath(config["musicfolder_name"])
        srv_system = 'dos'

    if initial:
        test_connection(link, parameters)
        print("Initial connection successful.")
        return

    if include_file is not None and exclude_file is not None:
        print("Do not use --include-from and --exclude-from simultaneously")
        return

    if include_file is not None:
        included = fetch_included_playlists(include_file)
    else:
        included = None

    if exclude_file is not None:
        excluded = fetch_excluded_playlists(exclude_file)
    else:
        excluded = None

    test_connection(link, parameters)
    srv_playlists = fetch_srv_playlists(link, parameters, srv_system,
                                        musicfolder, nd_musicfolder, included,
                                        excluded)
    local_playlists = fetch_local_playlists(pl_path)
    to_make, to_update = pl_to_make_and_update(srv_playlists, local_playlists)
    if to_make:
        make_new_local(to_make)
    if to_update:
        update_local(to_update)


if __name__ == "__main__":
    main()
