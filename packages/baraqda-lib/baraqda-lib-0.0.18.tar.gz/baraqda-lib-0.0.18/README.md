# baraqda-lib
Generating data for testing using real distribution of person attributes in particular society.
For now data is generated only for Polish person. 

# How to run
Install library from pip

    pip install baraqda-lib

Check if everything is working by simple code below:

    from baraqdalib import Person
    from baraqdalib import Addresses
    from baraqdalib import Generator

    if __name__ == '__main__':
        abba = Addresses()
        print(abba.generate())  # print generated address
        abba = Person()
        abba.set()  # Generate person attributes
        print(abba.get())  # print generated person attributes
        abba = Generator()
        print(abba.generate('PL', 'male_first_name', 100, sep='\t'))  # generate one attribute from provided data

# How to use
For generating address use:

    Addresses.generate()
Library does not save generated data.

If you want to generate more addresses or change country, define these parameters when calling function.
    
    Addresses.generate(counter = 100, lang = 'PL')

For generating person attributes use:

    Person.set()
    Person.get()

If you want to generate more person attributes put above code in loop. You can also specify nationality of person using parameter lang ('PL', 'DE').

If you don't want to generate the whole person but only one attribute use Generator class.
Example:
    
    Generator.generate('PL', 'female_first_name', 100, sep='\t'))

This code provides list of 100 female first name. 

List of available attributes to generate for Polish person.
- age, 
- blood_type,
- cities_pops,
- eyes,
- female_first_name,
- female_second_name,
- female_surname,
- hair,
- male_first_name,
- male_second_name,
- male_surname


# Generating data

Generating data take place in class `Generator()`. Instance of this class provide function to read data, store data,
display data that was read from files and most import make a toss. Generating address and person took place in class Addresses and Person.


## Functions in `Generator()`

### Generator.draw(lang: str, data_type: str, count: int = 1, sep: str = ' ') -> List[str]

Drawing a results from given file, returning list with len(list) = counter

        Parameters:
        lang (str): Two letters shortcut for country.
        data_type (str): Name of file from which data should be generated.
        count (int):  How many records should be generated, Default is 1.
        sep (str): Set separators for columns in files. Default is single space.

        Returns:
        list: Returning list of generated data.

### Generator.search_files(path, sep, lang) -> None
Running this function erase all stored data and read it again. Use with caution!
        
    Parameters:
        sep (str): separator of columns in files
        lang (str): Two letters shortcut for country

    Returns: None

### Generator.read_files(filepath, separator, lang, filename) -> None
Reading files into class variable self._data

        Parameters:
        filepath (str): Filepath for a file
        separator (str): Separator of columns in files
        lang (str): Two letters shortcut for country
        filename (str): Filename

        Returns: None
        """

### Generator.generate(lang: str, data_type: str, counter: int = 1, sep: str = ' ') -> List[str]
Generating data with reading files. This is recommended way of using generator. 

    Parameters:
        lang (str): two letters shortcut for country
        data_type (str): name of file from which data should be generated
        counter (int): default is 1. How many records should be generated
        sep (str): default is single space. Set separators for columns in files

    Returns:
        list: Returning list of generated data.
        """


### Generator.access_data(lang: str, data_type: str) -> Dict[str, list]
Access data which are read from files. Helpful when you
        want to make sure that your files are in correct format

    Parameters:
        lang (str): Two letters shortcut for country
        data_type (str): Name of file from which data should be generated

    Returns:
        Dict: Returning dictionary with loaded data in class instance


## Generate polish person and address

To generate person and address we can use class Person and class Addresses 
This two class generate only fake polish person.

Library generate only person nat

## Functions in `Addresses()`
### Addresses._set_codes(self):
Get postal codes from file postal_codes.csv and save in self._postal_code list

    Parameters : None

    Returns: None

 ### Addresses._set_cities(self):
 Get cities names  from file cities.csv and save in self._cities list

    Parameters : None

    Returns: None

 ### Addresses._set_streets(self):
 Get street names from file streets.csv and save in self._streets list

    Parameters : None

    Returns: None


### Addresses.generate(self, counter: int = 1, lang: str = 'PL')
Generating address with city, street, street number,  and postal code

    Parameters:
        counter (int): Default is 1. You can specify how much addreses you want to generate
        lang (str): Default is 'PL'. By this argument you can choose from wchich country addresses should be generated.

    Returns:
        Dict(Dict()): returning generated addresses in nested dictionary for easy access


### Addresses.get_code(self, city: str)
Search and return postal code for a given city

    Parameters:
        city (str): Name of the city

    Returns:
        str: Returns postal code

### Addresses.get_sym_city(self, city: str)
Searching for city in cities and returning sym (identification)

    Parameters:
        city (str): name of city for searching

    Returns:
        str : return sym for searching city

### Addresses.get_streets(self, city_sym: int)
Generate random street for given city sym (identification) that is in this city.

    Parameters:
        city_sym (int): number of city syn

    Returns:
        str: returns random street


## Functions in `Person()`
Generating attributes for Polish person. For simple use set() and get() to generate one record,
for more make for loop with these two functions.
 

### Person.toss(self)
    Parameters: None

    Returns:
        int: return random value of 0 or 1 which determines gender

### Person.set_date_of_birth(self, nr_of_years)
Create date of brith using generated number of years.

    Parameters:
        nr_of_years (int): number of years of generated person

    Returns:
        str: returns calculated date of birth

### Person.set_pesel(self, date_of_birth, female_or_male)
Create polish identification number, PESEL

    Parameters:
        date_of_birth (str):
        female_or_male (int): determines gender

    Returns:
        str: returning calculated PESEL

### Person.set(self)
Generating parameters for a person based on

    Parameters: None

    Returns: None


### Person.get(self)
Print generated attributes

    Parameters: None

    Returns: None
        