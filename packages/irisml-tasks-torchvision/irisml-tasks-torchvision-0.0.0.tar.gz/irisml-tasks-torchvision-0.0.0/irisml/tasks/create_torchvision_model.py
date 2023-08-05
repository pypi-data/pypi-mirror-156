import dataclasses
import logging

import torch
import torchvision.models
import irisml.core

logger = logging.getLogger(__name__)


class Task(irisml.core.TaskBase):
    """Create a torchvision model.

    Currently this task supports three kind of tasks. multiclass_classification, multilabel_classificaiton, and object_detection.
    """
    VERSION = '0.1.0'

    @dataclasses.dataclass
    class Config:
        name: str
        num_classes: int
        task_type: str = 'multiclass_classification'
        pretrained: bool = False

    @dataclasses.dataclass
    class Outputs:
        model: torch.nn.Module = None

    MODULES = {
        'multiclass_classification': (torch.nn.CrossEntropyLoss(), torch.nn.Softmax(1)),
        'multilabel_classification': (torch.nn.BCEWithLogitsLoss(), torch.nn.Sigmoid()),
        'object_detection': (None, torch.nn.Identity())  # Training is not supported.
    }

    class TorchvisionModel(torch.nn.Module):
        def __init__(self, model_name, num_classes, criterion, predictor, state_dict=None):
            super().__init__()
            self.model = self._init_model(model_name, num_classes)
            self._model_name = model_name
            self._num_classes = num_classes
            self._criterion = criterion
            self._predictor = predictor
            self.register_buffer('mean_value', torch.Tensor([0.485, 0.456, 0.406]).reshape((3, 1, 1)))
            self.register_buffer('std_value', torch.Tensor([0.229, 0.224, 0.225]).reshape((3, 1, 1)))
            if state_dict:
                self.model.load_state_dict(state_dict)

        def _init_model(self, model_name, num_classes):
            model_class = getattr(torchvision.models, model_name)
            model = model_class(pretrained=False, num_classes=num_classes)
            return model

        @property
        def criterion(self):
            return self._criterion

        @property
        def predictor(self):
            return self._predictor

        def forward(self, x: torch.Tensor) -> torch.Tensor:
            return self.model((x - self.mean_value) / self.std_value)

        def __getstate__(self):
            return {'model_name': self._model_name, 'num_classes': self._num_classes, 'criterion': self._criterion, 'predictor': self._predictor, 'state_dict': dict(self.model.state_dict())}

        def __setstate__(self, state):
            self.__init__(**state)

    def execute(self, inputs):
        if not hasattr(torchvision.models, self.config.name):
            raise ValueError(f"Model {self.config.name} is not supported by torchvision.")
        if self.config.task_type not in self.MODULES:
            raise RuntimeError(f"Task type {self.config.task_type} is not supported.")

        if self.config.task_type == 'object_detection':
            raise ValueError("Object Detection is not supported yet.")  # TODO

        logger.info(f"Creating a torchvision model: name={self.config.name}, num_classes={self.config.num_classes}, pretrained={self.config.pretrained}")

        criterion, predictor = self.MODULES[self.config.task_type]
        model = self.TorchvisionModel(self.config.name, self.config.num_classes, criterion, predictor)

        if self.config.pretrained:
            logger.debug("Loading pretrained weights for the model.")
            model_class = getattr(torchvision.models, self.config.name)
            pretrained_model = model_class(pretrained=True, progress=False)
            # We cannot directly construct since the pretrained weights will be loaded with strict mode.
            state_dict = model.model.state_dict()
            pretrained_state_dict = pretrained_model.state_dict()
            filtered_state_dict = {k: v for k, v in pretrained_state_dict.items() if pretrained_state_dict[k].shape == state_dict[k].shape}
            model.model.load_state_dict(filtered_state_dict, strict=False)

        return self.Outputs(model)
