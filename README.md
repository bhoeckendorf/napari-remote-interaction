# napari-remote-interaction

<!--
[![License](https://img.shields.io/pypi/l/napari-remote-interaction.svg?color=green)](https://github.com/bhoeckendorf/napari-remote-interaction/raw/main/LICENSE)
[![PyPI](https://img.shields.io/pypi/v/napari-remote-interaction.svg?color=green)](https://pypi.org/project/napari-remote-interaction)
[![Python Version](https://img.shields.io/pypi/pyversions/napari-remote-interaction.svg?color=green)](https://python.org)
[![tests](https://github.com/bhoeckendorf/napari-remote-interaction/workflows/tests/badge.svg)](https://github.com/bhoeckendorf/napari-remote-interaction/actions)
[![codecov](https://codecov.io/gh/bhoeckendorf/napari-remote-interaction/branch/main/graph/badge.svg)](https://codecov.io/gh/bhoeckendorf/napari-remote-interaction)
[![napari hub](https://img.shields.io/endpoint?url=https://api.napari-hub.org/shields/napari-remote-interaction)](https://napari-hub.org/plugins/napari-remote-interaction)
-->

Remotely interacts with [napari]

## Usage

### Setup

1. Enable remote interaction in napari  
   * Start remote interaction in napari with using either of the following menus:  
     * Tools &rarr; Utilities &rarr; Remote interaction  
     * Plugins &rarr; napari-remote-interaction: Remote interaction  
   * Set hostname, port and key arguments, then click "Connect"
2. Create RemoteInteractor in external process or on external host
   ```python
   from napari_remote_interaction import RemoteInteractor
   viewer = RemoteInteractor(hostname="*", port=5555, key="#mykey789")
   ```

### Interaction

`RemoteInteractor` is intended to eventually mirror the API of `napari.Viewer` as closely and completely as feasible. 
Currently, there are a few peculiarities:  

```python
# Create random test image
import numpy as np
image_czyx = np.random.randint(0, 255, (2, 32, 64, 64), np.uint8)

# View image with remotely running napari GUI
call = viewer.add_image(image_czyx, scale=[2.0, 1.0, 1.0], channel_axis=0)
viewer(call)
```

Note that we first called `viewer.add_image` normally, and then passed the return value to `viewer`. This pattern 
should work for most of `napari.Viewer`'s methods.

We can do a few more things, for example:
```python
# Get nr of layers. The extra call is taken care of in the case of len.
len(viewer.layers)

# Get data from our remote napari GUI (extra call needed again)
viewer(
    viewer.layers[0].data[0, :]
)

# Get an exception (IndexError) that is raised inside the remote napari GUI
viewer(
    viewer.layers[999]
)
```

----------------------------------

This [napari] plugin was generated with [Cookiecutter] using [@napari]'s [cookiecutter-napari-plugin] template.

<!--
Don't miss the full getting started guide to set up your new package:
https://github.com/napari/cookiecutter-napari-plugin#getting-started

and review the napari docs for plugin developers:
https://napari.org/plugins/stable/index.html
-->

## Installation

<!--
You can install `napari-remote-interaction` via [pip]:
```shell
pip install napari-remote-interaction
```
-->

To install the latest development version:
```shell
pip install git+https://github.com/bhoeckendorf/napari-remote-interaction.git
```

To update to the latest development version:
```shell
pip install --force-reinstall --no-deps git+https://github.com/bhoeckendorf/napari-remote-interaction.git
```


## Contributing

Contributions are very welcome. Tests can be run with [tox], please ensure
the coverage at least stays the same before you submit a pull request.

## License

Distributed under the terms of the [Apache Software License 2.0] license,
"napari-remote-interaction" is free and open source software

## Issues

If you encounter any problems, please [file an issue] along with a detailed description.


[napari]: https://github.com/napari/napari
[Cookiecutter]: https://github.com/audreyr/cookiecutter
[@napari]: https://github.com/napari
[MIT]: http://opensource.org/licenses/MIT
[BSD-3]: http://opensource.org/licenses/BSD-3-Clause
[GNU GPL v3.0]: http://www.gnu.org/licenses/gpl-3.0.txt
[GNU LGPL v3.0]: http://www.gnu.org/licenses/lgpl-3.0.txt
[Apache Software License 2.0]: http://www.apache.org/licenses/LICENSE-2.0
[Mozilla Public License 2.0]: https://www.mozilla.org/media/MPL/2.0/index.txt
[cookiecutter-napari-plugin]: https://github.com/napari/cookiecutter-napari-plugin

[file an issue]: https://github.com/bhoeckendorf/napari-remote-interaction/issues

[napari]: https://github.com/napari/napari
[tox]: https://tox.readthedocs.io/en/latest/
[pip]: https://pypi.org/project/pip/
[PyPI]: https://pypi.org/
