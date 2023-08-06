import matplotlib.pyplot as plt
import matplotlib
import numpy as np
import pdb


class ExtractedFigure(object):
    """
    Extract the plotted Artists in the AxesSubplots of a Figure and
    enable the reconfiguration of the Artist attributes
    """
    
    def __init__(self, fig):
        """
        Initialize the ExtractedFigure object
        
        Args:
            fig (matplotlib.figure.Figure): The Figure that will have its Artists modified

        Returns:
            None
        """
        self.extracted_figure = fig
        
    def retrieve_figure_subplots(self):
        """
        Extract the list of matplotlib AxesSubplots in the Figure
        
        (Note: the datatype of the AxesSubplot will be 
         matplotlib.axes._subplots.AxesSubplot)

        Args:
            None

        Returns:
            None
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

        Args:
            None

        Returns:
            None
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
        
