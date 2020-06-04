#  Copyright 2018 The TensorFlow Authors. All Rights Reserved.
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
"""tf.data.Dataset interface to the MNIST dataset."""

from __future__ import absolute_import, division, print_function

import gzip
import os
import shutil
import numpy as np
from pdb import set_trace as st

import numpy as np
import tensorflow as tf
from six.moves import urllib

from .mnist_transforms import *

__all__ = ["train", "test"]


def read32(bytestream):
    """Read 4 bytes from bytestream as an unsigned 32-bit integer."""
    dt = np.dtype(np.uint32).newbyteorder(">")
    return np.frombuffer(bytestream.read(4), dtype=dt)[0]


def check_image_file_header(filename):
    """Validate that filename corresponds to images for the MNIST dataset."""
    with tf.gfile.Open(filename, "rb") as f:
        magic = read32(f)
        num_images = read32(f)
        rows = read32(f)
        cols = read32(f)
        if magic != 2051:
            raise ValueError(
                "Invalid magic number %d in MNIST file %s" % (magic, f.name)
            )
        if rows != 28 or cols != 28:
            raise ValueError(
                "Invalid MNIST file %s: Expected 28x28 images, found %dx%d"
                % (f.name, rows, cols)
            )


def check_labels_file_header(filename):
    """Validate that filename corresponds to labels for the MNIST dataset."""
    with tf.gfile.Open(filename, "rb") as f:
        magic = read32(f)
        num_items = read32(f)
        if magic != 2049:
            raise ValueError(
                "Invalid magic number %d in MNIST file %s" % (magic, f.name)
            )


def download(directory, filename):
    """Download (and unzip) a file from the MNIST dataset if not already done."""
    filepath = os.path.join(directory, filename)
    if tf.gfile.Exists(filepath):
        return filepath
    if not tf.gfile.Exists(directory):
        tf.gfile.MakeDirs(directory)
    # CVDF mirror of http://yann.lecun.com/exdb/mnist/
    # url = "https://storage.googleapis.com/cvdf-datasets/mnist/" + filename + ".gz"
    url = "http://yann.lecun.com/exdb/mnist/" + filename + ".gz"
    zipped_filepath = filepath + ".gz"
    print("Downloading %s to %s" % (url, zipped_filepath))
    urllib.request.urlretrieve(url, zipped_filepath)
    with gzip.open(zipped_filepath, "rb") as f_in, open(filepath, "wb") as f_out:
        shutil.copyfileobj(f_in, f_out)
    os.remove(zipped_filepath)
    return filepath


def normalize(x: tf.Tensor) -> tf.Tensor:
    return (x - 0.1307) / 0.3081

def unit_test(image):
    # translate = Translate( dx = 0, dy = 6)
    # image = translate(image)

    # resize = Resize(0.5)
    # image = resize(image)

    # rotate = Rotate(10)
    # image = rotate(image)

    # random_translate = RandomTranslate(
    #                     min_dx = -3, max_dx = 3,
    #                     min_dy = -5, max_dy = 5
    #                 )
    # image = random_translate(image)

    # random_resize = RandomResize(min_ratio = 0.8, max_ratio = 1.2)
    # image = random_resize(image)

    # random_rotate = RandomRotate(min_angle = -45, max_angle = 45)
    # image = random_rotate(image)

    # translate = Translate( dx = 4, dy = 6)
    # rotate = Rotate(45)
    # transforms = Transforms(
    #     translate,
    #     rotate
    # )
    # image = transforms(image)

    return image

def dataset(
    directory,
    images_file,
    labels_file,
    normed=True,
    transforms=None
):
    images_file = download(directory, images_file)
    labels_file = download(directory, labels_file)

    check_image_file_header(images_file)
    check_labels_file_header(labels_file)

    def decode_image(image):
        # Normalize from [0, 255] to [0.0, 1.0]
        image = tf.decode_raw(image, tf.uint8)
        image = tf.cast(image, tf.float32)
        image = tf.reshape(image, [28, 28, 1])

        if transforms is not None:
            image = transforms(image)

        image = tf.reshape(image, [1, 28, 28])
        image = image / 255.0
        # image = tf.Print(image, [image.shape])
        if normed:
            return normalize(image)
        else:
            return image

    def decode_label(label):
        label = tf.decode_raw(label, tf.uint8)  # tf.string -> [tf.uint8]
        label = tf.reshape(label, [])  # label is a scalar
        return tf.to_int32(label)

    images = tf.data.FixedLengthRecordDataset(
        images_file, 28 * 28, header_bytes=16
    ).map(decode_image)
    labels = tf.data.FixedLengthRecordDataset(labels_file, 1, header_bytes=8).map(
        decode_label
    )
    dataset = tf.data.Dataset.zip((images, labels))
    return dataset


def train(directory, normed=True, transforms=None):
    """tf.data.Dataset object for MNIST training data."""
    return dataset(
        directory, "train-images-idx3-ubyte", "train-labels-idx1-ubyte",
        normed,
        transforms=transforms
    )


def test(directory, normed=True, transforms=None):
    """tf.data.Dataset object for MNIST test data."""
    return dataset(
        directory, "t10k-images-idx3-ubyte", "t10k-labels-idx1-ubyte",
        normed,
        transforms=transforms
    )
