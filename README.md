
# How to run

## Outside docker:
1. Create a python 3.11 virtual environment with
```  
python3.11 -m venv <virtual-environment-name>
```
2. Activate the venv with
```
source <virtual-environment-name>/bin/activate
```
 on Linux or
```
<virtual-environment-name>\Scripts\activate.bat
```
on Windows.

3. Install the requirements with
```
pip install -r requirements.txt
```
4. Run the cleaning scripts (optional, the cleaned files are already in the data folder)
```
cd src
python clean_users.py
python clean_transactions.py
```
5. Run the API with
```
cd src
uvicorn api:app --port 8123
```
The api swagger frontend will be available at http://localhost:8123/docs for testing.
## Docker:
In the project root directory, run the following commands:

```
docker build -t deel-test .
docker run -dp 8123:8000 deel-test
```
The api swagger frontend will be available at http://localhost:8123/docs for testing.



# Code Structure

- data: contains all the data files
- notebooks: contains the notebooks used for data exploration, analysis and tests. Should not be included in a production environment
- requirements: contains the python libraries required to run the code
- src: contains the source code for the API and algorithms.
  - api_models: contains the pydantic models used for the API
  - api: contains the API code
  - api_functions: contains the functions used by the API
  - clean_transactions: contains the functions used to clean the transactions data and saving it in a new file. This routine should be changed in production to a database routine.
  - clean_users: contains the functions used to clean the users data and saving it in a new file. This routine should be changed in production to a database routine.

# Data Exploration and Understanding:

## Users

On a quick data analysis, I have found the following special cases in Users data:

- There is one user without a name
- Some users have middle name, others the first letter of the middle name, others no middle name;
- The user Audrey (crHOEW9iLZ) only has one name;
- Some users have their names altogether, for example AuroraPowell (i52RbjL6om);
- The user with the name Isaac Bell Deel and Daniel Deel, we must be sure if Deel is his actual surname or if it was an input error on the Deel system, including company name. (6fc89iJwho and FhRDVhmleA). This may also be a problem for our text matching algorithm. Same with Andrew Rodeel. (Hl7n5MGoJo);
- There may be some misspelled names. Is Penelop a mispelling of Penelope? (7wgTardvTI). Same with Andrw Richardson (qBCElYF454);
- One user has special characters in its name, Μarιa Perikleous (Qg12EWasd);
- There are two users with the same name and different IDs, Isabella Wilson (ToAD2rzvGA and VfY9DmIkiL);

## Transactions

On a quick data analysis, I have found the following special cases in Transactions data:

- Names are written in different cases (upper, lower, mixed);
- Middle name is included in the name in some cases (sometimes in users files, other times in transactions files), and these possibly represent the same person;
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
- Descriptions with no name in transactions
- After "ref", we may have names instead of transaction reference.

# Task 1:

- Input: User name
- Output: List of transactions associated with the user.

## Approaches considered:

There are two ways to approach a problem of matching users with their payments:
1. Identifying named entities (NER) in the description and try to match them with the user name.
2. Try to match a given user name it with all transaction descriptions with every element we are sure is not the person's name removed, in order to find any matches.

Considering:
- The description of the transaction is very short, has a lot of mistakes and sometimes a nonsensical structure. 
- The names are sometimes jumbled in the text (e.g. the first name and the last name have words or text in between).
- The names are sometimes misspelled and there are many foreign names, which means it will be difficult to compare against name databases, in order to correct mistakes.

I believe NER might not give the best results for this problem. The 2nd option seems like it would yield better results, since we already know what we are looking for in the transaction descriptions.

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

This cleaning process is to be applied to any user name that is inputted into the API.


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
I have use a fuzzy matching algorithm, that tries to find the similarity between the name given and the found untagged elements in the transaction description. This algorithm returns a confidence score that, if higher than 60%, we include in the API results.
The fuzzy algorithm uses the Levenshtein distance to calculate word similarities. I have used a function that is agnostic to the word order, capitals and number of words (meaning "Charles Smith", "Smith Charles" and "smith 123 charles 456" should all have 100% similarity).


## Limitations:

