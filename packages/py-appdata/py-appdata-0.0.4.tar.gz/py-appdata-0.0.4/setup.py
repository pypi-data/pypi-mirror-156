# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['appdata']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'py-appdata',
    'version': '0.0.4',
    'description': 'Small utility library to provide easy access to files and key-value store in an application directory',
    'long_description': '# Python App Data\nThe py-appdata aims to solve the issue of storing simple application data and accessing it in an easy way.\n\nThe core idea is to expose a simple interface that has two properties\n - A get/set interface to simple values\n - A simple way of saving and retrieving files from the application directory\n\n## Stores\nThe `AppData` class provides an interface to two storage-abstractions: A file system and a key-value store. This lets\nyou easily save/retrieve files as well as setting/loading key/values which is a common app-data usage.\n\n## Get started\n````python\nfrom appdata import appdata\nfrom datetime import datetime, timezone\n\n# defaults to app_data\nappdata.set_file_store("my_app_data_dir")\n\n# defaults to kv_store\nappdata.set_key_value_store("my_store")\n\nappdata["last_login"] = datetime.utcnow().replace(tzinfo=timezone.utc)\n\nwith appdata.write("some_file.txt") as f:\n    f.write("Mjello")\n````\n## Auto save\nThe AppData object will auto save as a default. This means, whenever the KeyValue-store has been altered, it will \nautomatically flush.\nThis can be disabled, but then you are in charge of flushing. This can either be via the context manager or directly\nvia the save method.\n````python\nfrom appdata import appdata\n\nappdata.set_auto_save(False)\n\nwith appdata:\n    appdata["kv1"] = "something"\n    appdata["kv2"] = "something else"\n    \n# Or directly\n\nappdata["kv3"] = "something completely else"\nappdata.save()\n\n\n````\n\n## Dataclass support\nIf you like type hints, you can register a `dataclass` instance as a proxy for the key-value store\n```python\nfrom appdata import appdata\nfrom datetime import datetime, timezone\nfrom dataclasses import dataclass\n\n\n# Define the dataclass\n@dataclass\nclass KV:\n    last_login: datetime = None\n\n\n# Create an object to be referenced and register it to appdata\nkv = KV()\nappdata.register(kv)\n\n\n# The KeyValue object now acts as a proxy, and can be used throughout your project\nkv.last_login = datetime.utcnow().replace(tzinfo=timezone.utc)\n```\n\n## Custom KeyValue Store\nYou can create a custom KeyValue store by extending the `KeyValueStore` base class, or the `DictKeyValueStore` if you \nwant to use a dict internally, and serialize it in a special way. Remember to registering it to the AppData object.\n````python\nfrom appdata import appdata\nfrom appdata.kv_store import KeyValueStore\n\nclass MyKeyValueStore(KeyValueStore):\n    \n    ...\n\n\n# defaults to app_data\nappdata.set_key_value_store(MyKeyValueStore())\n````\n\n## Custom File Store\nYou can create a custom file store by extending the `FileStore` class and registering it to the AppData object\n````python\nfrom appdata import appdata\nfrom appdata.file_store import FileStore\n\nclass MyFileStore(FileStore):\n    \n    ...\n\n\n# defaults to app_data\nappdata.set_file_store(MyFileStore())\n````\n',
    'author': 'Jesper Jensen',
    'author_email': 'mail@jeshj.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/gedemagt/appdata',
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.7',
}


setup(**setup_kwargs)
