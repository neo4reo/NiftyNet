# -*- coding: utf-8 -*-
"""
windows aggregator resize each item
in a batch output and save as an image
"""
from __future__ import absolute_import, print_function, division

import os

import numpy as np

import niftynet.io.misc_io as misc_io
from niftynet.engine.windows_aggregator_base import ImageWindowsAggregator
from niftynet.layer.discrete_label_normalisation import \
    DiscreteLabelNormalisationLayer


class ClassifierSamplesAggregator(ImageWindowsAggregator):
    """
    This class decodes each item in a batch by saving classification
    labels to a new image volume.
    """
    def __init__(self,
                 image_reader,
                 name='image',
                 output_path=os.path.join('.', 'output')):
        ImageWindowsAggregator.__init__(self, image_reader=image_reader)
        self.name = name
        self.output_path = os.path.abspath(output_path)
        self.output_interp_order = 0

    def decode_batch(self, window, location):
        """
        window holds the classifier labels
        location is a holdover from segmentation and may be removed
        in a later refactoring, but currently hold info about the stopping
        signal from the sampler
        """
        n_samples = window.shape[0]
        print('......', window.shape)
        for batch_id in range(n_samples):
            if self._is_stopping_signal(location[batch_id]):
                return False
            self.image_id = location[batch_id, 0]
            self._save_current_image(window[batch_id, ...])
        return True

    def _save_current_image(self, image_out):
        if self.input_image is None:
            return
        window_shape = [1, 1, 1, 1, 1]
        image_out = np.reshape(image_out, window_shape)
        for layer in reversed(self.reader.preprocessors):
            if isinstance(layer, DiscreteLabelNormalisationLayer):
                image_out, _ = layer.inverse_op(image_out)
        subject_name = self.reader.get_subject_id(self.image_id)
        filename = "{}_niftynet_out.nii.gz".format(subject_name)
        source_image_obj = self.input_image[self.name]
        misc_io.save_data_array(self.output_path,
                                filename,
                                image_out,
                                source_image_obj,
                                self.output_interp_order)
        return
