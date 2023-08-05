from setuptools import find_packages, setup


setup(
    name='easy-megadock',
    version="0.0",
    packages=find_packages(where='.'),
    install_requires=["tqdm"],
    # data_files=[
    #   ('tools/', ['tools/megadock-gpu',
    #               'tools/decoygen',]),
    #   ('needlib/', ['lib/libcudart.so.8.0',
    #                 'lib/libcufft.so.8.0',]),
                         
    # ],
)