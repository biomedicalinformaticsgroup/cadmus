# Cadmus
This projects is to build full text retrieval system setup for generation of large biomedical corpora from published literature.

## Requirements

In order to run the code, you will need a few things:

You need to have Java 7+.

An API key from NCBI (you can find more information [here](https://ncbiinsights.ncbi.nlm.nih.gov/2017/11/02/new-api-keys-for-the-e-utilities/)).

An API key from Crossref (you can find more information [here](https://apps.crossref.org/clickthrough/researchers/#/) you will need to agree the folowing two licenses:

1. Wiley Text and Data Mining License v1.1
2. Elsevier Text and Data Mining Service Agreement)

## Installation
Cadmus has a number of dependencies on other Python packages, it is recommended to install in an isolated environment

`!pip install git+https://github.com/biomedicalinformaticsgroup/cadmus.git`

## Get started

The format we are using for the search terms are the same as the one for [PubMed](https://pubmed.ncbi.nlm.nih.gov/). You can first try your search terms on PubMed and use it as input for bioscraping.

In order to create your corpora you are going to use the function called 'bioscraping'. The function is taking the following required parameters:

1. A PubMed query or a list of PubMed IDs
2. An email adress
3. Your NCBI_API_KEY
4. Your Crossref_API_KEY
   
The function can also receive optional parameters.

When running, on top of the live output, you can see when your result was last save in case of failure.


1. The start parameter tells the function at which service we were at before failure
2. The idx parameter tells the function what is the last saved processed row


Finally, in case you want to check if a document became available since the last time you tried. The function takes a last optional parameter called full_search. full_search has three predifined values:

1. The default Value None, the function only looks for the new articles since the last run
2. 'light', the function looks for the new articles since the last run and re-tried the row where we did not get any format.
3. 'heavy', the function looks for the new articles since the last run and re-tried the row where it did not retrieved a tagged version (i.e. html or xml).

    ```bioscraping(
    INPUT,
    EMAIL,
    NCBI_APY_KEY,
    CROSSREF_API_KEY
    )
    ```

## Important
 Published literature is subject to copyright andrestrictions on redistribution.  Users need to be mindful of the data storage requirements and how the derivedproducts are presented and shared.

## Extra ressources
You can find the Cadmus website - https://biomedicalinformaticsgroup.github.io/cadmus/

You can find a [Colab Notebook](https://colab.research.google.com/drive/15h9MjpD6oc90ehaQfm64k-bdHthBuHPW?usp=sharing) to get you started.

## FAQ

Q:Tika failed three times in a row, I can not parsed PDF format. What can I do ?

A:You can go to the folowing [website](https://repo1.maven.org/maven2/org/apache/tika/tika-server/1.24/), download 'tika-server-1.24.jar' and start it yourself.

Q:On PubMed, my search query has more than 90 000 results. The system only retrieved 90 000 publication. Why ?

A:When requesting the metadata, we set the limit to 90 000. If you update your result you will get new rows. If you believe that retriving more than 90 000 publications is important please let us know [here](https://github.com/biomedicalinformaticsgroup/cadmus/issues).

Q:I ran two times the same query, the number of potential publications changed. Why?

A:If the number of potential publication changed by a lot please let us know [here](https://github.com/biomedicalinformaticsgroup/cadmus/issues), tell us about the query, the previous number and the new number.
If you noticed a small difference, most likely the APIs the system is using were busy and your request did not receive an aswer this time. Give it some time and try to run again the same query using the extra parameter full_search = 'light' to update your result by looking again at the rows where the system did not find a content.

Q:I ran the same query that someone else and I got different result. Why?

A:The system is taking advantage of subscriptions. Maybe you do not have the same subsriptions, you did not run the system on the correct IP address to get access to the subscription.

Q:Can I redistribute the data?

A:Published literature is subject to copyright and restrictions on redistribution. Users need to be mindful of the data storage requirements and how the derived products are presented and shared.

Q:What's the difference between retrieved_df and retrieved_df2?

A:retrieved_df is a 'moving state' dataframe. Each time the system will run, it will store the information into retrieved_df to reduce to the row of interest.
retrieved_df2 is here to keep the information forever, once the system finished, retrieved_df2 will collect the new line from retrieved_df to group them with previous run.