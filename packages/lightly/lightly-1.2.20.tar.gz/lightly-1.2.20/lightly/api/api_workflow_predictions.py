from typing import List, Dict

import tqdm

from lightly.openapi_generated.swagger_client.models.prediction_task_schema import PredictionTaskSchema
from lightly.openapi_generated.swagger_client.models.prediction_singleton import PredictionSingleton
from lightly.openapi_generated.swagger_client.models.task_type import TaskType


class _PredictionsMixin:

    def _create_or_update_predictions(
        self,
        uuid: int,
        schema: PredictionTaskSchema,
        predictions: Dict[str, List[PredictionSingleton]],
        verbose: bool = False,
    ):
        """TODO"""

        self._predictions_api.create_or_update_prediction_task_schema_by_dataset_id(
            schema,
            self.dataset_id,
            uuid,
        )

        samples = self.get_all_samples()
        if verbose:
            samples = tqdm.tqdm(samples, desc='Uploading predictions:', unit='predictions')
        for sample in samples:

            singletons = predictions.get(sample.file_name, [])
            self._predictions_api.create_or_update_prediction_by_sample_id(
                singletons,
                self.dataset_id,
                sample.id,
                uuid,
            )


    def upload_classification_predictions(
        self,
        schema: PredictionTaskSchema,
        predictions: Dict[str, PredictionSingleton],
        uuid: int = 0,
        verbose: bool = False,
    ):
        """TODO"""

        if schema.type != TaskType.CLASSIFICATION:
            raise ValueError('TODO')

        self._create_or_update_predictions(
            uuid,
            schema,
            {
                filename: [singleton] for filename, singleton in predictions
            },
            verbose=verbose
        )