def generate(start='slug', step='parent__'):
    while True:
        yield start
        start = step + start
