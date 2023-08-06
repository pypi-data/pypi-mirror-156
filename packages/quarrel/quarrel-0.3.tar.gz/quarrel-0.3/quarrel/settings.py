import os

template_dirs = os.environ.get('QUARREL_TEMPLATE_DIRS') or '.'
template_dirs = template_dirs.split(',')
