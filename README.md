# An Image a Day

This repository is a database of desktop wallpapers, one for each day of the year.

### How do I subscribe?

1. Run `curl https://pl.ntr/an-image-a-day | bash` in your Terminal
2. Pick `Pictures/An Image a Day/Today` as the directory for your desktop wallpaper.

### How do I add new wallpapers?

The wallpaper database consists of daily records in JSON format. The file layout is hierarchical
based on the format `Wallpapers/<Channel>/<Year>/<Month>/<Day>.json`. While the JSON payloads can
be managed manually, it is recommended to use the `an-image-a-day` CLI instead.

> Check out the [Readme](an-image-a-day-cli/README.md) on the CLI for more details.

Once you added new JSON records to the Wallpapers folder, all you need to do is create a
pull request against this GitHub repository. As soon as it's merged, the wallpaper will
be automatically detected by the `an-image-a-day-downloader` script.

---

<p align="center">Copyright &copy; 2020 Niklas Rosenstein</p>
