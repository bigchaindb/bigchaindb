[Documentation on ReadTheDocs](http://bigchaindb.readthedocs.org/)

# The BigchainDB Documentation Strategy

* Include explanatory comments and docstrings in your code. Write [Google style docstrings](https://google.github.io/styleguide/pyguide.html?showone=Comments#Comments) with a maximum line width of 119 characters.
* For quick overview and help documents, feel free to create `README.md` or other `X.md` files, written using [GitHub-flavored Markdown](https://help.github.com/categories/writing-on-github/). Markdown files render nicely on GitHub. We might auto-convert some .md files into a format that can be included in the long-form documentation.
* We use [Sphinx](http://www.sphinx-doc.org/en/stable/) to generate the long-form documentation in various formats (e.g. HTML, PDF).
* We also use [Sphinx](http://www.sphinx-doc.org/en/stable/) to generate Python code documentation (from docstrings and possibly other sources).
* We will use [Apiary](https://apiary.io/) to document all REST APIs.

# How to Generate the HTML Version of the Long-Form Documentation

If you want to generate the HTML version of the long-form documentation on your local machine, you need to have Sphinx and some Sphinx-contrib packages installed. To do that, go to the BigchainDB `docs` directory (i.e. this directory) and do:
```bash
pip install -r requirements.txt
```
You can then generate the HTML documentation by doing:
```bash
make html
```
The generated HTML documentation will be in the `docs/build/html` directory. You can view it by opening `docs/build/html/index.html` in your web browser.
