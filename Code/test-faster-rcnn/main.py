from enum import Enum
from functools import cache
import json

from src.model import get_model_instance_segmentation, get_model_object_detection, set_optimizer, set_scheduler
from src.train import get_train_dataset, train_epoch
from src.test import get_test_dataset, test_epoch
from src.config import *

import torch
from torchvision.models.detection.roi_heads import maskrcnn_loss

class Phase(Enum):
    TRAIN = "train"
    TEST = "test"

@cache
def get_raw_annotations(phase):
    annotations_path = (
        TRAIN_ANNOTATIONS_PATH if phase == Phase.TRAIN
        else TEST_ANNOTATIONS_PATH
    )

    with open(os.path.join(ROOT_DIR, annotations_path), "r") as file_json:
        annotations_data = json.loads(file_json.read())
        return annotations_data


class ModelRunner:
    def __init__(self, batch_size: int=100) -> None:
        self.batch_size = batch_size
        # self.model = build_model()
   
    def train_and_test(self):
        # train_annotations = get_raw_annotations(Phase.TRAIN)
        # test_annotations = get_raw_annotations(Phase.TEST)
        train_ds = get_train_dataset(self.batch_size)
        test_ds = get_test_dataset(self.batch_size)
        
        # self.model = get_model_instance_segmentation()
        self.model = get_model_object_detection()
        self.optimizer = set_optimizer(self.model)
        self.scheduler = set_scheduler(self.optimizer)
        self.loss_func = maskrcnn_loss

        for epoch in range(1, EPOCHS + 1):
            train_epoch(epoch, train_ds, self.model, self.optimizer, self.loss_func)

            # do metrics measurement here

            test_epoch(epoch, test_ds, self.model, self.loss_func)

            # do metrics measurements here
            # IOU


            # save best model
            torch.save(self.model.state_dict(), "custom_faster_rcnn_model.pt")


# call model and return results
runner = ModelRunner(batch_size=BATCH_SIZE)
results = runner.train_and_test()