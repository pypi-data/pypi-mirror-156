# Snyk Tags Tool

Snyk Tags is a CLI tool that uses the Snyk Project API to assign tags in bulk to Snyk projects based on the type.

Snyk Tags will update all projects of a type within a specific Snyk Group with either an SCA, SAST, IaC or Container tag to help filter projects by Snyk product.

You can also specify applying the tags to a specific Snyk organization and create your own custom tags.

Once this is run, go into the UI and click on the tags filter in the projects page (left-hand menu). Select the Type tag and the product as the key. All your Snyk projects from a specific product will be shown via this filter.

## Installation and requirements

### Requirements

Requires Python version above 3.6

### Installation

To install the simplest way is to use pip:

```bash
pip install snyk-tags
```

Alternatively you can clone the repo and then run the following commands:

```python
poetry install # To install dependencies
python -m snyk-tags # To run snyk-tags
```

## Usage

**Usage:** snyk-tags [OPTIONS] COMMAND [ARGS]

**COMMAND**:

- apply: ```snyk-tags apply --help```
  - container: ```snyk-tags apply container```
  - iac: ```snyk-tags apply iac```
  - sast: ```snyk-tags apply sast```
  - sca: ```snyk-tags apply sca```
  - custom: ```snyk-tags apply custom```

**OPTIONS**:

- **[-v, --version]**: ```snyk tags -v```
- **[--containertype]**: ```snyk-tags apply container --containertype=deb```
  - Define the type of Snyk Container projects to tag
- **[--scatype]**: ```snyk-tags apply sca --scatype=maven```
  - Define the type of Snyk Open Source projects to tag
- **[--projecttype]**: ```snyk-tags apply custom --projecttype=maven --tagkey=Type --tagvalue=Value```
  - Define the type of project to tag, must be accompanied by ```tagkey``` and ```tagvalue```
- **[--tagkey]**: ```snyk-tags apply custom --projecttype=deb --tagkey=Type --tagvalue=Value```
  - Define the custom tag
- **[--tagvalue]**: ```snyk-tags apply custom --projecttype=iac --tagkey=Type --tagvalue=Value```
  - Define the value of the custom tag

**ARGS**:

- **[--group-id]**: ```snyk tags sast --group-id```
  - Define the Group ID you want to apply the tags to
  - Can also be imported as an environment variable
- **[--org-id]**: ```snyk tags sast --group-id```
  - Define the Organization ID you want to apply the tags to
  - Can also be imported as an environment variable
- **[--token]**: ```snyk-tags apply sast --token=xxx```
  - Define the Snyk API Token you want to use (needs Group access by default)
  - Can also be imported as an environment variable
