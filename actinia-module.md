## actinia-core process-chain templating

You can run actinia-gdi in multiple ways (see README.md). If actinia-gdi is installed as actinia-core plugin, endpoints for module self-description are added. These modules are a collection of common GRASS GIS modules (grass-module) and of specific actinia-modules. While GRASS GIS is able to tell input/output parameters for a certain GRASS GIS module via `--interface-description` which can easily be converted to JSON, actinia-modules are more complex.

Most of these actinia-modules are stored as process-chain template. Process-chains are a way to tell actinia-core what needs to be processed and are mostly a list of GRASS commands in a defined JSON format.

This readme explains the module self-description which actinia provides as well as process-chain templates and the combination of self-description for temlpates. Last but not least conventions for template creation are listed.

Content:
1. Module self-description
1. Process-chain templates
1. Template self-description
1. Conventions for template creation
1. Overview of endpoints for self-description


### 1. Module self-description

One grass-module self-description can be requested as follows:

`curl -X GET http://127.0.0.1:8088/api/v1/modules/v.buffer`

One example response to describe the GRASS GIS module "v.buffer" looks like this:

```
{
  "categories": [
    "area",
    "buffer",
    "circle",
    "geometry",
    "grass-module",
    "grow",
    "line",
    "shrink",
    "vector"
  ],
  "description": "Creates a buffer around vector features of given type.",
  "id": "v.buffer",
  "parameters": {
    "angle": {
      "description": ". Angle of major axis in degrees",
      "required": false,
      "schema": {
        "default": "0",
        "type": "number"
      }
    },
    "c": {
      "description": ". Do not make caps at the ends of polylines",
      "schema": {
        "default": "False",
        "type": "boolean"
      }
    },
    "cats": {
      "description": "Category values. Example: 1,3,7-9,13",
      "required": false,
      "schema": {
        "subtype": "cats",
        "type": "string"
      }
    },
    "column": {
      "description": ". Name of column to use for buffer distances",
      "required": false,
      "schema": {
        "subtype": "dbcolumn",
        "type": "string"
      }
    },
    "distance": {
      "description": ". Buffer distance along major axis in map units",
      "required": false,
      "schema": {
        "type": "number"
      }
    },
    "help": {
      "description": ". Print usage summary",
      "schema": {
        "default": "False",
        "type": "boolean"
      }
    },
    "input": {
      "description": "Name of input vector map. Or data source for direct OGR access",
      "required": true,
      "schema": {
        "subtype": "vector",
        "type": "string"
      }
    },
    "layer": {
      "description": "Layer number or name ('-1' for all layers). A single vector map can be connected to multiple database tables. This number determines which table to use. When used with direct OGR access this is the layer name.",
      "required": false,
      "schema": {
        "default": "-1",
        "subtype": "layer_all",
        "type": "string"
      }
    },
    "minordistance": {
      "description": ". Buffer distance along minor axis in map units",
      "required": false,
      "schema": {
        "type": "number"
      }
    },
    "output": {
      "description": ". Name for output vector map",
      "required": true,
      "schema": {
        "subtype": "vector",
        "type": "string"
      }
    },
    "overwrite": {
      "description": ". Allow output files to overwrite existing files",
      "schema": {
        "default": "False",
        "type": "boolean"
      }
    },
    "quiet": {
      "description": ". Quiet module output",
      "schema": {
        "default": "False",
        "type": "boolean"
      }
    },
    "s": {
      "description": ". Make outside corners straight",
      "schema": {
        "default": "False",
        "type": "boolean"
      }
    },
    "scale": {
      "description": ". Scaling factor for attribute column values",
      "required": false,
      "schema": {
        "default": "1.0",
        "type": "number"
      }
    },
    "t": {
      "description": ". Transfer categories and attributes",
      "schema": {
        "default": "False",
        "type": "boolean"
      }
    },
    "tolerance": {
      "description": ". Maximum distance between theoretical arc and polygon segments as multiple of buffer (default 0.01)",
      "required": false,
      "schema": {
        "type": "number"
      }
    },
    "type": {
      "description": ". Input feature type",
      "required": false,
      "schema": {
        "default": "point,line,area",
        "enum": [
          "point",
          "line",
          "boundary",
          "centroid",
          "area"
        ],
        "type": "array"
      }
    },
    "verbose": {
      "description": ". Verbose module output",
      "schema": {
        "default": "False",
        "type": "boolean"
      }
    },
    "where": {
      "description": "WHERE conditions of SQL statement without 'where' keyword. Example: income < 1000 and population >= 10000",
      "required": false,
      "schema": {
        "subtype": "sql_query",
        "type": "string"
      }
    }
  }
}

```

### 2. Process-chain templates
An example process-chain looks like this:

```
{
    "list": [
        {
            "id": "add_column_for_area",
            "module": "v.db.addcolumn",
            "inputs": [
                {
                    "param": "map",
                    "value": "polygons"
                },
                {
                    "param": "columns",
                    "value": "area_h DOUBLE PRECISION"
                }
            ]
        },
        {
            "id": "caulate_area",
            "module": "v.to.db",
            "inputs": [
                {
                    "param": "map",
                    "value": "polygons"
                },
                {
                    "param": "column",
                    "value": "area_h"
                },
                {
                    "param": "option",
                    "value": "area"
                },
                {
                    "param": "unit",
                    "value": "h"
                }
            ]
        },
        {
            "id": "v_db_select",
            "module": "v.db.select",
            "inputs": [
                {
                    "param": "map",
                    "value": "polygons"
                },
                {
                    "param": "column",
                    "value": "area_h"
                }
            ]
        }
    ],
}

```

