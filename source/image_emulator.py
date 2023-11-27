import os

import numpy as np
from scipy.signal import convolve2d
from PIL import  Image
from os import listdir
from os.path import isfile, join
import pandas as pd
import pathlib
import re
from scipy.ndimage import gaussian_filter
import pickle
from data_manager import DataManager
class iImageEmulator:
    '''parses events and creates a simualetd image'''
    def generate(self,position,n=20,channelIndex=None):
        '''returns image array from position value. If channel is none returns n color image'''
        pass

class ImageEmulatorFromArray(iImageEmulator):
    simulator=None
    def __init__(self,image=[],isGaussianZImageDistort=True):
        self.setImageFromArray(image)
        self.isGaussianZImageDistort=isGaussianZImageDistort
        self.zOrigin=0

    def setImageFromArray(self,image):
        if not isinstance(image,(list,np.ndarray)):
            raise TypeError
        if isinstance(image,list):
            image=np.array(image)
        self.image=image


    def generate(self,position,n=20,channelIndex=None):
        z=position[2]
        sig=5*(abs(z-self.zOrigin)+0.5)
        ax = np.linspace(-(n - 1) / 2., (n - 1) / 2., n)
        gauss = np.exp(-0.5 * np.square(ax) / np.square(sig))
        kernel = np.outer(gauss, gauss)
        kernel=kernel/np.sum(kernel)
        if channelIndex:
            image=self.image[:,:,channelIndex]
        else:
            image=self.image
        image=convolve2d(image, kernel, 'same')
        return image.astype('uint16')

class TestImageEmulator (iImageEmulator):
    simulator=None
    def __init__(self,isGaussianZImageDistort=True):
        image = np.array(Image.open('data/test/fluorescentcells.jpg')).astype('uint16')
        image=np.sum(image[:512,:512,:]/3,axis=2).astype('uint16')
        self.setImageFromArray(image)
        self.isGaussianZImageDistort=isGaussianZImageDistort
        self.zOrigin=0

    def setImageFromArray(self,image):
        if not isinstance(image,(list,np.ndarray)):
            raise TypeError
        if isinstance(image,list):
            image=np.array(image)
        self.image=image

    def generate(self,position,n=20,channelIndex=None):
        z=position[2]
        if channelIndex:
            image=self.image[:,:,channelIndex]
        else:
            image=self.image
        sig=5*(abs(z-self.zOrigin))
        if sig==0:
            return image #return image in special case that sigma is at 0 to avoid inf up ahead
        ax = np.linspace(-(n - 1) / 2., (n - 1) / 2., n)
        gauss = np.exp(-0.5 * np.square(ax) / np.square(sig))
        kernel = np.outer(gauss, gauss)
        kernel=kernel/np.sum(kernel)
        image=convolve2d(image, kernel, 'same')
        return image.astype('uint16')

