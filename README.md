# All-in-One Investments Tracker

Django based application to manage your investments wallets build with different type of assets. Dedicated mainly for investors with more passive approach, than for a day-traders.

## Table of Contents
- [Setup](#setup)
- [Features](#features)
- [To-do](#to-do)
- [Tech Stack](#tech_stack)
- [Contributing](#contributing)
- [License](#license)

  
## Setup

To run your local copy of application 

1. Clone the repository: `git clone https://github.com/MaBober/investments_tracker.git`
2. Navigate to the project directory: `cd repo`
3. Install the requirements: `pip install -r requirements.txt`. I strongly recommend to do it with activated virtual environment for this application.
5. Run migrations: `python manage.py migrate`
6. Start the server: `python manage.py runserver`
7. Interact with applition using [API Endpoints](api_endpoints) or using admin panel on `http://127.0.0.1:8000/admin`

## Features

At this project stage application provide limited functions.

### API functions (regular user)
- Creating diffrent wallets to organize your assets (e.g. safety cushion and long-term wallet)
- Matching diffrent type of accounts (e.g. brokerage account and bank account) with your wallet
- Adding money deposits to your accounts
- Adding BUY and SELL transactions made with your accounts.

##### API Endpoints

- `GET /wallets/`: Retrieve a list of wallets.
- `GET /wallets/<int:pk>/`: Retrieve a specific wallet.
- `GET /accounts/`: Retrieve a list of accounts.
- `POST /accounts/`: Create a new account.
- `GET /accounts/<int:pk>/`: Retrieve a specific account.
- `PUT /accounts/<int:pk>/`: Update a specific account.
- `DELETE /accounts/<int:pk>/`: Delete a specific account.
- `GET /deposits/`: Retrieve a list of deposits.
- `POST /deposits/`: Create a new deposit.
- `GET /deposits/<int:pk>/`: Retrieve a specific deposit.
- `PUT /deposits/<int:pk>/`: Update a specific deposit.
- `DELETE /deposits/<int:pk>/`: Delete a specific deposit.
- `GET /transactions/`: Retrieve a list of transactions.
- `POST /transactions/`: Create a new transaction.
- `GET /transactions/<int:pk>/`: Retrieve a specific transaction.
- `PUT /transactions/<int:pk>/`: Update a specific transaction.
- `DELETE /transactions/<int:pk>/`: Delete a specific transaction.
- `GET /users/`: Retrieve a list of users.

For more details about each endpoint, please refer to the source code.

### Admin panel functions
- Adding new asset types to apllications, including all supporting data like diffrent currencies and exchange markets.
- Manually updating of asset prices.

## To-do

Features which will be implemented in the future:
- New assets type - cryptocurrency and bonds.
- Summary of the present percentage composition of wallet, based on realtime assets prices.
- Defining user investment strategy to make sugestions about future deposits and wallet composition updates.

## Tech Stack

**Server Side:**
- [Python](https://www.python.org/)
- [Django](https://www.djangoproject.com/)
- [Django REST Framework](https://www.django-rest-framework.org/)

**Database:**
- [SQLite](https://www.sqlite.org/)

**Testing:**
- [PyTest](https://docs.pytest.org/en/latest/)


## Contributing

This is an open-source project and all contributions you make will be greatly appreciated.

If you have new ideas, or would like to cover one of the exisitng issue, fork the repository and make Pull Request with your updates.

## License

This project is open source and available under the MIT License.

## Contact

Application created by [@MaBober](https://github.com/MaBober)

[![LinkedIn][github-shield]][github-bober-url]
[![LinkedIn][linkedin-shield]][linkedin-bober-url]


[github-bober-url]: https://github.com/MaBober
[linkedin-bober-url]: https://www.linkedin.com/in/marcinbober/
[github-shield]: https://img.shields.io/badge/GitHub-100000?style=for-the-badge&logo=github&logoColor=white
[linkedin-shield]: https://img.shields.io/badge/-LinkedIn-black.svg?style=for-the-badge&logo=linkedin&colorB=555