There are some reasons why it might be useful to store a process chain and create a template out of it:
* If this process-chain is applied multiple times to different input data, most of it won't change, but the user needs to store the process-chain himself and change the values
* Or the user might not know how to formulate a whole process-chain but wishes to use predefined ones and only change some parameters.
* A client with autogenerated requests talks to the API directly and needs a consistent way to adress predefined processes.
Therefore Actinia-gdi is able to store process-chain templates and the user only needs to enter certain values. A template might look like this:


```
{
    "id": "vector_area",
    "description": "Computes the areas in h for selected map.",
    "template": {
        "list": [
            {
                "id": "add_column_for_area",
                "module": "v.db.addcolumn",
                "inputs": [
                    {
                        "param": "map",
                        "value": "{{ name }}"
                    },
                    {
                        "param": "columns",
                        "value": "{{ column }}"
                    }
                ]
            },
            {
                "id": "calculate_area",
                "module": "v.to.db",
                "inputs": [
                    {
                        "param": "map",
                        "value": "{{ name }}"
                    },
                    {
                        "param": "columns",
                        "value": "{{ column_name }}"
                    },
                    {
                        "param": "option",
                        "value": "area"
                    },
                    {
                        "param": "unit",
                        "value": "h"
                    }
                ]
            },
            {
                "id": "v_db_select",
                "module": "v.db.select",
                "inputs": [
                    {
                        "param": "map",
                        "value": "{{ name }}"
                    },
                    {
                        "param": "columns",
                        "value": "{{ column_name }}"
                    }
                ]
            }
        ],
        "version": "1"
    }
}


```
This way, the user only needs to set values for the defined variables. The user doesn't even need to know the whole template. Actinia-gdi will translate it into one actinia-module, exploiting only the values necessary for input:

```
{
        "list": [
            {
                "id": "vector_area",
                "module": "vector_area",
                "inputs": [
                    {
                        "param": "v.db.addcolumn_map",
                        "value": "{{ name }}"
                    },
                    {
                        "param": "v.db.addcolumn_columns",
                        "value": "{{ columns }}"
                    },
                    {
                        "param": "v.to.db_map",
                        "value": "{{ name }}"
                    },
                    {
                        "param": "v.to.db_columns",
                        "value": "{{ column_name }}"
                    },
                    {
                        "param": "v.db.select_map",
                        "value": "{{ name }}"
                    },
                    {
                        "param": "v.db.select_columns",
                        "value": "{{ column_name }}"
                    }
                ]
            }
        ],
        "version": "1"
    }
```

For the user this looks like one module in the process-chain. In further development, it will be shrinked even more to not exploit the same variable twice. This might then look like this:

```
{
        "list": [
            {
                "id": "vector_area",
                "module": "vector_area",
                "inputs": [
                    {
                        "param": "v.db.addcolumn_map",
                        "value": "{{ name }}"
                    },
                    {
                        "param": "v.db.addcolumn_columns",
                        "value": "{{ columns }}"
                    },
                    {
                        "param": "v.to.db_columns",
                        "value": "{{ column_name }}"
                    }
                ]
            }
        ],
        "version": "1"
    }

```


### 3. Template self-description

Mapping the process-chain template to a self-description will look as follows and the user wont feel the difference between a grass-module and an actinia-module anymore:

```
{
  "categories": [
    "actinia-module"
  ],
  "description": "Copies zipcodes_wake and compute the areas in h.",
  "id": "vector_area",
  "parameters": {
    "v.db.addcolumn_columns": {
      "description": "Name and type of the new column(s) ('name type [,name type, ...]'). Types depend on database backend, but all support VARCHAR(), INT, DOUBLE PRECISION and DATE. Example: 'label varchar(250), value integer'",
      "required": true,
      "schema": {
        "type": "array"
      }
    },
    "v.db.addcolumn_map": {
      "description": "Name of vector map. Or data source for direct OGR access",
      "required": true,
      "schema": {
        "subtype": "vector",
        "type": "string"
      }
    },
    "v.to.db_columns": {
      "description": "Name of attribute column(s) to populate. Name of attribute column(s)",
      "required": true,
      "schema": {
        "subtype": "dbcolumn",
        "type": "array"
      }
    }
  }
}


```
### 4. Conventions for template creation

* __Only use placeholder for a whole value of a GRASS GIS attribute.__


* __Do not use placeholder for only part of a value of a GRASS GIS attribute.__
E.g. not like this:
`{param: "g.copy_vector", value: "zipcodes_wake,{{ name }}" }`
As the self-desription will display the data type of the whole parameter, placeholder of only one part of the value could lead to weird results.
Exceptions might be ok for filesystem-paths. TODO discuss.


* __Make use of importer and exporter where possible, especially for Landsat / Sentinel data.__
Both are special modules from actinia-core. Safety mechanisms are already implemented and optimized, e.g. clean up of download cache from node / feature to block download if it threatenes health of node...





### 5. Overview of endpoints for self-description

List / Describe only GRASS Modules

* GET /grassmodules
* GET /grassmodules/d.barscale
* GET /grassmodules/d.barscale3

List / Describe only Modules (process-chain templates)

* GET /actiniamodules
* GET /actiniamodules/vector_area

List / Describe combined

* GET /modules
* GET /modules/d.barscale
* GET /modules/vector_area
* GET /modules/vector_area5

Full API docs

* GET /swagger.json
