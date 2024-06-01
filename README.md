# Tools
Scripts to help me analyze different data. 

I usually put these in my bashrc profile to be conveniently used. You might want to define the input files as *$PWD/input_file* if you don't want to type the whole path.

## Descriptions

### niceview 
It is a simple python script to better analyze and present messy csv files.

### coltoro
I created this tool to better visualize multi-column files. It reformats a multi-column file so that the columns are displayed one ofter another. You can specify the delimiter token separating the columns as well as the space you want between two lines. The reformatted file is then piped into vim so that you can browse it, save it or clip from it.

### teatool
I created this tool to analyze translation outputs for quality metrics such as empty translations and source copying and hallucinatory outputs. Each file to be analyzed must have exactly three columns: source, translation, and reference. For best results, consider running the output of the program (translation_stats.csv) through niceview. 

