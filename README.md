# An Image a Day

This repository is a database of desktop wallpapers, one for each day of the year. The images are
curated manually from one of the below sources and recorded in JSON format in the `Wallpapers/`
directory. 

* [Pexels](https://www.pexels.com/)
* [WallpapersHome](https://wallpapershome.com/)

## Getting started

We currently target OSX as the main platform. Mac users can run the following in the Terminal
to perform a full installation of all dependencies (this includes Homebrew and various brew
packages).

```
curl https://raw.githubusercontent.com/an-image-a-day/an-image-a-day/master/aiad-downloader/setup.sh | bash
```

The daily image will be available in the `Home > Pictures > An Image a Day > Today` directory
and should be set as the source for your desktop wallpaper on every desktop.

<p align="center"><img src="https://user-images.githubusercontent.com/1318438/82971508-21ab1f00-9fd3-11ea-8d05-2b72340ce6d8.png"></p>

## Can I contribute?

You are most welcome to contribute! If you are not a developer, you can become an **image curator**.

#### Curating wallpapers

While the wallpaper metadata in the `Wallpapers/` folder can be created manually, it is much more
convenient to use the [aiad-cli](aiad-cli) and feed it with links from one of the supported
wallpaper providers.

```
aiad-cli save https://www.pexels.com/photo/vehicles-on-road-near-lampposts-1689882/
```

For details on how to install and use aiad-cli, check out the [Readme](aiad-cli/README.md).

---

<p align="center">Copyright &copy; 2020 Niklas Rosenstein</p>
