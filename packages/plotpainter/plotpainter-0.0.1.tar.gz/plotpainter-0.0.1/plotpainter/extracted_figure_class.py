import matplotlib
matplotlib.use("TkAgg")
from matplotlib import pyplot as plt
import numpy as np
#import pdb
from matplotlib.collections import (
    Collection, CircleCollection, LineCollection, PathCollection,
    PolyCollection, RegularPolyCollection)
from matplotlib.lines import Line2D
from matplotlib.container import ErrorbarContainer, BarContainer, StemContainer
from matplotlib.patches import (Patch, Rectangle, Shadow, FancyBboxPatch,
                                StepPatch)

# Given a figure, return the subplots and their children

class ExtractedArtist(object):
    """
    Extracted matplotlib artist or container of artists.
    """
    
    def __init__(self, artist, axessubplot, color, label, art_type):
        
        self.artist = artist
        self.subplot = axessubplot
        self.color = color
        self.label = label
        self.art_type = art_type
        
    def set_color(self, newcolor):
        
        # Set color for Line2D
        if isinstance(self.artist, Line2D):
            self.artist.set_color(newcolor)
            self.color = newcolor

        # Set facecolor and edgecolor for Patch
        elif isinstance(self.artist, Patch):
            self.artist.set_facecolor(newcolor)
            self.artist.set_edgecolor(newcolor)
            self.color = newcolor

        # Set facecolor and edgecolor for Collection
        elif isinstance(self.artist, Collection):
            self.artist.set_facecolor(newcolor)
            self.artist.set_edgecolor(newcolor)
            self.color = newcolor

        # Set facecolor and edgecolor for BarContainer
        # Note: All Rectangles in BarContainer are assumed to have the same
        # facecolor and edgecolor.
        elif isinstance(self.artist, BarContainer):
            children = self.artist.get_children()
            
            for child in children:
                child.set_facecolor(newcolor)
                child.set_edgecolor(newcolor)
                
            self.color = newcolor

        # Retrieve color for ErrorbarContainer
        # Note: The marker and errorbars in ErrorbarContainer are 
        # assumed to have the same color.
        elif isinstance(self.artist, ErrorbarContainer):
            children = self.artist.get_children()
            
            for child in children:
                child.set_color(newcolor)
                child.set_color(newcolor)
                
            self.color = newcolor

        else:
            print('Plotted artist class not supported.')
        
        

