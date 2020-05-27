#!/bin/bash
#
# Set up a crontab for fetching the latest daily image from the an-image-a-day
# Wallpaper database.

if ! [[ "$OSTYPE" =~ ^darwin ]]; then
  >&2 echo "error: setup script currently supports OSX only (found: $OSTYPE)"
  exit 1
fi

DIRECTORY=~/Pictures/"An Image a Day"
SCHEDULE="*/10 * * * *"
CHANNEL=General

while [[ $# -gt 0 ]]; do
  case $1 in
    -D|--directory)
      DIRECTORY="$2"
      shift; shift
      ;;
    -s|--schedule)
      SCHEDULE="$2"
      shift; shift
      ;;
    -c|--channel)
      CHANNEL="$2"
      shift; shift
      ;;
    -h|--help)
      echo "usage: setup.sh [OPTIONS]"
      echo ""
      echo "options:"
      echo "  -D, --directory       Override the directory. Defaults to \"$DIRECTORY\"."
      echo "  -s, --schedule        Override the Cron schedule. Defaults to \"$SCHEDULE\"."
      echo "  -c, --channel         Override the wallpaper channel. Defaults to \"$CHANNEL\"."
      exit 0
      ;;
    *)
      >&2 echo "error: unknown argument: $1"
      exit 1
      ;;
    esac
done

CLONE_DIRECTORY="$DIRECTORY/Data"
CLONE_URL=https://github.com/an-image-a-day/an-image-a-day.git

INSTALL_WITH_BREW=()
if ! command -v curl >/dev/null; then
  INSTALL_WITH_BREW+=('curl')
fi
if ! command -v jq >/dev/null; then
  INSTALL_WITH_BREW+=('jq')
fi
if ! command -v git >/dev/null; then
  INSTALL_WITH_BREW+=('git')
fi
if (( ${#INSTALL_WITH_BREW[@]} )); then
  echo "Installing with Homebrew: ${INSTALL_WITH_BREW[*]}"
  brew install ${INSTALL_WITH_BREW[*]} --quiet
fi

set -e
if ! [ -d "$CLONE_DIRECTORY" ]; then
  echo "Cloning repository ..."
  git clone "$CLONE_URL" "$CLONE_DIRECTORY" -q
else
  echo "Updating repository ..."
  git -C "$CLONE_DIRECTORY" pull -q
fi

# Ensure that these commands can be found by updating the PATH in the crontab.
JQPATH="$(dirname `which jq`)"
CURLPATH="$(dirname `which curl`)"
GITPATH="$(dirname `which git`)"

echo "Updating crontab ..."
CRON_COMMAND="PATH=\"\$PATH:$JQPATH:$CURLPATH:$GITPATH\" && cd \"$CLONE_DIRECTORY\" && git pull -q && an-image-a-day-downloader/downloader.sh -D \"$DIRECTORY\" -c \"$CHANNEL\""
CRONTAB=$(crontab -l | grep -v an-image-a-day)
CRONTAB="$CRONTAB

# Registered by an-image-a-day/an-image-a-day-downloader/setup.sh
$SCHEDULE $CRON_COMMAND"
echo "$CRONTAB" | crontab

echo "Run downloader now ..."
bash -c "$CRON_COMMAND"

echo "Done."
