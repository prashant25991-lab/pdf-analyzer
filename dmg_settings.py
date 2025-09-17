# -*- coding: utf-8 -*-
# DMG build settings for PDF Preflight Tool

import os.path

# Volume format (UDBZ is most efficient, HFS+ is most compatible)
format = 'UDBZ'

# Volume size (None means minimum size + 20MB of free space)
size = None

# Files to include in DMG
files = [ 'dist/PDF Preflight Tool.app' ]

# Symlinks to create 
symlinks = { 'Applications': '/Applications' }

# Volume name
volume_name = 'PDF Preflight Tool'

# DMG window settings
window_rect = ((100, 100), (640, 480))

# Icon size
icon_size = 128

# File positions in DMG window
icon_locations = {
    'PDF Preflight Tool.app': (170, 120),
    'Applications': (470, 120),
}

# Background (optional)
# background = 'dmg_background.png'

# License (optional)
# license = {
#     'default-language': 'en_US',
#     'licenses': { 'en_US': 'LICENSE.txt' },
#     'buttons': {
#         'en_US': [
#             b'English',
#             b'Agree',
#             b'Disagree', 
#             b'Print',
#             b'Save',
#             b'If you agree with the terms of this license, click "Agree" to access the software.  If you do not agree, press "Disagree".'
#         ]
#     }
# }