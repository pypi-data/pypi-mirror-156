from random import randrange
from baraqdalib import Generator
from datetime import datetime


class Person:
    """Generating attributes for Polish person. For simple use set() and get() to generate one record,
     for more make for loop with these two functions.
    """
    def __init__(self):
        self.person_generator = Generator()

    def toss(self):
        """
        Parameters: None

        Returns:
        int: return random value of 0 or 1 which determines gender
        """
        return randrange(0, 2)  # checking if it is a male (1) or a female (0)

    def set_date_of_birth(self, nr_of_years):
        """Create date of brith using generated number of years in previous step

        Parameters:
        nr_of_years (int): number of years of generated person

        Returns:
        str: returns calculated date of birth
        """
        current_year = str(datetime.now())
        current_year = int(current_year[0:4])
        year_of_birth = current_year - nr_of_years
        month = randrange(1, 13)
        if month == 2 and year_of_birth % 4 == 0 and (year_of_birth % 100 != 0 or year_of_birth % 400 == 0):
            day = randrange(1, 29)
        elif month == 2 and year_of_birth % 4 != 0:
            day = randrange(1, 29)
        elif month == 1 or month == 3 or month == 5 or month == 7 or month == 8 or month == 10 or month == 12:
            day = randrange(1, 31)
        else:
            day = randrange(1, 31)
        if month < 10:
            if day < 10:
                date_of_birth = '0' + str(day) + '.0' + str(month) + '.' + str(year_of_birth)
            else:
                date_of_birth = str(day) + '.0' + str(month) + '.' + str(year_of_birth)
        else:
            if day < 10:
                date_of_birth = '0' + str(day) + '.' + str(month) + '.' + str(year_of_birth)
            else:
                date_of_birth = str(day) + '.' + str(month) + '.' + str(year_of_birth)
        return date_of_birth

    def set_german_ID(self, date_of_birth):
        """ Create German identifacation number

         Parameters:
         date_of_birth (str):

         Returns:
         str: returning calculated ID number
         """
        german_ID = date_of_birth[-2:]+date_of_birth[3:5] + date_of_birth[:2] +str(randrange(1, 9)) \
                    + str(int(date_of_birth[-2:])+10) + date_of_birth[3:5]+date_of_birth[:2] \
                    + str(randrange(1, 9)) + "D" + str(randrange(1, 9))
        return german_ID

    def set_pesel(self, date_of_birth, female_or_male):                 #func creates polish ID number
        """ Create polish identifacation number, PESEL

        Parameters:
        date_of_birth (str):
        female_or_male (int): determines gender

        Returns:
        str: returning calculated PESEL
        """
        if female_or_male == 'Male':
            gender = randrange(1, 10, 2)
        else:
            gender = randrange(0, 9, 2)
        if date_of_birth[-4] == '1':
            pesel = date_of_birth[-2:] + date_of_birth[3:5] + date_of_birth[0:2] + str(randrange(100, 999)) + str(
                gender)
            control_sum = str(int(pesel[0])*1)[-1] + str(int(pesel[1])*3)[-1] + str(int(pesel[2])*7)[-1] + str(int(pesel[3])*9)[-1] + str(int(pesel[4])*1)[-1] + str(int(pesel[5])*3)[-1] + \
                          str(int(pesel[6])*7)[-1] + str(int(pesel[7])*9)[-1] + str(int(pesel[8])*1)[-1] + str(int(pesel[9])*3)[-1]
            pesel = pesel + control_sum[-1]
        else:
            pesel = date_of_birth[-2:] + str(int(date_of_birth[3:5])+20) + date_of_birth[0:2] + str(randrange(100, 999)) + str(
                gender)
            control_sum = str(int(pesel[0])*1)[-1] + str(int(pesel[1])*3)[-1] + str(int(pesel[2])*7)[-1] + str(int(pesel[3])*9)[-1] + str(int(pesel[4])*1)[-1] + str(int(pesel[5])*3)[-1] + \
                          str(int(pesel[6])*7)[-1] + str(int(pesel[7])*9)[-1] + str(int(pesel[8])*1)[-1] + str(int(pesel[9])*3)[-1]
            pesel = pesel + control_sum[-1]
        return pesel



    def set(self, lang):      #generating parameters of a person based on our generator
        """Generating parameters for a person based on

        Parameters: None

        Returns: None
        """
        self.eyes = str(self.person_generator.generate(lang, 'eyes', 1, sep='\t'))[2:-2] #unisex attributes
        self.age = str(self.person_generator.generate(lang, 'age', 1, sep='\t'))[2:4]
        self.hair = str(self.person_generator.generate(lang, 'hair', 1, sep='\t'))[2:-2]
        self.blood_type= str(self.person_generator.generate(lang, 'blood_type', 1, sep='\t'))[2:-2]
        self.mothers_maiden_name = str(self.person_generator.generate(lang, 'female_surname', 1, sep='\t'))[2:-2]
        if self.age == 'less then a year':
            self.nr_of_years = 0                #temporary value needed to determine date of birth
            self.date_of_birth = self.set_date_of_birth(self.nr_of_years)
        else:                                   #0 if he/she was born this year
            self.nr_of_years = int(self.age[0:2])
            self.date_of_birth = self.set_date_of_birth(self.nr_of_years)
        if self.toss() == 0:
            self.gender = 'Female'              #female attributes
            self.first_name = str(self.person_generator.generate(lang, 'female_first_name', 1, sep='\t'))[2:-2]
            self.second_name = str(self.person_generator.generate(lang, 'female_second_name', 1, sep='\t'))[2:-2]
            while self.second_name == self.first_name:
                self.second_name = str(self.person_generator.generate(lang, 'female_second_name', 1, sep='\t'))[2:-2]
            self.surname = str(self.person_generator.generate(lang, 'female_surname', 1, sep='\t'))[2:-2]
            if lang == 'PL': #determinating nationality
                self.id_number = self.set_pesel(self.date_of_birth, 'Female')
            elif lang == 'DE':
                self.id_number = self.set_german_ID(self.date_of_birth)
        else:
            self.gender = 'Male'                #male attributes
            self.first_name = str(self.person_generator.generate(lang, 'male_first_name', 1, sep='\t'))[2:-2]
            self.second_name = str(self.person_generator.generate(lang, 'male_second_name', 1, sep='\t'))[2:-2]
            while self.second_name == self.first_name:
                self.second_name = str(self.person_generator.generate(lang, 'male_second_name', 1, sep='\t'))[2:-2]
            self.surname = str(self.person_generator.generate(lang, 'male_surname', 1, sep='\t'))[2:-2]
            if lang == 'PL': #determinating nationality
                self.id_number = self.set_pesel(self.date_of_birth, 'Male')
            elif lang == 'DE':
                self.id_number = self.set_german_ID(self.date_of_birth)

    def get(self):
        """Print generated attribiutes

        Parameters: None

        Returns: None
        """
        if self.second_name == ' ':
            self.attributes = {
                "name": self.first_name,
                "surname": self.surname,
                "gender": self.gender,
                "mother_maiden_name": self.mothers_maiden_name,
                "eyes": self.eyes,
                "hair": self.hair,
                "age_in_years": self.age,
                "date_of_birth": self.date_of_birth,
                "blood_type": self.blood_type,
                "ID": self.id_number

            }
        else:
            self.attributes = {
                "name": self.first_name,
                "second name": self.second_name,
                "surname": self.surname,
                "gender": self.gender,
                "mother_maiden_name": self.mothers_maiden_name,
                "eyes": self.eyes,
                "hair": self.hair,
                "age_in_years": self.age,
                "date_of_birth": self.date_of_birth,
                "blood_type": self.blood_type,
                "ID": self.id_number

            }
        return self.attributes

