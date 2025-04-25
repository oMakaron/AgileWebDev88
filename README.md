# AgileWebDev88
An agile web dev project by group 88 of UWA's CITS3403
Name and readme soon to be changed after discussion

## Getting Set Up
The below steps should be sufficient to get the project up and running on your
local machine (at least for Unix-like operating systems).

### 1. Cloning the Repo
```bash
git clone https://github.com/oMakaron/AgileWebDev88.git
cd AgileWebDev88
```

### 2. Setting up a Virtual Environment
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Installing Requirements
```bash
pip install -r requirements.txt
```

### 4. Use
```bash
flask run
```

## Testing

### 1. Running Tests
To run the tests, run the following:
```bash
coverage run -m unittest discover tests/
```
This will run every file found in `tests/` that begins with `test_` and report any failures, as
well as generate a report of what lines in the project that the tests actually cover.

To view the coverage, run the following:
```bash
coverage report -m
```

### 2. Writing Tests
Tests are found in the `tests/` directory. Each file in the directory should correspond to a file in `app/`.

Tests follow this template:
```python
class Test(TestCase):

    def test_something(self) -> None:
        # ... test logic here ...
        self.assertEqual(expected, given)
```

Each test should be specific and cover a narrow range of expected behaviour, and have a descriptive
name explaining what the test is trying to do.

You should aim for high coverage in the `coverage report`. To find out what you haven't tested, look
at the the `Missing` column of the output to find what lines aren't covered. If something doesn't make
sense to be tested, add `# pragma: no cover` after the line.

## Requirements
This project uses Flask and it's assosciated dependencies. The full list can be
found in ``requirements.txt``.
