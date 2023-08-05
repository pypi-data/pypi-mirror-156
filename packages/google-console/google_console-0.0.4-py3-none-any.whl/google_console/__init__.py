import sys


try:
    __GC_SETUP__  # type: ignore
except NameError:
    __GC_SETUP__ = False


if __GC_SETUP__:
    sys.stderr.write("Partial import of google_console during the build process.\n")
else:
    from .scopes import scopes
    from .gmail import Gmail
    from .photos import Photos
    from .drive import Drive
    from .youtube import YouTube

    print("Welcome to google-console python library. This library created and maintained by MLnAi Lab")
    
    __all__ = ["scopes", "Gmail", "Photos", "Drive", "YouTube"]


__version__ = "0.0.4"
