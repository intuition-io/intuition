intuition-pkgs:
  pkg.installed:
    - reload_modules: true
    - pkgs:
      - git-core
      - r-base
      - python-pip
      - python-dev
      - g++
      - make
      - gfortran
      - libfreetype6-dev
      - libpng-dev
      - libopenblas-dev
      - liblapack-dev

# Requirements modules need first numpy to be installed
init-intuition:
  pip.installed:
    - names:
      - setuptools
      - distribute
      - flake8
      - nose
      - numpy
    - require:
      - pkg: intuition-pkgs

intuition:
  pip.installed:
    - require:
      - pip: init-intuition

init-insights:
  pip.installed:
    - names:
      - patsy
      - scipy
    - require:
      - pip: intuition

insights:
  pip.installed:
    - require:
      - pip: init-insights
