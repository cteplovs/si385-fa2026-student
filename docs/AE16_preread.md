# SI 385: Data Exploration

## Application exercise 16, pre-read: groups in musical taste

*Dr. Chris Teplovs, School of Information, University of Michigan*

*For session 18, Wednesday November 4, 2026.*

---

This pre-read gives Wednesday's data and question, then reviews how PCA and t-SNE differ in what
they keep when they reduce many columns to two.

## Data

The data are the same as Monday's: 240 people's ratings of eleven genres of music, each from 1
(dislike) to 10 (like), in `data/music_tastes.csv`. The ratings were generated for this course from
a survey of an earlier class, so no row describes a real person, but the genres and the patterns
between them come from that survey.

## Question

> **Do these people fall into distinct groups of musical taste?**

There are no answer options. In class, you will reduce the ratings to two dimensions with t-SNE,
compare the result with Monday's principal components, and use both to answer the question with
your team.

## Working and submitting

Your team may work on the question together in class. Each of you should then write your own
answer in the session 18 notebook and upload your copy to *AE 16* on Canvas before the end of
class.

## Two-dimensional maps

Each person in the data is a point in eleven dimensions, one per genre, and a plot has only two, so
any reduction of the ratings to two columns keeps some of the differences between people and loses
others. PCA, which we used on
Monday, projects the points onto the two directions along which they vary most, keeping the
distances along those two directions and dropping the variation in all the others. t-SNE instead
places each point's nearest neighbours near it in the plot, and does not preserve the distances
between points that are not neighbours. Its main setting, *perplexity*, sets roughly how many
neighbours of each point the method keeps close.

The two plots therefore have to be read differently when you look for groups. In a PCA plot, a gap
between two sets of points means that they are at least that far apart in the full eleven
dimensions, because a projection can only shorten distances. The reading describes how t-SNE treats
clusters, so please read that passage with Wednesday's question in mind.

## Reading

Wednesday's reading, on which RAT 14 is based, is the second half of Géron's chapter on
dimensionality reduction, from *LLE* to the end: ch. 7 in the *Scikit-Learn and PyTorch* edition. From this session
on, please use that edition, because some RAT items depend on passages that appear only in it.

## Optional preparation

If you have time before Wednesday, please consider what you would expect a two-dimensional map of
these people to look like if their tastes fell into distinct groups, and what you would expect if
they did not.

*Data: ratings generated for SI 385 from the pattern of an earlier class's survey of musical
tastes.*
