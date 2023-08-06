from io import BytesIO
from pathlib import Path

import numpy
from PIL import Image, ImageOps

__version__ = "4.2.1"
"""
You may copy this file, if you keep the copyright information below:


Copyright (c) 2013-2020, Johannes Buchner
https://github.com/JohannesBuchner/imagehash

All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are
met:

Redistributions of source code must retain the above copyright
notice, this list of conditions and the following disclaimer.

Redistributions in binary form must reproduce the above copyright
notice, this list of conditions and the following disclaimer in the
documentation and/or other materials provided with the distribution.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS
IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED
TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A
PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
(INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

"""


def average_hash(image, hash_size=8, mean=numpy.mean):
    """
    Average Hash computation
    Implementation follows http://www.hackerfactor.com/blog/index.php?/archives/432-Looks-Like-It.html
    @image must be a PIL instance.
    @mean how to determine the average luminescence. can try numpy.median instead.
    """
    if hash_size < 2:
        raise ValueError("Hash size must be greater than or equal to 2")

    # reduce size and complexity, then covert to grayscale
    image = image.convert("L").resize((hash_size, hash_size), Image.ANTIALIAS)

    # find average pixel value; 'pixels' is an array of the pixel values, ranging from 0 (black) to 255 (white)
    pixels = numpy.asarray(image)
    avg = mean(pixels)

    # create string of bits
    diff = pixels > avg
    return diff


def dhash(image, hash_size=8):
    """
    Difference Hash computation.
    following http://www.hackerfactor.com/blog/index.php?/archives/529-Kind-of-Like-That.html

    @image must be a PIL instance.
    """
    # resize(w, h), but numpy.array((h, w))
    if hash_size < 2:
        raise ValueError("Hash size must be greater than or equal to 2")

    image = image.convert("L").resize((hash_size + 1, hash_size), Image.ANTIALIAS)
    pixels = numpy.asarray(image)
    # compute differences between columns
    diff = pixels[:, 1:] > pixels[:, :-1]
    return diff


def colorhash(image, binbits=3):
    """
    Color Hash computation.
    Computes fractions of image in intensity, hue and saturation bins:

    * the first binbits encode the black fraction of the image
    * the next binbits encode the gray fraction of the remaining image (low saturation)
    * the next 6*binbits encode the fraction in 6 bins of saturation, for highly saturated parts of the remaining image
    * the next 6*binbits encode the fraction in 6 bins of saturation, for mildly saturated parts of the remaining image

    @binbits number of bits to use to encode each pixel fractions
    """

    # bin in hsv space:
    intensity = numpy.asarray(image.convert("L")).flatten()
    h, s, v = [numpy.asarray(v).flatten() for v in image.convert("HSV").split()]
    # black bin
    mask_black = intensity < 256 // 8
    frac_black = mask_black.mean()
    # gray bin (low saturation, but not black)
    mask_gray = s < 256 // 3
    frac_gray = numpy.logical_and(~mask_black, mask_gray).mean()
    # two color bins (medium and high saturation, not in the two above)
    mask_colors = numpy.logical_and(~mask_black, ~mask_gray)
    mask_faint_colors = numpy.logical_and(mask_colors, s < 256 * 2 // 3)
    mask_bright_colors = numpy.logical_and(mask_colors, s > 256 * 2 // 3)

    c = max(1, mask_colors.sum())
    # in the color bins, make sub-bins by hue
    hue_bins = numpy.linspace(0, 255, 6 + 1)
    if mask_faint_colors.any():
        h_faint_counts, _ = numpy.histogram(h[mask_faint_colors], bins=hue_bins)
    else:
        h_faint_counts = numpy.zeros(len(hue_bins) - 1)
    if mask_bright_colors.any():
        h_bright_counts, _ = numpy.histogram(h[mask_bright_colors], bins=hue_bins)
    else:
        h_bright_counts = numpy.zeros(len(hue_bins) - 1)

    # now we have fractions in each category (6*2 + 2 = 14 bins)
    # convert to hash and discretize:
    maxvalue = 2**binbits
    values = [min(maxvalue - 1, int(frac_black * maxvalue)), min(maxvalue - 1, int(frac_gray * maxvalue))]
    for counts in list(h_faint_counts) + list(h_bright_counts):
        values.append(min(maxvalue - 1, int(counts * maxvalue * 1.0 / c)))
    # print(values)
    bitarray = []
    for v in values:
        bitarray += [v // (2 ** (binbits - i - 1)) % 2 ** (binbits - i) > 0 for i in range(binbits)]
    return numpy.asarray(bitarray).reshape((-1, binbits))


def compare_hashes(pillow_images: list, hash_type="average", hash_size=16, max_difference=0):
    image_hashes = []
    for pillow_image in pillow_images:
        if isinstance(pillow_image, (str, Path, BytesIO)):
            pillow_image = Image.open(pillow_image)
        pillow_image = ImageOps.exif_transpose(pillow_image)
        if hash_type == "dhash":
            image_hash = dhash(pillow_image, hash_size)
        elif hash_type == "colorhash":
            image_hash = colorhash(pillow_image)
        else:
            image_hash = average_hash(pillow_image, hash_size)
        image_hash = image_hash.flatten()
        for _ in range(len(image_hashes)):
            distance = numpy.count_nonzero(image_hash != image_hashes[_])
            assert distance <= max_difference, f"{distance} > {max_difference}"
        image_hashes.append(image_hash)
