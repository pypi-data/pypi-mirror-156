Changes
-------

6.0.dev2 (2022-06-27)
~~~~~~~~~~~~~~~~~~~~~

* Fight with Python packaging tool idiosyncrasies, replace flit with hatchling__

  __ https://hatch.pypa.io/latest/config/build/#build-system


6.0.dev1 (unreleased)
~~~~~~~~~~~~~~~~~~~~~

* Renew development environment:

  - modernized packaging using `PEP 517`__ and flit__
  - replaced tox__ with nix__

  __ https://peps.python.org/pep-0517/
  __ https://flit.readthedocs.io/en/latest/
  __ https://tox.wiki/en/latest/
  __ https://nixos.org/guides/how-nix-works.html

6.0.dev0 (2021-10-17)
~~~~~~~~~~~~~~~~~~~~~

* Target Python 3.9+

* Do not emit ``length=1`` in the metadata of unlimited ``text`` fields

* Drop the asyncio variant of the proxies: if/when needs arise I shall reimplement them on top
  of new SA 1.4+ functionality


Previous changes are here__.

__ https://gitlab.com/metapensiero/metapensiero.sqlalchemy.proxy/-/blob/master/OLDERCHANGES.rst
