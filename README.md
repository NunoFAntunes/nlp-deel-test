# Data Exploration and Understanding:

## Users

On a quick data analysis, we have found the following special cases in Users data:

- There is one user without a name
- Some users have middle name, others middle name letter, others no middle name
- The user Audrey (crHOEW9iLZ) only has one name
- Some users have their names altogether, for example AuroraPowell (i52RbjL6om)
- The user with the name Isaac Bell Deel and Daniel Deel, we must be sure if Deel is his actual surname or if it was an input error on the Deel system, including company name. (6fc89iJwho and FhRDVhmleA). This may also be a problem for our text matching algorithm. Same with Andrew Rodeel. (Hl7n5MGoJo)
- There may be some mispelled names. Is Penelop a mispelling of Penelope? (7wgTardvTI). Same with Andrw Richardson (qBCElYF454)
- One user has special characters in its name, Μarιa Perikleous (Qg12EWasd)
- There are two users with the same name and different IDs, Isabella Wilson (ToAD2rzvGA and VfY9DmIkiL)

## Transactions

On a quick data analysis, we have found the following special cases in Transactions data:

- Names are written in different cases (upper, lower, mixed)
- Middle name is included in the name in some cases (sometimes in users files, other times in transactions files), and these possibly represent the same person
- Middle name is different in users file and transactions file. For example: Olivia Roland Smith (transactions) and Olivia North Smith (users). Are these the same person?
- Names in different charsets.
  - Chinese:
    - The name 杨陈 (transactions) and Yang Chen (users).
  - Greek:
    - The name Αλέξανδρος Μπέικερ (transactions) and Alexander Baker (users) may be the same person.
    - The person Ἄλεξις Ava Anderson (transactions) and Alexis Anderson (users) may be the same person.
  - Hebrew:
    - אֲבִיגַיִל גרין (transactions) and Abigail Green (users) may be the same person.
- Random punctuation marks in names. For example !Isabel Wilson (transactions) and Isabel Wilson (users).
- Random Spaces in names. From Elijah Thomas for Deel, Hen ry Hill for Deel
- Random numbers in names. Harper580Adams, Michael 60413 Moore
- Names in leet writing (Ellie L0NG)
- Random diacritics in names (Évèlyn Allèn Jr.)
- Random special characters in names (Matthe';w Ki|ng)
- Misspelled names Davd # Carter
- Broken up names Andrew Richar dson
- Text with no name in transactions

# Task 1:

- Input: User name
- Output: List of transactions associated with the user.

## Approach:

There are two ways to approach this problem:
1- We can start with the transaction description, identify named entities (NER) and try to match them with the user name.
2- We can start with the user name from users.csv, and try to match it with all transaction descriptions, in order to find any matches.

Considering we have access to this users data, the 2nd option seems like it would yield better results, since we already know what we are looking for in the transaction descriptions.

Ideally, we should first try to associate the transaction data with the Users of the platform, in the users.csv file.
The input username should be validated, by matching it against the users.csv file. If the user exists, then we return all transactions associated with this user.
The mapping between a specific user and its transactions should be done apriori, not when the request is made to the API, in order to reduce the computation time. This means we should run our algorithm once, creating a dictionary mapping between users and transactions. If new transactions are added every day, we can set up a periodic task to continuing building upon the dictionary mapping, by running these new transactions through the built algorithm. This is assuming this system/API is used often.
The algorithm could be ran as a periodic task on all registered transactions in two ways:

- Immediately when a transaction is added to the system, it is mapped to a user by the algorithm
- A periodic task can be setup to run at night or in periods of lower system activity, takes the batch of transactions added that day, and maps them to users.
  Since deel has clients all over the world, we would have to study on the best times to run this periodic task, in order to not affect the system performance, were we to opt for the later solution.

## Algorithm:

1- Transaction description cleaning
2- NER on transactions, find out user names
3- Setup list of possible user names
4- Matching with users.csv
5- Return transactions associated with user
