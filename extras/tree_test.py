def eval_index(database, current_index):
    index_split = [f'.keys()[{str(x)}]' for x in current_index]  # Result will look like ['.keys()[1]','.keys()[2]','.keys()[3]'] etc
    all_indexes = ''.join(index_split)  # Result will look like .keys()[1].keys()[2].keys()[3] etc
    return eval(f'database{all_indexes}', locals())


testdb = {'1': {'2': {'3': {'4': 'test'}}}, '__test_': 'itworks'}

print(eval_index(testdb, [0, 1]))

# x.keys()[y].keys()

# dict(dict(x.keys())[1])[1]