# Repository Coverage



| Name                                   |    Stmts |     Miss |   Cover |   Missing |
|--------------------------------------- | -------: | -------: | ------: | --------: |
| src/pyhpcc/\_\_init\_\_.py             |        0 |        0 |    100% |           |
| src/pyhpcc/command\_config.py          |       84 |        0 |    100% |           |
| src/pyhpcc/config.py                   |       30 |        0 |    100% |           |
| src/pyhpcc/errors.py                   |       18 |        0 |    100% |           |
| src/pyhpcc/handlers/\_\_init\_\_.py    |        0 |        0 |    100% |           |
| src/pyhpcc/handlers/thor\_handler.py   |       63 |       11 |     83% |60, 90-97, 101, 103, 107-108 |
| src/pyhpcc/models/\_\_init\_\_.py      |        0 |        0 |    100% |           |
| src/pyhpcc/models/auth.py              |       35 |        5 |     86% |   127-132 |
| src/pyhpcc/models/file.py              |       88 |        7 |     92% |106, 123-124, 176, 185-186, 248 |
| src/pyhpcc/models/hpcc.py              |       90 |        4 |     96% |251, 421, 609, 629 |
| src/pyhpcc/models/workunit\_submit.py  |      171 |       52 |     70% |114-115, 149-150, 175-176, 237-238, 262-274, 296-313, 337, 360-363, 391-392, 415, 430-432, 449-451, 469-473, 481 |
| src/pyhpcc/utils.py                    |      218 |       29 |     87% |8, 61-63, 87-88, 163-165, 208-209, 245-246, 277-282, 319-324, 372-373, 431-432 |
| tests/conftest.py                      |       94 |        4 |     96% |73, 78, 83, 88 |
| tests/models/test\_auth.py             |       34 |        0 |    100% |           |
| tests/models/test\_file.py             |      109 |       28 |     74% |25-36, 55-57, 68-93, 104-121, 131-151, 169-170 |
| tests/models/test\_hpcc\_api.py        |      201 |       26 |     87% |20, 32-33, 42, 54, 69, 83, 99, 118, 134, 149, 171, 174, 184, 198, 209, 221, 234, 244, 258, 269, 306, 329, 356, 371, 421 |
| tests/models/test\_workunit\_submit.py |      103 |       13 |     87% |25, 43-44, 136-145, 169-173 |
| tests/test\_command\_config.py         |       72 |        4 |     94% |49-50, 136-137 |
| tests/test\_utils.py                   |       14 |        0 |    100% |           |
|                              **TOTAL** | **1424** |  **183** | **87%** |           |


## Setup coverage badge

Below are examples of the badges you can use in your main branch `README` file.

### Direct image

[![Coverage badge](https://github.com/amila-desilva/pyhpcc/raw/python-coverage-comment-action-data/badge.svg)](https://github.com/amila-desilva/pyhpcc/tree/python-coverage-comment-action-data)

This is the one to use if your repository is private or if you don't want to customize anything.



## What is that?

This branch is part of the
[python-coverage-comment-action](https://github.com/marketplace/actions/python-coverage-comment)
GitHub Action. All the files in this branch are automatically generated and may be
overwritten at any moment.