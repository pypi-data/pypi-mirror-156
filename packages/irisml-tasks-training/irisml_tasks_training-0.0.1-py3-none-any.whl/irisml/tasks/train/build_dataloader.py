import inspect
import torch.utils.data


class Dataset(torch.utils.data.Dataset):
    def __init__(self, dataset, transform):
        self._dataset = dataset
        self._transform = transform
        self._num_transform_args = len(inspect.getargspec(transform).args) - 1
        assert 1 <= self._num_transform_args <= 2

    def __len__(self):
        return len(self._dataset)

    def __getitem__(self, index):
        item = self._dataset[index]
        assert len(item) == 2
        if self._num_transform_args == 1:
            return self._transform(item[0]), item[1]
        elif self._num_transform_args == 2:
            return self._transform(*item)


def build_dataloader(dataset, transform, batch_size: int):
    my_dataset = Dataset(dataset, transform)
    return torch.utils.data.DataLoader(my_dataset, batch_size=batch_size)
