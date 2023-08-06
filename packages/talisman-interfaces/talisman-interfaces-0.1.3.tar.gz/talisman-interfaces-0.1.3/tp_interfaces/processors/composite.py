from typing import Iterable, Optional, Sequence, Tuple, Type, TypeVar

from tdm.abstract.datamodel import AbstractTreeDocumentContent
from tdm.datamodel import TalismanDocument

from tp_interfaces.abstract import AbstractCompositeModel, AbstractDocumentProcessor, ImmutableBaseModel
from tp_interfaces.abstract.model.model import MergeModel

_DocumentContent = TypeVar('_DocumentContent', bound=AbstractTreeDocumentContent)
_Config = TypeVar('_Config', bound=ImmutableBaseModel)


class SequentialConfig(ImmutableBaseModel):
    configs: Optional[Tuple[ImmutableBaseModel, ...]]


class SequentialDocumentProcessor(
    AbstractCompositeModel[AbstractDocumentProcessor],
    AbstractDocumentProcessor[SequentialConfig, _DocumentContent]
):

    def __init__(self, processors: Iterable[AbstractDocumentProcessor], *, merge: bool = True):
        merged = _merge_models(processors) if merge else processors

        AbstractCompositeModel[AbstractDocumentProcessor].__init__(self, merged)
        AbstractDocumentProcessor.__init__(self)

        config_types = tuple(processor.config_type for processor in self._models)

        class _SequentialConfig(SequentialConfig):
            configs: Optional[Tuple[config_types]]

        self._config_type = _SequentialConfig
        self._config_types = config_types

    def process_doc(self, document: TalismanDocument[_DocumentContent], config: _Config) -> TalismanDocument[_DocumentContent]:
        return self.process_docs([document], config)[0]

    def process_docs(
            self,
            documents: Sequence[TalismanDocument[_DocumentContent]],
            config: SequentialConfig
    ) -> Tuple[TalismanDocument[_DocumentContent], ...]:
        configs = config.configs if config.configs is not None else [model.config_type() for model in self._models]
        for processor_idx, processor in enumerate(self._models):
            documents = processor.process_docs(documents, configs[processor_idx])
        return documents

    @property
    def config_type(self) -> Type[SequentialConfig]:
        return self._config_type


def _merge_models(models: Iterable[AbstractDocumentProcessor]) -> Iterable[AbstractDocumentProcessor]:
    current_merger: Optional[MergeModel] = None
    for model in models:
        if current_merger is not None:
            if current_merger.can_be_merged(model):
                current_merger = current_merger.merge(model)
            else:
                yield current_merger
                current_merger = None
        if current_merger is None:
            if isinstance(model, MergeModel):
                current_merger = model
            else:
                yield model
    if current_merger is not None:
        yield current_merger
