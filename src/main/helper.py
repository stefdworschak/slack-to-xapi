import hashlib
import logging

logger = logging.getLogger(__name__)


def get_or_none(model, **kwargs):
    try:
        return model.objects.get(**kwargs)
    except model.DoesNotExist:
        logger.warning(f'User matching query does not exist: {kwargs}')
    except model.MultipleObjectsReturned:
        logger.warning(f'Multiple objects returned for query: {kwargs}')
    return None


def create_sha1(email):
    hashed_string = hashlib.sha1()
    hashed_string.update(bytes(email, 'utf-8'))
    return hashed_string.hexdigest()
