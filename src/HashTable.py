import json
import mmh3

class HashTable:
    def __init__(self, size=500):
        # Initialize the hash table with a list of empty buckets
        self.size = size
        self.table = [[] for _ in range(self.size)]  # Using a list of lists for chaining

    
    # Add a scenario where 2 inputs map to the same key 
    def hash_function(self, key):
        """
        Simple hash function using Python's built-in hash() and FNV-1a for better distribution.
        """
        # FNV-1a Hashing function
        # fnv_prime = 16777619
        # hash_value = 2166136261
        # for char in key:
        #     hash_value ^= ord(char)
        #     hash_value *= fnv_prime
        # return hash_value % self.size
        return mmh3.hash(str(key)) % self.size

    # Inserting variables (Lexer's role)
    def insert(self, key):
        """
        Insert a key (variable name) into the hash table.
        This function only inserts the name of the variable initially.
        """ 
        
        entry = {
        'value': None,      # Placeholder for the value (to be updated later)
        'type': None,       # Placeholder for the type (to be updated later)
        'is_array': False,  # Placeholder for whether it's an array (to be updated later)
        'size': None,       # Placeholder for the array size (to be updated later)
        'const': None,       # Placeholder for the constant status (to be updated later)
    }

        # Insert into hash table with proper handling of collisions
        index = self.hash_function(key)
        for idx, existing_entry in enumerate(self.table[index]):
            if existing_entry[0] == key:
                # Avoid inserting duplicates
                return
        self.table[index].append((key, entry))  # Add new entry

   
    def update(self, key, var_type, up_type=None,value=None, size=None, is_const=False, ix=None):
        # ix is the index inside an array 
        """
        Update the entry for an existing variable in the symbol table with
        its type, value, array size, and constant status.
        """
        # getting the index
        index = self.hash_function(key)
        if(index is None):
            ValueError(f"{key} was not declared")
        
        if var_type == "CHAR":  # can be a char array or a single char
        # All cases:
            """
            DECLARATION
            CHAR T var
            T = 'X' var_init
            CHAR T[5] array
            INSTRUCTION
            T[2] = 'w' array_assign
        """
            if up_type == "var":
                is_array = False
                value = ''
                # size is none
                
            elif up_type == "var_init":
                is_array = False
                # value from parameters
                if (value is None):
                    ValueError("Missing CHAR value")
                # size is none
                
            elif up_type == "array":
                is_array = True    
                value = ' ' * size
                # size from parameters
                 
            elif up_type == "array_assign":
                # get ix from parameters
                is_array = True # kept as True
                index, pos, entry = self.search(key)
                
                if ix is None or not (0 <= ix < entry['size']) or not (entry["is_array"]):
                    raise IndexError(f"Index {ix} is out of bounds for variable {key}")
                
                if not isinstance(entry['value'], str):
                    raise ValueError(f"Variable {key} is not a string and cannot be indexed")
                
                value_as_list = list(entry['value'])  # Convert string to list for mutability
                value_as_list[ix] = value  # Update the character at the specified index
                updated_value = ''.join(value_as_list)  # Convert back to a string
                value = updated_value
                

        elif var_type in ["INTEGER", "FLOAT"]:
            """
            INTEGER A ; A = 5; INTEGER N[5]; N[2] = 5;
            var ,     , var_init ,  array , array_assign
            """
            if up_type == "var":
                is_array = False
                value = None
            
            elif up_type == "var_init":
                is_array = False
                # value from parameters
                if(value is None):
                    ValueError("Missing INTEGER value")
                # size is none
                
            elif up_type == "array":
                is_array = True
                value = [None] * size # padding with none
                # size from parameters
                
            elif up_type == "array_assign":
                #get ix from parameters
                is_array = True # keep it as true
                index, pos, entry = self.search(key)
                
                if entry["type"] == None:
                    raise ValueError(f"{key} was not declared")
                
                # type_checks = {
                # "INTEGER": lambda value: all(isinstance(item, int) for item in value),
                # "FLOAT": lambda value: all(isinstance(item, float) for item in value)
                # }

                # CONDITION = type_checks.get(var_type, lambda _: False)(entry['value'])
                
                if ix is None or not (0 <= ix < entry['size']) or not (entry["is_array"]):
                    raise IndexError(f"Index {ix} is out of bounds for variable {key}")
                
                # if not (isinstance(entry['value'], list) and CONDITION):
                #     raise ValueError(f"Variable {key} is not a list of {var_type} and cannot be indexed")

                tmp = entry['value']  
                tmp[ix] = value
                value = tmp
                
        
        if (is_const == True and value == None):
            raise ValueError(f"{var_type} {key} is CONST and has to be initialized")
        
        
        # Update the entry with the provided information
        for idx, (existing_key, entry) in enumerate(self.table[index]):
            if existing_key == key:
                entry['value'] = value
                entry['type'] = var_type
                entry['is_array'] = is_array
                entry['size'] = size if up_type != "array_assign" else entry['size']
                entry['const'] = is_const
                return
       

        # Update the entry in the symbol table
        for idx, existing_entry in enumerate(self.table[index]):
            if existing_entry[0] == key:
                self.table[index][idx] = (key, entry)  # Update the entry
                return

    
    def search(self, key):
        """
        Search for a value by key in the hash table.
        Returns None if the key is not found.
        """
        
        index = self.hash_function(key)
        
        for pos, entry in enumerate(self.table[index]):
            if entry[0] == key:
                 return (index, pos, entry[1])  # (bucket index, position in bucket, entry)
        return None  # Key not found

    
    def delete(self, key):
        """
        Delete a key-value pair from the hash table.
        Returns False if the key is not found.
        """
        index = self.hash_function(key)
        for idx, entry in enumerate(self.table[index]):
            if entry[0] == key:
                del self.table[index][idx]  # Remove the entry
                return True
        return False  # Key not found

    def display(self):
        """
        Display the hash table's content for debugging purposes.
        """
        for i, bucket in enumerate(self.table):
            if bucket:
                print(f"Bucket {i}: {bucket}")
    
    def save_to_json(self, filename):
        """
        Save the hash table's contents to a JSON file.
        """
        hash_table_dict = {}
        for bucket in self.table:
            for key, entry in bucket:
                hash_table_dict[key] = entry

        with open(filename, 'w') as f:
            json.dump(hash_table_dict, f, indent=4)
    
    def load_from_dict(self, data):
        """
        Populate the hash table from a dictionary.
        """
        for key, entry in data.items():
            index = self.hash_function(key)
            self.table[index].append((key, entry))

