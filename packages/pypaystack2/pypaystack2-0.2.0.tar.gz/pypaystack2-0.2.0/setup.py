# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['pypaystack2']

package_data = \
{'': ['*']}

install_requires = \
['requests>=2.28.0,<3.0.0']

setup_kwargs = {
    'name': 'pypaystack2',
    'version': '0.2.0',
    'description': '',
    'long_description': '# PyPaystack2\n\nA fork of [PyPaystack](https://github.com/edwardpopoola/pypaystack). A simple python wrapper for Paystack API.\n\nThis package works as you\'d expect pypaystack package to work, except\nthat all imports are from `pypaystack2` instead of `pypaystack`\n\ne.g\n\n```python\nfrom pypaystack2 import Transaction\n```\n\ninstead of\n\n```python\nfrom pypaystack import Transaction\n```\n\n## Features\n\n- Charge customers\n- Verify transactions\n- Create Plans\n- Get single or multiple transactions\n- Get single or multiple customers\n\n## Installation\n\n1. Create your [Paystack account](https://paystack.com/) to get your Authorization key that is required to use this package.\n2. Store your authorization key in your environment variable as "PAYSTACK_AUTHORIZATION_KEY" or pass it into the  \npypaystack objects at initiatialization.\n3. Install pypaystack2 package.\n\n```bash\npip install -U pypaystack2\n```\n\n## Examples\n\n```python\nfrom pypaystack2 import Transaction, Customer, Plan, Interval\n\n"""\nNote\n=====\nAll Response objects are namedtuples containing status_code, status, message and data\ne.g\ntransaction = Transaction(authorization_key="sk_myauthorizationkeyfromthepaystackguys")\nresponse = transaction.charge(email="customer@domain.com", auth_code="CustomerAUTHcode", amount=10000)\nprint(response.status_code)\nprint(response.status)\nprint(respons.data)\n"""\n\n#Instantiate the transaction object to handle transactions.  \n#Pass in your authorization key - if not set as environment variable PAYSTACK_AUTHORIZATION_KEY\n\ntransaction = Transaction(authorization_key="sk_myauthorizationkeyfromthepaystackguys")\nresponse = transaction.charge(email="customer@domain.com", auth_code="CustomerAUTHcode", amount=10000) # Charge a customer N100.\nresponse  = transaction.verify(refcode) # Verify a transaction given a reference code "refcode".\n\n\n#Instantiate the customer class to manage customers\n\ncustomer = Customer(authorization_key="sk_myauthorizationkeyfromthepaystackguys")\nresponse = customer.create(email="customer2@gmail.com", first_name="John", last_name="Doe", phone="080123456789") #Add new customer\nresponse = customer.getone("CUS_xxxxyy") # Get customer with customer code of  CUS_xxxxyy\nresponse = customer.getall() # Get all customers\n\n\n#Instantiate the plan class to manage plans\n\nplan = Plan(authorization_key="sk_myauthorizationkeyfromthepaystackguys")\nresponse = plan.create(name="Test Plan", amount=150000, interval=Interval.WEEKLY) # Add new plan\nresponse = plan.getone(240) # Get plan with id of 240\nresponse = plan.getall() # Get all plans\n\n```\n',
    'author': 'Edward Popoola',
    'author_email': 'edwardpopoola@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
