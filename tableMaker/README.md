# tableMaker
This takes a simple markup of a table in a text file and converts it to valid LaTeX. Format of markup
is given in the Syntax section below.

## Instructions
There are three modes of operation:
### Standalone
You can do
`python tableMaker.py output.txt` where output.txt is the text file with the table you want to convert.
This produces "output.pdf" (matches the text file name with different extension). 

### Pipe
If you want to control the aspects of LaTeX compilation, you can also pipe in a table text file via
`cat output.txt | python tableMaker.py`. This spits out the LaTeX source. You can reproduce the standalone
functionality and even crop the resultant pdf file by doing 
`cat output.txt | python tableMaker.py | pdflatex | pdfcrop texput.pdf`. When piping into pdflatex, it seems
the default output file name is "texput.pdf".


### Import
You can also programmatically use the tableMaker by importing it via `import tableMaker as tm` (provided the tableMaker is 
in your PYTHONPATH). Then you can do stuff like
`print tm.getString("output.txt", complete=True)`
or
`print tm.getString("output.txt", complete=False)`.
This takes in the same text file and returns the LaTeX string. When
complete=True, you get a full LaTeX document, ready for compilation. When it is False, you only get the "\begin{tabular} ... \end{tabular}" part, so you can embed the table in other LaTeX code if desired.




## Syntax
Here is the output.txt file and the resulting table

```
\textbf{col1} | \textbf{col2} | \textbf{col3}  | \textbf{col4} | \textbf{col5}

mrc 1 2 cols  | b             | c              | d             | e
a             | b             | c              | d             | e
a             | mrc 2 1 rows  | mrc 3 3 $\met$ | d             | e
a             | b             | c              | d             | e
a             | b             | c              | d             | e
```


![output.pdf](https://raw.githubusercontent.com/aminnj/makers/master/tableMaker/images/output.png)

* You can specify normal latex (note the textbf and $$)
* Yes, $\met$ is built in, as is $\pt$, $\mt$, and $\mtmin$. :)
* `mrc # # [text]` is the format to specify a multirow/column environment. First number specifies the number
  of rows, second specifies the number of columns, and third ([text]) is simply the content to put into the box.
  Note that this code is placed in the top left cell that will comprise the combined box. Look at output.pdf 
  as an example for this text.
* Empty lines will cause another horizontal line to be drawn.
* When specifying mrc environment, the other cells can be empty or filled...they will get overwritten anyways!
* Note that spacing is not essential (except in the "mrc # # [text]" construction). I just did it for aesthetics here.
* Delimiter must be "|".
