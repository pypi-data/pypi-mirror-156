""" Data parameters and algorithms. """
from typing import Sequence

import masterful.enums
from masterful.data import DataParams


def learn_data_params(
    dataset: "masterful.data.DatasetLike",
    image_range: "masterful.enums.ImageRange",
    num_classes: int,
    sparse_labels: bool,
    task: "masterful.enums.Task",
    bounding_box_format: "masterful.enums.BoundingBoxFormat" = None,
) -> DataParams:
  """Learns the :class:`DataParams` for the given dataset.

  Most parameters can be introspected from the dataset itself.
  Anything that cannot be introspected is passed into this function
  as an argument, or set on the :class:`DataParams` after creation.

  Example:

  .. code-block:: python

    training_dataset: tf.data.Dataset = ...
    dataset_params = masterful.data.learn_data_params(
        dataset=training_dataset,
        image_range=masterful.enums.ImageRange.ZERO_255,
        num_classes=10,
        sparse_labels=False,
        task=masterful.enums.Task.CLASSIFICATION)

  Args:
    dataset: A `tf.data.Dataset` instance to learn the parameters for.
    image_range: The range of pixels in the input image space that
      of the dataset.
    num_classes: The number of possible classes in the dataset.
    sparse_labels: True if the labels are in sparse format, False
      for dense (one-hot) labels.
    task: The task this dataset will be used for.
    bounding_box_format: The format of bounding boxes in the label,
      if they exist.

  Returns:
    A new instance of DataParams describing the passed in dataset.
  """
  raise RuntimeError(
      "Please call masterful.register() with your account ID and authorization key before using the API."
  )


def learn_data_params_for_datasets(
    datasets: Sequence["masterful.data.DatasetLike"],
    image_range: "masterful.enums.ImageRange",
    num_classes: int,
    sparse_labels: Sequence[bool],
    task: "masterful.enums.Task",
    bounding_box_format: "masterful.enums.BoundingBoxFormat" = None,
) -> Sequence[DataParams]:
  """Learns the :class:`DataParams` for the given datasets.

  Convenience method for learning the data parameters for multiple
  datasets at a time.

  Example:

  .. code-block:: python

    # Learn parameters for three datasets at the same time
    training_dataset: tf.data.Dataset = ...
    validation_dataset: tf.data.Dataset = ...
    test_dataset: tf.data.Dataset = ...

    (training_dataset_params, validation_dataset_params, test_dataset_params) = masterful.data.learn_data_params(
        datasets=[training_dataset, validation_dataset, test_dataset),
        image_range=masterful.enums.ImageRange.ZERO_255,
        num_classes=10,
        sparse_labels=[False, False, False],
        task=masterful.enums.Task.CLASSIFICATION)


  Args:
    datasets: A list/tuple of `tf.data.Dataset` instance to learn the parameters for.
    image_range: The range of pixels in the input image space that
      of the dataset.
    num_classes: The number of possible classes in the dataset.
    sparse_labels: A list/tuple of True if the labels are in sparse format, False
      for dense (one-hot) labels.
    task: The task this dataset will be used for.
    bounding_box_format: The format of bounding boxes in the label,
      if they exist.

  Returns:
    A sequence of DataParams instances describing the passed in datasets.
  """
  raise RuntimeError(
      "Please call masterful.register() with your account ID and authorization key before using the API."
  )
