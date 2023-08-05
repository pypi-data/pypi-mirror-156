import unittest
import torch
from irisml.core import Context
from irisml.tasks.create_torchvision_model import Task


class TestCreateTorchvisionModel(unittest.TestCase):
    def test_classification(self):
        config = Task.Config(name='mobilenet_v2', num_classes=1000, task_type='multiclass_classification')
        task = Task(config, Context())
        outputs = task.execute(None)
        self.assertIsInstance(outputs.model, torch.nn.Module)

        config = Task.Config(name='mobilenet_v2', num_classes=1000, task_type='multilabel_classification')
        task = Task(config, Context())
        outputs = task.execute(None)
        self.assertIsInstance(outputs.model, torch.nn.Module)
