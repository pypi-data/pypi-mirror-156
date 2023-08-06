import os
import sys
import subprocess
from setuptools import setup, find_packages
from setuptools.command.build_ext import build_ext
from setuptools.command.build_py import build_py

TORCH_VERSION = '1.11.0'
CONDA_PREFIX = os.environ.get("CONDA_PREFIX", None)


class Build(build_ext):
    """Customized setuptools build command - builds protos on build."""
    def run(self):
        run_makefile()
        build_ext.run(self)


def boost_env_prefix(conda_prefix):
    split_path = list(os.path.split(conda_prefix))
    if split_path[-2] == "envs" and "conda" in split_path[-3]:
        split_path[-1] = "boost"
    elif "conda" in split_path[-1]:
        split_path += ["envs", "boost"]
    return "/" + "/".join(split_path)


def run_makefile():
    # if user use conda run makefile
    if CONDA_PREFIX is not None:
        print("Download version with accelerated calculation.")

        # check if gpu exists
        import torch
        if not torch.cuda.is_available():
            print("Does not support GPU.\nBuild accelerated features.")
            path = os.getcwd() + "/runMakefileCPU.py"
        else:
            print("Support GPU.\nBuild accelerated features for GPU.")
            path = os.getcwd() + "/runMakefileGPU.py"

        # build Makefile
        os.chdir("src/graphMeasures/features_algorithms/accelerated_graph_features/src")
        print("cd ed")
        os.system("conda env create -f env.yml --force")
        print("created conda env")
        cmd = '. ' + CONDA_PREFIX + '/etc/profile.d/conda.sh && conda activate boost'
        print(cmd)
        subprocess.call(cmd, shell=True, executable='/bin/bash')
        print("did subprocess thingy")
        command = "conda run -n boost python " + path
        process = subprocess.Popen(
            command.split(), stdout=subprocess.PIPE
        )
        print("another subprocessing")
        output = process.stdout.read()
        print(output)
        output, error = process.communicate()
        print(output)
        print(error)

    else:
        print("Does not use Conda environment or Linux.\nDownload version without accelerated calculation.")


if __name__ == '__main__':
    # run_makefile()

    # get text for setup
    with open("requirements.txt") as f:
        requirements = [l.strip() for l in f.readlines()]
        # if CONDA_PREFIX is None:
        #     requirements.append(f"torch~={TORCH_VERSION}")
        # else:
        #     requirements.append(f"pytorch~={TORCH_VERSION}")

    with open("README.md") as r:
        readme = r.read()

    setup(
        name="graph-measures",
        version="0.1.28",
        license="GPL",
        maintainer="Amit Kabya",
        author="Itay Levinas",
        maintainer_email="kabya.amit@gmail.com",
        url="https://github.com/AmitKabya/graph-measures",
        description="A python package for calculating "
                    "topological graph features on cpu/gpu",
        long_description=readme,
        long_description_content_type="text/markdown",
        keywords=["gpu", "graph", "topological-features-calculator"],
        description_file="README.md",
        license_files="LICENSE.rst",
        install_requires=requirements,
        packages=find_packages('src'),
        python_requires=">=3.6.8",
        include_package_data=True,
        has_ext_modules=lambda: True,
        package_dir={"": "src"},
        cmdclass={
            'build_ext': Build
        },
        classifiers=[
            'Programming Language :: Python',
            'Programming Language :: C++',
            'Operating System :: Unix',
            'Operating System :: POSIX :: Linux',

        ],
        easy_install="ok_zip"
    )
