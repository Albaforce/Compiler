import json
import mmh3

class HashTable:
    def __init__(self, size=100):
        # Initialize the hash table with a list of empty buckets
        self.size = size
        self.table = [[] for _ in range(self.size)]  # Using a list of lists for chaining

    # TO DO : mmh3 + chaining , but for now FNV-1a works  
    def hash_function(self, key):
        """
        Simple hash function using Python's built-in hash() and FNV-1a for better distribution.
        """
        # FNV-1a Hashing function
        fnv_prime = 16777619
        hash_value = 2166136261
        for char in key:
            hash_value ^= ord(char)
            hash_value *= fnv_prime
        return hash_value % self.size

    def insert(self, key, value, var_type, size=None, is_const=False):
        """
        Insert a key-value pair into the hash table.
        value: actual value (either scalar or array)
        var_type: type of the variable ('CHAR', 'FLOAT', 'INTEGER')
        size: size of the array (only for CHAR arrays)
        is_const: whether it's a constant
        """
        # Default is_array is False and size is None unless a size is provided.
        is_array = False
        if size is not None:  # If size is given, assume it's an array
            is_array = True

        # Handle insertion for CHAR arrays
        if var_type == 'CHAR' and size is not None:
            entry = {
                'value': value,  # CHAR array
                'type': var_type,
                'is_array': True,
                'size': size,
                'const': is_const
            }
        # Handle insertion for INTEGER and FLOAT
        elif var_type in ['INTEGER', 'FLOAT']:
            entry = {
                'value': value,  # scalar values
                'type': var_type,
                'is_array': False,
                'size': None,
                'const': is_const
            }
        # Handle CHAR type without size (single character)
        elif var_type == 'CHAR' and size is None:
            entry = {
                'value': value,  # single CHAR
                'type': var_type,
                'is_array': False,
                'size': None,
                'const': is_const
            }
        else:
            raise ValueError("Unsupported type or parameters")

        # Insert into hash table with proper handling of collisions
        index = self.hash_function(key)
        for idx, existing_entry in enumerate(self.table[index]):
            if existing_entry[0] == key:
                self.table[index][idx] = (key, entry)  # Update existing entry
                return
        self.table[index].append((key, entry))  # Add new entry

    def search(self, key):
        """
        Search for a value by key in the hash table.
        Returns None if the key is not found.
        """
        index = self.hash_function(key)
        for entry in self.table[index]:
            if entry[0] == key:
                return entry[1]  # Return the value associated with the key
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


# Example usage
if __name__ == "__main__":
    # Create a new hash table
    hash_table = HashTable()

    # Insert some key-value pairs
    hash_table.insert("intVar", 10, "INTEGER", is_const=True)
    hash_table.insert("charVar", "A", "CHAR", is_const=False)
    hash_table.insert("String", "ABC", "CHAR", size=3, is_const=False)
    hash_table.insert("floatVar", 3.14, "FLOAT", is_const=True)
    hash_table.insert("Idf", 0, "INTEGER", is_const=False)

    # Search for keys
    print(f"charVar: {hash_table.search('charVar')}")
    print(f"charArray: {hash_table.search('charArray')}")
    print(f"intVar: {hash_table.search('intVar')}")

    # Delete a key
    print("Deleting 'intVar':", hash_table.delete("intVar"))

    # Display the contents of the hash table
    hash_table.display()

    # Save the contents to a JSON file
    hash_table.save_to_json('hash_table.json')
