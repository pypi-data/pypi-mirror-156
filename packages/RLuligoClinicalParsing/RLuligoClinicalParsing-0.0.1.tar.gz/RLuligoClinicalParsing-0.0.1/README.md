# r-luligo-clinical-parsing

<b>SOLUTION TYPE:</b> Proof of Concept. <br> 
<b>DEVELOPER:</b> Rolando Ramirez Luligo. <br>
<b>PURPOSE:</b> to automatically escape nested characters that break the pandas dataframe.

<p><b>How to install the RLuligoClinicalParsing Package?</b></p>
<code>pip install -U git+https://github.com/rolandoluligo/r-luligo-clinical-parsing.git@main</code>
<p></p>
<p><b>How to use the package?</b></p>

The python package includes a function named LuligoParsingNotes (p1,p2,p3) that receives 3 string parameters

<code>csvfile (p1)</code> = which must be the full path of the csv file in gcs.

<code>fdelimmter (p2)</code> = which is the field delimiter character being used in the csv file (comma or other character).

<code>tidentifier (p3)</code> = which is the text identifier character being used to wrap the text field in the csv file.

<b>Is there a sample code?</b> Yes

<code>#Python</code>

<code>import RLuligoClinicalParsing as CDIParser</code>

<code>csvfile = "gcs://bucket/clinical_note.csv"</code>
  
<code>Fdelimmter = '|'</code>

<code>Tidentifier = '`'</code>

<code>df = CDIParser.LuligoParsingNotes(csvfile, fdelimmter, tidentifier)</code>
  
<b>What output the function returns?</b> 

A panda’s data-frame generated from the input csv file.
