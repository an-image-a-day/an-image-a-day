# an-image-a-day-cli

CLI to help generating wallpaper JSON records from URLs.

```
Usage: an-image-a-day [OPTIONS] COMMAND [ARGS]...

Options:
  --help  Show this message and exit.

Commands:
  resolve  Resolve a URL to a Wallpaper spec and dump it as JSON to stdout.
  save     Resolve a URL and save it as the next daily wallpaper.
```

__Supported URLs__

* [Pexels](https://pexels.com) (requires a `PEXELS_TOKEN` environment variable to be set)

__Roadmap__

* [WallpapersHome](https://wallpapershome.com/)

---

<p align="center">Copyright &copy; 2020 Niklas Rosenstein</p>
