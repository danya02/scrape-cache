from .url import HttpController, SimpleFileResourceController
from .wallhaven import WallhavenController

download_methods = {'HttpController': HttpController, 'WallhavenController': WallhavenController, 'SimpleFileResourceController': SimpleFileResourceController}

