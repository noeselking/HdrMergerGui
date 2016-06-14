#!/usr/bin/python3
# -*- coding: utf-8 -*-

import exifread


class CameraInfo:
    aperture = None
    exposureTime = None
    ISO = None


def getExifInfo(filename):
    with open(filename, 'rb') as file:
        tags = exifread.process_file(file)

    info = CameraInfo()

    info.aperture = str(tags["EXIF FNumber"]) if "EXIF FNumber" in tags else "Unknown"
    info.exposureTime = str(tags["EXIF ExposureTime"]) if "EXIF ExposureTime" in tags else "Unknown"
    info.ISO = str(tags["EXIF ISOSpeedRatings"]) if "EXIF ISOSpeedRatings" in tags else "Unknown"

    return info
