from collections import defaultdict
import json
import logging


APP_NAME = 'q'

logger = logging.getLogger(__name__)


class Config():
    def __init__(self):
        self.loaded_json = defaultdict(dict)

    def load_json(self, filename):
        if filename not in self.loaded_json:
            try:
                with open(filename, 'r') as f:
                    self.loaded_json[filename] = json.load(f)
            except Exception as e:
                logger.warn('Error loading {}: {}'.format(filename, e))
        return self.loaded_json[filename]

    def save_json(self, data, filename):
        try:
            with open(filename, 'w') as f:
                json.dump({key: list(value) for key, value in data.items()}, f)
        except Exception as e:
            logger.error('Error saving {}: {}'.format(filename, e))
            logger.error(data)

    def get_aws_credentials(self, decode=False):
        return self._get_material_set('aws_material_set', decode)

    def get_yelp_credentials(self, decode=False):
        return self._get_material_set('yelp_material_set', decode)

    def get_spotify_credentials(self, decode=True):
        return self._get_material_set('spotify_material_set', decode)

    @property
    def irc_verify_ssl(self):
        return self.get_boolean(None, 'irc_verify_ssl')


config = Config()
