"""Entrypoint for the masterful.train package."""
import os
# Must be set before importing tensorflow.
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
os.environ['TF_CPP_MAX_LOG_LEVEL'] = '0'
os.environ['TF_CPP_MAX_VLOG_LEVEL'] = '0'

import argparse
import tensorflow as tf

# Register if not running locally. Registration
# only works by using the evironment variables.
import masterful
if 'backend' not in dir(masterful) or os.environ.get('NOOP_REGISTER',
                                                     None) == '1':
  masterful = masterful.register()
import masterful.train.trainer as trainer


def _silence_logging():
  tf.compat.v1.logging.set_verbosity(tf.compat.v1.logging.ERROR)

  import logging

  logging.getLogger('tensorflow').setLevel(logging.ERROR)
  logging.getLogger('absl').setLevel(logging.ERROR)
  logging.getLogger().setLevel(logging.ERROR)

  from absl import logging as absl_logging
  absl_logging.set_verbosity(logging.ERROR)


_silence_logging()


def main(override=None):
  """
  Main entrypoint for the standalone version of this package.
  """
  # This script only runs under Tensorflow 2.0
  assert tf.__version__.startswith("2")

  parser = argparse.ArgumentParser()
  parser.add_argument("--config",
                      help="Training configuration YAML file",
                      type=str,
                      required=True)
  args = parser.parse_args()

  trainer.train_from_config(config_path=args.config)


main()