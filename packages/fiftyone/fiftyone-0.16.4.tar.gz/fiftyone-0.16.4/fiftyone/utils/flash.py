"""
Utilities for working with
`Lightning Flash <https://github.com/PyTorchLightning/lightning-flash>`_.

| Copyright 2017-2022, Voxel51, Inc.
| `voxel51.com <https://voxel51.com/>`_
|
"""
import inspect
import itertools

import numpy as np

import fiftyone.core.labels as fol
import fiftyone.core.media as fom
import fiftyone.core.utils as fou

fou.ensure_import("flash>=0.7dev")
import flash
import flash.core.classification as fc
import flash.image as fi
import flash.image.detection.output as fdo
import flash.image.segmentation.output as fso
import flash.video as fv


_SUPPORTED_MODELS = (
    fi.ImageClassifier,
    fi.ObjectDetector,
    fi.SemanticSegmentation,
)

_SUPPORTED_EMBEDDERS = fi.ImageEmbedder


def apply_flash_model(
    samples,
    model,
    label_field="predictions",
    confidence_thresh=None,
    store_logits=False,
    batch_size=None,
    num_workers=None,
    transform_kwargs=None,
    trainer_kwargs=None,
):
    """Applies the given
    :class:`Lightning Flash model <flash:flash.core.model.Task>` to the samples
    in the collection.

    Args:
        samples: a :class:`fiftyone.core.collections.SampleCollection`
        model: a :class:`flash:flash.core.model.Task`
        label_field ("predictions"): the name of the field in which to store
            the model predictions. When performing inference on video frames,
            the "frames." prefix is optional
        confidence_thresh (None): an optional confidence threshold to apply to
            any applicable labels generated by the model
        store_logits (False): whether to store logits for the model
            predictions. This is only supported when the provided ``model`` has
            logits
        batch_size (None): an optional batch size to use. If not provided, a
            default batch size is used
        num_workers (None): the number of workers for the data loader to use
        transform_kwargs (None): an optional dict of transform kwargs to pass
            into the created data module used by some models
        trainer_kwargs (None): an optional dict of kwargs used to initialize the
            :mod:`Trainer <flash:flash.core.trainer>`. These can be used to,
            for example, configure the number of GPUs to use and other
            distributed inference parameters
    """
    output = _get_output(model, confidence_thresh, store_logits)

    if trainer_kwargs is None:
        trainer_kwargs = {}

    data_kwargs = {
        "num_workers": num_workers or 1,
        "batch_size": batch_size or 1,
    }
    if transform_kwargs:
        data_kwargs["transform_kwargs"] = transform_kwargs

    datamodule_cls = _MODEL_TO_DATAMODULE_MAP[type(model)]

    datamodule = datamodule_cls.from_fiftyone(
        predict_dataset=samples, **data_kwargs
    )
    predictions = flash.Trainer(**trainer_kwargs).predict(
        model, datamodule=datamodule, output=output
    )
    predictions = list(itertools.chain.from_iterable(predictions))
    predictions = {p["filepath"]: p["predictions"] for p in predictions}

    samples.set_values(label_field, predictions, key_field="filepath")


def compute_flash_embeddings(
    samples,
    model,
    embeddings_field=None,
    batch_size=None,
    num_workers=None,
    transform_kwargs=None,
    trainer_kwargs=None,
):
    """Computes embeddings for the samples in the collection using the given
    :class:`Lightning Flash model <flash:flash.core.model.Task>`.

    This method only supports applying an
    :ref:`ImageEmbedder <flash:image_embedder>` to an image collection.

    If an ``embeddings_field`` is provided, the embeddings are saved to the
    samples; otherwise, the embeddings are returned in-memory.

    Args:
        samples: a :class:`fiftyone.core.collections.SampleCollection`
        model: a :class:`flash:flash.core.model.Task`
        embeddings_field (None): the name of a field in which to store the
            embeddings
        batch_size (None): an optional batch size to use. If not provided, a
            default batch size is used
        num_workers (None): the number of workers for the data loader to use
        transform_kwargs (None): an optional dict of transform kwargs to pass
            into the created data module used by some models
        trainer_kwargs (None): an optional dict of kwargs used to initialize the
            :mod:`Trainer <flash:flash.core.trainer>`. These can be used to,
            for example, configure the number of GPUs to use and other
            distributed inference parameters

    Returns:
        one of the following:

        -   ``None``, if an ``embeddings_field`` is provided
        -   a ``num_samples x num_dim`` array of embeddings, if
            ``embeddings_field`` is None
    """
    if not isinstance(model, _SUPPORTED_EMBEDDERS):
        raise ValueError(
            "Unsupported model type %s. Supported model types are %s"
            % (type(model), _SUPPORTED_EMBEDDERS)
        )

    if trainer_kwargs is None:
        trainer_kwargs = {}

    data_kwargs = {
        "num_workers": num_workers or 1,
        "batch_size": batch_size or 1,
    }
    if transform_kwargs:
        data_kwargs["transform_kwargs"] = transform_kwargs

    datamodule = fi.ImageClassificationData.from_fiftyone(
        predict_dataset=samples, **data_kwargs
    )
    embeddings = flash.Trainer(**trainer_kwargs).predict(
        model, datamodule=datamodule
    )
    embeddings = np.stack(sum(embeddings, []))

    if embeddings_field is not None:
        samples.set_values(embeddings_field, embeddings)
        return

    return embeddings


def _get_output(model, confidence_thresh, store_logits):
    if isinstance(model, fi.ImageClassifier):
        prev_args = {}
        try:
            prev_args = dict(inspect.getmembers(model.output))
        except AttributeError as e:
            pass

        kwargs = {
            "multi_label": prev_args.get("multi_label", False),
            "store_logits": store_logits,
        }

        if "threshold" in prev_args:
            kwargs["threshold"] = prev_args["threshold"]

        if confidence_thresh is not None:
            kwargs["threshold"] = confidence_thresh

        return fc.FiftyOneLabelsOutput(**kwargs)

    if isinstance(model, fi.ObjectDetector):
        return fdo.FiftyOneDetectionLabelsOutput(threshold=confidence_thresh)

    if isinstance(model, fi.SemanticSegmentation):
        return fso.FiftyOneSegmentationLabelsOutput()

    raise ValueError(
        "Unsupported model type %s. Supported model types are %s"
        % (type(model), _SUPPORTED_MODELS)
    )


_MODEL_TO_DATAMODULE_MAP = {
    fi.ObjectDetector: fi.ObjectDetectionData,
    fi.ImageClassifier: fi.ImageClassificationData,
    fi.SemanticSegmentation: fi.SemanticSegmentationData,
    fv.VideoClassifier: fv.VideoClassificationData,
}
