import hashlib
import pandas as pd
import os
import sys
from datetime import date



class UnHasher:
    def __init__(self, encoding: str = 'utf-8') -> None:
        self.hashing_tech: str = ''
        self.target_file: str = ''
        self.match_file: str = ''
        self.encoding: str = encoding
        self.hashed_file_name: str = ''

    def main_menu_(self) -> None:
        """
        Main menu of the tool.
        """
        while True:
            menu_options = ("\nSelect the number of one option from the list below.",
                            "\t1) Hash a list of IDs using a specific hashing method",
                            "\t2) Match a target file of hashed IDs with an internal list of hashes",
                            "\t3) Exit")
            for m in menu_options:
                print(m)
            option = input("\nSelect an option from the menu: ")
            if not option.isdigit():
                print('Invalid option. Try again typing a number from the list of options.')
            elif int(option) == 1:
                self.hash()
                break
            elif int(option) == 2:
                self.unhash()
                break
            elif int(option) == 3:
                break
            else:
                print('Invalid option. Try again entering a valid option.')

    @staticmethod
    def check_target_file(target_file) -> bool:
        if target_file[-4:] == '.csv' and os.path.exists(target_file):
            print('\nTarget file of hashes set to {}'.format(target_file))
            return target_file
        elif target_file[-4:] != '.csv':
            print('\nThe file extension is other than CSV. This module only accepts CSV files.')
            return ''
        else:
            print('\nFile not found. Check spelling and enter again')
            return ''

    @staticmethod
    def select_hash_method(match_file: str, encoding: str, hash_tech: str) -> pd.Series:
        # Import lookup hash list
        print('\nLoading lookup list.')
        df = pd.read_csv(match_file, encoding=encoding)
        to_match = df.iloc[:, 0]

        # Hash according to the hashing method selected
        if hash_tech == 'MD5':
            for i in range(len(to_match)):
                to_match[i] = hashlib.md5(to_match[i].encode(encoding)).hexdigest()
        elif hash_tech == 'SHA-1':
            for i in range(len(to_match)):
                to_match[i] = hashlib.sha1(to_match[i].encode(encoding)).hexdigest()
        elif hash_tech == 'SHA-224':
            for i in range(len(to_match)):
                to_match[i] = hashlib.sha224(to_match[i].encode(encoding)).hexdigest()
        elif hash_tech == 'SHA-256':
            for i in range(len(to_match)):
                to_match[i] = hashlib.sha256(to_match[i].encode(encoding)).hexdigest()
        elif hash_tech == 'SHA-384':
            for i in range(len(to_match)):
                to_match[i] = hashlib.sha384(to_match[i].encode(encoding)).hexdigest()
        elif hash_tech == 'SHA-512':
            for i in range(len(to_match)):
                to_match[i] = hashlib.sha512(to_match[i].encode(encoding)).hexdigest()
        else:
            print('\nThere was an error with the hashing technique selected.')
            sys.exit()
        print('Lookup list succesfully hashed')
        return to_match

    def hash_menu(self) -> None:
        """
        It prompts a list of available languages to hash/unhash.
        :return:
        """
        # Hashmap of functions and hashing methods
        hash_functions = ("\n\t1) MD5", "\t2) SHA-1", "\t3) SHA-224", "\t4) SHA-256", "\t5) SHA-384", "\t6) SHA-512")
        hash_keymap = {1: "MD5", 2: "SHA-1", 3: "SHA-224", 4: "SHA-256", 5: "SHA-384", 6: "SHA-512"}

        # Ask for the hashing technique to be used
        while self.hashing_tech == '':
            print('\nSelect the number of the hashing technique from the list: ')
            for ht in hash_functions:
                print(ht)
            selected: str = input("Method number: ")
            if not selected.isdigit():
                print("\nThat option is not available. Please try again entering a number.")
            elif 1 <= int(selected) <= 6:
                self.hashing_tech = hash_keymap[int(selected)]
            else:
                print("\nThe input is not valid. Try again entering a valid integer from the list")

    def hash(self) -> None:
        print('\n>>> Selected unhashing tool.')

        # Ask for file format anc check if it's CSV and exists
        while self.target_file == '':
            self.target_file = input("\nEnter the name of the file with the hashed IDs (only CSV format is accepted): ")
            self.target_file = self.check_target_file(self.target_file)

        # Start menu to select hashing technique
        self.hash_menu()

        # Ask of the output file name
        while self.hashed_file_name == '':
            self.hash_file_name = input(
                "\n(OPTIONAL) Enter the name of the new file (with .csv extension) or leave blank to use a default name: ")
            if self.hash_file_name[-4:] != '.csv':
                self.hash_file_name == ''
                print("\nThe format of the entered name is not valid. Make sure it ends as '.csv'.")
            elif not self.hash_file_name or len(self.hash_file_name) <= 1:
                self.hash_file_name = '{0}_hash_list_{1}.csv'.format(self.hashing_tech, date.today())
            elif len(self.hash_file_name) > 4 and self.hash_file_name[-4:] == '.csv':
                print('\nOutput file name set to {}'.format(self.hash_file_name))
                break

        # Parameter selection confirmation
        while True:
            mess_ = ('\nOriginal file to be hashed: {}'.format(self.target_file),
                     'Hashing method selected: {}'.format(self.hashing_tech),
                     'Output file name: {}'.format(self.hash_file_name)
                     )
            for txt in mess_:
                print(txt)
            print('\nDo you want to start the hashing module with these parameters? (Y/N)')
            option_ = input('[WARNING!] Type N to reset all the parameters and return to the main menu ').lower()
            if option_ not in ('y', 'n'):
                print("\nI didn't understand the input... Please enter Y (Yes) or N (No). ")
            elif option_ == 'n':
                self.hash_file_name = ''
                self.hashing_tech = ''
                self.main_menu_()
            elif option_ == 'y':
                # Start the hashing loop
                print('\nStarting the hashing loop. This may take a while...')
                out_ = self.select_hash_method(self.target_file, self.encoding, self.hashing_tech)
                out_.to_csv(self.hash_file_name)
                print('\nYour file has been successfully hashed. Returning to main menu.')
                self.hash_file_name = ''
                self.hashing_tech = ''
                self.target_file = ''
                return
            else:
                print('\nThe entered option is not valid. Please try again.')

    def pull_raw_data(self) -> pd.DataFrame():
        """
        This function can generate a new list of samples extracted from User Graph through Hive.
        :return: CSV file.
        """
        db = AXDBTools()
        graph_sql = """
            SELECT
             distinct uuid
            FROM
             xdevice.graph_communities_reference xd
            WHERE
             uuid_type in('idfa','gaid')
             and platform = 'AS'
             AND day = '2022-03-01'
                """
        # run hive query
        ids = set(db.run_hive_query(graph_sql)['uuid'])

        # Save pulled ids in a txt file
        file_name: str = './input/raw_data_{}.csv'.format(date.today())
        with open(file_name, 'a') as f:
            for i in ids:
                f.write(i)
                f.write(',')
                f.write('\n')
        self.match_file = file_name

    def unhash(self) -> None:
        """
        It starts the Unhashing module of the tool.
        """
        # global exists_
        print('\n>>> Selected unhashing tool.')

        # Ask for file format anc check if it's CSV and exists
        while self.target_file == '':
            self.target_file = input("\nEnter the name of the file with the hashed IDs (only CSV format is accepted): ")
            self.target_file = self.check_target_file(self.target_file)

        # Ask if there's is another file of hashes or if the user need to pull a new sample to hash.
        # It will prompt the pull_raw_data() function to generate a new file pulling data from Hive.
        exists_ = ''
        while not (exists_ and self.match_file):
            exists_ = input(
                "\nDo you already have a list of hashed IDs to match? (Y/N) \n(WARNING) If not a Hive pull request will be generated. This may take some time: ").lower()
            if exists_ == 'y':
                # Same check flow as in target_file
                while not self.match_file:
                    self.match_file = input("\nEnter the name of the file (only CSV format is accepted): ")
                    if self.match_file[-4:] == '.csv' and os.path.exists(self.match_file):
                        print('\nSample file of hashes set to {}'.format(self.match_file))

                        continue
                    elif self.match_file[-4:] != '.csv':
                        self.match_file = ''
                        print('\nThe file extension is other than CSV. This module only accepts CSV files.')
                    else:
                        self.match_file = ''
                        print('\nFile not found. Check spelling and enter again')
            elif exists_ == 'n':
                print("\nInitializing ID data extraction. This might take a while...")
                self.pull_raw_data()
                break
            elif exists_ == 'exit':
                return
            else:
                print(
                    "\nI didn't understand the input. Please enter Y for yes, N for no or enter Exit to get back to the main menu.")

        # Start hash menu
        self.hash_menu()

        # Check if parameters are correct. If not, return to main menu.
        params = ('\nThe selected parameters are: ',
                  'Target file to match: {}'.format(self.target_file),
                  'Lookup file: {}'.format(self.match_file),
                  'Hashing method: {}'.format(self.hashing_tech))

        for message in params:
            print(message)
        confirmation = input(
            '\nAre all these parameters correct? (Y/N) \n  Press N to reset all the parameters and go back to the main menu: ').lower()

        # Kick the lookup function
        if confirmation == 'y':
            print('\nStarting lookup analysis.')

            # Import target file to unhash
            print('\nImporting target list')
            target_ = pd.read_csv(self.target_file, encoding=self.encoding)
            target_ = target_.iloc[:, 0]

            # Hash the lookup match list
            to_match = self.select_hash_method(self.target_file, self.encoding, self.hashing_tech)

            # Check if raw hashes are in the pulled sample
            print('\nStarting matching algorithm.')
            count: int = 0
            calculated: int = 0
            matched_id: set = set()
            n_: int = len(target_)
            for hash in target_:
                calculated += 1
                if ((calculated / n_) * 100) % 5 == 0:
                    print('\nChecked {}% of the DB'.format((calculated / n_) * 100))
                if hash in to_match:
                    print('\n{0} ID hashes matched. {1}% of the DB.'.format(count, (count / calculated) * 100))
                    print(hash)
                    matched_id.add(hash)
                    count += 1
                # if (calculated / len(target_)) % 5 == 0:
                #     print('{}% of the target ids already looked up.'.format(calculated / hash))
            # Save list of IDs
            matched_id.to_csv('matched_results_{}.csv'.format(date.today()))

            print('\nFinished! These are the results:')
            print('\n', '-' * 30)
            print('{0} ID hashes matched. {1}% of the DB.'.format(count, (count / calculated) * 100))
            print('Find the list of matched IDs in the file matched_results.\nThank you for using UnHasher!')
            print('-' * 30)
            sys.exit()

        elif confirmation == 'n':
            self.target_file = ''
            self.match_file = ''
            self.hashing_tech = ''
            return None

        else:
            print("\nI didn't understand the input. Please enter either Y for yes or N for no.")



if __name__ == "__main__":
    print("\nWelcome to the UnHasher!")
    uh = UnHasher()
    uh.main_menu_()
