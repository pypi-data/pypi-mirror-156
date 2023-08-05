# -*- coding: utf-8 -*-
# File: hflayoutlm.py

# Copyright 2021 Dr. Janis Meyer. All rights reserved.
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

"""
HF Layoutlm model for diverse downstream tasks.
"""

from copy import copy
from typing import Dict, List, Optional, Sequence, Union

from ..utils.detection_types import Requirement
from ..utils.file_utils import (
    get_pytorch_requirement,
    get_transformers_requirement,
    pytorch_available,
    transformers_available,
)
from ..utils.settings import names
from .base import LMTokenClassifier, PredictorBase, TokenClassResult
from .pt.ptutils import set_torch_auto_device

if pytorch_available():
    import torch
    from torch import Tensor  # pylint: disable=W0611

if transformers_available():
    from transformers import LayoutLMForTokenClassification, PretrainedConfig


def predict_token_classes(
    uuids: List[str],
    input_ids: "Tensor",
    attention_mask: "Tensor",
    token_type_ids: "Tensor",
    boxes: "Tensor",
    tokens: List[str],
    model: "LayoutLMForTokenClassification",
) -> List[TokenClassResult]:
    """
    :param uuids: A list of uuids that correspond to a word that induces the resulting token
    :param input_ids: Token converted to ids to be taken from LayoutLMTokenizer
    :param attention_mask: The associated attention masks from padded sequences taken from LayoutLMTokenizer
    :param token_type_ids: Torch tensor of token type ids taken from LayoutLMTokenizer
    :param boxes: Torch tensor of bounding boxes of type 'xyxy'
    :param tokens: List of original tokens taken from LayoutLMTokenizer
    :param model: layoutlm model for token classification
    :return: A list of TokenClassResults
    """
    outputs = model(input_ids=input_ids, bbox=boxes, attention_mask=attention_mask, token_type_ids=token_type_ids)
    token_class_predictions = outputs.logits.argmax(-1).squeeze().tolist()
    input_ids_list = input_ids.squeeze().tolist()
    return [
        TokenClassResult(uuid=out[0], token_id=out[1], class_id=out[2], token=out[3])
        for out in zip(uuids, input_ids_list, token_class_predictions, tokens)
    ]


