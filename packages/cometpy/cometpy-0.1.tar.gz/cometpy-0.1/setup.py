import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="cometpy",
    version="0.1",
    author="Gokcen Kestor",
    author_email="gokcen.kestor@pnnl.gov",
    description="Comet Domain Specific Compiler as Python package",
    long_description=long_description,
    long_description_content_type="text/markdown",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
    ],
    packages=setuptools.find_packages(),
    package_dir={"cometpy": "cometpy"},
    package_data={"cometpy": ["comet_build/bin/comet-opt" , "llvm_build/bin/mlir-opt", "llvm_build/bin/mlir-translate","llvm_build/bin/lli",\
         "comet_build/lib/libcomet_runner_utils.dylib"]},
    python_requires=">=3.6",
)