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
    title_fontsize=24,
    factor=1,
    axis_labelsize=8,
    basemap_color=(31/256, 119/256, 180/256, 0.1),
    basemap_edgecolor='lightgray',
    point_marker='o',
    point_color='red',
    point_alpha=0.5,
    legend_points=[1,10,50,200],
    legend_borderpad=1.8,
    legend_labelspacing=2.5,
    legend_handletextpad=1.8,
    frameon=True,
    legend_loc='upper left'
    ):
    """
    Plot points on a basemap.
    """

    basemap.plot(
        ax=ax,
        color=basemap_color,
        edgecolor=basemap_edgecolor,
        linewidth=0.5,
    )
    ax.tick_params(labelsize=axis_labelsize)
    scatter = gdf.plot(
        ax=ax,
        marker=point_marker,
        color=point_color,
        alpha=point_alpha,
        markersize=points * factor
    )
    kw = dict(
        prop="sizes",
        num=legend_points,
        color=point_color,
        alpha=point_alpha,
        func=lambda s: s/factor,
    )
    ax.legend(
        *scatter.collections[1].legend_elements(**kw),
        loc=legend_loc,
        borderpad=legend_borderpad,
        labelspacing=legend_labelspacing,
        handletextpad=legend_handletextpad,
        frameon=frameon,
    )
    if title:
        ax.set_title(title, fontdict={'fontsize':title_fontsize})
    return ax


def annotate_geoplot(ax, gdf, text):
    "Annotate names on plot."

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
