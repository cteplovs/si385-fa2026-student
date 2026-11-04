# SI 385: Data Exploration

## Application exercise 14, pre-read: house values in California districts

*Dr. Chris Teplovs, School of Information, University of Michigan*

*For session 16, Wednesday October 28, 2026. Revised Tuesday October 27.*

---

## Data

The data are the ones Géron uses in chapter 2: the 1990 United States census for California,
summarised for each of 20,640 districts. Each row describes a district rather than a house, with
its location, the median age of its houses, its total rooms, bedrooms, population and households,
its median household income, how near it is to the ocean, and its median house value.

## Question

> **Build the pipeline, then use it to say what sets a district's house value, and how much of it
> you can explain.**

There are no answer options this time. In class, the session 16 notebook will take you through
scikit-learn's pipelines, train-test splits, cross-validation and the coefficients of a linear
regression, and then give you a scaffold for your own answer.

## Working and submitting

Your team may work on the question together in class, and each of you should start from different
columns from your teammates and then compare what you find. Each of you should then write your own
answer in Step 4 of the notebook and upload your copy of `L16_pipelines.py` to *AE 14* on Canvas by
23:59 on Thursday. The answer is worth 6 points: 4 for your explanation, and 2 for comparing your
results with your teammates'.

## Optional preparation

If you have time before Wednesday, the following will help.

- Please read Wednesday's reading, Géron ch. 2 or the two scikit-learn pages named in the RAT 12
  announcement. Géron's chapter works through these same data.
- Consider which of the columns you would expect to matter most for a district's house value, and
  why.

## Before class

Please run `uv run update.py` in your course folder before Wednesday, which brings in the session
16 notebook and the housing data.

*Data: Géron, A. (2022). Hands-On Machine Learning with Scikit-Learn, Keras and TensorFlow, 3rd
ed., ch. 2, from the 1990 United States census for California (Pace, R. K. and Barry, R. (1997).
Sparse spatial autoregressions. Statistics and Probability Letters 33, 291–297).*
