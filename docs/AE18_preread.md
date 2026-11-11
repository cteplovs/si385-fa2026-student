# SI 385: Data Exploration

## Application exercise 18, pre-read: segments of listeners

*Dr. Chris Teplovs, School of Information, University of Michigan*

*For session 20, Wednesday November 11, 2026.*

---

This pre-read gives Wednesday's data and question, then reviews why k-means cannot tell you how
many clusters to look for, and introduces the methods we will use in class to choose that number
or to do without one.

## Data

The data are the ratings from sessions 17 and 18: 240 people's ratings of eleven genres of music,
each from 1 (dislike) to 10 (like), in `data/music_tastes.csv`. The ratings were generated for this
course from a survey of an earlier class, so no row describes a real person. As we said at the end
of session 18, they were generated from three continuous tastes, with no groups of people built in.

## Question

> **A music streaming service wants to divide these listeners into segments and recommend
> different playlists to each segment. Should it, and if so, how many segments should it use?**

There are no answer options. In class, we will introduce two ways of choosing the number of
clusters for k-means and a clustering method that does not need one, and you will use them to
answer the question with your team.

## Working and submitting

Your team may work on the question together in class. Each of you should then write your own
answer in the session 20 notebook and upload your copy to *AE 18* on Canvas before the end of
class.

## Choosing the number of clusters

k-means, which we used on Monday, divides the rows into whatever number of clusters, *k*, you give
it, whether or not the data contain groups. Its measure of fit, the total within-cluster variation
(which scikit-learn calls *inertia*), generally falls as *k* rises, because more centres can sit
closer to the rows, so choosing the *k* with the lowest inertia would mean choosing the most
clusters. The reading describes two other measures: the *elbow*, which is the value of *k* after
which another cluster lowers the inertia much less than the one before it did, and the *silhouette
score*, which compares each row's distance to its own cluster with its distance to the next
closest one.

DBSCAN, the third method, does not take a number of clusters. Instead, it groups rows that lie in
dense regions and labels rows in sparse regions as anomalies, and its two settings define what
counts as dense. Whether a segmentation would be useful to the service is a separate question from
whether the listeners form groups, so please consider both when you read.

## Reading

Wednesday's reading, on which RAT 16 is based, is from Géron, *Hands-On Machine Learning with
Scikit-Learn and PyTorch* (2025), chapter 8, *Unsupervised Learning Techniques*: the subsection
*Finding the optimal number of clusters*, the sections *Limits of k-Means* and *DBSCAN*, and the
paragraph on agglomerative clustering under *Other Clustering Algorithms*.

## Optional preparation

If you have time before Wednesday, please consider what silhouette scores you would expect for
clusters cut from data with no groups, and what the service would gain or lose by recommending
playlists to segments that are not distinct groups.
