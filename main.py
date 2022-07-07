import hashlib
import pandas as pd
import os


class UnHasher:
    def __init__(self, encoding: str = 'utf-8') -> None:
        self.hashing_tech: str = ''
        self.target_file: str = ''
        self.match_file: str = ''
        self.encoding: str = encoding



    def main_menu_(self) -> None:
        """
        Main menu of the tool.
        """
        while True:
            menu_options = ("\nSelect the number of one option from the list below.",
                            "\t1) Create a list of hashed IDs",
                            "\t2) Match a target file with hashed IDs with an internal list of hashes",
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
    def check_target_file(target_file: str) -> bool:
        while not target_file:
            target_file = input("\nEnter the name of the file with the hashed IDs (only CSV format is accepted): ")
            if target_file[-4:] == '.csv' and os.path.exists(target_file):
                print('\nTarget file of hashes set to {}'.format(target_file))
            elif target_file[-4:] != '.csv':
                print('\nThe file extension is other than CSV. This module only accepts CSV files.')
                return False
            else:
                print('\nFile not found. Check spelling and enter again')
                return False
        return True

    def hash_menu(self) -> None:
        """
        It prompts a list of available languages to hash/unhash.
        :return:
        """
        hash_functions = ("\n\t1) MD5", "\t2) SHA-1", "\t3) SHA-224", "\t4) SHA-256", "\t5) SHA-384", "\t6) SHA-512",
                          "\t7) Return to main menu")
        hash_keymap = {1: "MD5", 2: "SHA-1", 3: "SHA-224", 4: "SHA-256", 5: "SHA-384", 6: "SHA-512"}
        while True:
            for ht in hash_functions:
                print(ht)
            selected: str = input("\nSelect the number of the hashing technique from the list: ")
            if not selected.isdigit():
                print("\nThe input is not valid. Please try again entering a number.")
                print("\nThe input is not valid. Please try again entering a number.")
            elif 1 <= int(selected) <= 6:
                self.hashing_tech = hash_keymap[int(selected)]
                return
            elif int(selected) == 7:
                print('\nResetting parameters and returning to the main menu...')
                self.target_file = ''
                self.match_file = ''
                self.main_menu_()
            else:
                print("\nThat option is not available. Try again entering a valid integer from the list")

    def hash(self):
        print('\nSelected unhashing tool.')

        # Ask for file format anc check if it's CSV and exists
        while self.target_file == '':
            self.target_file = input("\nEnter the name of the file with the hashed IDs (only CSV format is accepted): ")
            if not self.check_target_file(self.target_file): self.target_file = ''

        # Start menu to select hashing technique
        self.hash_menu()

    def pull_raw_data(self) -> str:
        """
        This function can generate a new list of samples extracted from User Graph through Hive.
        :return: CSV file.
        """
        db = AXDBTools()
        graph_sql = """
            SELECT
             DISTINCT uuid
            FROM
             graph_data
            WHERE
             uuid_type in('idfa','gaid')
                """
        # run hive query
        ids = set(db.run_hive_query(graph_sql)['uuid'])

        # Save pulled ids in a txt file
        with open('./input/raw_data.csv', 'a') as f:
            for i in ids:
                f.write(i)
                f.write(',')
                f.write('\n')
        self.match_file = './input/raw_data.csv'

    def unhash(self) -> None:
        """
        It starts the Unhashing module of the tool.
        """
        # global exists_
        print('\nSelected unhashing tool.')

        # Ask for file format anc check if it's CSV and exists
        while self.target_file == '':
            self.target_file = input("\nEnter the name of the file with the hashed IDs (only CSV format is accepted): ")
            if not self.check_target_file(self.target_file): self.target_file = ''

        # Ask if there's is another file of hashes or if the user need to pull a new sample to hash.
        # It will prompt the pull_raw_data() function to generate a new file pulling data from Hive.
        exists_ = ''
        while not (exists_ and self.match_file):
            exists_ = input(
                "\nDo you already have a list of hashed IDs to match? (Y/N) \n(WARNING) If not a Hive pull request will be generated. This may take some time. ").lower()
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

        self.hash_menu()

        # Check if parameters are correct. If not, return to main menu.
        params = ('\nThe selected parameters are: ',
                  'Target file to match: {}'.format(self.target_file),
                  'Lookup file: {}'.format(self.match_file),
                  'Hashing technique: {}'.format(self.hashing_tech))

        for message in params:
            print(message)
        confirmation = input(
            '\nAre all these parameters correct? (Y/N) \n  Press N to reset and go back to the main menu: ').lower()

        # Kick the lookup function
        if confirmation == 'y':
            print('\nStarting lookup analysis.')

            # Import target file to unhash
            print('\nImporting target list')
            target_ = pd.read_csv(self.target_file, encoding=self.encoding)
            target_ = target_.iloc[:, 0]

            # Import lookup hash list
            print('\nLoading lookup list.')
            df = pd.read_csv(self.match_file, encoding=self.encoding)
            to_match = df.iloc[:, 0]

            # Convert internal ids into the selected hashing technique
            print('\nHashing lookup list.')
            if self.hashing_tech == 'MD5':
                for i in range(len(to_match)):
                    to_match[i] = hashlib.md5(to_match[i].encode(self.encoding)).hexdigest()

            elif self.hashing_tech == 'SHA-1':
                for i in range(len(to_match)):
                    to_match[i] = hashlib.sha1(to_match[i].encode(self.encoding)).hexdigest()

            elif self.hashing_tech == 'SHA-224':
                for i in range(len(to_match)):
                    to_match[i] = hashlib.sha224(to_match[i].encode(self.encoding)).hexdigest()

            elif self.hashing_tech == 'SHA-256':
                for i in range(len(to_match)):
                    to_match[i] = hashlib.sha256(to_match[i].encode(self.encoding)).hexdigest()

            elif self.hashing_tech == 'SHA-384':
                for i in range(len(to_match)):
                    to_match[i] = hashlib.sha384(to_match[i].encode(self.encoding)).hexdigest()

            elif self.hashing_tech == 'SHA-512':
                for i in range(len(to_match)):
                    to_match[i] = hashlib.sha512(to_match[i].encode(self.encoding)).hexdigest()

            else:
                print('\nThere was an error with the hashing technique selected.')
                return
            print('Lookup list succesfully hashed')

            # Check if raw hashes are in the pulled sample
            print('\nStarting matching algorithm.')
            count = 0
            calculated = 0
            n_ = len(target_)
            for hash in target_:
                calculated += 1
                # print(hash)
                if ((calculated / n_) * 100) % 5 == 0:
                    print('\nChecked {}% of the DB'.format((calculated / n_) * 100))
                if hash in to_match:
                    print('{0} ID hashes matched. {1}% of the DB.'.format(count, (count / calculated) * 100))
                    count += 1
                    print(hash)
                # if (calculated / len(target_)) % 5 == 0:
                #     print('{}% of the target ids already looked up.'.format(calculated / hash))
            print('\nFinished! These are the results:')
            print('\n', '-' * 30)
            print('{0} ID hashes matched. {1}% of the DB.'.format(count, (count / calculated) * 100))
            print('Find the list of matched IDs in the file matched_results.csv.\nThank you for using UnHasher!')
            print('-' * 30)
            # sys.exit()

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
