# third party
import matplotlib.pyplot as plt
from matplotlib import rcParams
rcParams.update({
    "font.family": "serif",  # use serif/main font for text elements
    "text.usetex": True,     # use inline math for ticks
    "pgf.rcfonts": False,    # don't setup fonts from rc parameters
})
from adjustText import adjust_text


def geoplot_points(
    ax,
    basemap,
    gdf,
    points,
    title=None,
    factor=1,
    frameon=True,
    legend_loc='upper left'
    ):
    """
    Plot points on a basemap.
    """

    basemap.plot(
        ax=ax,
        color=(31/256, 119/256, 180/256, 0.1),
        edgecolor='lightgray',
        linewidth=0.5,
    )
    ax.tick_params(labelsize=8)
    scatter = gdf.plot(
        ax=ax,
        marker='o',
        color='red',
        alpha=0.5,
        markersize=points * factor
    )
    kw = dict(
        prop="sizes",
        num=[1,10,50,200],
        color='red',
        alpha=0.5,
        func=lambda s: s/factor,
    )
    legend = ax.legend(
        *scatter.collections[1].legend_elements(**kw),
        loc=legend_loc,
        borderpad=1.8,
        labelspacing=2.5,
        handletextpad=1.8,
        frameon=frameon,
    )
    if title:
        ax.set_title(title, fontdict={'fontsize':24})
    return ax


def annotate_geoplot(ax, gdf, text):
    texts = [
        ax.text(
            row['geometry'].x,
            row['geometry'].y,
            row[text],
            ha='center',
            va='center',
            fontsize=9,
            ) for _, row in gdf.iterrows()
        ]
    return adjust_text(texts, ax=ax)
