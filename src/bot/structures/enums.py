"""Models."""

import enum


class GPTModel(enum.StrEnum):
    MODEL_3 = 'gpt-3.5-turbo-1106'
    MODEL_4 = 'gpt-4-1106-preview'
    OMNI = 'gpt-4o'


class DALLeResolutions(enum.StrEnum):
    SQUARE256 = '256x256'
    SQUARE512 = '512x512'
    SQUARE1024 = '1024x1024'
    VERTICAL1792 = '1792x1024'
    HORIZONTAL1792 = '1024x1792'


class DALLeQuality(enum.StrEnum):
    HD = 'hd'
    STANDARD = 'standard'


class RunStatus(enum.StrEnum):
    QUEUED = 'queued'
    COMPLETED = 'completed'
    REQUIRES_ACTION = 'requires_action'
    CANCELLED = 'cancelled'
    IN_PROGRESS = 'in_progress'
