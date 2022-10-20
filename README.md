```nnnn  nnnnnnnn      aaaaaaaaaaaaa  ppppp   ppppppppp       ssssssssss   
n:::nn::::::::nn    a::::::::::::a p::::ppp:::::::::p    ss::::::::::s  
n::::::::::::::nn   aaaaaaaaa:::::ap:::::::::::::::::p ss:::::::::::::s 
nn:::::::::::::::n           a::::app::::::ppppp::::::ps::::::ssss:::::s
  n:::::nnnn:::::n    aaaaaaa:::::a p:::::p     p:::::p s:::::s  ssssss 
  n::::n    n::::n  aa::::::::::::a p:::::p     p:::::p   s::::::s      
  n::::n    n::::n a::::aaaa::::::a p:::::p     p:::::p      s::::::s   
  n::::n    n::::na::::a    a:::::a p:::::p    p::::::pssssss   s:::::s 
  n::::n    n::::na::::a    a:::::a p:::::ppppp:::::::ps:::::ssss::::::s
  n::::n    n::::na:::::aaaa::::::a p::::::::::::::::p s::::::::::::::s 
  n::::n    n::::n a::::::::::aa:::ap::::::::::::::pp   s:::::::::::ss  
  nnnnnn    nnnnnn  aaaaaaaaaa  aaaap::::::pppppppp      sssssssssss    
                                    p:::::p                             
                                    p:::::p                             
                                   p:::::::p                            
                                   p:::::::p                            
                                   p:::::::p                            
                                   ppppppppp    

Navidrome                          Playlist            Syncer
```
Simple tool made for creating and updating local copies of playlists from [Navidrome](https://www.navidrome.org/).
# Prerequisites
- [Python 3](https://www.python.org/downloads/)
- [PyYAML](https://pyyaml.org/) (`pip install PyYAML`)
- [requests](https://requests.readthedocs.io/en/latest/) (`pip install requests`)

# Installation

Download the files
- Clone the repo:
```
git clone https://github.com/PokerFacowaty/naps
```
- ... or simply download `naps.py` and `config.yaml` and store them in the same directory

# Configuration
## config.yaml
- Open `config.yaml`
- By default, the file will look like this:
```yaml
# Docs: https://github.com/PokerFacowaty/naps
api_version: 1.16.1
user:
encoded_password:
salt:
link:
musicfolder_name: /music
local_musicfolder:
playlist_dir:
device_id:
custom_filenames:
  #Playlist name: My_custom_filename.m3u8
```
Explanations for all config entries:
- `api_version:` - the API version used by the server, `1.16.1` is there by default, as [it is used by Navidrome at the time of writing](https://www.navidrome.org/docs/developers/subsonic-api/)
- `user:` - put in your Navidrome's account username
- `encoded_password:` - Subsonic API uses MD5 + salt encrypting method, encode your password using a generator that puts the salt **after** the password like [randommer.io](https://randommer.io/Hash/MD5) and paste the resulting hash here
- `salt:` - salt used for the MD5 encryption
- `link:` - full link to your Navidrome instance, ex. `https://navidrome.example.com`
- `musicfolder_name: /music` - the name of the directory used by Navidrome to store music. If you haven't specifically changed the [ND_MUSICFOLDER](https://www.navidrome.org/docs/usage/configuration-options/) variable at any time when configuring Navidrome and you're running it on a Linux (or other POSIX system) server, leave it at the default `/music`.
  - You can easily check your ND_MUSICFOLDER by opening any song's details in Navidrome's UI - [screenshot](https://i.imgur.com/TXFVuJf.png)
  - If you're changing the default, make sure your directory has a slash at the start and no slash at the end
- `local_musicfolder:` - an absolute path to ND_MUSICFOLDER's local equivalent, ex. `/home/pokerfacowaty/Music`, `C:\Music`
- `playlist_dir:` - an absolute path to the directory containing your local playlists, ex. `/home/pokerfacowaty/Playlists`, `C:\Playlists`
- `device_id:` - a name for the current device using the API, ex. `MyPC`
- `custom_filenames:` - normally, every playlist downloaded from Navidrome with naps will be named (playlist name).m3u8, here you can list any exceptions you'd like to add to that rule, the commented out example `#Playlist name: My_custom_filename.m3u8` is provided to let you know how to write these exceptions

## Inital connection
Use the command line to start naps with the `-i` flag when in the same directory:
```
python naps.py -i
```
(or if you have Python 2 installed)
```
python3 naps.py -i
```

If no errors were shown and the `"Initial connection successful."` message appears, you've just succesfully connected for the first time. Open your Navidrome UI, open the [Players page from the dropdown in the top-right corner](https://i.imgur.com/ETP0Y1L.png), choose the player with the ID you put in `device_id` and switch the [Report Real Path option](https://i.imgur.com/p7bDy2J.png) on. This ensures naps will receive actual filepaths for the requested songs.

# Usage
To use naps, simply start it when in the same directory:

```
python naps.py
```
(or if you have Python 2 installed)
```
python3 naps.py
```

## Arguments
- `-h, --help` - show help
- `-i` - initial connection
- `-c, --config <file>` - use a custom config file
- `--include-from <file>` - provide a text file with names of all the playlists that should be included in the sync (rclone-style)
- `--exclude-from <file>` - provide a text file with names of all the playlists that should be excluded in the sync (rclone-style)

If you wish to perform syncing periodically, use a program such as cron.

# FAQ
- Q: Is naps compatible with other Subsonic-compatible apps?
- A: The main difference between Navidrome and ex. Airsonic is that [Navidrome is hard-coded to only support a single music folder](https://www.navidrome.org/docs/developers/subsonic-api/). I don't see a way of supporting multiple different direcotries (especially within the same playlist) without pretty much rewriting naps. Single directory on apps allowing multiple ones *might* be supported, though it is untested at this point. I might get around to it in the future. You are more than welcome to submit a PR if you figured out the support for another Subsonic-compatible app.

- Q: Can I use naps between Windows and Linux?
- A: naps should be fully compatible with different filesystems, though I myself have only tested Windows and Linux clients on a Linux server.

- Q: Where did the name come from?
- A: I didn't have any special idea for the name (aside from liking recursive acronyms like GNU), so I filtered 400k+ English words for ones that had 'n' for 'Navidrome' and 'ps' for 'playlist syncer' in them and 'naps' was among them.

# Thanks to
- [andrzej](https://blog.andr.host/) for the code review and tips