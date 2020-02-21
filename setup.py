import numpy

from setuptools import setup, find_packages
from setuptools.extension import Extension


numpy_include = numpy.get_include()

try:
    from Cython.Distutils import build_ext

    use_cython = True
    cmdclass = {"build_ext": build_ext}
except ImportError:
    use_cython = False
    cmdclass = {}
finally:
    print("Regenerating C extension code using Cython: {}".format(use_cython))

suffix = "pyx" if use_cython else "c"

entry_points = [
    "w_direct = westpa.commands.w_direct:main",
    "w_dumpsegs = westpa.commands.w_dumpsegs:main",
    "w_postanalysis_matrix = westpa.commands.w_postanalysis_matrix:main",
    "w_fork = westpa.commands.w_fork:main",
    "w_select = westpa.commands.w_select:main",
    "ploterr = westpa.commands.ploterr:main",
    "w_states = westpa.commands.w_states:main",
    "w_run = westpa.commands.w_run:main",
    "w_nto = westpa.commands.w_nto:main",
    "w_kinavg = westpa.commands.w_kinavg:main",
    "w_eddist = westpa.commands.w_eddist:main",
    "w_assign = westpa.commands.w_assign:main",
    "w_trace = westpa.commands.w_trace:main",
    "w_truncate = westpa.commands.w_truncate:main",
    "w_crawl = westpa.commands.w_crawl:main",
    "w_init = westpa.commands.w_init:main",
    "plothist = westpa.commands.plothist:main",
    "w_kinetics = westpa.commands.w_kinetics:main",
    "w_fluxanl = westpa.commands.w_fluxanl:main",
    "w_reweight = westpa.commands.w_reweight:main",
    "w_pdist = westpa.commands.w_pdist:main",
    "w_ipa = westpa.commands.w_ipa:main",
    "w_bins = westpa.commands.w_bins:main",
    "w_succ = westpa.commands.w_succ:main",
    "w_stateprobs = westpa.commands.w_stateprobs:main",
    "w_postanalysis_reweight = westpa.commands.w_postanalysis_reweight:main",
]

setup(
    name="westpa",
    packages=find_packages(),
    version="0.0.5",
    cmdclass=cmdclass,
    entry_points={"console_scripts": entry_points},
    install_requires=["blessings", "h5py", "pyyaml", "scipy", "matplotlib"],
    ext_modules=[
        Extension(
            "westpa.fasthist._fasthist",
            [
                "westpa/fasthist/_fasthist.{}".format(suffix)
            ],  # ,"fasthist/_fasthist_supp.c"],
            include_dirs=[".", numpy_include],
            # hack-ish; included since my dev box has trouble
            extra_compile_args=["-O3"],
        ),
        Extension(
            "westpa.mclib._mclib",
            ["westpa/mclib/_mclib.{}".format(suffix)],
            include_dirs=[".", numpy_include],
            extra_compile_args=["-O3"],
        ),
        Extension(
            "westpa.binning._assign",
            ["westpa/binning/_assign.{}".format(suffix)],
            include_dirs=[".", numpy_include],
            # hack-ish; included since my dev box has trouble
            extra_compile_args=["-O3"],
        ),
        Extension(
            "westpa.kinetics._kinetics",
            ["westpa/kinetics/_kinetics.{}".format(suffix)],
            include_dirs=[".", numpy_include],
            extra_compile_args=["-O3"],
        ),
        Extension(
            "westpa.reweight._reweight",
            ["westpa/reweight/_reweight.{}".format(suffix)],
            include_dirs=[".", numpy_include],
            extra_compile_args=["-O3"],
        ),
    ],
)
