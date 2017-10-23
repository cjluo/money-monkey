# Copyright 2016 Google Inc. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ==============================================================================

import threading
import logging

from grpc.beta import implementations
import tensorflow as tf
import numpy as np

from tensorflow_serving.apis import predict_pb2
from tensorflow_serving.apis import prediction_service_pb2


class Inference:
    def __init__(self, hostport, work_dir):
        self._hostport = hostport
        self._work_dir = work_dir
        self._condition = threading.Condition()

    def do_inference(self, data):

        logger = logging.getLogger()

        def _callback(result_future):
            exception = result_future.exception()
            if exception:
                logger.error(exception)
            else:
                logger.info("score %s", np.array(
                    result_future.result().outputs['score'].double_val))
            with self._condition:
                self._condition.notify()

        host, port = self._hostport.split(':')
        channel = implementations.insecure_channel(host, int(port))
        stub = prediction_service_pb2.beta_create_PredictionService_stub(
            channel)

        request = predict_pb2.PredictRequest()
        request.model_spec.name = 'score'
        request.model_spec.signature_name = 'output'

        request.inputs['x'].CopyFrom(
            tf.contrib.util.make_tensor_proto(data, shape=[1, len(data)]))

        result_future = stub.Predict.future(request, 5.0)  # 5 seconds
        result_future.add_done_callback(_callback)
        with self._condition:
            self._condition.wait()
        return np.array(result_future.result().outputs['score'].double_val)
