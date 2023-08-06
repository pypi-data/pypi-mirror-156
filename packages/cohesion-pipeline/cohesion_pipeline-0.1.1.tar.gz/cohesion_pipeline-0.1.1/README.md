# The Cohesion Pipeline

Given a division, Cohesion pipeline should give a cohesion score and recommend a suitable name for each group
A suitable should suit each member of the group and be the tightest one (no entities in other groups suits the name), using inter and intra score


## Installation

```bash
pip install cohesion-pipeline
```

## Usage Example
The input to the cohesion_score functin must be a csv,txt,tsv file with a tab['\t'] seperator and must have 'label' and 'text' columns
```python
import pandas as pd
from cohesion import cohesion_pipeline

data = {"text":
            ["we like to play football",
             "I'm playing football better than neymar and cristano ronaldo",
             'I like Fifa more than I like football, My Fav team is #RealMadrid Hala Madrid',
             'Hamburger or Pizza? what would i choose? I will eat both of them, it so tasty!',
             'banana pancakes with syrup maple, thats my favorite meal'],
        'label':
            [1, 1, 1, 2, 2]}
df = pd.DataFrame(data)
score, res = cohesion_pipeline.cohesion_df(df)
print("Cohesion Final score is", score)
print("Cohesion Topics are:", res)

```
