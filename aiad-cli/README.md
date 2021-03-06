# aiad-cli

CLI to help generating wallpaper JSON records from URLs.

__Synopsis__

```
Usage: aiad-cli [OPTIONS] COMMAND [ARGS]...

Options:
  --help  Show this message and exit.

Commands:
  resolve  Resolve a URL to a Wallpaper spec and dump it as JSON to stdout.
  save     Resolve a URL and save it as the next daily wallpaper.
```

### Installation & Usage

Clone the repository

    $ git clone https://github.com/an-image-a-day/an-image-a-day
    $ cd an-image-a-day

Create a Python 3 virtual environment:

    $ python3 -m venv .venv
    $ . .venv/bin/activate

Install the CLI into that environment:

    $ pip install -e ./aiad-cli

Use the CLI from the project root directory to save wallpaper specs into the database:

    $ aiad-cli save https://www.pexels.com/photo/4k-wallpaper-android-wallpaper-astro-astrology-1146134/ \
        --keywords sky,night,stars

### Supported URLs

| Site | Status | Notes |
| ---- | ------ | ----- |
| [Pexels](https://pexels.com) | Complete | Expects a `PEXELS_TOKEN` environment variable. |
| [Unsplash](https://unsplash.com) | Complete | Expects a `UNSPLASH_ACCESS_KEY` environment variable. |
| [WallpapersHome](https://wallpapershome.com/) | Complete | |
| [DeviantArt](https://www.deviantart.com/) | Planned | |
| [ArtStation](https://www.artstation.com/) | Planned | |

---

<p align="center">Copyright &copy; 2020 Niklas Rosenstein</p>
