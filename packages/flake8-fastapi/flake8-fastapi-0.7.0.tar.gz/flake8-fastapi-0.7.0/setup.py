# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['flake8_fastapi', 'flake8_fastapi.visitors']

package_data = \
{'': ['*']}

install_requires = \
['fastapi>=0.65.1', 'flake8-plugin-utils>=1.3.2,<2.0.0']

entry_points = \
{'flake8.extension': ['CF = flake8_fastapi.plugin:FastAPIPlugin']}

setup_kwargs = {
    'name': 'flake8-fastapi',
    'version': '0.7.0',
    'description': 'flake8 plugin that checks FastAPI code against opiniated style rules 🤓',
    'long_description': '<h1 align="center">\n    <strong>flake8-fastapi</strong>\n</h1>\n<p align="center">\n    <a href="https://github.com/Kludex/flake8-fastapi" target="_blank">\n        <img src="https://img.shields.io/github/last-commit/Kludex/flake8-fastapi" alt="Latest Commit">\n    </a>\n        <img src="https://img.shields.io/github/workflow/status/Kludex/flake8-fastapi/Test">\n        <img src="https://img.shields.io/codecov/c/github/Kludex/flake8-fastapi">\n    <br />\n    <a href="https://pypi.org/project/flake8-fastapi" target="_blank">\n        <img src="https://img.shields.io/pypi/v/flake8-fastapi" alt="Package version">\n    </a>\n    <img src="https://img.shields.io/pypi/pyversions/flake8-fastapi">\n    <img src="https://img.shields.io/github/license/Kludex/flake8-fastapi">\n</p>\n\nA [flake8](https://flake8.pycqa.org/en/latest/index.html) plugin that helps you avoid simple FastAPI mistakes.\n\n## Installation\n\nFirst, install the package:\n\n``` bash\npip install flake8-fastapi\n```\n\nThen, check if the plugin is installed using `flake8`:\n\n``` bash\n$ flake8 --version\n3.9.2 (flake8-fastapi: 0.2.0, mccabe: 0.6.1, pycodestyle: 2.7.0, pyflakes: 2.3.1) CPython 3.8.11 on Linux\n```\n\n## Rules\n\n<!-- prettier-ignore-start -->\n  - [CF001 - Route Decorator Error](#cf001---route-decorator-error)\n  - [CF002 - Router Prefix Error](#cf002---router-prefix-error)\n  - [CF008 - CORSMiddleware Order](#cf008---corsmiddleware-order)\n  - [CF009 - Undocumented HTTPException](#cf009---undocumented-httpexception)\n  - [CF011 - No Content Response](#cf011---no-content-response)\n<!-- prettier-ignore-end -->\n\n### CF001 - Route Decorator Error\n\nDevelopers that were used to [flask](https://flask.palletsprojects.com/en/2.0.x/) can be persuaded or want to use the same pattern in FastAPI:\n\n```python\nfrom fastapi import FastAPI\n\napp = FastAPI()\n\n\n@app.route("/", methods=["GET"])\ndef home():\n    return "Hello world!"\n```\n\nBut on FastAPI, we have a simpler way to define this (and is the most known way to create endpoints):\n\n```python\nfrom fastapi import FastAPI\n\napp = FastAPI()\n\n\n@app.get("/")\ndef home():\n    return "Hello world!"\n```\n\n### CF002 - Router Prefix Error\n\nOn old FastAPI versions, we were able to add a prefix only on the `include_router` method:\n\n```python\nfrom fastapi import APIRouter, FastAPI\n\nrouter = APIRouter()\n\n\n@router.get("/")\ndef home():\n    ...\n\n\napp = FastAPI()\napp.include_router(router, prefix="/prefix")\n```\n\nNow, it\'s possible to add in the `Router` initialization:\n\n```python\nfrom fastapi import APIRouter, FastAPI\n\nrouter = APIRouter(prefix="/prefix")\n\n\n@router.get("/")\ndef home():\n    ...\n\n\napp = FastAPI()\napp.include_router(router)\n```\n\n\n### CF008 - CORSMiddleware Order\n\nThere\'s a [tricky issue](https://github.com/tiangolo/fastapi/issues/1663) about [CORSMiddleware](https://www.starlette.io/middleware/#corsmiddleware) that people are usually unaware. Which is that this middleware should be the last one on the middleware stack. You can read more about it [here](https://github.com/tiangolo/fastapi/issues/1663).\n\nLet\'s see an example of what doesn\'t work:\n\n```python\nfrom fastapi import FastAPI\n\napp = FastAPI()\n\napp.add_middleware(\n    CORSMiddleware,\n    allow_origins=[\'*\'],\n    allow_credentials=True,\n    allow_methods=[\'*\'],\n    allow_headers=[\'*\']\n)\napp.add_middleware(GZipMiddleware)\n```\n\nAs you see, the last middleware added is not `CORSMiddleware`, so it will not work as expected. On the other hand, if you change the order, it will:\n\n```python\nfrom fastapi import FastAPI\n\napp = FastAPI()\n\napp.add_middleware(GZipMiddleware)\napp.add_middleware(\n    CORSMiddleware,\n    allow_origins=[\'*\'],\n    allow_credentials=True,\n    allow_methods=[\'*\'],\n    allow_headers=[\'*\']\n)\n```\n\n### CF009 - Undocumented HTTPException\n\nCurrently, there\'s no automatic solution to document the `HTTPException`s, besides the experimental package [`fastapi-responses`](https://github.com/Kludex/fastapi-responses).\n\nFor that reason, it\'s easy to forget the documentation, and have a lot of undocumented endpoints. Let\'s see an example:\n\n```python\nfrom fastapi import FastAPI, HTTPException\n\napp = FastAPI()\n\n\n@app.get("/")\ndef home():\n    raise HTTPException(status_code=400, detail="Bad Request")\n```\n\nThe above endpoint doesn\'t have a `responses` field, even if it\'s clear that the response will have a `400` status code.\n\n### CF011 - No Content Response\n\nCurrently, if you try to send a response with no content (204), FastAPI will send a 204 status with a non-empty body.\nIt will send a body content-length being 4 bytes.\n\nYou can verify this statement running the following code:\n\n```python\n# main.py\nfrom fastapi import FastAPI\n\napp = FastAPI()\n\n\n@app.get("/", status_code=204)\ndef home():\n    ...\n```\n\nNow feel free to run with your favorite server implementation:\n\n```bash\nuvicorn main:app\n```\n\nThen use curl or any other tool to send a request:\n\n```bash\n$ curl localhost:8000\n*   Trying 127.0.0.1:8000...\n* TCP_NODELAY set\n* Connected to localhost (127.0.0.1) port 8000 (#0)\n> GET / HTTP/1.1\n> Host: localhost:8000\n> User-Agent: curl/7.68.0\n> Accept: */*\n>\n* Mark bundle as not supporting multiuse\n< HTTP/1.1 204 No Content\n< date: Sat, 24 Jul 2021 19:21:24 GMT\n< server: uvicorn\n< content-length: 4\n< content-type: application/json\n<\n* Connection #0 to host localhost left intact\n```\n\nThis goes against the [RFC](https://tools.ietf.org/html/rfc7231#section-6.3.5), which specifies that a 204 response should have no body.\n\n## License\n\nThis project is licensed under the terms of the MIT license.\n',
    'author': 'Marcelo Trylesinski',
    'author_email': 'marcelotryle@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/Kludex/flake8-fastapi',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