class ExtractedFigure(object):
    """
    Extract the plotted Artists in the AxesSubplots of a Figure and
    enable the reconfiguration of the Artist attributes
    """
    
    def __init__(self, fig):
        """
        Initialize the ExtractedFigure object
        
        Parameters:
        -------------
        fig: matplotlib.figure.Figure
            The Figure that will have its Artists modified
        """
        self.extracted_figure = fig
        
        # Retrieve the figure AxesSubplots
        self.retrieve_figure_subplots()
        
        # Retrieve the artists or artist containers plotted in each
        # subplot
        self.retrieve_axes_artists()
        
        # Retrieve the artist colors (all artists assumed to be the same
        # color)
        self.retrieve_colors_from_artists()

        # Retrieve the artist types
        self.retrieve_types_from_artists()
        
        # Create the array of Extracted Artists
        self.create_extracted_artist_list()
        
        
    def retrieve_figure_subplots(self):
        """
        Extract the list of matplotlib AxesSubplots in the Figure
        
        (Note: the datatype of the AxesSubplot will be 
         matplotlib.axes._subplots.AxesSubplot)
        """
        
        figure_subplots = []
        
        # Get the children of the Figure
        figure_children = self.extracted_figure.get_children()
        
        # If the item in the list of Figure children is a subclass of 
        # matplotlib.axes._subplots.SubplotBase, then it is an AxesSubplot
        for item in figure_children:
            if issubclass(type(item), matplotlib.axes._subplots.SubplotBase):
                figure_subplots.append(item)
            else:
                None
                
        # Save the AxesSubplot list
        self.axes_array = np.array(figure_subplots)
        
        return
    
    def retrieve_axes_artists(self):
        """
        For all AxesSubplots in the Figure, retrieve the plotted artists, 
        their labels, and current colors.
        """
        
        plotted_artists = []
        
        for subplot in self.axes_array:
            curr_ax_handles = []
            
            # For each AxesSubplot, extract the plotted artists
            for artist in subplot._children:
                if isinstance(artist, (Line2D, Patch, Collection)):
                    curr_ax_handles.append(artist)
                    
            # For each AxesSuplot, extract the containers of artists
            for container in subplot.containers:
                curr_ax_handles.append(container)
                
            # Remove all artists or containers that have '_nolegend_' for
            # a label, indicating that it is not an individual instance
            # plotted in the AxesSubplot
            
            good_artist_inds = []
            
            for ii in np.arange(len(curr_ax_handles)):
                if curr_ax_handles[ii].get_label() == '_nolegend_':
                    None
                else:
                    good_artist_inds.append(ii)
                    
            curr_ax_handles = np.array(curr_ax_handles, dtype = object)[good_artist_inds]
                    
            plotted_artists.append(curr_ax_handles)
        
        self.plotted_artists = plotted_artists
        
        # Retrieve the label for each plotted artist or container of artists
        plotted_artists_labels = []
        
        for ii in np.arange(len(self.plotted_artists)):
            
            curr_plotted_artists_labels = []
            
            for jj in np.arange(len(self.plotted_artists[ii])):
                curr_label = self.plotted_artists[ii][jj].get_label()
                curr_plotted_artists_labels.append(curr_label)
                
            plotted_artists_labels.append(np.array(curr_plotted_artists_labels))
            
        self.plotted_artists_labels = plotted_artists_labels


    def retrieve_types_from_artists(self):
        """
        Retieve the type for an artist or container of artists.
        
        """
        
        plotted_artists_types = []
        
        for ax_ind in np.arange(len(self.axes_array)):
            plotted_artists_types_curr = []
            for ind in np.arange(len(self.plotted_artists[ax_ind])):
                
                # Current artist in list
                artist = self.plotted_artists[ax_ind][ind]
                
                # Retrieve color from Line2Ds
                if isinstance(artist, Line2D):
                    plotted_artists_types_curr.append(['line'])
                    
                # Retrieve facecolor from Patches
                elif isinstance(artist, Patch):
                    plotted_artists_types_curr.append(['patch'])
                    
                # Retrieve type from Collections
                elif isinstance(artist, Collection):
                    plotted_artists_types_curr.append(['collection'])
                
                # Retrieve type from BarContainer
                elif isinstance(artist, BarContainer):
                    plotted_artists_types_curr.append(['bar_plot'])
                    
                # Retrieve type from ErrorbarContainer
                elif isinstance(artist, ErrorbarContainer):
                    plotted_artists_types_curr.append(['errorbar_plot'])
                    
                else:
                    print('Plotted artist class not supported.')
                    
            plotted_artists_types.append(plotted_artists_types_curr)
            
        self.plotted_artists_types = plotted_artists_types
        

    def retrieve_colors_from_artists(self):
        """
        Retrieve the color, or facecolor and edgecolor, for an artist or
        container of artists.
        
        """
        
        plotted_artists_colors = []
        
        for ax_ind in np.arange(len(self.axes_array)):
            plotted_artists_colors_curr = []
            for ind in np.arange(len(self.plotted_artists[ax_ind])):
                
                # Current artist in list
                artist = self.plotted_artists[ax_ind][ind]
                
                # Retrieve color from Line2Ds
                if isinstance(artist, Line2D):
                    linecolor = artist.get_color()
                    plotted_artists_colors_curr.append([linecolor])
                    
                # Retrieve facecolor from Patches
                elif isinstance(artist, Patch):
                    facecolor = artist.get_facecolor()
                    #edgecolor = artist.get_edgecolor()
                    #artist_colors = [facecolor, edgecolor]
                    #plotted_artists_colors_curr.append(artist_colors)
                    
                    plotted_artists_colors_curr.append([facecolor])
                    
                # Retrieve facecolor from Collections
                elif isinstance(artist, Collection):
                    facecolor = artist.get_facecolor()
                    #edgecolor = artist.get_edgecolor()
                    #artist_colors = [facecolor, edgecolor]
                    #plotted_artists_colors_curr.append(artist_colors)
                    plotted_artists_colors_curr.append([facecolor])
                
                # Retrieve facecolor and edgecolor from BarContainer
                # Note: All Rectangles in BarContainer are assumed to have the same
                # facecolor and edgecolor.
                elif isinstance(artist, BarContainer):
                    facecolor = artist.get_children()[0].get_facecolor()
                    #edgecolor = artist.get_children()[0].get_edgecolor()
                    #artist_colors = [facecolor, edgecolor]
                    #plotted_artists_colors_curr.append(artist_colors)
                    plotted_artists_colors_curr.append([facecolor])
                    
                # Retrieve color from ErrorbarContainer
                # Note: The marker and errorbars in ErrorbarContainer are 
                # assumed to have the same color.
                elif isinstance(artist, ErrorbarContainer):
                    color = artist.get_children()[0].get_color()
                    plotted_artists_colors_curr.append([color])
                    
                else:
                    print('Plotted artist class not supported.')
                    
            plotted_artists_colors.append(plotted_artists_colors_curr)
            
        self.plotted_artists_colors = plotted_artists_colors
        
    def create_extracted_artist_list(self):
        
        extracted_artist_list = []
        
        for ax_ind in np.arange(len(self.axes_array)):
            artist_list = self.plotted_artists[ax_ind]
            extracted_artist_list_curr = []
            
            for art_ind in np.arange(len(artist_list)):
                
                # Create the ExtractedArtist object
                extracted_artist = ExtractedArtist(artist = artist_list[art_ind],
                                                   axessubplot = self.axes_array[ax_ind],
                                                   color = self.plotted_artists_colors[ax_ind][art_ind],
                                                   label = self.plotted_artists_labels[ax_ind][art_ind],
                                                   art_type = self.plotted_artists_types[ax_ind][art_ind])
                
                # Add to list
                extracted_artist_list_curr.append(extracted_artist)
                
            extracted_artist_list.append(extracted_artist_list_curr)
            
        self.extracted_artist_list = extracted_artist_list
        
        
        
        
        
            
        
            
        
        
        
