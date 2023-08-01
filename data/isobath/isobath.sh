gdal_contour -a z -b 1 -fl -30 -29 -28 -27 -26 -25 -24 -23 -22 -21 -20 -19 -18 -17 -16 -15 -14 -13 -12 -11 -10 -9 -8 -7 -6 -5 -4 -3 -2 -1 0 1 2 -nln isobath_contour -f "GPKG" ETOPO_2022_v1_30s_N90W180_bed.nc isobath_contour.gpkg

qgis_process.bin run qgis:linestopolygons --INPUT="./isobath_contour.gpkg" --OUTPUT="./isobath_poly.gpkg"

