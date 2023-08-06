import os

from pdf2image import convert_from_path

from . import files
from . import _C


DPI = _C.DPI


def get_imgs_from_pdf(filedir,
                      dpi=DPI,
                      ):
    imgs = convert_from_path(filedir, dpi=dpi)
    return imgs


def save_imgs_from_pdf(filedir, save_path,
                       dpi=DPI,
                       fext='png',
                       ):
    filename = os.path.split(filedir)[-1]
    imgs = convert_from_path(filedir, dpi=dpi)
    for k, img in enumerate(imgs):
        new_filename = f'{os.path.splitext(filename)[0]}.{k}.{fext.lower()}' if len(imgs) > 1 else f'{os.path.splitext(filename)[0]}.{fext.lower()}'
        new_filedir = os.path.join(save_path, new_filename)
        files.mkdirs_for_filedir(new_filedir)
        img.save(new_filedir, fext.upper())
