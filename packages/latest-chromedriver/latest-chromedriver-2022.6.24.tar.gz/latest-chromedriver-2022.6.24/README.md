# Latest ChromeDriver

"Latest ChromeDriver" is a module for python scirpts in order to find the correct version of the ChromeDriver depending on Google Chrome version.

## Purpose

The purpose of this module is not to be deployed to live system like webservers or similar.

This module is intended for use in scripts that are running on different client machines, where Google Chrome could be in different versions or auto updated.

## Getting Started

These instructions will get you a copy of the project up and running on your local machine on a windows system.

### Prerequisites

In order to install this module you need to have:

* Google Chrome
* Python >= 3

### Installing

Installation is pretty forward and it is done through pip

```
pip install latest-chromedriver
```

A basic use can be achieved like:

```
import latest_chromedriver

latest_chromedriver.safely_set_chromedriver_path()
```


## Built With

* [logzero](https://logzero.readthedocs.io/en/latest/) - A simple library for easy logging (could change it to standard logging module)
* [requests](https://requests.readthedocs.io/en/latest/) - Requests is an elegant and simple HTTP library for Python, built for human beings
* [ubelt](https://ubelt.readthedocs.io/en/latest/ubelt.html) - A “utility belt” of commonly needed utility and helper functions
* [py-cpuinfo](https://github.com/workhorsy/py-cpuinfo) - Gets CPU info with pure Python

## Contributing

Please read [CONTRIBUTING.md](CONTRIBUTING.md) for details on our code of conduct, and the process for submitting pull requests to us.

## Authors

* **Charalampos Gkikas** - *Initial work* - [hargikas](https://github.com/hargikas)

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details
