---
title: Toponym distributions
---

<img src="illustrations/banner.png"/>

<script type="text/javascript" src="https://cdn.jsdelivr.net/npm//vega@5"></script>
<script type="text/javascript" src="https://cdn.jsdelivr.net/npm//vega-lite@4.0.2"></script>
<script type="text/javascript" src="https://cdn.jsdelivr.net/npm//vega-embed@6"></script>

# Distributions
All newspapers seem to cover only a handful of places extensively. In the graph below the five most frequently mentioned toponyms are graphed per geographical category and newspaper. Hover over the bars to see a tooltip with the corresponding toponym. 

  <div id="vis"></div>
  <script>
    (function(vegaEmbed) {
      var spec = {"config": {"view": {"continuousWidth": 400, "continuousHeight": 300}}, "data": {"name": "data-toponym-distributions"}, "facet": {"column": {"type": "nominal", "field": "source"}, "row": {"type": "nominal", "field": "category"}}, "spec": {"mark": "bar", "encoding": {"tooltip": {"type": "nominal", "field": "toponym"}, "x": {"type": "nominal", "field": "ranking", "sort": "y"}, "y": {"type": "quantitative", "field": "articles", "scale": {"type": "log"}}}, "height": 200}, "$schema": "https://vega.github.io/schema/vega-lite/v4.0.2.json", "datasets": {"data-toponym-distributions": [{"category": "countries", "ranking": 1, "source": "Leeuwarder Courant", "articles": 234, "toponym": "Verenigd Koninkrijk"}, {"category": "countries", "ranking": 1, "source": "Telegraaf", "articles": 283, "toponym": "Verenigd Koninkrijk"}, {"category": "countries", "ranking": 1, "source": "Trouw", "articles": 455, "toponym": "Verenigd Koninkrijk"}, {"category": "countries", "ranking": 1, "source": "Volkskrant", "articles": 446, "toponym": "Verenigd Koninkrijk"}, {"category": "countries", "ranking": 2, "source": "Leeuwarder Courant", "articles": 96, "toponym": "Nederland"}, {"category": "countries", "ranking": 2, "source": "Telegraaf", "articles": 161, "toponym": "Nederland"}, {"category": "countries", "ranking": 2, "source": "Trouw", "articles": 185, "toponym": "Nederland"}, {"category": "countries", "ranking": 2, "source": "Volkskrant", "articles": 218, "toponym": "Nederland"}, {"category": "countries", "ranking": 3, "source": "Leeuwarder Courant", "articles": 57, "toponym": "Verenigde Staten"}, {"category": "countries", "ranking": 3, "source": "Telegraaf", "articles": 91, "toponym": "Verenigde Staten"}, {"category": "countries", "ranking": 3, "source": "Trouw", "articles": 183, "toponym": "Verenigde Staten"}, {"category": "countries", "ranking": 3, "source": "Volkskrant", "articles": 159, "toponym": "Verenigde Staten"}, {"category": "countries", "ranking": 4, "source": "Leeuwarder Courant", "articles": 31, "toponym": "Duitsland"}, {"category": "countries", "ranking": 4, "source": "Telegraaf", "articles": 54, "toponym": "Duitsland"}, {"category": "countries", "ranking": 4, "source": "Trouw", "articles": 88, "toponym": "Duitsland"}, {"category": "countries", "ranking": 4, "source": "Volkskrant", "articles": 121, "toponym": "Duitsland"}, {"category": "countries", "ranking": 5, "source": "Leeuwarder Courant", "articles": 29, "toponym": "Frankrijk"}, {"category": "countries", "ranking": 5, "source": "Telegraaf", "articles": 53, "toponym": "Frankrijk"}, {"category": "countries", "ranking": 5, "source": "Trouw", "articles": 88, "toponym": "Frankrijk"}, {"category": "countries", "ranking": 5, "source": "Volkskrant", "articles": 114, "toponym": "Frankrijk"}, {"category": "places", "ranking": 1, "source": "Leeuwarder Courant", "articles": 80, "toponym": "Brussel"}, {"category": "places", "ranking": 1, "source": "Telegraaf", "articles": 122, "toponym": "Brussel"}, {"category": "places", "ranking": 1, "source": "Trouw", "articles": 155, "toponym": "Brussel"}, {"category": "places", "ranking": 1, "source": "Volkskrant", "articles": 190, "toponym": "Brussel"}, {"category": "places", "ranking": 2, "source": "Leeuwarder Courant", "articles": 15, "toponym": "Parijs"}, {"category": "places", "ranking": 2, "source": "Telegraaf", "articles": 31, "toponym": "Parijs"}, {"category": "places", "ranking": 2, "source": "Trouw", "articles": 42, "toponym": "Parijs"}, {"category": "places", "ranking": 2, "source": "Volkskrant", "articles": 77, "toponym": "Parijs"}, {"category": "places", "ranking": 3, "source": "Leeuwarder Courant", "articles": 8, "toponym": "New York"}, {"category": "places", "ranking": 3, "source": "Telegraaf", "articles": 17, "toponym": "Berlijn"}, {"category": "places", "ranking": 3, "source": "Trouw", "articles": 26, "toponym": "Berlijn"}, {"category": "places", "ranking": 3, "source": "Volkskrant", "articles": 42, "toponym": "Berlijn"}, {"category": "places", "ranking": 4, "source": "Leeuwarder Courant", "articles": 6, "toponym": "Dublin"}, {"category": "places", "ranking": 4, "source": "Telegraaf", "articles": 13, "toponym": "New York"}, {"category": "places", "ranking": 4, "source": "Trouw", "articles": 24, "toponym": "New York"}, {"category": "places", "ranking": 4, "source": "Volkskrant", "articles": 36, "toponym": "New York"}, {"category": "places", "ranking": 5, "source": "Leeuwarder Courant", "articles": 5, "toponym": "Berlijn"}, {"category": "places", "ranking": 5, "source": "Telegraaf", "articles": 13, "toponym": "Dublin"}, {"category": "places", "ranking": 5, "source": "Trouw", "articles": 24, "toponym": "Dublin"}, {"category": "places", "ranking": 5, "source": "Volkskrant", "articles": 23, "toponym": "Dublin"}, {"category": "places_uk", "ranking": 1, "source": "Leeuwarder Courant", "articles": 76, "toponym": "Londen"}, {"category": "places_uk", "ranking": 1, "source": "Telegraaf", "articles": 132, "toponym": "Londen"}, {"category": "places_uk", "ranking": 1, "source": "Trouw", "articles": 135, "toponym": "Londen"}, {"category": "places_uk", "ranking": 1, "source": "Volkskrant", "articles": 194, "toponym": "Londen"}, {"category": "places_uk", "ranking": 2, "source": "Leeuwarder Courant", "articles": 6, "toponym": "Manchester"}, {"category": "places_uk", "ranking": 2, "source": "Telegraaf", "articles": 6, "toponym": "Manchester"}, {"category": "places_uk", "ranking": 2, "source": "Trouw", "articles": 14, "toponym": "Manchester"}, {"category": "places_uk", "ranking": 2, "source": "Volkskrant", "articles": 21, "toponym": "Manchester"}, {"category": "places_uk", "ranking": 3, "source": "Leeuwarder Courant", "articles": 3, "toponym": "Belfast"}, {"category": "places_uk", "ranking": 3, "source": "Telegraaf", "articles": 4, "toponym": "Liverpool"}, {"category": "places_uk", "ranking": 3, "source": "Trouw", "articles": 6, "toponym": "Birmingham"}, {"category": "places_uk", "ranking": 3, "source": "Volkskrant", "articles": 14, "toponym": "Oxford"}, {"category": "places_uk", "ranking": 4, "source": "Leeuwarder Courant", "articles": 2, "toponym": "Edinburgh"}, {"category": "places_uk", "ranking": 4, "source": "Telegraaf", "articles": 3, "toponym": "Aberdeen"}, {"category": "places_uk", "ranking": 4, "source": "Trouw", "articles": 5, "toponym": "Belfast"}, {"category": "places_uk", "ranking": 4, "source": "Volkskrant", "articles": 11, "toponym": "Liverpool"}, {"category": "places_uk", "ranking": 5, "source": "Leeuwarder Courant", "articles": 2, "toponym": "Liverpool"}, {"category": "places_uk", "ranking": 5, "source": "Telegraaf", "articles": 3, "toponym": "Belfast"}, {"category": "places_uk", "ranking": 5, "source": "Trouw", "articles": 5, "toponym": "Dover"}, {"category": "places_uk", "ranking": 5, "source": "Volkskrant", "articles": 7, "toponym": "Belfast"}, {"category": "places_nl", "ranking": 1, "source": "Leeuwarder Courant", "articles": 28, "toponym": "Amsterdam"}, {"category": "places_nl", "ranking": 1, "source": "Telegraaf", "articles": 124, "toponym": "Amsterdam"}, {"category": "places_nl", "ranking": 1, "source": "Trouw", "articles": 53, "toponym": "Amsterdam"}, {"category": "places_nl", "ranking": 1, "source": "Volkskrant", "articles": 77, "toponym": "Amsterdam"}, {"category": "places_nl", "ranking": 2, "source": "Leeuwarder Courant", "articles": 16, "toponym": "Den Haag"}, {"category": "places_nl", "ranking": 2, "source": "Telegraaf", "articles": 40, "toponym": "Den Haag"}, {"category": "places_nl", "ranking": 2, "source": "Trouw", "articles": 29, "toponym": "Den Haag"}, {"category": "places_nl", "ranking": 2, "source": "Volkskrant", "articles": 41, "toponym": "Den Haag"}, {"category": "places_nl", "ranking": 3, "source": "Leeuwarder Courant", "articles": 9, "toponym": "Utrecht"}, {"category": "places_nl", "ranking": 3, "source": "Telegraaf", "articles": 16, "toponym": "Rotterdam"}, {"category": "places_nl", "ranking": 3, "source": "Trouw", "articles": 16, "toponym": "Rotterdam"}, {"category": "places_nl", "ranking": 3, "source": "Volkskrant", "articles": 16, "toponym": "Utrecht"}, {"category": "places_nl", "ranking": 4, "source": "Leeuwarder Courant", "articles": 8, "toponym": "Rotterdam"}, {"category": "places_nl", "ranking": 4, "source": "Telegraaf", "articles": 6, "toponym": "Utrecht"}, {"category": "places_nl", "ranking": 4, "source": "Trouw", "articles": 13, "toponym": "Utrecht"}, {"category": "places_nl", "ranking": 4, "source": "Volkskrant", "articles": 14, "toponym": "Rotterdam"}, {"category": "places_nl", "ranking": 5, "source": "Leeuwarder Courant", "articles": 7, "toponym": "Groningen"}, {"category": "places_nl", "ranking": 5, "source": "Telegraaf", "articles": 6, "toponym": "Tilburg"}, {"category": "places_nl", "ranking": 5, "source": "Trouw", "articles": 9, "toponym": "Groningen"}, {"category": "places_nl", "ranking": 5, "source": "Volkskrant", "articles": 11, "toponym": "Leiden"}]}};
      var embedOpt = {"mode": "vega-lite"};
      vegaEmbed("#vis", spec, embedOpt)
        .catch(error => showError(el, error));
    })(vegaEmbed);

  </script>