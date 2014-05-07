import sys, os


if sys.version < '3':
    sys.path.append('PyMySQL-master')
else:
    sys.path.append(os.path.join(os.path.dirname(__file__)))
    sys.path.append(os.path.join(os.path.dirname(__file__), 'PyMySQL-master'))
