---
title: Results
---

<script type="text/javascript" src="https://cdn.jsdelivr.net/npm//vega@5"></script>
<script type="text/javascript" src="https://cdn.jsdelivr.net/npm//vega-lite@4.0.2"></script>
<script type="text/javascript" src="https://cdn.jsdelivr.net/npm//vega-embed@6"></script>

# LexisNexis Place Extraction

Check out the places mentioned in [this interactive map](map_toponyms.html).

## Articles

<div id="vis_pub_month"></div>
<script>
    (function(vegaEmbed) {
    var spec = {"config": {"view": {"continuousWidth": 400, "continuousHeight": 300}}, "data": {"name": "data-95f0ac09e71d1ebb2ce6a523858975b1"}, "mark": "bar", "encoding": {"color": {"type": "nominal", "field": "source"}, "x": {"type": "ordinal", "field": "publication_date", "sort": ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"], "title": "publication date"}, "y": {"type": "quantitative", "aggregate": "sum", "field": "number_of_articles", "title": "number of articles"}}, "$schema": "https://vega.github.io/schema/vega-lite/v4.0.2.json", "datasets": {"data-95f0ac09e71d1ebb2ce6a523858975b1": [{"publication_date": "January", "source": "Leeuwarder Courant", "number_of_articles": 26}, {"publication_date": "January", "source": "Telegraaf", "number_of_articles": 53}, {"publication_date": "January", "source": "Trouw", "number_of_articles": 51}, {"publication_date": "January", "source": "Volkskrant", "number_of_articles": 65}, {"publication_date": "February", "source": "Leeuwarder Courant", "number_of_articles": 23}, {"publication_date": "February", "source": "Telegraaf", "number_of_articles": 52}, {"publication_date": "February", "source": "Trouw", "number_of_articles": 48}, {"publication_date": "February", "source": "Volkskrant", "number_of_articles": 44}, {"publication_date": "March", "source": "Leeuwarder Courant", "number_of_articles": 42}, {"publication_date": "March", "source": "Telegraaf", "number_of_articles": 58}, {"publication_date": "March", "source": "Trouw", "number_of_articles": 67}, {"publication_date": "March", "source": "Volkskrant", "number_of_articles": 72}, {"publication_date": "April", "source": "Leeuwarder Courant", "number_of_articles": 28}, {"publication_date": "April", "source": "Telegraaf", "number_of_articles": 35}, {"publication_date": "April", "source": "Trouw", "number_of_articles": 39}, {"publication_date": "April", "source": "Volkskrant", "number_of_articles": 40}, {"publication_date": "May", "source": "Leeuwarder Courant", "number_of_articles": 23}, {"publication_date": "May", "source": "Telegraaf", "number_of_articles": 29}, {"publication_date": "May", "source": "Trouw", "number_of_articles": 46}, {"publication_date": "May", "source": "Volkskrant", "number_of_articles": 43}, {"publication_date": "June", "source": "Leeuwarder Courant", "number_of_articles": 31}, {"publication_date": "June", "source": "Telegraaf", "number_of_articles": 55}, {"publication_date": "June", "source": "Trouw", "number_of_articles": 51}, {"publication_date": "June", "source": "Volkskrant", "number_of_articles": 75}, {"publication_date": "July", "source": "Leeuwarder Courant", "number_of_articles": 17}, {"publication_date": "July", "source": "Telegraaf", "number_of_articles": 28}, {"publication_date": "July", "source": "Trouw", "number_of_articles": 33}, {"publication_date": "July", "source": "Volkskrant", "number_of_articles": 44}, {"publication_date": "August", "source": "Leeuwarder Courant", "number_of_articles": 10}, {"publication_date": "August", "source": "Telegraaf", "number_of_articles": 25}, {"publication_date": "August", "source": "Trouw", "number_of_articles": 20}, {"publication_date": "August", "source": "Volkskrant", "number_of_articles": 33}, {"publication_date": "September", "source": "Leeuwarder Courant", "number_of_articles": 14}, {"publication_date": "September", "source": "Telegraaf", "number_of_articles": 46}, {"publication_date": "September", "source": "Trouw", "number_of_articles": 34}, {"publication_date": "September", "source": "Volkskrant", "number_of_articles": 38}, {"publication_date": "October", "source": "Leeuwarder Courant", "number_of_articles": 13}, {"publication_date": "October", "source": "Telegraaf", "number_of_articles": 25}, {"publication_date": "October", "source": "Trouw", "number_of_articles": 23}, {"publication_date": "October", "source": "Volkskrant", "number_of_articles": 38}, {"publication_date": "November", "source": "Leeuwarder Courant", "number_of_articles": 28}, {"publication_date": "November", "source": "Telegraaf", "number_of_articles": 47}, {"publication_date": "November", "source": "Trouw", "number_of_articles": 34}, {"publication_date": "November", "source": "Volkskrant", "number_of_articles": 45}, {"publication_date": "December", "source": "Leeuwarder Courant", "number_of_articles": 21}, {"publication_date": "December", "source": "Telegraaf", "number_of_articles": 35}, {"publication_date": "December", "source": "Trouw", "number_of_articles": 39}, {"publication_date": "December", "source": "Volkskrant", "number_of_articles": 44}]}};
    var embedOpt = {"mode": "vega-lite"};

    function showError(el, error){
        el.innerHTML = ('<div class="error" style="color:red;">'
                        + '<p>JavaScript Error: ' + error.message + '</p>'
                        + "<p>This usually means there's a typo in your chart specification. "
                        + "See the javascript console for the full traceback.</p>"
                        + '</div>');
        throw error;
    }
    const el = document.getElementById('vis_pub_month');
    vegaEmbed("#vis_pub_month", spec, embedOpt)
        .catch(error => showError(el, error));
})(vegaEmbed);
</script>


## Lemma clouds

### Volkskrant

<!-- <embed src="illustrations/wc_volkskrant.pdf"/> -->
<img src="illustrations/wc_volkskrant.png"/>

### Trouw

<!-- <embed src="illustrations/wc_trouw.pdf"/> -->
<img src="illustrations/wc_trouw.png"/>

### Telegraaf

<!-- <embed src="illustrations/wc_telegraaf.pdf"/> -->
<img src="illustrations/wc_telegraaf.png"/>

### Leeuwarder Courant

<!-- <embed src="illustrations/wc_leeuwarder_courant.pdf"/> -->
<img src="illustrations/wc_leeuwarder_courant.png"/>
