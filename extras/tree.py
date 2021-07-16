from pyndb import PYNDatabase
testdb = PYNDatabase({'1': {'2': {'3': {'4': 'test'}}}, '__test_': 'itworks'})

attrs = dir(testdb)
CORE_NAMES = testdb.universal.CORE_NAMES + testdb.universal.MASTER_NAMES

print(CORE_NAMES)
print(attrs)

attrs[:] = [a for a in attrs if not (a.startswith('__') and a.endswith('__')) and a not in CORE_NAMES]

print(attrs)


class Tree:
    def __init__(self, database):
        self.db = database.fileObj
        self.result = ''
        self.current_index = []

    def worker(self):
        index_split = self.current_index.split('.')
        number_of_dashes = int(index_split[len(index_split)-1])  # Gets the last number in the current index
        self.result += f'{"-"*number_of_dashes}+ '  # Result will look like ---+ name

    def eval_index(self):
        index_split = [f'[{str(x)}]' for x in self.current_index]  # Result will look like ['[1]','[2]','[3]'] etc
        all_indexes = ''.join(index_split)  # Result will look like [1][2][3] etc
        eval(f'self.db{all_indexes}', locals())