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
- After ref, we may have names instead of transaction reference.

# Task 1:

- Input: User name
- Output: List of transactions associated with the user.

## Approaches considered:

There are two ways to approach this problem:
1. We can start with the transaction description, identify named entities (NER) and try to match them with the user name.
2. We can start with the user name from users.csv, and try to match it with all transaction descriptions, in order to find any matches.

Considering we have access to this users data, the 2nd option seems like it would yield better results, since we already know what we are looking for in the transaction descriptions. Additionally, the description of the transaction is very short, with a lot of mistakes and sometimes with sentence a structure that does not make sense. The names are also sometimes jumbled in the text (e.g. the first name and the last name have words or text in between) This leads me to believe NER might not give the best results.


## Algorithm:

1. Users name cleaning
  1. Handle other alphabets, accents, etc
  2. Convert to lowercase
2. Transaction description cleaning
  1. Handle other alphabets, accents, etc
  2. Convert to lowercase
  3. Remove all elements that are not part of the name (e.g. reference, from, to, numbers, etc)
  4. Remove unnecessary spaces 
3. Compare users name with description, using fuzzy matching (approximate string matching)



## Steps

In order to maximize the probability of finding names in the text, and considering surnames can be very varied and hard to find or match against specific rules (especially in this case, where we can have misspelled surnames, written in leet, detached from the first name), I have opted to remove all the elements from the text that I can identify as definitely not being part of the name.

One of these elements is the reference. References always start with ref, followed by 15 characters, two forward slashes, 11 or 12 digits, another two forward slashes and cntr.

To separate the ref number from the rest of the text I have created a regex which managed to cover 100% of the references in the text and not catch anything else.
The initial regex, which catches 99% of all cases is the following:

```
ref .{10,25}\/\/.{10,20}\/\/c\s*n\s*t\s*r
```

This regex also catches cases where the reference has white spaces in it, including cases which have spaces within the "cntr" token. This token is a crucial part to tag the string as it indicates the end of a reference. In order to solve this, we considered all forms of cntr with white spaces, using \s\*.

This approach did not work in the following case:

> from or deel, ref rw6j3kybdwn7acc// john mitchell 77152073245//cntr

In this case, the reference was split in between the first and second part with the person's name, which we cannot remove. It seems like the system may be in some way concatenating the first and second part of the reference and in this specific case, the name was mistakenly added between these components. For this reason, in order to also remove misformed references, we include two extra regex rule that try to match the two halves of the reference and remove them independently. These two rules are the following:

```
ref .{10,25}\/
```

```
\d{9,15}\/\/c\s*n\s*t\s*r
```

Note that in this final regex, we cannot match everything before "cntr" to be part of the reference, we can only match digits, using \d. This is because otherwise the regex would match text that is not part of the reference, such as the name of the person.

The final regex is the following:

```
ref .{10,25}\/\/.{10,20}\/\/c\s*n\s*t\s*r|ref .{10,25}\/|\d{9,15}\/\/c\s*n\s*t\s*r
```

I then removed all tokens that I am sure are not the name of the person, along with numbers and digits that are definitely not person's names, with the following regex:

```
for deel|to deel|deel|from|payment|transfer|received|\d{1,10}
```

Ideally, we should first try to associate the transaction data with the Users of the platform, in the users.csv file.
The input username should be validated, by matching it against the users.csv file. If the user exists, then we return all transactions associated with this user.
The mapping between a specific user and its transactions should be done apriori, not when the request is made to the API, in order to reduce the computation time. This means we should run our algorithm once, creating a dictionary mapping between users and transactions. If new transactions are added every day, we can set up a periodic task to continuing building upon the dictionary mapping, by running these new transactions through the built algorithm. This is assuming this system/API is used often.
The algorithm could be ran as a periodic task on all registered transactions in two ways:

- Immediately when a transaction is added to the system, it is mapped to a user by the algorithm
- A periodic task can be setup to run at night or in periods of lower system activity, takes the batch of transactions added that day, and maps them to users.
  Since deel has clients all over the world, we would have to study on the best times to run this periodic task, in order to not affect the system performance, were we to opt for the later solution.