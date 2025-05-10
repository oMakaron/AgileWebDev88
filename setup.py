from shutil import which
from subprocess import check_call
from sys import executable, platform
from pathlib import Path


def main():
    print("Setting up project...")

    venv_path = Path("venv")
    if not venv_path.exists():
        print("Creating virtual environment...", end=" ")
        check_call([executable, "-m", "venv", str(venv_path)])
        print("done.")
    else:
        print("Virtual environment already exists.")

    pip_exec = venv_path / ("Scripts" if platform == "win32" else "bin") / "pip"
    flask_exec = venv_path / ("Scripts" if platform == "win32" else "bin") / "flask"

    print("Installing dependencies...")
    check_call([str(pip_exec), "install", "-r", "requirements.txt"])

    print("Installing Tailwind...")
    if not (npm_exec := which("npm")):
        print("npm is not installed. Please install it and rerun this script.")
        return


    check_call([npm_exec, "install", "-D", "tailwindcss@3"])

    print("Building CSS...")
    if not (npx_exec := which("npx")):
        print("npx is not installed. Please install it and rerun this script.")
        return

    check_call([
        npx_exec, "tailwindcss",
        "-i", "app/static/css/input.css",
        "-o", "app/static/css/output.css"
    ])

    env_path = Path(".env")
    if not env_path.exists():
        print("Creating .env file...")
        secret_key = input("Please enter your secret key: ")
        env_path.write_text(
            f"FLASK_APP=main.py\n"
            f"FLASK_SECRET_KEY=\"{secret_key}\"\n"
        )
    else:
        print(".env file already exists.")

    print("Initializing database...")
    check_call([str(flask_exec), "db", "upgrade"])

    print("Setup complete.")


if __name__ == "__main__":
    main()

