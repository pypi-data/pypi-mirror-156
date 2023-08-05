""" Data parameters and algorithms. """
from dataclasses import dataclass
import numpy as np
import tensorflow as tf
from typing import Callable, Iterator, Optional, Tuple, Union

import masterful.enums
"""
A `DatasetLike` object conforms to a subset of inputs
that are supported by `tf.keras.Model.fit()`. These include:

- A tf.data.Dataset
- A tuple of numpy arrays, (x, y)
- A numpy array, x
- A Keras Sequence
- A generator and output signature. The generator is a function
  which returns an object which conforms to the `iter()` protocol.
"""
DatasetLike = Union[tf.data.Dataset, np.ndarray, Tuple[np.ndarray, np.ndarray],
                    tf.keras.utils.Sequence, Tuple[Callable[[], Iterator],
                                                   Tuple[tf.TensorSpec,
                                                         tf.TensorSpec]]]


@dataclass
class DataParams:
  """Parameters describing the datasets used during training.

  These parameters describe both the structure of the dataset
  (image and label shapes for examples) as well as semantic
  structure of the labels (the bounding box format for example,
  or whether or not the labels are sparse or dense).

  Args:
    num_classes: The number of possible classes in the dataset.
    task: The task this dataset will be used for.
    image_shape: The input shape of image data in the dataset,
      in the format (height, width, channels) if `input_channels_last=True`,
      otherwise (channels, height, width) if `input_channels_last=False`.
    image_range: The range of pixels in the input image space that
      of the dataset.
    image_dtype: The image data type in the dataset.
    image_channels_last: The ordering of the dimensions in the inputs.
      `input_channels_last=True` corresponds to inputs with shape
      (height, width, channels) while `input_channels_last=False`
      corresponds to inputs with shape (channels, height, width). Defaults
      to True.
    label_dtype: The data type of the labels.
    label_shape: The shape of the labels.
    label_structure: The tensor format of the label examples.
    label_sparse: True if the labels are in sparse format, False
      for dense (one-hot) labels.
    label_bounding_box_format: The format of bounding boxes in the label,
      if they exist.
  """
  num_classes: int = None
  task: "masterful.enums.Task" = None

  image_shape: Tuple = None
  image_range: "masterful.enums.ImageRange" = None
  image_dtype: tf.dtypes.DType = None
  image_channels_last: bool = True

  label_dtype: type = None
  label_shape: Tuple = None
  label_structure: "masterful.enums.TensorStructure" = None
  label_sparse: bool = None
  label_bounding_box_format: Optional[
      "masterful.enums.BoundingBoxFormat"] = None

  @property
  def image_width(self) -> int:
    """Gets the width of the images in this dataset."""
    if len(self.image_shape) > 2:
      return (self.image_shape[1]
              if self.image_channels_last else self.image_shape[2])
    else:
      return self.image_shape[1]

  @property
  def image_height(self) -> int:
    """Gets the height of the images in this dataset."""
    if len(self.image_shape) > 2:
      return (self.image_shape[0]
              if self.image_channels_last else self.image_shape[1])
    else:
      return self.image_shape[0]

  @property
  def image_channels(self) -> int:
    """Gets the number of channels in the images in this dataset."""
    if len(self.image_shape) > 2:
      return (self.image_shape[2]
              if self.image_channels_last else self.image_shape[0])
    else:
      return 0
