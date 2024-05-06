# Web Application README

### User Registration/Login
- Users can register or log in using their credentials to access the system.
- During registration, users provide their name, username, and userid.
- Webpages Involved:
  - `login.html`: Allows users to log in by submitting a POST request verified against the 'users' table in the database. Incorrect login credentials lead to 'incorrect_login.html'.
  - `register.html`: Enables the creation of a new user by providing name, username, and userid. Errors during registration, due to constraints, result in 'incorrect_user.html'.

### Dashboard
- Upon login, users are directed to a dashboard showing wallet balances, recent transactions, asset addition, transaction buttons, and, for miner-type users, rewards info redirection.
- File: `index.html`
- Wallet information extracted from 'digitalassets', 'digitalcurrency', 'currency' tables, and 'miner' table for miner status.

### Transaction Creation
- Users can initiate transactions specifying recipient's userid and asset-type, with further dropdowns for digital currency, currency, and digital assets.
- File: `transaction.html`
- Invalid requests or errors result in 'incorrect_transaction.html'.
- Backend operations involve various tables: 'completes', 'execute_transaction_storedin', 'performs', 'controls', 'gains_reward_relays_reward', 'digitalcurrency', 'currency', 'digitalasset'.

### Transaction History
- Users can view their transaction history and filter transactions based on incoming/outgoing transactions.
- File: `history.html`
- Redirects to 'incoming_transactions.html' and 'outgoing_transactions.html'.
- Extraction and sorting based on 'execute_transaction_storedin', 'controls', and 'node' table data.

### Node Management
- Nodes are randomly chosen from the 'node' and 'miner' tables in the backend for transactions or mining purposes.

### Mining Information
- Users interested in mining can access statistics, participate in mining pools, and view mining rewards.
- File: `rewards.html`
- Mining rewards details extracted from 'gains_reward_relays_reward' table.

### Wallet Management
- Users can manage digital assets within their wallets, including depositing, withdrawing, and exchanging assets.
- Addition of assets involves selecting asset type and valuation/amount (without an actual payment gateway).


## Javscript and JQuery Usage
In the `transaction.html` and `add_assets.html`, we use the Javascript to dynamically create dropdown menu based on the asset types. JQuery is being used to personalise the rewards, transaction-history, asset addition, user profile and rewards for a logged in user.

## Tools Used
We have used Stackoverflow for debugging the code, Bootstrap documentation, HTML and CSS to design the website.
