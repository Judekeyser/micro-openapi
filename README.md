# Micro-OpenAPI

The code in this repository is aimed at demonstrating how to combine Pydantic,
APISpec and a micro-framework, to help you write OpenAPI documentation.
We currently have sketched examples in Flask; Falcon and Starlette will come soon.

## What it is not

This library is not a tool to help you validate body request, content, or other parameters.

It is not a tool to think for you and allow you to speed up what you should be good at.

It is not a tool to automatically generate OpenAPI documentation based on Pydantic,
or any other, typing or validation library.

## The issues it tries to solve

Maintaining OpenAPI documentation can be difficult. The usual formats (JSON or YAML)
ask you to write texts, in aside files or in doc-strings. This might not be convenient for
different reasons:

1. **Non locality**: Having the specification in another file,
or even another place in code, diminishes code locality and 
increases the overhead for a reader to keep information in memory;
2. **External dialect**: Writing YAML or JSON, even though not difficult per se, 
involved an external dialect that might not help in code readability. They also tend to 
take more space they would need, or introduce noisy characters;
3. **Unchecked writing**: Writing plain text (even through a format) usually increases
the changes to perform typos or even OpenAPI errors.
4. **Compromise** (worst of all worlds): Solution that try to find a compromise between 
two type systems, usually fail at it and cannot render the flavors of both (often not even of a
single one of them).
5. **Intrusive policy**: Hyper-branded solutions (see FastAPI or APIFlask, for example) are 
opinionated and perform micro-framework intrusions: they alter the micro-framework they 
hook and limit it in an intrusive way; in some cases, prevent other third parties to
continue working along.

## What it is

Micro-OpenAPI is a micro annotation set that is aimed to live along class-based
views (which you can find in Starlette, Flask, or Falcon). We have chosen class-based approach
because it suits well the OpenAPI wording already, where a single path is declined
through operations. This is a radically different approach to FastAPI, for example,
which stresses RPC style of code.

The primilary goal is to **help you write OpenAPI specification** along with Pydantic code,
by providing annotations that roughly act as the **identity over functions**, yet
**memoizing definitions** to infer a specification using APISpec and Pydantic.

Even though the examples tend to be funky,
it is *not aimed to create a new layer of abstraction* on top of the micro-framework you
love the most. We tried to show, through a real non scholar example,
how the tool can be used.

# Install

First install the `microapi` library in a fresh environment.
```py
python3.9 -m venv venv39
source venv39/bin/activate
pip install -r requirements.txt
pip install mypy
pip install build

# Run MyPy, for satisfaction purpose

python -m build

# Install the wheel in your environment
```

It is recommended to [check out the examples](./examples/README.md) to get an idea of what the
library actually does.