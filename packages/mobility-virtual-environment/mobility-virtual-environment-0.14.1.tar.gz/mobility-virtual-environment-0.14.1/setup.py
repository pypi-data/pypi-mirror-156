# setup.py - this is the setup.py file to create a MoVE python package
#
# usage:     python3 -m build
#
# Marc Compere, comperem@gmail.com
# created : 20 Jun 2022
# modified: 25 Jun 2022

import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="mobility-virtual-environment",
    version="0.14.1",
    author="Marc Compere",
    author_email="comperem@gmail.com",
    description="The Mobility Virtual Environment (MoVE) tests multi-vehicle mobility scenarios.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    keywords="multi-vehicle, multi-agent, simulation, mobility, v2v",
    url="https://gitlab.com/comperem/move",
    project_urls={
        "Bug Tracker": "https://github.com/pypa/sampleproject/issues",
    },
    
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Science/Research",
        "Topic :: Communications",
        "Topic :: Scientific/Engineering",
        "Topic :: Scientific/Engineering :: Physics",
        "Topic :: Scientific/Engineering :: Visualization",
        "Topic :: System :: Networking",
        "Programming Language :: Python :: 3",
        "Operating System :: POSIX :: Linux",
        #"Operating System :: OS Independent",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)"
    ],
    
    package_dir={"": "src"},
    #packages=setuptools.find_packages(where="src"),
    packages=['move/core','move/data_displays','move/routes','move/scenario','move/veh_model'],
    include_package_data=True, # include non-.py files as well
    #packages=['package_name', 'package_name.test'],
    
    #scripts=['src/move/vehicle_model/main_veh_model.py'], #,'bin/script2'], # *python* scripts
    scripts=['src/move/bin_src/run_move_dashboard.sh', 'src/move/bin_src/run_move_live_mapping.sh',
             'src/move/bin_src/test_python_packages.py', 'src/move/bin_src/test_parallel_ssh_with_screen.py',
             'src/move/bin_src/killall_vehicle_models.sh'],
             
    python_requires=">=3.7",
    install_requires=[  "wheel", "screen", "numpy", "msgpack", "msgpack-numpy",
                        "parallel-ssh", "utm", "bokeh", "imutils", "matplotlib",
                        "opencv-python"], # "requests <= 0.4"],
)











