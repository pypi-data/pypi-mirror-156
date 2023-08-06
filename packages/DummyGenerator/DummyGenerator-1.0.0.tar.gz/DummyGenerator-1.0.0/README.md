# Dummy Generator
### _Generate people that doesn't exist_

Ever needed a bunch of dummy accounts to teest your application? Dummy Generator is here to solve your problem.
This package will generate a person with personal details that doesn't exist, even with an image!

## Installation

Dummy Generator requires [Python](https://www.python.org/) 3.7 or higher to run.

```
python3 -m pip install DummyGenerator
```

## Usage

```py
from DummyGenerator import DummyGenerator
```

Create a person

```py
from DummyGenerator import DummyGenerator

person = DummyGenerator.create_person()
```

This will return a dict with name, gender, age, address and image.

```py
person = {
    "name": str
    "gender": str
    "age": int
    "address": str
    "image": bytearray
}
```

## Contact
**Discord:** Soerensen#1458
**Twitter:** @RealSoerensen

## License
MIT