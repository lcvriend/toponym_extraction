---
title: Case Study
---

<script type="text/javascript" src="https://cdn.jsdelivr.net/npm//vega@5"></script>
<script type="text/javascript" src="https://cdn.jsdelivr.net/npm//vega-lite@4.0.2"></script>
<script type="text/javascript" src="https://cdn.jsdelivr.net/npm//vega-embed@6"></script>

# LexisNexis Place Extraction Case Study:
**Places discussed in context of the Brexit in Dutch newspapers in 2017**

This case study shows an example of the kind of analysis that can be done when using *named entity recognition* to annotate text with geographical entitities. The code and scripts that were used in this analysis can be found [here](https://github.com/lcvriend/lexisnexis_place_extraction).

## Articles

All articles in 2017 containing at least one mention of the phrase 'Brexit' were selected from four Dutch newspapers:

* Two 'quality' papers:
    * [De Volkskrant](https://www.volkskrant.nl/)
    * [Trouw](https://www.trouw.nl/)
* One 'popular' paper:
    * [De Telegraaf](https://www.telegraaf.nl/)
* One regional paper:
    * [De Leeuwarder Courant](https://www.lc.nl/)

In total 1830 articles were found meeting these criteria. The articles that were used in this case study can be found [here](https://github.com/lcvriend/lexisnexis_place_extraction/blob/master/data/lexisnexis_dataset.csv). The content itself is copyrighted, so unfortunately the dataset contains only metadata and not the actual articles themselves. All The meta data of Brexit has been in the news throughout in these four news papers:

#### Number of articles containing the term 'Brexit' per month in 2017
<div id="vis_pub_month"></div>
<script>
    (function(vegaEmbed) {
    var spec = {"config": {"view": {"continuousWidth": 400, "continuousHeight": 300}}, "data": {"name": "data-95f0ac09e71d1ebb2ce6a523858975b1"}, "mark": "bar", "encoding": {"color": {"type": "nominal", "field": "source"}, "x": {"type": "ordinal", "field": "publication_date", "sort": ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"], "title": "publication date"}, "y": {"type": "quantitative", "aggregate": "sum", "field": "number_of_articles", "title": "number of articles"}}, "$schema": "https://vega.github.io/schema/vega-lite/v4.0.2.json", "datasets": {"data-95f0ac09e71d1ebb2ce6a523858975b1": [{"publication_date": "January", "source": "Leeuwarder Courant", "number_of_articles": 26}, {"publication_date": "January", "source": "Telegraaf", "number_of_articles": 53}, {"publication_date": "January", "source": "Trouw", "number_of_articles": 51}, {"publication_date": "January", "source": "Volkskrant", "number_of_articles": 65}, {"publication_date": "February", "source": "Leeuwarder Courant", "number_of_articles": 23}, {"publication_date": "February", "source": "Telegraaf", "number_of_articles": 52}, {"publication_date": "February", "source": "Trouw", "number_of_articles": 48}, {"publication_date": "February", "source": "Volkskrant", "number_of_articles": 44}, {"publication_date": "March", "source": "Leeuwarder Courant", "number_of_articles": 42}, {"publication_date": "March", "source": "Telegraaf", "number_of_articles": 58}, {"publication_date": "March", "source": "Trouw", "number_of_articles": 67}, {"publication_date": "March", "source": "Volkskrant", "number_of_articles": 72}, {"publication_date": "April", "source": "Leeuwarder Courant", "number_of_articles": 28}, {"publication_date": "April", "source": "Telegraaf", "number_of_articles": 35}, {"publication_date": "April", "source": "Trouw", "number_of_articles": 39}, {"publication_date": "April", "source": "Volkskrant", "number_of_articles": 40}, {"publication_date": "May", "source": "Leeuwarder Courant", "number_of_articles": 23}, {"publication_date": "May", "source": "Telegraaf", "number_of_articles": 29}, {"publication_date": "May", "source": "Trouw", "number_of_articles": 46}, {"publication_date": "May", "source": "Volkskrant", "number_of_articles": 43}, {"publication_date": "June", "source": "Leeuwarder Courant", "number_of_articles": 31}, {"publication_date": "June", "source": "Telegraaf", "number_of_articles": 55}, {"publication_date": "June", "source": "Trouw", "number_of_articles": 51}, {"publication_date": "June", "source": "Volkskrant", "number_of_articles": 75}, {"publication_date": "July", "source": "Leeuwarder Courant", "number_of_articles": 17}, {"publication_date": "July", "source": "Telegraaf", "number_of_articles": 28}, {"publication_date": "July", "source": "Trouw", "number_of_articles": 33}, {"publication_date": "July", "source": "Volkskrant", "number_of_articles": 44}, {"publication_date": "August", "source": "Leeuwarder Courant", "number_of_articles": 10}, {"publication_date": "August", "source": "Telegraaf", "number_of_articles": 25}, {"publication_date": "August", "source": "Trouw", "number_of_articles": 20}, {"publication_date": "August", "source": "Volkskrant", "number_of_articles": 33}, {"publication_date": "September", "source": "Leeuwarder Courant", "number_of_articles": 14}, {"publication_date": "September", "source": "Telegraaf", "number_of_articles": 46}, {"publication_date": "September", "source": "Trouw", "number_of_articles": 34}, {"publication_date": "September", "source": "Volkskrant", "number_of_articles": 38}, {"publication_date": "October", "source": "Leeuwarder Courant", "number_of_articles": 13}, {"publication_date": "October", "source": "Telegraaf", "number_of_articles": 25}, {"publication_date": "October", "source": "Trouw", "number_of_articles": 23}, {"publication_date": "October", "source": "Volkskrant", "number_of_articles": 38}, {"publication_date": "November", "source": "Leeuwarder Courant", "number_of_articles": 28}, {"publication_date": "November", "source": "Telegraaf", "number_of_articles": 47}, {"publication_date": "November", "source": "Trouw", "number_of_articles": 34}, {"publication_date": "November", "source": "Volkskrant", "number_of_articles": 45}, {"publication_date": "December", "source": "Leeuwarder Courant", "number_of_articles": 21}, {"publication_date": "December", "source": "Telegraaf", "number_of_articles": 35}, {"publication_date": "December", "source": "Trouw", "number_of_articles": 39}, {"publication_date": "December", "source": "Volkskrant", "number_of_articles": 44}]}};
    var embedOpt = {"mode": "vega-lite"};
    vegaEmbed("#vis_pub_month", spec, embedOpt);
})(vegaEmbed);
</script>

## Geodata

The toponyms were taken from [GeoNames](http://www.geonames.org/) and [REST Countries](http://restcountries.eu/) datasets. The map below shows all data points that were selected from the GeoNames dataset for the *named entity recognition*.  

#### Place distribution in the GeoNames dataset
<img src="illustrations/distribution_places_world.png"/>

## Toponyms

Using [spaCy's named entitiy recognition](https://spacy.io/usage/linguistic-features#named-entities) all entities in the newspaper articles were collected and counted. The entities were divided into the following categories:

* Countries
* Places in the world
* Places in the UK
* Places in the Netherlands
* Places in Friesland

The interactive graphs below shows several measures for the found results. Use the legend to zoom in on a specific newspaper.

####
<div id="vis_toponyms"></div>
<script>
(function(vegaEmbed) {
    var spec = {"config": {"view": {"continuousWidth": 400, "continuousHeight": 300}}, "hconcat": [{"mark": "bar", "encoding": {"color": {"type": "nominal", "field": "source"}, "opacity": {"condition": {"value": 1, "selection": "selector075"}, "value": 0.2}, "x": {"type": "nominal", "field": "source"}, "y": {"type": "quantitative", "field": "unique", "title": "number of unique toponyms"}}, "height": 328, "selection": {"selector075": {"type": "multi", "fields": ["source"], "bind": "legend"}}}, {"mark": "bar", "encoding": {"color": {"type": "nominal", "field": "source"}, "opacity": {"condition": {"value": 1, "selection": "selector075"}, "value": 0.2}, "x": {"type": "nominal", "field": "source"}, "y": {"type": "quantitative", "aggregate": "sum", "field": "frequency", "title": "total frequency of toponyms"}}, "height": 328, "selection": {"selector075": {"type": "multi", "fields": ["source"], "bind": "legend"}}}, {"vconcat": [{"mark": "bar", "encoding": {"color": {"type": "nominal", "field": "source"}, "x": {"type": "quantitative", "aggregate": "sum", "field": "articles", "title": "number of articles"}, "y": {"type": "nominal", "field": "category", "sort": ["countries", "places", "places_uk", "places_nl", "places_fr"]}}, "selection": {"selector075": {"type": "multi", "fields": ["source"], "bind": "legend"}}, "transform": [{"filter": {"selection": "selector075"}}]}, {"mark": "bar", "encoding": {"color": {"type": "nominal", "field": "source"}, "x": {"type": "quantitative", "aggregate": "sum", "field": "unique", "title": "number of unique toponyms"}, "y": {"type": "nominal", "field": "category", "sort": ["countries", "places", "places_uk", "places_nl", "places_fr"]}}, "selection": {"selector075": {"type": "multi", "fields": ["source"], "bind": "legend"}}, "transform": [{"filter": {"selection": "selector075"}}]}, {"mark": "bar", "encoding": {"color": {"type": "nominal", "field": "source"}, "x": {"type": "quantitative", "aggregate": "sum", "field": "frequency", "title": "total frequency of toponyms"}, "y": {"type": "nominal", "field": "category", "sort": ["countries", "places", "places_uk", "places_nl", "places_fr"]}}, "selection": {"selector075": {"type": "multi", "fields": ["source"], "bind": "legend"}}, "transform": [{"filter": {"selection": "selector075"}}]}]}], "data": {"name": "data-408f63f986752ab52a835209d4593cdd"}, "$schema": "https://vega.github.io/schema/vega-lite/v4.0.2.json", "datasets": {"data-408f63f986752ab52a835209d4593cdd": [{"source": "Leeuwarder Courant", "category": "countries", "frequency": 1254, "unique": 81, "articles": 226}, {"source": "Leeuwarder Courant", "category": "places", "frequency": 338, "unique": 65, "articles": 131}, {"source": "Leeuwarder Courant", "category": "places_fr", "frequency": 45, "unique": 10, "articles": 18}, {"source": "Leeuwarder Courant", "category": "places_nl", "frequency": 203, "unique": 32, "articles": 71}, {"source": "Leeuwarder Courant", "category": "places_uk", "frequency": 165, "unique": 16, "articles": 84}, {"source": "Telegraaf", "category": "countries", "frequency": 1764, "unique": 79, "articles": 365}, {"source": "Telegraaf", "category": "places", "frequency": 553, "unique": 65, "articles": 204}, {"source": "Telegraaf", "category": "places_fr", "frequency": 0, "unique": 0, "articles": 0}, {"source": "Telegraaf", "category": "places_nl", "frequency": 420, "unique": 37, "articles": 183}, {"source": "Telegraaf", "category": "places_uk", "frequency": 319, "unique": 32, "articles": 151}, {"source": "Trouw", "category": "countries", "frequency": 3574, "unique": 117, "articles": 434}, {"source": "Trouw", "category": "places", "frequency": 1025, "unique": 116, "articles": 274}, {"source": "Trouw", "category": "places_fr", "frequency": 2, "unique": 1, "articles": 1}, {"source": "Trouw", "category": "places_nl", "frequency": 310, "unique": 39, "articles": 113}, {"source": "Trouw", "category": "places_uk", "frequency": 461, "unique": 47, "articles": 168}, {"source": "Volkskrant", "category": "countries", "frequency": 3631, "unique": 125, "articles": 491}, {"source": "Volkskrant", "category": "places", "frequency": 1180, "unique": 153, "articles": 330}, {"source": "Volkskrant", "category": "places_fr", "frequency": 2, "unique": 2, "articles": 2}, {"source": "Volkskrant", "category": "places_nl", "frequency": 528, "unique": 56, "articles": 145}, {"source": "Volkskrant", "category": "places_uk", "frequency": 728, "unique": 71, "articles": 230}]}};
    var embedOpt = {"mode": "vega-lite"};
    vegaEmbed("#vis_toponyms", spec, embedOpt);
})(vegaEmbed);
</script>

Of course it is particularly interesting to see *what* places are mentioned in the articles and how they are distributed on a map. Explore the results in [this interactive map](map_toponyms.html). The circles represent the number of times the toponym was found in the dataset. With the layer control you can switch on/off layers. Click on a circle to open a tooltip with more information on the toponym and the frequency with which it occurs in the text and articles.


## Lemma clouds
The articles were also lemmatized using spaCy. Below these lemma's have been turned into clouds: 

### Volkskrant
<img src="illustrations/wc_volkskrant.png"/>

### Trouw
<img src="illustrations/wc_trouw.png"/>

### Telegraaf
<img src="illustrations/wc_telegraaf.png"/>

### Leeuwarder Courant
<img src="illustrations/wc_leeuwarder_courant.png"/>
