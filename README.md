# teenytinycompiler
Adapted from: https://austinhenley.com/blog/teenytinycompiler1.html
Compiles to C
`python3 teenytiny.py [filename]`

Supports the following:
## Assignment
`LET foo = bar`

## Conditionals
`IF condition THEN
  statement
ENDIF`

## Looping
`WHILE condition REPEAT
  statement
ENDWHILE`

## Print
`PRINT "text"`


## Label and GOTO
`LABEL foo`
`GOTO foo`
