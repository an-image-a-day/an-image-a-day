#!/bin/bash

CHANNEL=General
DATE=`date +%Y/%m/%d`
RESOLUTION="4K"
DIRECTORY=~/Pictures/"An Image a Day"
WALLPAPERS_DATABASE="$(dirname $(dirname ${BASH_SOURCE[0]}))/Wallpapers"
OVERWRITE=false
QUIET=false

while [[ $# -gt 0 ]]; do
  case $1 in
    -c|--channel)
      CHANNEL="$2"
      shift; shift
      ;;
    -d|--date)
      DATE="$2"
      shift; shift
      ;;
    -D|--directory)
      DIRECTORY="$2"
      shift; shift
      ;;
    --database)
      WALLPAPERS_DATABASE="$2"
      shift; shift
      ;;
    --overwrite)
      OVERWRITE=true
      shift
      ;;
    -q|--quiet)
      QUIET=true
      shift
      ;;
    -h|--help)
      echo "usage: downloader.sh [OPTIONS]"
      echo ""
      echo "options:"
      echo "  -h, --help          Show this help message and exit."
      echo "  -c, --channel       The name of the Wallpapers channel. Defaults to General."
      echo "  -d, --date          The date to download a wallpaper for. Must be of the form YYYY/MM/DD."
      echo "                        Defaults to the current date."
      echo "  -R, --resolution    The resolution name to pick from the wallpaper spec. Defaults to \"$RESOLUTION\"."
      echo "  -D, --directory     The directory to download images to. Defaults to \"$DIRECTORY\"."
      echo "  --database          The directory with the wallpapers database. Defaults to the \"Wallpapers\""
      echo "                        directory of the an-image-a-day repository computed relative to the location "
      echo "                        of this script."
      echo "  --overwrite         Re-download existing images."
      echo "  -q, --quiet         Less output."
      exit 0
      ;;
    *)
      >&2 echo "error: unknown argument: $1"
      exit 1
      ;;
  esac
done

if ! [[ "$DATE" =~ ^[0-9]{4}/[0-9]{2}/[0-9]{2}$ ]]; then
  >&2 echo "error: invalid date format: $DATE"
  exit 1
fi

FILENAME=`echo "$WALLPAPERS_DATABASE"/"$CHANNEL"/"$DATE"*.json`
if ! [[ -f "$FILENAME" ]]; then
  >&2 echo "error: file \"$FILENAME\" not found."
  exit 1
fi

IMAGE_URL=`cat "$FILENAME" | jq '.resolution_aliases."'"$RESOLUTION"'".image_url' -r`
FILENAME=`cat "$FILENAME" | jq '.resolution_aliases."'"$RESOLUTION"'".filename' -r`
if [ "$IMAGE_URL" == "null" ]; then
  >&2 echo "error: no image_url for resolution \"$RESOLUTION\" in \"$FILENAME\"."
  exit 1
fi
if [ "$FILENAME" == "null" ]; then
  >&2 echo "error: no filename for resolution \"$RESOLUTION\" in \"$FILENAME\"."
  exit 1
fi

FILENAME="${DATE//\//-}-$FILENAME"
OUTPUT_FILENAME="$DIRECTORY/$FILENAME"
if [ $OVERWRITE = false ] && [ -e "$OUTPUT_FILENAME" ]; then
  [ $QUIET = false ] && echo >&2 "note: file \"$OUTPUT_FILENAME\" already exists."
else
  mkdir -p "$DIRECTORY"
  curl -s "$IMAGE_URL" -o "$OUTPUT_FILENAME"
fi

mkdir -p "$DIRECTORY/Today"
rm -f -- "$DIRECTORY/Today"/*
ln -s "$OUTPUT_FILENAME" "$DIRECTORY/Today/$FILENAME"
