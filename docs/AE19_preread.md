# SI 385: Data Exploration

## Application exercise 19, pre-read: four questions about Michiganders

*Dr. Chris Teplovs, School of Information, University of Michigan*

*For session 21, Monday November 16, 2026.*

---

This pre-read gives the data and question for session 21 and introduces the three kinds of
classifier we will compare in class: logistic regression, decision trees and random forests.

## Data

The data are the answers of 102,581 Michigan residents to the 2023 American Community Survey, the
Census Bureau's yearly survey, in `data/acs_michigan_2023.parquet`. The Bureau publishes the
answers of about one person in a hundred. Each row is one person, and the columns describe their
age, schooling, work, household, disabilities and citizenship, with the Census codes replaced by
labels you can read.

Each outcome in the file is defined only for the people it applies to and is missing for everyone
else:

| Outcome | Population | True if the person |
|---|---|---|
| `earns_over_50k` | People over 16 who work and have some income | earned more than $50,000 |
| `employed` | People aged 16 to 90 | was a civilian at work |
| `public_coverage` | People under 65 with an income of $30,000 or less | had public health coverage |
| `moved_last_year` | People aged 18 to 35 | lived in a different house a year earlier |

The outcomes and the groups they cover follow the definitions of Ding, Hardt, Miller and Schmidt
(2021), who proposed them as replacements for an older census dataset that has been used to
compare classifiers since the 1990s.

## Question

> **Michigan's state government wants to predict all four outcomes for people it has not
> surveyed. Should it use the same kind of model for every outcome, and if so, which?**

There are no answer options. In class, each member of your team will take a different outcome and
fit all three kinds of classifier to it, and your team will compare what you found. If your team
has three members, please choose together which outcome to leave out.

## Working and submitting

Your team may work on the question together in class. Each of you should then write your own
answer in the session 21 notebook and upload your copy to *AE 19* on Canvas before the end of
class. Your answer should use the numbers from your own outcome and say what your teammates'
outcomes added to it.

## Three kinds of classifier

A classifier predicts which of two or more classes a row belongs to. *Logistic regression* fits a
weighted sum of the columns and converts it into a probability, so each column has one
coefficient, which measures how much that column raises or lowers the odds of the outcome,
whatever the other columns are. A *decision tree* splits the rows on one column at a time, for example on
age at 62, and then splits each group again, so it can find thresholds and combinations that a
weighted sum cannot express. A tree grown until every group is pure fits the training rows
exactly and usually predicts new ones badly, which is why trees are limited in depth or pruned. A
*random forest* grows hundreds of trees, each on a different sample of the rows and columns, and
predicts the class that most of them predict, which is usually more accurate than one tree but
gives up the single set of splits that you could read.

Whether one of these predicts best is a different question from whether its advantage is large
enough to matter to the people using it, so please consider both when you read.

## Reading

Session 21's reading, on which RAT 17 is based, is four sections of James, Witten, Hastie,
Tibshirani and Taylor, *An Introduction to Statistical Learning with Applications in Python*
(2023), which is free to download from statlearning.com: section 4.3, *Logistic Regression*;
section 8.1, *The Basics of Decision Trees*; section 8.2.1, *Bagging*; and section 8.2.2,
*Random Forests*.

## Optional preparation

If you have time before session 21, please think about which of the four outcomes you would expect
to depend on age in a way that a single coefficient could not describe, and what a state agency
would lose by using a model whose predictions it could not explain to the people they concern.

*Data: US Census Bureau, American Community Survey 2023 1-year Public Use Microdata Sample,
Michigan person file, public domain. Outcome definitions from Ding, F., Hardt, M., Miller, J. and
Schmidt, L. (2021). Retiring Adult: New datasets for fair machine learning. Advances in Neural
Information Processing Systems 34.*
