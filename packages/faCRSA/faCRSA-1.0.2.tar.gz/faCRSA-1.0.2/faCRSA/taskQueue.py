from huey import SqliteHuey

huey = SqliteHuey(filename='data.db')

import tasks