class ImageEmulator2Channel():
    def __init__(self):
        self.x_size = None
        self.y_size = None
        self.alpha=np.array([0.,0.,0.])
        self.loadImageFilePath('data/core/cell_library')
        self.num_cells_in_image=[]

    def loadImageFilePath(self,cell_library_folder_path):
        if isinstance(cell_library_folder_path,str):
            cell_library_folder_path=pathlib.Path(cell_library_folder_path)
        if not isinstance(cell_library_folder_path,pathlib.Path):
            raise TypeError


        # current_dir = pathlib.Path().absolute()
        # Path to data
        # cell_library_folder_path = current_dir.joinpath('cell_library')
        background_library_path = cell_library_folder_path.joinpath('background_pixels_library.npy')
        dataframe_library_path = cell_library_folder_path.joinpath('dataframe_library.csv')
        # extracting library data
        background_pixels_library = np.load(
            background_library_path)  # Reading the background library [C, Number_pixels]
        dataframe_cell_library = pd.read_csv(
            dataframe_library_path)  # Returns a dataframe with the following columns [cell_id, size,
        # ,ts_size] and each row represents a cell.
        list_library_cells = self.read_files(
            cell_library_folder_path)  # Returns a list of cells where each cell has the shape [Z,Y,X,C]
        self.list_library_cells=list_library_cells
        self.dataframe_cell_library=dataframe_cell_library
        self.background_pixels_library=background_pixels_library

    def read_files(self,directory):
        list_files_names_complete = sorted(
            [f for f in listdir(directory) if isfile(join(directory, f)) and ('cell_') in f],
            key=str.lower)  # reading all files in the folder with prefix 'cell_'
        list_files_names_complete.sort(
            key=lambda f: int(re.sub('\D', '', f)))  # sorting the index in numerical order
        path_files_complete = [str(directory.joinpath(f).resolve()) for f in
                               list_files_names_complete]  # creating the complete path for each file
        list_library_cells = [np.load(f) for f in path_files_complete]
        return list_library_cells

    def simulatePositions(self,image_size_X_Y, number_of_cells_in_simulation, generate_cells_close_to_each_other=True):
        t=image_size_X_Y
        image_size_X_Y[0]=t[1]
        image_size_X_Y[1] = t[0]
        initial_dictionary_for_df = {
            'start_y_position': [],
            'start_x_position': [],
            'centroid_y': [],
            'centroid_x': [],
            'z_size': [],
            'y_size': [],
            'x_size': [],
            'nucleus_area': [],
            'number_of_spots': [],
            'ts_size_0': [],
            'ts_size_1': [],
            'ts_size_2': [],
            'ts_size_3': [],
            'library_id': [],
        }
        # this statement generate a large number of cells if generate_cells_close_to_each_other is true.
        if generate_cells_close_to_each_other == True:
            large_number_initial_simulation = number_of_cells_in_simulation * 3
        else:
            large_number_initial_simulation = number_of_cells_in_simulation
        # Create the DataFrame
        number_cells_in_library = len(self.list_library_cells)
        max_cell_size = np.max([np.max(cell.shape[1:3]) for _, cell in enumerate(self.list_library_cells)])

        simulation_dataframe = pd.DataFrame(initial_dictionary_for_df)
        # max_cell_size
        MAX_NUM_ITERATIONS = 20000
        printed_cells = 0
        min_position_image_edge = max_cell_size
        max_y_position = image_size_X_Y[0] - min_position_image_edge
        max_x_position = image_size_X_Y[1] - min_position_image_edge
        counter = 0
        # random indexes for selecting a cell from library
        number_cells_in_library = len(self.list_library_cells)
        rnd_index_cells = np.random.randint(0, number_cells_in_library, size=MAX_NUM_ITERATIONS).astype(int)
        # This creates a random positions with a len MAX_NUM_ITERATIONS
        y_positions = np.random.randint(min_position_image_edge, max_y_position - max_cell_size,
                                        size=MAX_NUM_ITERATIONS).astype(int)
        x_positions = np.random.randint(min_position_image_edge, max_x_position - max_cell_size,
                                        size=MAX_NUM_ITERATIONS).astype(int)
        z_positions = np.zeros(MAX_NUM_ITERATIONS, dtype=int)
        cell_size_Z_Y_X = np.zeros((number_cells_in_library, 3))
        for i in range(number_cells_in_library):
            cell_size_Z_Y_X[i, :] = self.list_library_cells[i][:, :, :, 0].shape
        # Main while loop that iterates until number_of_cell_in_image is reached or counter>MAX_NUM_ITERATIONS
        list_cells_position = []
        while (counter < MAX_NUM_ITERATIONS - 1) and (printed_cells <= large_number_initial_simulation - 1):
            add_cell = False
            tested_positions = []
            if printed_cells > 0:
                # Test cell positions
                cell_Z_Y_X_positions = [z_positions[counter], y_positions[counter], x_positions[counter]]
                tested_positions = list_cells_position.copy()
                tested_positions.append(cell_Z_Y_X_positions)
                array_tested_positions = np.asarray(tested_positions)
                # Calculating a distance matrix.
                distance_matrix = np.zeros((array_tested_positions.shape[0], array_tested_positions.shape[0]))
                for i in range(len(array_tested_positions)):
                    for j in range(len(array_tested_positions)):
                        if j < i:
                            distance_matrix[i, j] = np.linalg.norm(
                                (array_tested_positions[i, :] - array_tested_positions[j, :]))
                # Masking the distance matrix. Ones indicate the distance is less or equal than threshold_distance
                mask_distance_matrix = (distance_matrix <= max_cell_size)
                # Negation (NOT) of the distance_matrix .
                negation_subsection_mask_distance_matrix = ~mask_distance_matrix
                lower_diagonal_mask_distance_matrix = np.tril(negation_subsection_mask_distance_matrix, k=-1)
                add_cell = np.all(lower_diagonal_mask_distance_matrix[-1, :-1])
                del array_tested_positions
            else:
                cell_Z_Y_X_positions = [z_positions[counter], y_positions[counter], x_positions[counter]]
                add_cell = True
            if add_cell == True:
                library_cell_index = rnd_index_cells[counter]
                list_cells_position.append(cell_Z_Y_X_positions)
                centroid_y = y_positions[counter] + cell_size_Z_Y_X[library_cell_index, 1] // 2
                centroid_x = x_positions[counter] + cell_size_Z_Y_X[library_cell_index, 2] // 2
                # extracting information about a given cell
                nucleus_area = self.dataframe_cell_library.loc[
                    (self.dataframe_cell_library['cell_id'] == library_cell_index)].nucleus_area.values[0]
                number_of_spots = self.dataframe_cell_library.loc[
                    (self.dataframe_cell_library['cell_id'] == library_cell_index)].number_of_spots.values[0]
                ts_array = np.zeros(4, dtype=int)

                list_ts = [self.dataframe_cell_library.loc[
                               (self.dataframe_cell_library['cell_id'] == library_cell_index)].ts_size_0.values,
                           self.dataframe_cell_library.loc[
                               (self.dataframe_cell_library['cell_id'] == library_cell_index)].ts_size_1.values,
                           self.dataframe_cell_library.loc[
                               (self.dataframe_cell_library['cell_id'] == library_cell_index)].ts_size_2.values,
                           self.dataframe_cell_library.loc[
                               (self.dataframe_cell_library['cell_id'] == library_cell_index)].ts_size_3.values]
                # min_length = min(len(ts_array), len(list_ts))
                for ijk in range(len(list_ts)):
                    ts_array[ijk] = list_ts[ijk][0]
                cell_data = pd.Series([y_positions[counter], x_positions[counter], centroid_y, centroid_x,
                                       cell_size_Z_Y_X[library_cell_index, 0], cell_size_Z_Y_X[library_cell_index, 1],
                                       cell_size_Z_Y_X[library_cell_index, 2], nucleus_area,
                                       number_of_spots] + ts_array.tolist() + [library_cell_index],
                                      index=simulation_dataframe.columns)
                simulation_dataframe = simulation_dataframe.append(cell_data, ignore_index=True)
                #simulation_dataframe = pd.concat([simulation_dataframe,cell_data],ignore_index=True)
                printed_cells += 1
            counter += 1
        new_dtypes = {'start_y_position': int, 'start_x_position': int, 'centroid_y': int, 'centroid_x': int,
                      'z_size': int, 'y_size': int, 'x_size': int, 'nucleus_area': int, 'number_of_spots': int,
                      'ts_size_0': int, 'ts_size_1': int, 'ts_size_2': int, 'ts_size_3': int, 'library_id': int}
        simulation_dataframe = simulation_dataframe.astype(new_dtypes)

        if generate_cells_close_to_each_other == True:
            # Calculating the distance matrix of selected cells
            tested_positions = simulation_dataframe[['start_y_position', 'start_x_position']]
            array_tested_positions = np.asarray(tested_positions)
            # Calculating a distance matrix.
            distance_matrix = np.zeros((array_tested_positions.shape[0], array_tested_positions.shape[0]))
            for i in range(len(array_tested_positions)):
                for j in range(len(array_tested_positions)):
                    distance_matrix[i, j] = np.linalg.norm(
                        (array_tested_positions[i, :] - array_tested_positions[j, :]))
            # Calculating the distance of the closest N cells around a given cell
            sum_rows = []
            number_neighbor_cell = 8
            for i in range(distance_matrix.shape[0]):
                row_values = distance_matrix[i]
                n_min_values_indices = np.argsort(row_values)[:number_neighbor_cell]
                sum_rows.append(np.sum(row_values[n_min_values_indices]))
            sum_rows = np.asarray(sum_rows)
            # Selecting only number_of_cells_in_simulation
            selected_indices = np.argsort(sum_rows)[:number_of_cells_in_simulation]
            simulation_dataframe_new = simulation_dataframe.iloc[selected_indices].copy()
            simulation_dataframe_new = simulation_dataframe_new.reset_index(drop=True)
            # simulation_dataframe_new['number'] =simulation_dataframe_new.index
            simulation_dataframe = simulation_dataframe_new
        # Creating a new df selecting only the cells
        size_Z = self.list_library_cells[0].shape[0]
        complete_image_size_Z_Y_X = [size_Z] + image_size_X_Y
        self.simulation_dataframe=simulation_dataframe
        self.complete_image_size_Z_Y_X=complete_image_size_Z_Y_X


    def setXYImageSize(self,size):
        if not isinstance(size,list):
            raise TypeError
        self.x_size=size[1]
        self.y_size=size[0]

    def setAlpha(self,alpha):
        if isinstance(alpha,list):
            alpha=np.array(alpha)
        if len(alpha) !=3:
            raise TypeError
        self.alpha=alpha

    def getAlpha(self):
        return self.alpha


    def generate(self,position,n=20,channelIndex=0,remove_elements_low_intensity=False):
        x_position=position[1]
        y_position=position[0]
        if len(position)==3:
            z_position = position[2]
        else:
            z_position=0
        #  Distorted z-plane
        z_position_hat = int( self.alpha[0] + (self.alpha[1] * x_position) + (self.alpha[2] * y_position) + z_position)
        number_color_channels = self.list_library_cells[0].shape[3]
        # Re-centering z_position index
        length_z_indices = self.complete_image_size_Z_Y_X[0]
        z_array = np.arange(0, length_z_indices, 1)
        z_position_center_as_zero = self.complete_image_size_Z_Y_X[0] // 2
        z_position_original = z_position_center_as_zero + z_position_hat
        z_array = [
            int(i - z_position_center_as_zero) if i < z_position_center_as_zero else int(i - z_position_center_as_zero)
            for i in range(length_z_indices)]
        list_mean_background_pixels_library = []
        # list_std_background_pixels_library=[]
        if not self.background_pixels_library is None:
            list_mean_background_pixels_library = [np.mean(self.background_pixels_library[i, :]) for i in
                                                   range(number_color_channels)]
        #    list_std_background_pixels_library = [np.std(background_pixels_library[i,:]) for i in range(number_color_channels)  ]
        y_range = [y_position, y_position + self.y_size]
        x_range = [x_position, x_position + self.x_size]

        def min_edge_value_full_image(tested_value, edge_values, original_edge):
            if tested_value < edge_values:
                new_range = 0
            else:
                new_range = tested_value
            moved_pixels = abs(original_edge - new_range)
            return new_range, moved_pixels

        def max_edge_value_full_image(tested_value, edge_values, original_edge):
            if tested_value > edge_values:
                new_range = edge_values
            else:
                new_range = tested_value
            moved_pixels = abs(new_range - original_edge-1)
            return new_range, moved_pixels

        # extending the image range to consider cell on the image border
        additional_range = 200
        extended_y_min_range, moved_px_y_min = min_edge_value_full_image(y_range[0] - additional_range, 0, y_range[0])
        extended_x_min_range, moved_px_x_min = min_edge_value_full_image(x_range[0] - additional_range, 0, x_range[0])
        extended_y_max_range, moved_px_y_max = max_edge_value_full_image(y_range[1] + additional_range,
                                                                         self.complete_image_size_Z_Y_X[1], y_range[1])
        extended_x_max_range, moved_px_x_max = max_edge_value_full_image(x_range[1] + additional_range,
                                                                         self.complete_image_size_Z_Y_X[2], x_range[1])
        extended_y_pixels = extended_y_max_range - extended_y_min_range
        extended_x_pixels = extended_x_max_range - extended_x_min_range

        # Function to calculate ranges
        def return_ranges(selected_row, initial_x_range=None, initial_y_range=None):
            tested_x_size = selected_row.x_size
            tested_y_size = selected_row.y_size
            is_even_x = tested_x_size % 2 == 0
            is_even_y = tested_y_size % 2 == 0
            if not (initial_x_range is None):
                tested_x_position = selected_row.start_x_position - initial_x_range
            else:
                tested_x_position = selected_row.start_x_position
            if not (initial_y_range is None):
                tested_y_position = selected_row.start_y_position - initial_y_range
            else:
                tested_y_position = selected_row.start_y_position
            min_y_value = tested_y_position - tested_y_size // 2
            max_y_value = tested_y_position + tested_y_size // 2 + int(is_even_x)
            min_x_value = tested_x_position - tested_x_size // 2
            max_x_value = tested_x_position + tested_x_size // 2 + int(is_even_y)
            return min_y_value, max_y_value, min_x_value, max_x_value

        # Test one by one if a cell is located inside the extended area
        list_is_inside_range = []
        for _, selected_row in self.simulation_dataframe.iterrows():
            min_y_value, max_y_value, min_x_value, max_x_value = return_ranges(selected_row, initial_x_range=None,
                                                                               initial_y_range=None)
            is_inside_range = (min_x_value >= extended_x_min_range) & (max_x_value <= extended_x_max_range) & (
                        min_y_value >= extended_y_min_range) & (max_y_value <= extended_y_max_range)
            list_is_inside_range.append(is_inside_range)
        condition = np.array(list_is_inside_range)
        dataframe_cells_in_image = self.simulation_dataframe[condition]
        # take the image position and the cell location
        number_cells_in_library = len(self.list_library_cells)
        volume_simulated_image = np.zeros((extended_y_pixels, extended_x_pixels, number_color_channels), dtype=int)
        # Repetitive calculation performed over library of cells. Including cell shapes, cell_indexes, simulated volumes
        list_volume_tested_cell = []
        for i in range(number_cells_in_library):
            # creating the image if z_position is inside z_array
            if np.isin (z_position_hat , z_array):
                list_volume_tested_cell.append(self.list_library_cells[i][z_position_original, :, :, :].astype(np.uint16))
            else:
                # iterating for each color channel
                temp_image = np.zeros_like(self.list_library_cells[i][0, :, :, :], dtype=np.uint16)
                for ch in range(number_color_channels):
                    temp_image[:,:,ch] = self.list_library_cells[i][z_position_center_as_zero,:,:,ch]
                list_volume_tested_cell.append(temp_image)
                del temp_image
        # Lambda function to calculate edges in simulation
        min_edge_simulation = lambda tested_value: 0 if tested_value < 0 else tested_value
        # main loop that creates the simulated image
        for _, selected_row in dataframe_cells_in_image.iterrows():
            library_id_selected = selected_row.library_id
            volume_selected_cell = list_volume_tested_cell[library_id_selected]
            min_y_value, max_y_value, min_x_value, max_x_value = return_ranges(selected_row,
                                                                               initial_x_range=extended_x_min_range,
                                                                               initial_y_range=extended_y_min_range)
            # Positions in final simulation
            y_min_in_simulation = min_edge_simulation(min_y_value)
            x_min_in_simulation = min_edge_simulation(min_x_value)
            # Subsection of the volume to add to the final image
            sub_volume_selected_cell = volume_selected_cell.copy()
            sim_y_max = y_min_in_simulation + sub_volume_selected_cell.shape[0]
            sim_x_max = x_min_in_simulation + sub_volume_selected_cell.shape[1]
            # adding the cell to the image
            volume_simulated_image[y_min_in_simulation:sim_y_max, x_min_in_simulation:sim_x_max,
            :] = sub_volume_selected_cell
            del sub_volume_selected_cell
        # Loop that creates the final dataframe only if the nucleus centroid is inside the desired area.
        list_is_inside_range = []
        for _, selected_row in dataframe_cells_in_image.iterrows():
            centroid_y = selected_row.centroid_y
            centroid_x = selected_row.centroid_x
            is_inside_range = (centroid_x >= x_range[0]) & (centroid_x <= x_range[1]) & (centroid_y >= y_range[0]) & (
                        centroid_y <= y_range[1])
            list_is_inside_range.append(is_inside_range)
        # Test one by one if a cell is located inside the
        condition_inside_final_area = np.array(list_is_inside_range)
        dataframe_cells_in_image = dataframe_cells_in_image[condition_inside_final_area]
        dataframe_cells_in_image.reset_index(drop=True, inplace=True)
        if not self.background_pixels_library is None:
            # adding background noise
            simulated_image = np.zeros_like(volume_simulated_image)
            for i in range(number_color_channels):
                temp_simulated_image = volume_simulated_image[:, :, i].copy()
                zero_indices = np.where(temp_simulated_image == 0)
                random_elements = np.random.choice(self.background_pixels_library[i, :], size=len(zero_indices[0]))
                # Replace zero elements with random elements
                temp_simulated_image[zero_indices] = random_elements
                simulated_image[:, :, i] = temp_simulated_image
        else:
            simulated_image = volume_simulated_image
        # add a filter to the image if z is out of bounds
        if not np.isin (z_position_hat , z_array):
            z_distance_from_edge = np.abs(z_position_hat) - np.max(z_array)
            scaling_factor = 1 * z_distance_from_edge
            sigma = 10  # The standard deviation of the Gaussian distribution
            for ch in range(number_color_channels):
                simulated_image[:, :, ch] = gaussian_filter(simulated_image[:, :, ch], sigma * scaling_factor)
                if (not self.background_pixels_library is None) and (remove_elements_low_intensity == True):
                    temp_simulated_image = simulated_image[:, :, ch].copy()
                    indices_to_replace = np.where(temp_simulated_image < list_mean_background_pixels_library[ch])
                    random_elements = np.random.choice(self.background_pixels_library[ch, :],
                                                       size=len(indices_to_replace[0]))
                    #    # Replace zero elements with random elements
                    temp_simulated_image[indices_to_replace] = random_elements
                    simulated_image[:, :, ch] = temp_simulated_image
        # Reshaping the final image
        simulated_image = simulated_image[moved_px_y_min:-moved_px_y_max - 1, moved_px_x_min:-moved_px_x_max - 1,
                          :].copy()
        self.dataframe_cells_in_image=dataframe_cells_in_image
        self.num_cells_in_image.append(dataframe_cells_in_image.shape[0])
        simulated_image=simulated_image[:,:,channelIndex]
        simulated_image=simulated_image.tolist()
        return np.array(simulated_image,dtype='uint16')

class ImageEmulatorWrapper():
    def __init__(self,system=None,isCached=True):
        self.system=system
        self.isCached=isCached
        self.cache= {}

    def generate(self, position, n=20, channelIndex=None):
        key=str(position)+'_'+str(channelIndex)+'_'+str(n)
        print(key)
        if self.isCached and (key in self.cache.keys()):
            print('Hit')
            return self.cache[key]
        else:
            image = self.system.generate(position, n=n, channelIndex=channelIndex)
            self.cache[key] = image
            print('No Hit')
            return image

    def saveCache(self):
        path=os.path.join('data','analysis','image_cache.pkl')
        with open(path, 'wb') as f:
            pickle.dump(self.cache,f)

    def tryLoadCache(self):
        path = os.path.join('data', 'analysis', 'image_cache.pkl')
        with open(path, 'rb') as f:
            cache=pickle.load(f)
        self.cache=cache

    def tryClearCache(self):
        path = os.path.join('data', 'analysis', 'image_cache.pkl')
        try:
            os.remove(path)
        except:
            pass