intuition-pkgs:
  pkg.installed:
    - reload_modules: true
    - pkgs:
      - git-core
      - r-base
      - python-pip
      - python-dev
      - gcc
      - g++
      - make
      - gfortran

# Requirements modules need first numpy to be installed
numpy:
  pip.installed:
    - require:
      - pkg: intuition-pkgs

# Python dependencies
requirements:
  pip.installed:
    - requirements: salt://intuition/scripts/installation/requirements.txt
    - require:
      - pip: numpy

# Make the library system wide available
/usr/local/lib/python2.7/dist-packages/intuition:
  file:
    - recurse
    - source: salt://intuition/intuition

# Copy market data to default location
/root/.intuition:
  file.recurse:
    - source: salt://intuition/config

# Copy market data to default location
/root/.intuition/data:
  file.recurse:
    - source: salt://intuition/data
    - require:
      - file: /root/.intuition
