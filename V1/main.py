
import re;

def is_valide_IDF (identifier) :

    pattern = r'^[A-Z][a-z0-9]{0,7}$'
    
    if re.match(pattern, identifier) :
        return True
    else :
        return False
    
identifiers = ['As56ss','sh78fh','Wi23la']
    
for identifier in identifiers :
    if is_valide_IDF(identifier): 
        print (identifier + ': valid')
    else: 
        print(identifier + ': invaid')