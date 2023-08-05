



class _SamplesMixin:


    def get_all_samples(self):
        """TODO"""
        return self._samples_api.get_samples_by_dataset_id(self.dataset_id)