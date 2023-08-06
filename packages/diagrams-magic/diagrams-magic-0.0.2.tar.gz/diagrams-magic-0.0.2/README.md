# diagrams-magic

The **diagrams-magic** is an IPython magic that enables calling [`diagrams` ](https://github.com/seflless/diagrams) within IPython kernel to draw graphs with pure texts. The most common use case, however, would be to use this magic within Jupyter Notebook, which integrates the IPython kernel within it.

## Requirements
- `diagrams`

  The mechanism of this magic is to call `diagrams` installed on local machine. So please ensure that `diagrams` is accessible on your system or in your virtual environment.

  If you have `node` and `npm` installed, you may install `diagrams` with

  `npm install -g diagrams`

- A (virtual) display driver

  `diagrams flowchart` and `diagrams sequence` starts an Electron app that requires a display to run. If you are using **Windows** or **MacOS**, this shouldn't be a problem.
  
  However if you are to deploy this magic on a headless **Linux** backend, `diagrams flowchart` and `diagrams sequence` will report 'Cannot open display' error. 

  This can be circumvented with a virtual display. We suggest installing `xvfb` so that our magic will detect the installed `xvfb-run` command and use it. The solution is detailed at [Electron's webpage](https://www.electronjs.org/docs/latest/tutorial/testing-on-headless-ci/#configuring-the-virtual-display-server).

## Installation

- From PIP:
  
  ```shell
  pip install diagrams-magic
  ```
  
- Development install:
  
  ```shell
  git clone https://github.com/chunxy/diagrams-magic.git
  cd diagrams-magic
  pip install -e ./
  ```

## Usage

As with usual IPython magic, remember to `%load_ext diagrams-magic` before using this magic.

This is a cell magic. In the first line of your cell, type `%%diagrams (flowchart|dot|sequence|railroad) [name]` to indicate which driver you are to use and the name of image file. If no `name` is provided, no image file will be generated in your current directory (but the image will still be available in the output cell). In the rest of this cell, simply type in the graph descriptions.

See the [demo file](./demo/diagrams.ipynb) for reference.

## Known Issue(s)

- `Invalid asm.js: Function definition doesn't match use`

  There might be error like above when you are using the `dot` driver. This is a known issue caused by the upstream `viz.js`. Usually the output won't be affected and thus you can ignore it, as long as the red error message won't be too harsh for your eyes.