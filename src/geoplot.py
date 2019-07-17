# third party
import matplotlib.pyplot as plt
from adjustText import adjust_text

# local
from src.config import PARAM, PATH_SHAPES, PATH_RESULTS


def geoplot_points(
    ax,
    basemap,
    gdf,
    points,
    title=None,
    factor=1,
    ):
    """
    Plot points on a basemap.
    """

    basemap.plot(ax=ax, color='lightyellow', edgecolor='lightgray')
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
        loc="upper left",
        borderpad=2.0,
        labelspacing=4.5,
        handletextpad=2.0,
        frameon=False,
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
            fontsize=14,
            ) for _, row in gdf.iterrows()
        ]
    return adjust_text(texts, ax=ax)
