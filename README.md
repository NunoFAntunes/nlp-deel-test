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


The cleaning of descriptions and usernames should run as a recurring task or every time a new transaction is added. 
It should not run when an API call is made, in order to avoid unnecessary processing and to improve the performance of the API. This is assuming this API is used often.


## Algorithm:

1. User name cleaning
    1. Handle other alphabets, accents, etc
    2. Convert to lowercase
2. Transaction description cleaning
    1. Handle other alphabets, accents, etc
    2. Convert to lowercase
    3. Remove all elements that are not part of the name (e.g. reference, from, to, numbers, etc)
    4. Remove unnecessary spaces 
3. Compare users name with description, using fuzzy matching (approximate string matching)

### User name cleaning
I have used the unidecode library to convert all characters to their closest ASCII representation. This is useful to handle names with accents, other alphabets, etc. For example, the name Μarιa Perikleous is converted to Maria Perikleous.

I then convert the name to lowercase, to make it easier to compare with the transaction description.


### Transaction cleaning

Similarly to the usernames, I begin by converting all characters to their closest ASCII representation and then convert the text to lowercase.

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

### Fuzzy matching
We use a fuzzy matching algorithm, that tries to find the similarity between the name given and the found untagged elements in the transaction description. This algorithm returns a confidence score that, if higher than 60%, we include in the API results.
The fuzzy algorithm uses the Levenshtein distance to calculate word similarities. We have used a function that is agnostic to the word order, capitals and number of words (meaning "Charles Smith", "Smith Charles" and "smith 123 charles 456" should all have 100% similarity).


## Limitations:

- The cleaning of descriptions is very aggressive, which for this use case, with the given users is not a problem but may be in a production system. For example, we filter out "deel", "from", "payment", "received", "transfer". In case any user has a name that includes any of these words (let's say Peter Deelson, Michel Afrom), they will be filtered out. There are ways to mitigate this problem, by matching only when these words are surrounded by spaces.
- The fuzzy matching algorithm is not perfect. It may return false positives, especially when the name is very common. For example, if the user name is "John Smith", the algorithm may return a high similarity score for "John Smith" and "John Smithson". 
- Blindly trusting the algorithm for description and user matching would not be a good idea, it should always be validated by a human.
- If the description format changes too much, the algorithm may fail.
- If the description is in another language, the algorithm is not prepared to filter these tokens and will fail. 