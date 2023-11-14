import sys
import pathlib
import warnings
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
warnings.filterwarnings("ignore")
current_dir = pathlib.Path().absolute()
fa_dir = current_dir.parents[0].joinpath('src')
# Importing fish_analyses module
sys.path.append(str(fa_dir))
import external.fish_analyses as fa

# Defining directories
current_dir = pathlib.Path().absolute()
fa_dir = current_dir.parents[0].joinpath('src')
# Importing fish_analyses module
sys.path.append(str(fa_dir))
import external.fish_analyses as fa
emulator=fa.MicroscopeSimulation()
cell_library_folder_path = current_dir.joinpath('data','core','cell_library')
list_library_cells, dataframe_cell_library, background_pixels_library = emulator.initialize(cell_library_folder_path)

image_size_Y_X = [5000,5000]
number_of_cells_in_simulation = 50
simulation_dataframe,complete_image_size_Z_Y_X = emulator.generate_simulated_positions(image_size_Y_X,number_of_cells_in_simulation,list_library_cells,dataframe_cell_library)
simulation_dataframe.tail()

# Region to display
z_position = 7 #[-13:13]
y_position =  2000
x_position = 2000
x_size = 512
y_size = 512
simulated_image,dataframe_cells_in_image = emulator.make_simulated_image(z_position, y_position, x_position, x_size, y_size, complete_image_size_Z_Y_X, simulation_dataframe, list_library_cells, background_pixels_library)
# Plotting
number_color_channels = simulated_image.shape[2]
fig, ax = plt.subplots(1,number_color_channels, figsize=(15, 7))
# Plotting the heatmap of a section in the image
print('z-position: ', str(z_position))
for i in range (number_color_channels):
    #simulated_image_removed_extreme_values = simulated_image[:,:,i]#fa.RemoveExtrema(simulated_image[:,:,i],min_percentile=0, max_percentile=99.9).remove_outliers()  #np.max(simulated_image[:,:,:,i],axis = 0)
    simulated_image_removed_extreme_values = fa.RemoveExtrema(simulated_image[:,:,i],min_percentile=0, max_percentile=99.9).remove_outliers()  #np.max(simulated_image[:,:,:,i],axis = 0)

    ax[i].imshow(simulated_image_removed_extreme_values);ax[i].set(title='Channel '+ str(i)); ax[i].axis('off');ax[i].grid(False)
    #print('mean int ch: ',str(i),' ' , np.mean(simulated_image_removed_extreme_values))
plt.show()
import cProfile
with cProfile.Profile() as pr:
    # ... do something ...
    dataframe = fa.PipelineFISH(
        image=simulated_image,
        channels_with_cytosol=None,
        channels_with_nucleus=[0],
        channels_with_FISH=[1],
        diameter_nucleus=80,
        diameter_cytosol=0,
        voxel_size_z=500,
        voxel_size_yx=130,
        file_name_str='temp',
        psf_z=500,
        psf_yx=300,
        show_plots=False,
        # folder_name='termi'
    ).run()[0]
    pr.print_stats()
1+1