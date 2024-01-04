## Lab05 - Exercise - Process

With the unpickled files from `lab05_unpickle`, wrap the shape colour data in a bigger data structure:

```json
{
    "mostCommon" : {
        "colour" : "[most-common-colour]",
        "shape" : "[most-common-shape]"
    },
    "rawData" : [insert-raw-data-from-shapecolour.p]
}
```

[Items in brackets] should be replaced with actual values or data structures.

Write a function `process` inside file `process.py` that creates this new data structure, then outputs it as JSON to a file `processed.json`

Ensure your code is pylint compliant.
