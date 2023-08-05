# Streamlit App

## Installation
First, you need to install the dependencies

### Using `pip`
```bash
cd {{ROOT_DIR_NAME}}/streamlit
pip install -r requirements.txt
```

### Using `conda`
```bash
cd {{ROOT_DIR_NAME}}/streamlit
conda install --file requirements.txt
```

### Using `poetry`
```bash
cd {{ROOT_DIR_NAME}}/streamlit
cat requirements.txt | xargs poetry add
```

## Usage
### Run the app
```bash
cd {{ROOT_DIR_NAME}}/streamlit
streamlit run App.py
```

## Multipage

To use the native multipage feature, you need to add a new file under the `pages` directory.
The name displayed in the sidebar will be the same as the file name.

See this [documentation](https://docs.streamlit.io/library/get-started/multipage-apps) for more details.
