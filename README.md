# MVPA-MEG (Master’s project)

## Top level workflow
* Preprocessing (per subject)
* Dataset generation (per cortical area + sensor space)
* Adding conditions (per condition type)
* MVPA analyses (per analysis)

```mermaid
graph LR;
  preprocess --> dataset;
  dataset --> conditions;
  conditions --> analyses;
```


# Per subject (preprocessing.py)
* **create_directories()**
  * => bunch of directories
* **read_raw()**
  * => raw object
* **downsample()** (optional)
  * => downsampled raw object
* **filter()** (optional)
  * => filtered raw object
* **remove_artifacts()** (optional)
  * => raw object without artifacts
* **epoch()**
  * => epoch file
  * => sensor space data
* **source_localize()**
  * => source space data

```mermaid
graph LR;
    create["create_directories(...)"] --> read_raw;
    read_raw["read_raw(...)"] --> downsample;
    downsample(["downsample(...)"]) --> filter;
    filter(["filter(...)"]) --> remove_artifacts;
    remove_artifacts(["remove_artifacts(...)"]) --> epoch;
    epoch["epoch(...)"] --> source_localize;
    source_localize["source_localize(...)"];
    
    classDef parallel fill: #990000, stroke: #333, stroke-width: 3px, font-size:10px;
    
```
    
# Per cortical area (dataset.py)
* **generate_area_data()**/**generate_area_data_mmap()**


NB: round nodes are optional

