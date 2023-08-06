## Sample Pool Aliquot Size Calculator
---

This package can be used to quickly calculate the ratio of 1 unit volume one may need to use so that all aliquots contain the same amount of proteomics content

## Dependencies
```toml
pandas = "^1.4.3"
```

## Usage 
```python
import pandas as pd
from sample_pool.experiment import Experiment

# Read tabulated text file containing the data
path = r".\RN_220625_Hippo-TiO2_15TMT_Minipool_PSMs.txt"
df = pd.read_csv(path, sep="\t")

# Create a variable with list of columns containing sample data
samples = [
            "Abundance: 126",
            "Abundance: 127N",
            "Abundance: 127C",
            "Abundance: 128N",
            "Abundance: 128C",
            "Abundance: 129N",
            "Abundance: 129C",
            "Abundance: 130N",
            "Abundance: 130C",
            "Abundance: 131N",
            "Abundance: 131C",
            "Abundance: 132N",
            "Abundance: 132C",
            "Abundance: 133N",
            "Abundance: 133C"
        ]

# Create Experiment object with the dataframe and sample list as parameters
exp = Experiment(df, samples)

# Get aliquot size ratio as a dictionary with key being sample name and value being volume ratio
size = exp.get_aliquot_size(minimum_good_samples=10)

# By default get_aliquot_size would use the sample with the lowest normalized sum intensity as the base for ratio calculation. To specify the sample, you can use based_on_sample parameter.
size = exp.get_aliquot_size(based_on_sample="Abundance: 127C", minimum_good_samples=10)
print(size)
```
