import glob
import os
import sys


def all_depencies():
    cur = os.path.dirname(sys.modules['UIDep'].__file__)
    frame_work = ["PresentationFramework.Classic, Version=3.0.0.0, Culture=neutral, PublicKeyToken=31bf3856ad364e35",
                  "PresentationCore, Version=3.0.0.0, Culture=neutral, PublicKeyToken=31bf3856ad364e35"]
    dep = [os.path.abspath(c) for c in glob.glob(os.path.join(cur, '*.dll'))]
    return frame_work + dep