- The cleaning of descriptions is very aggressive, which for this use case, with the given users is not a problem but may be in a production system. For example, we filter out "deel", "from", "payment", "received", "transfer". In case any user has a name that includes any of these words (let's say Peter Deelson, Michel Afrom), they will be filtered out. There are ways to mitigate this problem, by matching only when these words are surrounded by spaces or new lines.
- The confidence doesn't directly mean the system is completely sure the searched person is the person involved in the transaction. For example, if there's two users, one whose name is "Peter Richardson", and another one whose name is "Richardson", a search for "Richardson" will still return a 100% confidence on any transaction where "Peter Richardson" is mentioned, despite not being the same user.
- The fuzzy matching algorithm is not perfect. It may return false positives, especially when the name is very common. For example, if the user name is "John Smith", the algorithm may return a high similarity score for "John Smith" and "John Smithson". 
- Blindly trusting the algorithm for description and user matching would not be a good idea, it should always be validated by a human.
- If the description format changes too much, the algorithm may fail.
- If the description is in another language, the algorithm is not prepared to filter these tokens and may fail. 
- Although I have taken some measures to make sure the code was optimized, I have not ran any efficiency tests. The libraries unidecode and fuzzywuzzy have not been tested for efficiency. Additionally, some regex may be able to be swapped for string operations that should run slightly faster.


# Task 2:


## Algorithm
For this task, we must perform the following steps:
1. Clean the description field. I have proceeded with a very simple cleaning process, removing some punctuation characters (excluded forward slashes due to them being used in the reference) and converting all characters to lowercase.
2. Transforming the transaction descriptions into embeddings (dense vector representations).
3. Saving the embeddings associated with transaction ids, in a database (in this case, a dataframe).

For inference, the following is performed:
1. Cleaning the user input in the same way, removing punctuation and converting to lowercase.
2. Transforming the user input into an embedding.
3. Comparing the user input embedding to all transaction embeddings in the database, with a vector similiarity metric (I have used the cosine similarity).
4. Filtering the results for similarities over a defined threshold, ordering the results according to the similarity score and returning the results.

## Limitations:

- Considering the description has a lot of structural mistakes, the embeddings may not be very accurate. For example, if the description is "from or deel ref rw6j3kybdwn7acc// john mitchell 77152073245//cntr", the embedding will be very different from the embedding of "from john mitchell". This may be solved by using a more complex cleaning process, which would be more robust to these mistakes. 
- I did not sanitize the query input against forward slashes, meaning searches with forward slashes will not work for now.


# Task 3:

## Exercise 1
- Protect this API with authentication, bearer tokens, etc.
- The data is currently inside the dockerfile, which is not the correct procedure. I should have used docker volumes.
- Try to enforce a standard for the description format, in order to make the cleaning easier. For example, we could enforce that the reference is always at the end of the description.
- The cleaning of descriptions should run as a recurring task or every time a new transaction is added, in order for the module of Task 1 to work. It should not run when an API call is made, in order to avoid unnecessary processing and to improve the performance of the API. The code is prepared for this but the task is not implemented.
- The task description states that this endpoint will be used to match users with their payments. This means that in order to take this concept to production, we would probably have to create an adapter to connect to the database of clients and transactions and a job that would fetch all existing users and transactions from the database, and utilize the API to do the matching.
- We could create jobs for batch processing of data in the API, making sure the API calls are non-blocking and can run in parallel.
- We should discuss if the best approach for this problem is to use as input the username and try to match transactions to it, or to instead use as input of the API, the transaction ID, trying to match potential users that have made this transaction to it. Assuming many more transactions are added to the database than users are, this approach may be better.
- We should make it so the script only runs on data that has not yet been matched, we shouldn't run this script on the entire transaction database, as it would be extremely inefficient and even introduce bugs (for example if a new user is added with the name John Smith and we re-run the script against the entire transaction database, we could get matches of past transactions to this new user, that did not exist in the past).
- The results should never overwrite any existing fields on the database, but be added as an extra field in the transaction table. 

## Exercise 2

- Apply a more complex cleaning process on the descriptions, structuring them in a more organized way, before calculating the embeddings. This can be used by repurposing the regex developed for detecting reference numbers and developing other algorithms for detection of other tokens included in the description.
- Develop the database connector.
- Develop a job that calculates embeddings for every description and stores them in the database (if this system is used very often).
- Implement a system where the user can select which of the search results matched the query that was inputted. If we have a dataset with this matching, we may be able to later improve the system with a supervised learning approach.
