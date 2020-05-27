# aiad-downloader

This directory contains two things:

* `fetch.sh` &ndash; A shell script to download the daily image from the [An Image a Day][]
  repository.
* `install.sh` &ndash; A shell script to install the `fetch.sh` script as a Cron job including
  all its dependencies (Homebrew, jq, git).

Under all circumstances it is expected that `curl` is already available on your system.

---

<p align="center">Copyright &copy; 2020 Niklas Rosenstein</p>
