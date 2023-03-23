import pickle


class File:
    def __init__(self, way='saves/Details.dev'):
        self.__way = way

    @property
    def way(self):
        return self.__way

    def download(self):
        """load information from file"""
        try:
            with open(self.__way, 'rb') as file:
                print(f'Loaded from {self.__way}')
                return pickle.load(file)
        except FileNotFoundError:
            print(f'|E|Cannot find the file {self.__way}')
            return None
        except EOFError:
            print(f'|E| Wrong format of file {self.__way}')
            return None

    def upload(self, obj):
        """save information into file"""
        with open(self.__way, 'wb') as file:
            pickle.dump(obj, file)
            print(f'Loaded to {self.__way}')

    def download_text(self):
        """load information from file in text mode"""
        try:
            with open(self.__way, 'r') as file:
                print(f'Loaded from {self.__way}')
                return file.read()
        except FileNotFoundError:
            print(f'|E|Cannot find the file {self.__way}')
            return None
        except EOFError:
            print(f'|E| Wrong format of file {self.__way}')
            return None
