# SI 385: Data Exploration

## Application exercise 15, pre-read: tastes in music

*Dr. Chris Teplovs, School of Information, University of Michigan*

*For session 17, Monday November 2, 2026.*

---

This pre-read gives Monday's data and question, then reviews two things the session will rely on:
train-test splits and cross-validation, which we did not reach on Wednesday, and standardizing.

## Data

The data are 240 people's ratings of eleven genres of music, each from 1 (dislike) to 10 (like):
blues, classical, country, electronic, folk, hip hop, jazz, Latin, pop, R&B/soul and rock. The
ratings were generated for this session from a survey of an earlier class, so no row describes a
real person, but the genres and the patterns between them come from that survey.

## Question

> **How do these people's tastes in music differ?**

There are no answer options. In class, we will introduce principal component analysis (PCA), and
you will use it to answer the question with your team.

## Working and submitting

Your team may work on the question together in class, and each of you will describe a different
part of the answer. Each of you should then write your own answer in Step 4 of the notebook and
upload your copy of `L17_pca.py` to *AE 15* on Canvas before the end of class. The answer is worth
6 points: 4 for describing your part and checking it against the data, and 2 for your team's
decision about how much of the answer it takes.

## Train-test splits and cross-validation

A model always fits the data it was fitted on better than it fits new data, so a score computed on
the fitting data overstates how well the model will do on data it has not seen. A *train-test
split* sets some of the rows aside as a *test set* before fitting, fits the model on the rest (the
*training set*), and scores its predictions on the test set.

A single split has a weakness: the score depends on which rows happened to land in the test set,
and with a few hundred rows a different random split can give a noticeably different score.
*k-fold cross-validation* uses the data more fully. It divides the rows into *k* parts, or folds,
fits the model on *k* − 1 of them and scores it on the one left out, and repeats until every fold
has been left out once. The mean of the *k* scores gives the typical score, and their spread shows
how much to trust it.

The rows left out must also be kept out of any preprocessing, such as imputing or scaling, because a
scaler fitted on all the rows has already used the test fold. Putting the preprocessing and the
model in one pipeline and passing the pipeline to `cross_validate` arranges that, since every step
is refitted on the training folds each time.

To see both at work, please open the session 16 notebook, `L16_pipelines.py`, and run its sections
*Train-test splits* and *Cross-validation*. The slider in the first shows how far twenty random test
sets can disagree when there are only a few hundred rows.

## Standardizing

To standardize a column is to subtract its mean and divide by its standard deviation, so that every
value becomes a *z-score*: the number of standard deviations it lies above or below the column's
mean. A standardized column has a mean of 0 and a standard deviation of 1, whatever units it
started in. scikit-learn's `StandardScaler` standardizes every column at once. Like the other
transformers in the session 16 notebook, its `fit` computes and stores each column's mean and
standard deviation, and its `transform` applies them.

On Monday we will standardize the ratings before fitting PCA, even though every genre is already
rated on the same 1-to-10 scale. Consider, before class, what, if anything, standardizing would
change about columns that share a scale.

## Reading

Monday's reading, on which RAT 13 is based, is Géron's chapter on dimensionality reduction: ch. 8
in the third edition, or ch. 7 in the *Scikit-Learn and PyTorch* edition.

## Optional preparation

If you have time before Monday, please consider which genres you would expect the same people to
like.

*Data: ratings generated for SI 385 from the pattern of an earlier class's survey of musical
tastes.*
