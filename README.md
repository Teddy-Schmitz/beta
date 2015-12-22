# Beta

Beta is a continuous deployment tool for AWS API Gateway. It's purpose is to make managing a project using API Gateway version controlled and tested.
Designed to be used with [alpha](https://github.com/boxidau/alpha) the lambda ci/cd tool.


## Installation
```
git clone git@github.com:jdioutkast/beta.git
cd beta
pip install .
```

After a bit more testing and possibly a name change I'll make a proper pip package

Beta uses standard boto3 authentication methods (envvar, ~/.aws/credentials) Make sure you have this [setup](http://boto3.readthedocs.org/en/latest/guide/configuration.html).


## Project Setup

Your project should have a structure like so:
```
example_project
├── gateway.json
├── test-lambda
│   ├── lambda.json
│   └── src
│       ├── index.js
│       └── required-file.js
```

In this example test-lambda are individual functions that make up a project called example_project

Each project folder must contain gateway.json.
See the example_project folder in this git repo for examples of gateway.json

## Usage

### Push

Will backup and create a new api gateway based on the configuration specified

```
# push an entire project
# path defaults to current directory
# path should contain folders each containing gateway.json
beta push [/path/to/project]

# push a single function, config and policy
# path defaults to current directory
# path should contain gateway.json
beta push --single [/path/to/function]
```

## Contributing
If you'd like to contribute please fork the repo and submit a PR!
