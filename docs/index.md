---
title: Case Study
---

<img src="illustrations/banner.png"/>

<script type="text/javascript" src="https://cdn.jsdelivr.net/npm//vega@5"></script>
<script type="text/javascript" src="https://cdn.jsdelivr.net/npm//vega-lite@4.0.2"></script>
<script type="text/javascript" src="https://cdn.jsdelivr.net/npm//vega-embed@6"></script>

# What places do Dutch newspapers cover when talking about Brexit?
**Toponym Extraction Case Study:**  
*Using named entity recognition to extract geographical information from newspapers*

This case study shows an example of the kind of analysis that can be done when using *named entity recognition* to annotate texts with geographical entitities. The code and scripts that were used in this analysis can be found in the [GitHub repo](https://github.com/lcvriend/toponym_extraction).

## Idea

> “The press, as we now know it, has grown and evolved rapidly over the last 200 years (particularly since 1850), generating an ever-growing flood of geographical information.” (Harvey, 2005, p.230)

Newspapers inform us about what is happening in the world. In this sense they are conveying to us geographical information. One tool we have at our disposal for reasoning about our world are [toponyms](https://en.wikipedia.org/wiki/Toponymy), i.e. place names. This raises the question how much newspapers refer to places through toponyms.

Let's try to find that out by analyzing Dutch newspaper coverage on Brexit.

## Articles

To start we select all articles in 2017 containing at least one mention of the phrase 'Brexit' in four Dutch newspapers:

* Two 'quality' newspapers:
    * [De Volkskrant](https://www.volkskrant.nl/)
    * [Trouw](https://www.trouw.nl/)
* One 'popular' newspaper:
    * [De Telegraaf](https://www.telegraaf.nl/)
* One regional newspaper:
    * [De Leeuwarder Courant](https://www.lc.nl/)

In total 1,830 articles were found meeting these criteria. The articles that were used in this case study can be found [here](https://github.com/lcvriend/lexisnexis_place_extraction/blob/master/data/lexisnexis_dataset.csv). The content itself is copyrighted, so unfortunately the dataset contains only metadata and not the actual articles themselves. Check out these [word clouds](lemma_clouds.md) though to see which lemma's are most prevalent in the respective newspapers. The Brexit has been in the news throughout in these four news papers:

#### Number of articles containing the term 'Brexit' per month in 2017
<div id="vis_pub_month"></div>
<script>
    (function(vegaEmbed) {
      var spec = {"config": {"view": {"continuousWidth": 400, "continuousHeight": 300}}, "data": {"name": "data-articles-per-month"}, "mark": "bar", "encoding": {"color": {"type": "nominal", "field": "source"}, "opacity": {"condition": {"value": 1, "selection": "selector-source-articles-per-month"}, "value": 0.2}, "tooltip": {"type": "quantitative", "aggregate": "sum", "field": "articles"}, "x": {"type": "nominal", "field": "month", "sort": ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]}, "y": {"type": "quantitative", "aggregate": "sum", "field": "articles", "title": "number of articles"}}, "selection": {"selector-source-articles-per-month": {"type": "multi", "fields": ["source"], "bind": "legend"}}, "$schema": "https://vega.github.io/schema/vega-lite/v4.0.2.json", "datasets": {"data-articles-per-month": [{"source": "Leeuwarder Courant", "month": "April", "articles": 28}, {"source": "Leeuwarder Courant", "month": "August", "articles": 10}, {"source": "Leeuwarder Courant", "month": "December", "articles": 21}, {"source": "Leeuwarder Courant", "month": "February", "articles": 23}, {"source": "Leeuwarder Courant", "month": "January", "articles": 26}, {"source": "Leeuwarder Courant", "month": "July", "articles": 17}, {"source": "Leeuwarder Courant", "month": "June", "articles": 31}, {"source": "Leeuwarder Courant", "month": "March", "articles": 42}, {"source": "Leeuwarder Courant", "month": "May", "articles": 23}, {"source": "Leeuwarder Courant", "month": "November", "articles": 28}, {"source": "Leeuwarder Courant", "month": "October", "articles": 13}, {"source": "Leeuwarder Courant", "month": "September", "articles": 14}, {"source": "Telegraaf", "month": "April", "articles": 35}, {"source": "Telegraaf", "month": "August", "articles": 25}, {"source": "Telegraaf", "month": "December", "articles": 35}, {"source": "Telegraaf", "month": "February", "articles": 52}, {"source": "Telegraaf", "month": "January", "articles": 53}, {"source": "Telegraaf", "month": "July", "articles": 28}, {"source": "Telegraaf", "month": "June", "articles": 55}, {"source": "Telegraaf", "month": "March", "articles": 58}, {"source": "Telegraaf", "month": "May", "articles": 29}, {"source": "Telegraaf", "month": "November", "articles": 47}, {"source": "Telegraaf", "month": "October", "articles": 25}, {"source": "Telegraaf", "month": "September", "articles": 46}, {"source": "Trouw", "month": "April", "articles": 39}, {"source": "Trouw", "month": "August", "articles": 20}, {"source": "Trouw", "month": "December", "articles": 39}, {"source": "Trouw", "month": "February", "articles": 48}, {"source": "Trouw", "month": "January", "articles": 51}, {"source": "Trouw", "month": "July", "articles": 33}, {"source": "Trouw", "month": "June", "articles": 51}, {"source": "Trouw", "month": "March", "articles": 67}, {"source": "Trouw", "month": "May", "articles": 46}, {"source": "Trouw", "month": "November", "articles": 34}, {"source": "Trouw", "month": "October", "articles": 23}, {"source": "Trouw", "month": "September", "articles": 34}, {"source": "Volkskrant", "month": "April", "articles": 40}, {"source": "Volkskrant", "month": "August", "articles": 33}, {"source": "Volkskrant", "month": "December", "articles": 44}, {"source": "Volkskrant", "month": "February", "articles": 44}, {"source": "Volkskrant", "month": "January", "articles": 65}, {"source": "Volkskrant", "month": "July", "articles": 44}, {"source": "Volkskrant", "month": "June", "articles": 75}, {"source": "Volkskrant", "month": "March", "articles": 72}, {"source": "Volkskrant", "month": "May", "articles": 43}, {"source": "Volkskrant", "month": "November", "articles": 45}, {"source": "Volkskrant", "month": "October", "articles": 38}, {"source": "Volkskrant", "month": "September", "articles": 38}]}};
      var embedOpt = {"mode": "vega-lite"};
    vegaEmbed("#vis_pub_month", spec, embedOpt);
})(vegaEmbed);
</script>

## Geodata

Now we need to get hold of list toponyms that we can use in the *named entity recognition*. Two freely available resources that we can use for this purpose are the [GeoNames](http://www.geonames.org/) and [REST Countries](http://restcountries.eu/) datasets. The map below shows all data points that were selected from the GeoNames dataset for the task at hand. The dataset contains 45,300 toponyms in total.

#### Place distribution in the GeoNames dataset
<img src="illustrations/distribution_places_world.png"/>

## Toponyms

Using `spaCy's` [named entitiy recognition functionality](https://spacy.io/usage/linguistic-features#named-entities) we can then collect and count all toponyms in the newspaper articles. Perhaps unsurprisingly only a fraction of the total toponyms are recognized:

Toponyms         | REST/GeoNames | Found in dataset | % Found 
-----------------|--------------:|-----------------:|---------:
Countries        |           268 |              151 |    56.3 
Cities Friesland |            27 |               11 |    40.7 
Cities NL        |           474 |              119 |    25.1 
Cities UK        |         1,532 |              147 |     9.6 
Cities world     |        43,237 |              844 |     2.0 

The interactive graphs below shows several measures for the found results. Click on the legend labels to zoom in on a specific newspaper. Select multiple newspapers by shift-clicking.

#### Some measures on the occurrence of toponyms in the selected articles
<div id="vis_toponyms"></div>
<script>
(function(vegaEmbed) {
    var spec = {"config": {"view": {"continuousWidth": 400, "continuousHeight": 300}}, "hconcat": [{"mark": "bar", "encoding": {"color": {"type": "nominal", "field": "source"}, "opacity": {"condition": {"value": 1, "selection": "selector001"}, "value": 0.2}, "x": {"type": "nominal", "field": "source"}, "y": {"type": "quantitative", "aggregate": "sum", "field": "unique", "title": "number of unique toponyms"}}, "height": 328, "selection": {"selector001": {"type": "multi", "fields": ["source"], "bind": "legend"}}}, {"mark": "bar", "encoding": {"color": {"type": "nominal", "field": "source"}, "opacity": {"condition": {"value": 1, "selection": "selector001"}, "value": 0.2}, "x": {"type": "nominal", "field": "source"}, "y": {"type": "quantitative", "aggregate": "sum", "field": "frequency", "title": "total frequency of toponyms"}}, "height": 328, "selection": {"selector001": {"type": "multi", "fields": ["source"], "bind": "legend"}}}, {"vconcat": [{"mark": "bar", "encoding": {"color": {"type": "nominal", "field": "source"}, "x": {"type": "quantitative", "aggregate": "sum", "field": "articles", "title": "number of articles"}, "y": {"type": "nominal", "field": "category", "sort": ["countries", "places", "places_uk", "places_nl", "places_fr"]}}, "selection": {"selector001": {"type": "multi", "fields": ["source"], "bind": "legend"}}, "transform": [{"filter": {"selection": "selector001"}}]}, {"mark": "bar", "encoding": {"color": {"type": "nominal", "field": "source"}, "x": {"type": "quantitative", "aggregate": "sum", "field": "unique", "title": "number of unique toponyms"}, "y": {"type": "nominal", "field": "category", "sort": ["countries", "places", "places_uk", "places_nl", "places_fr"]}}, "selection": {"selector001": {"type": "multi", "fields": ["source"], "bind": "legend"}}, "transform": [{"filter": {"selection": "selector001"}}]}, {"mark": "bar", "encoding": {"color": {"type": "nominal", "field": "source"}, "x": {"type": "quantitative", "aggregate": "sum", "field": "frequency", "title": "total frequency of toponyms"}, "y": {"type": "nominal", "field": "category", "sort": ["countries", "places", "places_uk", "places_nl", "places_fr"]}}, "selection": {"selector001": {"type": "multi", "fields": ["source"], "bind": "legend"}}, "transform": [{"filter": {"selection": "selector001"}}]}]}], "data": {"name": "data-408f63f986752ab52a835209d4593cdd"}, "$schema": "https://vega.github.io/schema/vega-lite/v4.0.2.json", "datasets": {"data-408f63f986752ab52a835209d4593cdd": [{"source": "Leeuwarder Courant", "category": "countries", "frequency": 1254, "unique": 81, "articles": 226}, {"source": "Leeuwarder Courant", "category": "places", "frequency": 338, "unique": 65, "articles": 131}, {"source": "Leeuwarder Courant", "category": "places_fr", "frequency": 45, "unique": 10, "articles": 18}, {"source": "Leeuwarder Courant", "category": "places_nl", "frequency": 203, "unique": 32, "articles": 71}, {"source": "Leeuwarder Courant", "category": "places_uk", "frequency": 165, "unique": 16, "articles": 84}, {"source": "Telegraaf", "category": "countries", "frequency": 1764, "unique": 79, "articles": 365}, {"source": "Telegraaf", "category": "places", "frequency": 553, "unique": 65, "articles": 204}, {"source": "Telegraaf", "category": "places_fr", "frequency": 0, "unique": 0, "articles": 0}, {"source": "Telegraaf", "category": "places_nl", "frequency": 420, "unique": 37, "articles": 183}, {"source": "Telegraaf", "category": "places_uk", "frequency": 319, "unique": 32, "articles": 151}, {"source": "Trouw", "category": "countries", "frequency": 3574, "unique": 117, "articles": 434}, {"source": "Trouw", "category": "places", "frequency": 1025, "unique": 116, "articles": 274}, {"source": "Trouw", "category": "places_fr", "frequency": 2, "unique": 1, "articles": 1}, {"source": "Trouw", "category": "places_nl", "frequency": 310, "unique": 39, "articles": 113}, {"source": "Trouw", "category": "places_uk", "frequency": 461, "unique": 47, "articles": 168}, {"source": "Volkskrant", "category": "countries", "frequency": 3631, "unique": 125, "articles": 491}, {"source": "Volkskrant", "category": "places", "frequency": 1180, "unique": 153, "articles": 330}, {"source": "Volkskrant", "category": "places_fr", "frequency": 2, "unique": 2, "articles": 2}, {"source": "Volkskrant", "category": "places_nl", "frequency": 528, "unique": 56, "articles": 145}, {"source": "Volkskrant", "category": "places_uk", "frequency": 728, "unique": 71, "articles": 230}]}};
    var embedOpt = {"mode": "vega-lite"};
    vegaEmbed("#vis_toponyms", spec, embedOpt);
})(vegaEmbed);
</script>

The analysis also tells us specifically *what* places were mentioned in the articles. By plotting that information on a map we can see the geographical distribution of news on Brexit. Explore the results in [this interactive map](map_toponyms.html). The circle sizes represent the number of times a toponym was found in the dataset. With the layer control you can switch on/off layers. Click on a circle to open a tooltip with more information on the toponym and the frequency with which it occurs in the text and articles.

## Insights

Some insights that can be gleaned from this analysis are:

1. The quality newspapers contain a greater volume of toponyms.
2. They also refer to a greater number of different places.
3. The coverage is heavily biased towards London, Brussels and Amsterdam.
4. The regional newspaper covers the north of NL, the other papers do not. 

## References
*Harvey, D. (2005). "The sociological and geographical imaginations". In: International Journal of Politics, Culture, and Society 18.3-4, p. 211–255.*
