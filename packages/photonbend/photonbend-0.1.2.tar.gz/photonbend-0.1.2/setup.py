# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['photonbend',
 'photonbend.core',
 'photonbend.exceptions',
 'photonbend.lens',
 'photonbend.projections',
 'photonbend.scripts',
 'photonbend.scripts.commands',
 'photonbend.utils']

package_data = \
{'': ['*']}

install_requires = \
['Pillow>=9.0.1,<10.0.0',
 'click>=8.0.4,<9.0.0',
 'numba>=0.55.1,<0.56.0',
 'numpy>=1.18,<1.22',
 'scipy>=1.8.0,<2.0.0']

entry_points = \
{'console_scripts': ['photonbend = photonbend.scripts.main:main']}

setup_kwargs = {
    'name': 'photonbend',
    'version': '0.1.2',
    'description': 'Photonbend allows one to convert photos between different sorts of lenses, rotate photos and make panoramas.',
    'long_description': "# Photonbend\nPhotonbend is a python module to handle photos, especially photos taken with fisheye lenses, and convert them between different kinds of lenses, FoV and types of photos like inscribed circles, cropped circles or even side-by-side double inscribed circles. It also allows you to rotate those photos, convert them to equirectangular panoramas or convert panoramas fisheye photos.\n\nIt can be used as a library to handle images on your own projects or it can be used as a standalone tool with its own set of commands to help you alter your images\n\n# Scripts\nWhen installing it sets up a script with 3 different commands to help you deal with your images\n\n## make-photo\nThis tool allows you to make a photo out of a panorama.\n\n### Make a 360 degrees photo with an equidistant lens\nThe example bellow creates a photo of type `inscribed`, with an `equidistant` lens, and a FoV of `360` degrees named `equidistant.jpg` from the panorama in file `./original/View_From_The_Deck_6k.jpg`\n\n> `photonbend make-photo --type inscribed --lens equidistant --fov 360 ./original/View_From_The_Deck_6k.jpg equidistant.jpg`\n\n[![Panorama](examples/original/View_From_The_Deck_small.jpg)](examples/original/View_From_The_Deck_6k.jpg)\n[![Equidistant Projection (lens)](examples/equidistant_small.jpg)](examples/equidistant.jpg)\n\n## alter-photo\nThis tool allows you to change your photos by exchanging lenses, FoV, types and rotate your images.\n\n### Change of projection (Lens)\nThe example bellow changes the photo lenses from `equidistant` projection to `equisolid` projection.\n\n> `photonbend alter-photo --itype inscribed --otype inscribed --ilens equidistant --olens equisolid --ifov 360 --ofov 360 equidistant.jpg equisolid.jpg`\n\n[![Equidistant Projection (lens)](examples/equidistant_small.jpg)](examples/equidistant.jpg)\n[![Equisolid Projection (lens)](examples/equisolid_small.jpg)](examples/equisolid.jpg)\n\n### Change of FoV\nThe example bellow changes the photo `equidistant.jpg`. Its FoV from `360` degrees to `180`, producing the image `equidistant-180.jpg`.\n\n> `photonbend alter-photo --itype inscribed --otype inscribed --ilens equidistant --olens equidistant --ifov 360 --ofov 180 equidistant.jpg equidistant-180.jpg` \n\n[![Fov 360 degrees](examples/equidistant_small.jpg)](examples/equidistant.jpg)\n[![FoV 180 degrees](examples/equidistant-180_small.jpg)](examples/equidistant-180.jpg)\n\n**Notice there is no more data about half of view of the original image on the modified one (Can't see the floor anymore).**\n\n### Change of type\nThe example bellow changes the photo `equidistant.jpg`. Its type from `inscribed` to `double`, producing `equidistant-double.jpg`.\n\n**Note**: Notice we also have to **change the FoV** when producing a **double inscribed** image. That happens because the double inscribed image uses two inscribed images side by side on a single image file. It is meant to be used with full 360 degrees images, but its FoV describes the maximum FoV of each of its inscribed image.\n\n> `photonbend alter-photo --itype inscribed --otype double --ilens equidistant --olens equidistant --ifov 360 --ofov 195 equidistant.jpg equidistant-double.jpg` \n\n[![Fov 360 degrees](examples/equidistant_small.jpg)](examples/equidistant.jpg)\n[![FoV 180 degrees](examples/equidistant-double_small.jpg)](examples/equidistant-double.jpg)\n\n\n### Change of type, lens and FoV\nThe example bellow changes the photo `equidistant.jpg` from type `inscribed` to `full`, its lenses from `equidistant` to `rectilinear` and its FoV from `360` degrees to `140`, producing the image `rectlinear-full.jpg`.\n\n> `photonbend alter-photo --itype inscribed --otype full --ilens equidistant --olens rectilinear --ifov 360 --ofov 140 equidistant.jpg rectlinear-full.jpg` \n\n[![Equidistant Projection (lens)](examples/equidistant_small.jpg)](examples/equidistant.jpg)\n[![Equisolid Projection (lens)](examples/rectlinear-full_small.jpg)](examples/rectlinear-full.jpg)\n\n\n### Rotation\nThe example bellow changes the photo `equidistant.jpg`, rotating it `-90` degrees in pitch, `0` degrees in yaw and `0` degrees in roll, producion `equidistant-rotated.jpg`.\n\n> `photonbend alter-photo --itype inscribed --otype inscribed --ilens equidistant --olens equidistant --ifov 360 --ofov 360 --rotation -90 0 0 equidistant.jpg equidistant-rotated.jpg` \n\n[![Fov 360 degrees](examples/equidistant_small.jpg)](examples/equidistant.jpg)\n[![FoV 180 degrees](examples/equidistant-rotated_small.jpg)](examples/equidistant-rotated.jpg)\n\n### Combining it all\nThe example bellow changes the photo `equidistant.jpg` from type `inscribed` to `full`, its lenses from `equidistant` to `rectilinear` and its FoV from `360` degrees to `140`. It is also rotated by `-90` degrees in pitch, `195` degrees in yaw and `0` degrees in roll producing the image `rectlinear-140-full-rotated.jpg`.\n\n> `photonbend alter-photo --itype inscribed --otype full --ilens equidistant --olens rectilinear --ifov 360 --ofov 140 --rotation -90 195 0 equidistant.jpg rectlinear-140-full-rotated.jpg` \n\n[![Equidistant Projection (lens)](examples/equidistant_small.jpg)](examples/equidistant.jpg)\n[![Equisolid Projection (lens)](examples/rectlinear-140-full-rotated_small.jpg)](examples/rectlinear-140-full-rotated.jpg)\n\n## make-pano\nThis tool allows you to change create panoramas out of your photos\n\n### Make a panorama\nMake a panorama out of an `inscribed`, `equidistant` lens, `360` degrees FoV photo named `equidistant.jpg`, producing `panorama.jpg`.\n\n> `photonbend make-pano --type inscribed --lens equidistant --fov 360 equidistant.jpg panorama.jpg`\n\n[![Panorama](examples/panorama_small.jpg)](examples/panorama.jpg)\n\n\n### Make a rotated panorama\nMake a panorama out of an `inscribed`, `equidistant` lens, `360` degrees FoV photo named `equidistant.jpg`, producing `panorama_rotated.jpg`.\n> `photonbend make-pano --type inscribed --lens equidistant --fov 360 --rotation -90 90 0 equidistant.jpg panorama.jpg`\n\n[![Panorama](examples/panorama-rotated_small.jpg)](examples/panorama-rotated.jpg)\n\n\n## About the source image used on this example:\n\nAuthor: Bob Dass <br>\nTitle: View From The Deck <br>\nAvailable at: https://flickr.com/photos/54144402@N03/50677156243/in/faves-195024173@N05/ <br>\nLicense: Creative Commons - Attribution 2.0 <br>\n[License summary here](https://creativecommons.org/licenses/by/2.0/) <br>\n[License text here](https://creativecommons.org/licenses/by/2.0/legalcode) <br>",
    'author': 'Edson Moreira',
    'author_email': 'w.moreirae@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<3.11',
}


setup(**setup_kwargs)
