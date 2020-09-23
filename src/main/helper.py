import logging

logger = logging.getLogger(__name__)


def get_or_none(model, **kwargs):
    try:
        return model.objects.get(**kwargs)
    except model.DoesNotExist as does_not_exist:
        logger.warning(f'User matching query does not exist: {kwargs}')
    except model.MultipleObjectsReturned as multiple_returned:
        logger.warning(f'User matching query does not exist: {kwargs}')
    return None
