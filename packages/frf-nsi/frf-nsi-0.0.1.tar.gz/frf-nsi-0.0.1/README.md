# Instructions how to Squat
- Run `pipenv sync` to create a new virtual environment `.venv` and install dependencies from `Pipfile.lock`
- Activate the virtual environment: `pipenv shell`
- In `setup.py`, replace `your-package-here` with the desired name of the package you want to squat on.
- If there is a `dist` folder, delete it
- Run `python setup.py sdist` to generate the source files inside a `dist` folder
- Upload the contents of `dist` using `twine upload dist/*`
- You may obtain FRF's Pypi account credentials by asking Siyi Fu or getting access to the company wide Bitwarden account

# TODO
- Add Dominic's Python package monitoring script.
- Setup automatic squatting using a pipeline with credentials from gitlab secrets. Run pipeline periodically to both monitor and squat any new FRF Python packages automatically.
    - Open to discuss whether or not we should squat on *every* package name or only those prepended by *frf* for example to avoid unecessary squatting.
- Set this to run on the engineering server.
