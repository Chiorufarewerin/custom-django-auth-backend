import wrapt

from .logging import logger

DEFAULT_AUTHENTICATION_BACKEND = 'django.contrib.auth.backends.ModelBackend'


def check_default_authentication_backend():
    try:
        from django.conf import settings
        if 'django.contrib.auth.backends.ModelBackend' not in settings.AUTHENTICATION_BACKENDS:
            return False
    except Exception:
        return False
    return True


def wrapt_authentication_backend(backend_class):
    backend_path = f'{backend_class.__module__}.{backend_class.__name__}'
    if not check_default_authentication_backend():
        logger.warning('Модуль %s не импортирован, так как не обнаружен стандартный бэкенд', backend_path)

    def load_backends_wrapper(wrapped, instance, args, kwargs):
        from django.conf import settings
        if backend_path not in settings.AUTHENTICATION_BACKENDS:
            if type(settings.AUTHENTICATION_BACKENDS) is tuple:
                settings.AUTHENTICATION_BACKENDS = (backend_path, ) + settings.AUTHENTICATION_BACKENDS
            elif type(settings.AUTHENTICATION_BACKENDS) is list:
                settings.AUTHENTICATION_BACKENDS = [backend_path, ] + settings.AUTHENTICATION_BACKENDS
            else:
                logger.error('Could not import %s to django', backend_path)
        return wrapped(*args, **kwargs)
    try:
        wrapt.wrap_function_wrapper('django.contrib.auth.__init__', '_get_backends', load_backends_wrapper)