"""
# Example usage
if __name__ == "__main__":
    # Create a new hash table
    hash_table = HashTable()

    # Insert some keys
    hash_table.insert("T")
    hash_table.insert("arr")
    # testing chars
    hash_table.insert("C")
    hash_table.insert("P")
    hash_table.insert("Array")
    
    # testing int / float
    hash_table.insert("B")
    hash_table.insert("W")
    hash_table.insert("Z")
    
    # update(self, key, var_type, up_type,value=None, size=None, is_const=False, index=None):
    hash_table.update("T","INTEGER","array",size=5)  # Declares T as an array of size 5
    hash_table.update("B","FLOAT","var")
    hash_table.update("Z","FLOAT","var_init",value=12.6)
    hash_table.update("T","INTEGER","array_assign",value=1,ix=0)
    
    hash_table.update("T","INTEGER","array_assign",value=1,ix=4)

    # CHAR C var
    hash_table.update("C","CHAR","var",is_const=True)
    #  P = 'X' var_init
    hash_table.update("P","CHAR","var_init",'X')
    # CHAR Array[5]  array
    hash_table.update("Array","CHAR","array",size=5)
    
    # Array[0] = "A"  array_assign
    hash_table.update("Array","CHAR","array_assign",value="A",ix=0)
    hash_table.update("Array","CHAR","array_assign",value="C",ix=2)
    
    # Test search functionality
    print("Searching for T:")
    t_entry = hash_table.search("T")
    if t_entry:
        print(f"T: {t_entry}")
    else:
        print("T not found.")
    

    # Display the contents of the hash table
    hash_table.display()

    # Save the contents to a JSON file
    hash_table.save_to_json('Symbol_Table.json')
"""