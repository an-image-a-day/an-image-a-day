# An Image a Day

This repository is a database of desktop wallpapers, one for each day of the year. Images are
selected manually and recorded in the `Wallpapers/` database from the following sources:

* [Pexels](https://pexels.com)

### How can I use this?

* <details><summary>Instructions for OSX</summary>

    1. Run `curl https://raw.githubusercontent.com/an-image-a-day/an-image-a-day/master/an-image-a-day-downloader/setup.sh | bash` in your Terminal
    2. Pick `Pictures/An Image a Day/Today` as the directory for your desktop wallpaper:

    <p align="center"><img src="https://user-images.githubusercontent.com/1318438/82971508-21ab1f00-9fd3-11ea-8d05-2b72340ce6d8.png"></p>

    </details>

* Other operating systems are not currently supported by the setup script.

### Can I contribute?

Yes! You can contribute wallpapers for upcoming calendar days or even create a new Wallpaper
channel. Simply create a Pull Request on this repository.

Wallpaper records are stored in the `Wallpapers/` directory following the layout
`Channel/YYYY/MM/DD.json`. While the records can be authored by hand, it is much easier
to automatically generate them with the [an-image-a-day-cli](an-image-a-day-cli).

---

<p align="center">Copyright &copy; 2020 Niklas Rosenstein</p>
