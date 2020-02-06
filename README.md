### Brainy bots

Here will live all the notes (in website), code, etc.

#### Website

The website is using a forked version of the [jemdoc+mathjax](http://www.mit.edu/~wsshin/jemdoc+mathjax.html) Python static site generator, with modifications to support subdirectories and hidden solutions.  To build, run `python3 build.py` in the `/website` directory, which will generate a static site in `/docs` (this is autoserved by Github pages).

TODO: change CSS to something prettier

#### Pi Setup

Robots use Raspberry Pi 3B+s with 2019-09-26 Raspbian Buster lite.  [This script](https://github.com/idev1/rpihotspot) is used for creating APs and forwarding wifi.