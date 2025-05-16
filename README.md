# DataVizApp
An agile web dev project by group 88 of UWA's CITS3403
  
## Purpose and Design 
This project is a data visualisation web application that helps users better understand their data. Users can upload CSV files, choose which columns to use as the X and Y axes, and then generate clear, visual graphs. They can also share selected charts with their friends on the platform. The goal is to make data easier to see, explore, and share.

The design of the application focuses on being simple, useful, and clean. It uses TailwindCSS to create a clear and responsive interface. The layout makes it easy for users to upload data, view all the charts they have generated, and share specific charts with others. The app is especially helpful for students or non-technical users who want to quickly visualise data without writing code.

## Group Members

| UWA ID   | Name          | GitHub Username |
|----------|-------------  |-----------------|
| 23810522 | Yuki Wei      | yuki-kii        |
| 23821639 | Daniel Jones  | DanielEJones    |
| 24328931 | Nick Alexander| oMakaron        |
| 23920389 | Will Vetter   | WillVetter      |

## Getting Set Up
The below steps should be sufficient to get the project up and running on your local machine (at least for Unix-like operating systems).


### 1. Cloning the Repo
```bash
git clone https://github.com/oMakaron/AgileWebDev88.git
cd AgileWebDev88
```

### 2. Set up the project
You can either use the install script `setup.py` or follow the below instructions:

### 2. Setting up a Virtual Environment
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Installing Requirements
```bash
pip install -r requirements.txt
```

### 4. Setting Up TailwindCSS (Version 3)
The `output.css` file is ignored in the repository and must be generated locally. Follow these steps:

1. **Install TailwindCSS**:  
   Ensure you have Node.js and npm installed. Then, install TailwindCSS version 3:
   ```bash
   npm install -D tailwindcss@3
   npx tailwindcss init
   ```

2. **Generate the Output CSS File**:  
   Run the following command to generate `static/css/output.css`:
   ```bash
   npx tailwindcss -i app/static/css/input.css -o app/static/css/output.css --watch
   ```

   This will create the `output.css` file in the `static/css` directory.

### 5. Setting Up the Database

We use **Flask-SQLAlchemy** to manage the database.

First, we need to let flask know where the app is:
```bash
export FLASK_APP=main.py
```

To update the database, run the following:
```bash
flask db migrate -m "migration message" # if you are the one who made changes
flask db upgrade
```

### 6. Running the Application
In order for the application to run, you will need to have a secret key set within the environment. You can set one using the following if you didn't set one with the install script:
```bash
export FLASK_SECRET_KEY='your-key-here'
```

Once that has been done, run the `main.py` file:
```bash
python main.py
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
        # ... test services here ...
        self.assertEqual(expected, given)
```

Each test should be specific and cover a narrow range of expected behaviour, and have a descriptive
name explaining what the test is trying to do.

You should aim for high coverage in the `coverage report`. To find out what you haven't tested, look
at the `Missing` column of the output to find what lines aren't covered. If something doesn't make
sense to be tested, add `# pragma: no cover` after the line.

## Requirements
This project uses Flask and its associated dependencies. The full list can be found in `requirements.txt`.

## Notes
- The `output.css` file is ignored in the repository (`.gitignore`) and must be generated locally.
- Use the `--watch` flag while developing to automatically rebuild the `output.css` file when changes are made.
