# Monthly Ascent
Download your Strava activities and visualize your monthly ascent with a
breakdown by activity type.


## Downloading Strava Activity Archive
This script uses the data archive that you can export from the Strava website. Go to
`Settings` -> `My Account` -> `Download or Delete Your Account` -> `Request
Your Archive`.

## Dependencies
Install the Python dependencies:

    pip install numpy matplotlib pandas python-tcxparser gpxpy

## Visualize
Download and unzip your Strava export arhive. Run `monthly-ascent.py` with the
path to the archive directory:

    unzip export_1234567.zip -d my_strava_archive
    ./monthly-ascent.py my_strava_archive
