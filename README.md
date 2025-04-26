# AgileWebDev88
An agile web dev project by group 88 of UWA's CITS3403  
Name and readme soon to be changed after discussion

## Getting Set Up
The below steps should be sufficient to get the project up and running on your local machine (at least for Unix-like operating systems).

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
   npx tailwindcss -i ./static/css/input.css -o ./static/css/output.css --watch
   ```

   This will create the `output.css` file in the `static/css` directory.

### 5. Running the Application
```bash
flask run
```

## Requirements
This project uses Flask and its associated dependencies. The full list can be found in `requirements.txt`.

## Notes
- The `output.css` file is ignored in the repository (`.gitignore`) and must be generated locally.
- Use the `--watch` flag while developing to automatically rebuild the `output.css` file when changes are made.
