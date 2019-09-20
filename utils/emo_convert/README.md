# emoji convertor

This is a simple implementation of emoji convertor.

## To use this

Please include the following lines in your code

```python
from utils.emo_convert.emo_convertor import convert_sentence
from utils.emo_convert.emo_map import emo_map_basic
```

Then you can use this plugin with

```python
converted = convert_sentence(sentence, emo_map_basic)
```

## For further development

You can simple add more emoji mappings in `emo_map_basic` or you can create other maps.
