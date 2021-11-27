# archetype-to-python
Transpile Archetype Language to Python

## Genesis of the project
In November 2021, looking at the Archetype language, which is a contract programming language for Tezos, I thought that this language would also be nice for describing REST APIs. For that, it would be necessary to write a transpiler from Archetype to another programming language. Besides, it makes a good project to remind me of how to write a compiler and explore modern parsing libraries. So I chose to target Python and that's where I discovered Lark, a really good parsing toolkit for Python.

## Project organisation

* Dockerfile: You can build and run this project with docker
* src/archetype-parser.py: The entrypoint of the generator
* test/main.py: The entrypoint of the tests of the generated code

## Run it

To generate some Python code using docker:

```
docker build -t archetype-parser . && docker run archetype-parser
```

You can also go into the src directory and use:

```
pip install -r requirements.txt
python archetype-parser.py
```
