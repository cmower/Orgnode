import Orgnode
import pprint
import datetime

data = Orgnode.makelist('test.org')
now = datetime.date.today()

for el in data:

    print("---------")
    print(el.Priority())

    print("type priority", type(el.Priority()))

    deadline = el.Deadline()
    print(deadline)
    print("type(deadline)=", type(deadline))

    if not isinstance(deadline, str):
        time_to_deadline = deadline - now
        print(type(time_to_deadline.days))
