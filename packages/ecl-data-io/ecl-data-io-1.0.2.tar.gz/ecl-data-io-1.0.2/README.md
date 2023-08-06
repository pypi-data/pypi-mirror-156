ecl-data-io
===========

Parser for the ecl output format, such as found in files with
extensions .UNRST, .EGRID, .INIT, etc. and also the corresponding
ascii files with extension .FUNRST, .FEGRID, .FINIT, etc.

The file format comes in two forms: formatted or unformatted, which are
ascii and binary respectively (the terminology comes from fortran).

The files consists of named arrays, starting with a 8 character ascii
keyword name, followed by a 4 byte signed integer which is the length
of the array, then a 4 character keyword describing the data type
of elements in the array. Each file consists of a sequence of such arrays.

ecl-data-io does not interpret the output, but simply give you the arrays:

```
import ecl_data_io as eclio

for kw, arr in eclio.read("my_grid.egrid"):
    print(kw)

>>> "FILEHEAD"
>>> "GRIDHEAD"
>>> "COORD"
>>> "ZCORN"
>>> "ACTNUM"
>>> "MAPAXES"
```


Similarly, the `write` function will generate such files:

```
import ecl_data_io as eclio

eclio.write("my_grid.egrid", {"FILEHEAD": [...], "GRIDHEAD": [10,10,10]})
```

The default format is is binary (unformatted), but it is possible to
read and write ascii aswell:


```
import ecl_data_io as eclio

eclio.write(
    "my_grid.egrid",
    {"FILEHEAD": [...], "GRIDHEAD": [10,10,10]},
    fileformat=eclio.Format.FORMATTED
)
```

lazy reading
------------

It is also possible to read through the file without loading
all arrays into memory, ie. lazily:

```
import ecl_data_io as eclio

for item in eclio.lazy_read("my_grid.egrid"):
    print(item.read_keyword())

>>> "FILEHEAD"
>>> "GRIDHEAD"
>>> "COORD"
>>> "ZCORN"
>>> "ACTNUM"
>>> "MAPAXES"
```

Note that `eclio.lazy_read` in the above example is a generator of array
entries and the file will be closed once the generator is finished. Therefore,
care will have to be taken in when arrays/keywords are read from the entries.
For better control, one can pass the opened file:

```
import ecl_data_io as eclio

with open("my_grid.egrid", "rb") as f:
    generator = eclio.lazy_read("my_grid.egrid")
    item = next(generator)
    print(item.read_keyword())

>>> "FILEHEAD"
```


Duplicate keywords
--------------------------

The simple write function works best for keywords with unique
names, however, if the file has multiple arays with the same name,
list of tuples can be used:


```
import ecl_data_io as eclio

contents = [
 ("COORD", [1.0, ...]),
 ("COORD", [2.0, ...]),
]

eclio.write("my/file.grdecl", contents)
```
