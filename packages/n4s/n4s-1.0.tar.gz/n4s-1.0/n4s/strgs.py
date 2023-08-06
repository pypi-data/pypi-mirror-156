import re

## REMOVES CHARACTERS FROM TEXT
def clean_text(Input: str, Casing: str="default", Remove_Spaces: bool=False):
    '''
    Input: input string (str)
    Casing: 'default', 'lower', 'upper', 'title', 'camel' (str)
    Remove_Spaces: removes spaces between words (boolean)
    '''
    ## REMOVE SPECIAL CHARACTERS FROM STRING
    clean = re.sub(r"[^a-zA-Z0-9 ,*\u2019-]+"," ",Input).strip()
    ## CONVERT TO LOWERCASE
    if Casing == "lower":
        clean = clean.lower()
    ## CONVERT TO UPPERCASE
    elif Casing == "upper":
        clean = clean.upper()
    ## CONVERT TO TITLECASE
    elif Casing == "title":
        if len(clean) > 0:
            ## COLLECT EVERY WORD BELOW 4 CHARACTERS
            s = clean.split()
            short_words = ' '.join(i.capitalize() for i in s if len(s[s.index(i)]) < 4).lower().split(" ")
            ## CAPITALIZE INPUT
            clean = ' '.join(i.capitalize() for i in s)
            ## REPLACE INSTANCES OF SHORT WORDS IN CAPITALIZED INPUT, AND UN-CAPITALIZE THEM
            for i in range(len(short_words)):
                if short_words[i] in clean.lower():
                    index = clean.lower().index(short_words[i])
                    clean = clean.replace(clean[index], clean[index].lower())
            ## CAPITALIZE FIRST AND LAST WORDS IN STRING
            clean = clean[0].capitalize() + clean[1:]
            clean = clean.replace(clean.split(" ")[-1], clean.split(" ")[-1].capitalize())
    
    ## CONVERT TO CAMEL CASE
    elif Casing == "camel":
        s = clean.split()
        if len(clean) > 0:
            clean = s[0] + ''.join(i.capitalize() for i in s[1:])
    
    ## REMOVE SPACES
    if Remove_Spaces:
        clean = clean.replace(" ", "")
    
    ## RETURN
    return clean.strip()

## FILTER A LIST OF WORDS FROM STRING
def filter_text(Text: str, Filter: list, debug: bool=False):
    '''
    ARGUMENTS
    - Text: input text (str)
    - Filter: words to remove (list)
    - debug: (boolean)
    DESCRIPTION
    
    - Filters out a list of words in a string of text
    '''
    try:
        clean = re.compile('|'.join(map(re.escape, Filter)))
        filtered_Text = clean.sub("", Text).replace('  ', ' ')
        return filtered_Text.strip()
    except Exception:
        if debug:
            return print("\nn4s.string.filter_text()\nOperation Failed\n")

## SHORTENS TEXT TO A SET LIMIT
def shorten_text(text: str, length: int, debug: bool=False, suffix: str='...'):
    '''
    ARGUMENTS
    - text: input (str)
    - length: length of string (int)
    - debug: (boolean)
    - suffix: default is '...' (str)
    DESCRIPTION
    - Shortens a string without cutting off words and adds a suffix
    '''
    ## DEBUGGER
    if debug:
        ## TEXT VALIDATION, STRING
        if not type(text) == str:
            print("\nInput text not a valid string")
            return
        ## LENGTH VALIDATION, INT
        if not type(length) == int:
            print("\nInput length not a valid integer")
            return
    ## MAIN
    try:
        ## RETURN TEXT IF LENGTH IS GREATER
        if len(text) <= length:
            return text
        else:
            ## SHORTEN TEXT AND ADD SUFFIX
            return ' '.join(text[:length+1].split(' ')[0:-1]) + suffix
    ## ERROR
    except Exception:
        return print("\nn4s.string.shorten_text():\nOperation Failed - Enable debug for more info\n")
