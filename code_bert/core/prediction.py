from uuid import uuid4
from transformers import *
import numpy as np
import torch


class Prediction():

    def __init__(self, model_path, model_type="QQP"):
        self.model_path = f"./{model_path}/{model_type}"
        
        self.tokenzier = AutoTokenizer.from_pretrained(self.model_path)
        self.model = RobertaForSequenceClassification.from_pretrained(self.model_path)

        self.processor = glue_processors['qqp']()
        self.output_mode = glue_output_modes['qqp']
        self.label_list = self.processor.get_labels()

    def _predict(self, example):
        features = glue_convert_examples_to_features(example,
                                                     self.tokenzier,
                                                     max_length=512,
                                                     label_list=self.label_list,
                                                     output_mode=self.output_mode)
        labels = torch.tensor([1]).unsqueeze(0)
        with torch.no_grad():
            output = self.model(torch.tensor(features[0].input_ids).unsqueeze(0), labels=labels)
            loss = output[0].numpy()
            match = np.argmax(output[1].numpy())
            return match, loss

    def predict(self, func_body, doc_str):
        guid = "test_0"
        example = [InputExample(guid=guid, text_a=func_body, text_b=doc_str, label=None)]
        return self._predict(example)