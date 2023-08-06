# Babel-heureka-code

[![Interrogate](badges/interrogate.svg)](https://github.com/econchick/interrogate)
[![Imports: isort](https://img.shields.io/badge/%20imports-isort-%231674b1?style=flat&labelColor=ef8336)](https://pycqa.github.io/isort/)
[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white)](https://github.com/pre-commit/pre-commit)
[![flake8](https://img.shields.io/static/v1?label=flake8&message=enabled&color=brightgreen&logoColor=white)](https://github.com/PyCQA/flake8)
[![Conventional Commits](https://img.shields.io/badge/Conventional%20Commits-1.0.0-brightgreen.svg?style=flat)](https://conventionalcommits.org)
[![PyPi](https://img.shields.io/pypi/v/Babel-heureka-code)](https://pypi.org/project/babel-heureka-code/)

## Nutzen
Dieses Projekt zielt darauf ab, eine einfache Möglichkeit für mehrsprachige Pythonprogramme zu bieten.

## Das Konzept
Der Gedanke hinter dem Projekt ist, dass an verschiedenen Stellen im Programm spezielle Objekte mit bestimmten IDs erstellt werden.
Diese können an einen Verwalter gebunden werden.
Der Verwalter kann daraufhin auf verschiedene Sprachen gesetzt werden.
Wird eine Übersetzung abgefragt z.B. durch die ```__str__``` Methode des Referenzobjekts wird der Verwalter die aktuell gesetzte Sprache nutzen, um die richtige Übersetzung zu ermitteln.

## Installation
```shell
pip install Babel-heureka-code
```

## Dokumentation
Die Dokumentation ist auf [https://heureka-code.github.io/Babel-heureka-code/](https://heureka-code.github.io/Babel-heureka-code/) einsehbar.
