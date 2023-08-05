import os
import re
import shutil

import isort
from pkg_resources import resource_filename


def handle_multipage(root: str, use_pr_st_template: bool = False) -> None:
    """Enable multipage mode (streamlit native)"""

    # Creating a new folder called "pages"
    os.mkdir(f"{root}/streamlit/pages")

    multipage_page_template = resource_filename(
        "pr_st_cli", "template/multipage/page.py"
    )
    multipage_main_template = resource_filename(
        "pr_st_cli", "template/multipage/main.py"
    )
    with open(multipage_page_template) as f:
        mutlipage_page_content = f.read()

    with open(multipage_main_template) as f:
        multipage_main_content = f.read()

    # Now we need to create a new file called "page1.py"
    with open(f"{root}/streamlit/pages/Page_2.py", "w") as f:
        f.write(
            mutlipage_page_content.replace("{{PAGE_NUMBER}}", "2").replace(
                "{{pr_st_cli_TEMPLATE_CONTENT}}",
                handle_pr_st_template(root, return_content=True)
                if use_pr_st_template
                else "",
            )
        )

    # Now we need to update the app.py file
    with open(f"{root}/streamlit/App.py", "r+") as f:
        content = f.read()

        f.seek(0)
        f.write(content.replace("{{MULTIPAGE_CONTENT}}", multipage_main_content))
        f.truncate()


def handle_pr_st_template(root: str, return_content: bool = False) -> str:
    """Enable pr-streamlit-template styles (see https://pypi.org/project/pr-streamlit-template/ for more info)"""

    pr_st_cli_template_dir = resource_filename(
        "pr_st_cli", "template/pr_st_template/func.py"
    )
    with open(pr_st_cli_template_dir) as f:
        pr_st_cli_template_content = f.read()

    if return_content:
        return pr_st_cli_template_content

    with open(f"{root}/streamlit/App.py", "r+") as f:
        content = f.read()

        f.seek(0)
        f.write(
            content.replace(
                "{{pr_st_cli_TEMPLATE_CONTENT}}", pr_st_cli_template_content
            )
        )
        f.truncate()

    return ""


def clean(root: str) -> None:
    for dir, _, files in os.walk(f"{root}/streamlit/"):
        for file in files:
            if file.endswith(".pyc"):
                continue

            with open(f"{dir}/{file}", "r+", encoding="utf-8") as f:
                content = f.read()

                # Clean up the macros
                content = re.sub(r"\{\{.*?\}\}", "", content)

                # Clean up the unnecessary new lines
                content = re.sub(r"\n{3,}", "\n\n", content)

                # Sorting the imports
                content = isort.code(content, float_to_top=True)

                f.seek(0)
                f.write(content)
                f.truncate()

    # Remove the __pycache__ folder
    try:
        shutil.rmtree(f"{root}/streamlit/__pycache__")
    except FileNotFoundError:
        pass


def handle_vault(root: str) -> None:
    """Use a vault.py file to get secrets from Azure KeyVault"""

    vault_file = resource_filename("pr_st_cli", "template/keyvault/vault.py")
    vault_app_content_file = resource_filename("pr_st_cli", "template/keyvault/App.py")
    with open(vault_app_content_file) as f:
        vault_app_content = f.read()

    with open(f"{root}/streamlit/App.py", "r+") as f:
        content = f.read()

        f.seek(0)
        f.write(content.replace("{{AZURE_KEYVAULT_CONTENT}}", vault_app_content))
        f.truncate()

    # copy the vault file to the root
    shutil.copy(vault_file, f"{root}/streamlit/vault.py")


def handle_readme(root: str) -> str:
    """Handle the readme.md file

    Args:
        root (str): The root directory of the project

    Returns:
        str: the readme content
    """
    with open(f"{root}/streamlit/README.md", "r+") as f:
        content = f.read()

        content = content.replace("{{ROOT_DIR_NAME}}", root)

        f.seek(0)
        f.write(content)
        f.truncate()

    return content
