pysquale
========

Useful lib for text processing in Portuguese.

The name of the lib was inspired by the name of the famous Brazilian
Teacher `Pasquale <https://pt.wikipedia.org/wiki/Pasquale_Cipro_Neto>`__

Usage
-----

.. code:: python

   from pysquale.common.pipeline import ReducerPipeline
   from pysquale.words.cleaning import remove_accentuation, remove_punctuation, to_lower

   func_list = [to_lower, remove_accentuation, remove_punctuation]
   text = "Olá, quem é você?"
   pipe = ReducerPipeline(target=text, items=func_list)
   output = pipe.run()
   print(output)

   # Should print:
   # ola quem e voce"

Contributing
------------

Pull requests are welcome. For major changes, please open an issue first
to discuss what you would like to change.

Please make sure to update tests as appropriate.

License
-------

`MIT <https://choosealicense.com/licenses/mit/>`__
