# Monthly Ascent
Download your Strava activities and visualize your monthly ascent with a
breakdown by activity type.

![Example monthly ascent plot](https://user-images.githubusercontent.com/820556/57760255-7bf47d00-76fb-11e9-8aa2-0824d66cf18c.png)

## Download Your Strava Activity Archive
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
