# SetPrecision

## About

- _**`SetPrecision`**_ is a small module providing a simple way to set the precision of a floating point number or decimal to the desired amount of digits following the decimal point.

---

## Installation

### Using PIP _(Recommended)_

> _Easiest_ method. Highly recommended over manual installation.

- To install _**`SetPrecision`**_ using `pip`, enter the following:

  ```python
  python -m pip install SetPrecision
  ```

- Done!

---

### Manual Installation

> _Not_ recommended.

1. Before use, navigate to intended installation location, and create a new directory.

2. Clone repository with the git client of your preference using the following command:

   - ```bash
     git clone https://github.com/schlopp96/SetPrecision/releases/latest
     ```

3. Install all dependencies for this package within said directory using:

   - ```bash
     pip install -r requirements.txt
     ```

- **(Optional)**: move installation directory to `"path/to/Python/Libs/site_packages"` to be able to import this package to a Python program like any other importable package.

- Done!

---

## Usage

- In order to use _**`SetPrecision`**_, start by importing the module to your Python environment:

  ```python
  from SetPrecision import set_precision
  ```

- Now, simply call the `set_precision` method and enter your desired number to be formatted as the `number` parameter, and the level of precision as the `precision` parameter:

  ```python

  >>> testA = 3.141592653589793 # Not necessary to set number as variable.

  >>> testA = set_precision(testA, 2)

  >>> print(testA)

  '3.15'

  >>> testB = 3.141592653589793

  >>> testB = set_precision(testB, 4)

  >>> print(testB)

  '3.1416'
  ```

> Note that the output is automatically rounded up when `number >= 5`, and down when `number < 5`.

- Both params can be entered in string format, and will output successfully assuming that both parameters can be cast to their appropriate types.
  - This is done automatically.

---

## Contact the Author

- If you have any questions, comments, or concerns that cannot be alleviated through the [project's GitHub repository](https://github.com/schlopp96/SetPrecision), please feel free to contact me through my email address:
  - `schloppdaddy@gmail.com`
