# -*- encoding: utf-8 -*-

import os
import sys
import inspect

root_folder = os.path.realpath(
    os.path.abspath(
        os.path.join(
            os.path.split(
                inspect.getfile(
                    inspect.currentframe()
                )
            )[0],
            '..'
        )
    )
)
if root_folder not in sys.path :
    sys.path.insert(0, root_folder)