class HFLayoutLmTokenClassifier(LMTokenClassifier):
    """
    A wrapper class for :class:`transformers.LayoutLMForTokenClassification` to use within a pipeline component.
    Check https://huggingface.co/docs/transformers/model_doc/layoutlm for documentation of the model itself.
    Note that this model is equipped with a head that is only useful when classifying tokens. For sequence
    classification and other things please use another model of the family.

    **Example**

        .. code-block:: python

            # setting up compulsory ocr service
            tesseract_config_path = ModelCatalog.get_full_path_configs("/dd/conf_tesseract.yaml")
            tess = TesseractOcrDetector(tesseract_config_path)
            ocr_service = TextExtractionService(tess)

            # hf tokenizer and token classifier
            tokenizer = LayoutLMTokenizer.from_pretrained("mrm8488/layoutlm-finetuned-funsd")
            layoutlm = HFLayoutLmTokenClassifier("path/to/config.json","path/to/model.bin",
                                                  categories_explicit= ['B-ANSWER', 'B-HEAD', 'B-QUESTION', 'E-ANSWER',
                                                                        'E-HEAD', 'E-QUESTION', 'I-ANSWER', 'I-HEAD',
                                                                        'I-QUESTION', 'O', 'S-ANSWER', 'S-HEAD',
                                                                        'S-QUESTION'])

            # token classification service
            layoutlm_service = LMTokenClassifierService(tokenizer,layoutlm,image_to_layoutlm)

            pipe = DoctectionPipe(pipeline_component_list=[ocr_service,layoutlm_service])

            path = "path/to/some/form"
            df = pipe.analyze(path=path)

            for dp in df:
                ...
    """

    def __init__(
        self,
        path_config_json: str,
        path_weights: str,
        categories_semantics: Optional[Sequence[str]] = None,
        categories_bio: Optional[Sequence[str]] = None,
        categories_explicit: Optional[Sequence[str]] = None,
    ):
        """
        :param categories_semantics: A dict with key (indices) and values (category names) for NER semantics, i.e. the
                                     entities self. To be consistent with detectors use only values >0. Conversion will
                                     be done internally.
        :param categories_bio: A dict with key (indices) and values (category names) for NER tags (i.e. BIO). To be
                               consistent with detectors use only values>0. Conversion will be done internally.
        :param categories_explicit: If you have a pre-trained model you can pass a complete list of NER categories, i.e.
                                    semantics and tags explicitly.
        """

        if categories_explicit is None:
            assert categories_semantics is not None
            assert categories_bio is not None

        self.path_config_json = path_config_json
        self.path_weights = path_weights
        self.categories_semantics = copy(categories_semantics) if categories_semantics is not None else None
        self.categories_bio = copy(categories_bio) if categories_bio is not None else None
        self.categories_explicit = copy(categories_explicit) if categories_explicit is not None else None

        self._categories: Dict[int, str] = (
            dict(enumerate(self.categories_explicit))  # type: ignore
            if categories_explicit is not None
            else self._categories_orig_to_categories(categories_semantics, categories_bio)  # type: ignore
        )
        self.device = set_torch_auto_device()
        config = PretrainedConfig.from_pretrained(pretrained_model_name_or_path=path_config_json)
        self.model = LayoutLMForTokenClassification.from_pretrained(
            pretrained_model_name_or_path=path_weights, config=config
        )

    @classmethod
    def get_requirements(cls) -> List[Requirement]:
        return [get_pytorch_requirement(), get_transformers_requirement()]

    def predict(self, **encodings: Union[List[str], "torch.Tensor"]) -> List[TokenClassResult]:
        """
        Launch inference on LayoutLm for token classification. Pass the following arguments

        :param input_ids: Token converted to ids to be taken from LayoutLMTokenizer
        :param attention_mask: The associated attention masks from padded sequences taken from LayoutLMTokenizer
        :param token_type_ids: Torch tensor of token type ids taken from LayoutLMTokenizer
        :param boxes: Torch tensor of bounding boxes of type 'xyxy'
        :param tokens: List of original tokens taken from LayoutLMTokenizer

        :return: A list of TokenClassResults
        """

        assert "input_ids" in encodings
        assert "attention_mask" in encodings
        assert "token_type_ids" in encodings
        assert "boxes" in encodings
        assert "tokens" in encodings

        assert isinstance(encodings["ids"], list)
        assert isinstance(encodings["input_ids"], torch.Tensor)
        assert isinstance(encodings["attention_mask"], torch.Tensor)
        assert isinstance(encodings["token_type_ids"], torch.Tensor)
        assert isinstance(encodings["boxes"], torch.Tensor)
        assert isinstance(encodings["tokens"], list)

        results = predict_token_classes(
            encodings["ids"],
            encodings["input_ids"],
            encodings["attention_mask"],
            encodings["token_type_ids"],
            encodings["boxes"],
            encodings["tokens"],
            self.model,
        )

        return self._map_category_names(results)

    @staticmethod
    def _categories_orig_to_categories(categories_semantics: List[str], categories_bio: List[str]) -> Dict[int, str]:
        categories_semantics, categories_bio = copy(categories_semantics), copy(categories_bio)
        categories_list = [
            x + "-" + y for x in categories_bio if x != names.NER.O for y in categories_semantics if y != names.C.O
        ] + [names.NER.O]
        return dict(enumerate(categories_list))

    def _map_category_names(self, token_results: List[TokenClassResult]) -> List[TokenClassResult]:
        for result in token_results:
            result.class_name = self._categories[result.class_id]
            result.semantic_name = result.class_name.split("-")[1] if "-" in result.class_name else names.C.O
            result.bio_tag = result.class_name.split("-")[0] if "-" in result.class_name else names.NER.O
        return token_results

    @property
    def categories(self) -> Dict[int, str]:
        """
        categories
        """
        return self._categories

    def clone(self) -> PredictorBase:
        return self.__class__(
            self.path_config_json,
            self.path_weights,
            self.categories_semantics,
            self.categories_bio,
            self.categories_explicit,
        )
