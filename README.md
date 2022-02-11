# Chemical Data Extractor

<p align="center">
<a href="https://github.com/ag-gipp/PythonProjectTemplate/actions/workflows/release.yml"><img alt="Actions Status" src="https://github.com/ag-gipp/PythonProjectTemplate/actions/workflows/release.yml/badge.svg">  
<a href="https://github.com/ag-gipp/PythonProjectTemplate/actions/workflows/main.yml"><img alt="Actions Status" src="https://github.com/ag-gipp/PythonProjectTemplate/actions/workflows/main.yml/badge.svg?branch=main">
<a href="https://github.com/ag-gipp/PythonProjectTemplate/blob/main/LICENSE"><img alt="License: MIT" src="https://black.readthedocs.io/en/stable/_static/license.svg"></a>
<a href="https://github.com/psf/black"><img alt="Code style: black" src="https://img.shields.io/badge/code%20style-black-000000.svg"></a>
</p>

This chemical data extractor reads XML files parsed by <a href="https://github.com/kermitt2/grobid">Grobid</a> and extracts chemical entities from these files.


## Getting Started

Install the dependencies from requirements.txt. Note that due to dependencies a direct installation may not be possible in that case run the command 

```console
python3 -m pip install chemdataextractor2 --use-feature=2020-resolver
```

to install chemdataextractor2 with all of its dependencies. 


## Contributing

Fork the repo, make changes and send a PR. We'll review it together!

## License

This project is licensed under the terms of MIT license. Please see the LICENSE file for details.
