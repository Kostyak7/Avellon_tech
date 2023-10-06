import os
import pathlib
import shutil
from uuid import uuid4
import statistics as st
from PySide6.QtWidgets import QWidget, QMessageBox
from PySide6.QtCore import Qt
from third_party import get_num_file_by_default, MessageBox
from graph_widget import XYDataFrame, MaxesDataFrame
import config as cf


class DataFile:
    def __init__(self, name_: str, step_path_: str, id_: str = None):
        self.name = name_
        self.step_path = step_path_

        self.id = id_
        if self.id is None:
            self.id = uuid4()
        self.measurement_num, self.sensor_num = get_num_file_by_default(os.path.basename(self.name),
                                                                        cf.DEFAULT_SENSOR_AMOUNT)
        self.max_value = None
        self.is_select = False

    def __eq__(self, other_) -> bool:
        return self.id == other_.id

    def path(self) -> str:
        return self.step_path + '/' + self.name

    def change_path(self, new_step_path_: str) -> None:
        self.step_path = new_step_path_

    def select(self, is_select_: bool = True) -> None:
        self.is_select = is_select_

    def max(self, is_reload_: bool = False) -> float:
        if is_reload_ or self.max_value is None:
            if self.get_xy_dataframe() is None:
                return float('-inf')
        return self.max_value

    def get_xy_dataframe(self) -> XYDataFrame:
        if self.measurement_num == -1 or self.sensor_num == -1:
            MessageBox().warning(cf.WRONG_FILENAME_WARNING_TITLE, cf.WRONG_FILENAME_WARNING_MESSAGE_F(self.name))
            self.max_value = None
            return None
        xy_dataframe = XYDataFrame(self.path())
        if not xy_dataframe.active:
            return None
        self.max_value = xy_dataframe.max_y
        return xy_dataframe

    def exist(self, step_path_: str = None) -> bool:
        if step_path_ is not None:
            self.change_path(step_path_)
        path = self.path()
        return os.path.isfile(path)


class Step:
    def __init__(self, number_: int, section_path_: str, id_: str = None):
        self.number = number_
        self.section_path = section_path_

        self.id = id_
        if self.id is None:
            self.id = uuid4()
        self.max_value = None
        self.data_list = []
        self.is_select = False

        if len([f for f in pathlib.Path(self.path()).glob('*')]):
            self.correlate_data()

    def __eq__(self, other_) -> bool:
        return self.id == other_.id

    def path(self) -> str:
        return self.section_path + '/' + str(self.number)

    def change_path(self, new_section_path_: str) -> None:
        self.section_path = new_section_path_
        path = self.path()
        for data_file in self.data_list:
            data_file.change_path(path)

    def select(self, is_select_: bool = True) -> None:
        self.is_select = is_select_
        for data_file in self.data_list:
            data_file.select(is_select_)

    def add_file(self, file_name_: str, id_: str = None) -> None:
        if id_ is not None:
            for data_file in self.data_list:
                if data_file.id == id_:
                    return
        if os.path.exists(self.path() + '/' + file_name_):
            self.data_list.append(DataFile(file_name_, self.path(), id_))

    def __remove_file_by_index(self, i_: int) -> None:
        if self.data_list[i_].exist():
            os.remove(self.data_list[i_].path())
        self.data_list.pop(i_)

    def remove_all(self, full_clean_: bool = False) -> None:
        i = len(self.data_list) - 1
        while i >= 0:
            self.__remove_file_by_index(i)
            i -= 1
        if full_clean_:
            shutil.rmtree(self.path())
            os.mkdir(self.path())

    def remove_file(self, **kwargs) -> None:
        if 'id' in kwargs:
            id_ = kwargs['id']
            for i in range(len(self.data_list)):
                if self.data_list[i].id == id_:
                    self.__remove_file_by_index(i)
                    return
        elif 'name' in kwargs:
            name_ = kwargs['name']
            for i in range(len(self.data_list)):
                if self.data_list[i].name == name_:
                    self.__remove_file_by_index(i)
                    return

    def max(self, is_reload_: bool = False) -> float:
        if is_reload_ or self.max_value is None:
            self.max_value = float('-inf')
            for data_file in self.data_list:
                data_file_max = data_file.max(is_reload_)
                if self.max_value < data_file_max:
                    self.max_value = data_file_max
        return self.max_value

    def get_xy_dataframes_list(self) -> list:
        xy_dataframes_list = list()
        i = 0
        for data_file in self.data_list:
            xy_dataframe = data_file.get_xy_dataframe()
            if xy_dataframe is None or data_file.sensor_num == -1:
                while i < len(self.data_list):
                    if self.data_list[i].sensor_num == -1:
                        self.remove_file(id=self.data_list[i].id)
                    else:
                        i += 1
                return list()
            if xy_dataframe.is_correct_read() and data_file.is_select:
                xy_dataframes_list.append(xy_dataframe)
            i += 1
        return xy_dataframes_list

    def get_sensor_maxes_dict(self) -> dict:
        sensor_dict = dict()
        i = 0
        for data_file in self.data_list:
            if data_file.get_xy_dataframe() is None or data_file.sensor_num == -1:
                while i < len(self.data_list):
                    if self.data_list[i].sensor_num == -1:
                        self.remove_file(id=self.data_list[i].id)
                    else:
                        i += 1
                return dict()
            if data_file.sensor_num not in sensor_dict:
                sensor_dict[data_file.sensor_num] = [None] * cf.DEFAULT_MEASUREMENT_NUMBER
            sensor_dict[data_file.sensor_num][data_file.measurement_num] = data_file.max()
            i += 1

        for sensor_num in sensor_dict.keys():
            i = 0
            while i < len(sensor_dict[sensor_num]):
                if sensor_dict[sensor_num][i] is None:
                    sensor_dict[sensor_num].pop(i)
                else:
                    i += 1
        return sensor_dict

    def get_sensor_maxes_of_maxes_list(self) -> list:
        sensor_list = [0] * cf.DEFAULT_MEASUREMENT_NUMBER
        i = 0
        for data_file in self.data_list:
            if data_file.get_xy_dataframe() is None or data_file.sensor_num == -1:
                while i < len(self.data_list):
                    if self.data_list[i].sensor_num == -1:
                        self.remove_file(id=self.data_list[i].id)
                    else:
                        i += 1
                return list()
            sensor_list[data_file.sensor_num] = max(sensor_list[data_file.sensor_num], data_file.max())
            i += 1
        return sensor_list

    def get_sensor_dataframe_list(self) -> list:
        sensor_dict = self.get_sensor_maxes_dict()
        dataframes_list = []
        for sensor_num in sensor_dict.keys():
            if len(sensor_dict[sensor_num]):
                dataframes_list.append(MaxesDataFrame(str(sensor_num), sensor_dict[sensor_num]))
        return dataframes_list

    def get_maxes_dataframe(self) -> MaxesDataFrame:
        maxes = []
        for data_file in self.data_list:
            if data_file.is_select:
                if data_file.max() != float('-inf'):
                    maxes.append(data_file.max())
        return MaxesDataFrame('step=' + str(self.number), maxes)

    def exist(self, section_path_: str = None) -> bool:
        if section_path_ is not None:
            self.change_path(section_path_)
        path = self.path()
        return os.path.isdir(path)

    def correlate_data(self, section_path_: str = None) -> None:
        if not self.exist(section_path_):
            return
        path = pathlib.Path(self.path())
        files_dict = dict()

        for file_name in pathlib.Path(path).glob('*'):
            if file_name.is_file():
                files_dict[file_name] = False

        i = 0
        while i < len(self.data_list):
            self_file_path = pathlib.Path(self.data_list[i].path())
            if self_file_path not in files_dict:
                self.__remove_file_by_index(i)
                continue
            files_dict[self_file_path] = True
            i += 1

        for file_name in files_dict.keys():
            if not files_dict[file_name]:
                self.add_file(os.path.basename(file_name))


class Section:
    def __init__(self, name_: str, borehole_path_: str, depth_: int = 0, length_: float = cf.DEFAULT_SECTION_LENGTH, id_: str = None):
        self.name = name_
        self.depth = depth_
        self.length = length_
        self.borehole_path = borehole_path_

        self.id = id_
        if self.id is None:
            self.id = uuid4()
        self.max_value = None
        self.step_list = []
        self.is_select = False

        if len([f for f in pathlib.Path(self.path()).glob('*')]):
            self.correlate_data()

    def __eq__(self, other_) -> bool:
        return self.id == other_.id

    def path(self) -> str:
        return self.borehole_path + '/' + self.name

    def change_path(self, new_borehole_path_: str) -> None:
        self.borehole_path = new_borehole_path_
        path = self.path()
        for step in self.step_list:
            step.change_path(path)

    def select(self, is_select_: bool = True) -> None:
        self.is_select = is_select_
        for step in self.step_list:
            step.select(is_select_)

    def max(self, is_reload_: bool = False) -> float:
        if is_reload_ or self.max_value is None:
            self.max_value = float('-inf')
            for step in self.step_list:
                step_max = step.max(is_reload_)
                if self.max_value < step_max:
                    self.max_value = step_max
        return self.max_value

    def add_step(self, number_: int, id_: str = None):
        if id_ is not None:
            for step in self.step_list:
                if step.id == id_:
                    return
        path_to_new = self.path() + '/' + str(number_)
        if not os.path.isdir(path_to_new):
            os.mkdir(path_to_new)
        new_step = Step(number_, self.path(), id_)
        new_step.correlate_data()
        self.step_list.append(new_step)

    def __remove_step_by_index(self, i_: int) -> None:
        if self.step_list[i_].exist():
            shutil.rmtree(self.step_list[i_].path())
        self.step_list.pop(i_)

    def remove_all(self, full_clean_: bool = False) -> None:
        i = len(self.step_list) - 1
        while i >= 0:
            self.__remove_step_by_index(i)
            i -= 1
        if full_clean_:
            shutil.rmtree(self.path())
            os.mkdir(self.path())

    def remove_step(self, **kwargs) -> None:
        if 'id' in kwargs:
            id_ = kwargs['id']
            for i in range(len(self.step_list)):
                if self.step_list[i].id == id_:
                    self.__remove_step_by_index(i)
                    return
        elif 'name' in kwargs:
            name_ = kwargs['name']
            for i in range(len(self.step_list)):
                if self.step_list[i].name == name_:
                    self.__remove_step_by_index(i)
                    return

    def exist(self, borehole_path_: str = None) -> bool:
        if borehole_path_ is not None:
            self.change_path(borehole_path_)
        path = self.path()
        return os.path.isdir(path)

    def correlate_data(self, borehole_path_: str = None) -> None:
        if not self.exist(borehole_path_):
            return
        path = pathlib.Path(self.path())
        step_dict = dict()

        for step_name in pathlib.Path(path).glob('*'):
            if step_name.is_dir() and os.path.basename(step_name).isdigit():
                step_dict[step_name] = False

        i = 0
        while i < len(self.step_list):
            self_step_path = pathlib.Path(self.step_list[i].path())
            if self_step_path not in step_dict:
                self.__remove_step_by_index(i)
                continue
            step_dict[self_step_path] = True
            self.step_list[i].correlate_data()
            i += 1

        for step_name in step_dict.keys():
            if not step_dict[step_name]:
                self.add_step(int(os.path.basename(step_name)))

    def get_xy_dataframes_list(self) -> list:
        xy_dataframes_list = []
        for step in self.step_list:
            xy_dataframes_list += step.get_xy_dataframes_list()
        return xy_dataframes_list

    def get_sensor_21_dataframe_list(self) -> list:
        dataframes_list = []
        for step in self.step_list:
            step_df_list = step.get_sensor_dataframe_list()
            for dataframe in step_df_list:
                # if len(dataframe.data['y']) == 21:
                #     dataframes_list.append(dataframe)
                dataframes_list.append(dataframe)
        return dataframes_list

    def get_sensor_dataframe_list(self) -> list:
        dataframes_list = []
        tmp_list = [None] * cf.DEFAULT_SENSOR_AMOUNT
        for step in self.step_list:
            step_df_dict = step.get_sensor_maxes_dict()
            for key in step_df_dict.keys():
                ikey = int(key)
                if tmp_list[ikey] is None:
                    tmp_list[ikey] = []
                tmp_list[ikey] += step_df_dict[key]
        for i in range(len(tmp_list)):
            dataframes_list.append(MaxesDataFrame(str(i), [] if tmp_list[i] is None else tmp_list[i]))
        return dataframes_list

    def get_maxes_dataframe_list(self) -> list:
        dataframes_list = list()
        for step in self.step_list:
            dataframes_list.append(step.get_maxes_dataframe())
        return dataframes_list

    def get_step_maxes_dataframe_list(self) -> list:
        dataframes_list = []
        maxes_steps_dict = dict()
        for step in self.step_list:
            step_df_list = step.get_sensor_dataframe_list()
            for dataframe in step_df_list:
                if dataframe.name not in maxes_steps_dict:
                    maxes_steps_dict[dataframe.name] = []
                maxes_steps_dict[dataframe.name].append([dataframe.max(), int(step.number)])
        for sensor_num in maxes_steps_dict.keys():
            maxes_steps_dict[sensor_num].sort(key=lambda ms_: ms_[1])
            maxes, tmp_dict = [], {'x': []}
            for ms_ in maxes_steps_dict[sensor_num]:
                maxes.append(ms_[0])
                tmp_dict['x'].append(ms_[1])
            maxes_dataframe = MaxesDataFrame(str(sensor_num), maxes, x_list=tmp_dict['x'])
            maxes_dataframe.tmp_value = tmp_dict
            dataframes_list.append(maxes_dataframe)
        return dataframes_list

    def get_step_maxes_dataframe_dict(self) -> dict:
        if len(self.step_list) < 1:
            return None
        dataframe_dict = dict()
        tmp_dict = dict()
        mean_x_list = []
        for dataframe in self.get_step_maxes_dataframe_list():
            dataframe_dict[int(dataframe.name)] = dataframe
            i = 0
            for x_ in dataframe.tmp_value['x']:
                if x_ not in tmp_dict:
                    mean_x_list.append(x_)
                    tmp_dict[x_] = list()
                tmp_dict[x_].append(dataframe.data['y'][i])
                i += 1
        mean_x_list.sort()
        mean_list = []
        median_list = []
        geometric_mean_list= []
        harmonic_mean_list = []
        median_grouped_list = []
        for x_ in mean_x_list:
            mean_list.append(st.mean(tmp_dict[x_]))
            median_list.append(st.median(tmp_dict[x_]))
            geometric_mean_list.append(st.geometric_mean(tmp_dict[x_]))
            harmonic_mean_list.append(st.harmonic_mean(tmp_dict[x_]))
            median_grouped_list.append(st.median_grouped(tmp_dict[x_]))
        dataframe_dict[-1] = MaxesDataFrame('mean-section=' + self.name, mean_list, x_list=mean_x_list)
        dataframe_dict[-2] = MaxesDataFrame('median-section=' + self.name, median_list, x_list=mean_x_list)
        dataframe_dict[-3] = MaxesDataFrame('geometric_mean-section=' + self.name, geometric_mean_list, x_list=mean_x_list)
        dataframe_dict[-4] = MaxesDataFrame('harmonic_mean-section=' + self.name, harmonic_mean_list, x_list=mean_x_list)
        dataframe_dict[-5] = MaxesDataFrame('median_grouped-section=' + self.name, median_grouped_list, x_list=mean_x_list)
        for i in range(1, 6):
            dataframe_dict[-i].tmp_value = mean_x_list
        return dataframe_dict


class Borehole:
    def __init__(self, name_: str, path_: str, id_: str = None):
        self.name = name_
        self.up_path = path_
        if not os.path.isdir(self.path()):
            os.mkdir(self.path())

        self.id = id_
        if self.id is None:
            self.id = uuid4()
        self.section_list = []

        self.load_info_from_file()

    def __eq__(self, other_) -> bool:
        return self.id == other_.id

    def path(self) -> str:
        return self.up_path + '/' + self.name

    def change_path(self, new_path_: str) -> None:
        self.up_path = new_path_
        path = self.path()
        for section in self.section_list:
            section.change_path(path)

    def add_section(self, name_: str, depth_: int = 0, length_: float = 0., id_: str = None) -> None:
        if id_ is not None:
            for step in self.section_list:
                if step.id == id_:
                    return
        path_to_new = self.path() + '/' + name_
        if not os.path.isdir(path_to_new):
            os.mkdir(path_to_new)
        self.section_list.append(Section(name_, self.path(), depth_, length_, id_))

    def __remove_section_by_index(self, i_: int) -> None:
        if self.section_list[i_].exist():
            shutil.rmtree(self.section_list[i_].path())
        self.section_list.pop(i_)

    def remove_all(self, full_clean_: bool = False) -> None:
        i = len(self.section_list) - 1
        while i >= 0:
            self.__remove_section_by_index(i)
            i -= 1
        if full_clean_:
            shutil.rmtree(self.path())
            os.mkdir(self.path())

    def remove_section(self, **kwargs) -> None:
        if 'id' in kwargs:
            id_ = kwargs['id']
            for i in range(len(self.section_list)):
                if self.section_list[i].id == id_:
                    self.__remove_section_by_index(i)
                    return
        if 'name' in kwargs:
            name_ = kwargs['name']
            for i in range(len(self.section_list)):
                if self.section_list[i].name == name_:
                    self.__remove_section_by_index(i)
                    return

    def exist(self, path_: str = None) -> bool:
        if path_ is not None:
            self.change_path(path_)
        path = self.path()
        return os.path.isdir(path)

    def correlate_data(self, path_: str = None) -> None:
        if not self.exist(path_):
            return
        path = pathlib.Path(self.path())
        section_dict = dict()

        for section_name in pathlib.Path(path).glob('*'):
            if section_name.is_dir():
                section_dict[section_name] = False

        i = 0
        while i < len(self.section_list):
            self_section_path = pathlib.Path(self.section_list[i].path())
            if self_section_path not in section_dict:
                self.__remove_section_by_index(i)
                continue
            section_dict[self_section_path] = True
            self.section_list[i].correlate_data()
            i += 1

        for section_name in section_dict.keys():
            if not section_dict[section_name]:
                self.add_section(os.path.basename(section_name))

    def get_xy_dataframes_dict(self) -> dict:
        xy_dataframes_dict = dict()
        for section in self.section_list:
            xy_dataframes_dict[section.name] = section.get_xy_dataframes_list()
        return xy_dataframes_dict

    def get_sensor_21_dataframe_dict(self) -> dict:
        dataframes_dict = dict()
        for section in self.section_list:
            section_df_list = section.get_sensor_21_dataframe_list()
            if len(section_df_list):
                dataframes_dict[section.name] = section_df_list
        return dataframes_dict

    def get_sensor_dataframe_dict(self) -> dict:
        dataframes_dict = dict()
        for section in self.section_list:
            section_df_list = section.get_sensor_dataframe_list()
            if len(section_df_list):
                dataframes_dict[section.name] = section_df_list
        return dataframes_dict

    def get_maxes_dataframe_dict(self) -> dict:
        dataframes_dict = dict()
        for section in self.section_list:
            dataframes_dict[section.name] = section.get_maxes_dataframe_list()
        return dataframes_dict

    def get_step_maxes_dataframe_dict(self) -> dict:
        dataframes_dict = dict()
        for section in self.section_list:
            tmp_dict = section.get_step_maxes_dataframe_dict()
            if tmp_dict is not None:
                dataframes_dict[section.name] = tmp_dict
        return dataframes_dict

    def get_step_depth_dataframe_dict(self):
        dataframes_dict = dict()
        maxes_dict = dict()
        for section in self.section_list:
            for step in section.step_list:
                if step.number not in dataframes_dict:
                    dataframes_dict[step.number] = dict()
                if section.depth not in dataframes_dict[step.number] and len(step.data_list):
                    dataframes_dict[step.number][section.depth] = dict()
                    maxes_dict[section.depth] = dict()
                for datafile in step.data_list:
                    if datafile.sensor_num not in dataframes_dict[step.number][section.depth]:
                        dataframes_dict[step.number][section.depth][datafile.sensor_num] = {'x': datafile.max(), 'rx': 0}
                    if datafile.sensor_num not in maxes_dict[section.depth]:
                        maxes_dict[section.depth][datafile.sensor_num] =  datafile.max()
                    dataframes_dict[step.number][section.depth][datafile.sensor_num]['x'] = max(dataframes_dict[step.number][section.depth][datafile.sensor_num]['x'], datafile.max())
                    maxes_dict[section.depth][datafile.sensor_num] = max(maxes_dict[section.depth][datafile.sensor_num], datafile.max())
        for step_num in dataframes_dict.keys():
            for section_depth in dataframes_dict[step_num].keys():
                sensor_list = list()
                for sensor_num in dataframes_dict[step_num][section_depth].keys():
                    sensor_list.append(dataframes_dict[step_num][section_depth][sensor_num]['x'])
                if len(sensor_list):
                    dataframes_dict[step_num][section_depth][-1] = {'x': st.mean(sensor_list), 'rx': 0}
                    dataframes_dict[step_num][section_depth][-2] = {'x': st.median(sensor_list), 'rx': 0}
                    dataframes_dict[step_num][section_depth][-3] = {'x': st.geometric_mean(sensor_list), 'rx': 0}
                    dataframes_dict[step_num][section_depth][-4] = {'x': st.harmonic_mean(sensor_list), 'rx': 0}
                    dataframes_dict[step_num][section_depth][-5] = {'x': st.median_grouped(sensor_list), 'rx': 0}
                    i = -5
                    while i < 0:
                        if i not in maxes_dict[section_depth]:
                            maxes_dict[section_depth][i] = dataframes_dict[step_num][section_depth][i]['x']
                        maxes_dict[section_depth][i] = max(dataframes_dict[step_num][section_depth][i]['x'], maxes_dict[section_depth][i])
                        i += 1
        for step_num in dataframes_dict.keys():
            for section_depth in dataframes_dict[step_num].keys():
                for key in dataframes_dict[step_num][section_depth].keys():
                    dataframes_dict[step_num][section_depth][key]['rx'] = dataframes_dict[step_num][section_depth][key]['x'] / maxes_dict[section_depth][key]
        return dataframes_dict

    def save_info_to_file(self, filename_: str = cf.BOREHOLE_INFO_SAVE_FILENAME) -> None:
        path_filename = self.path() + '/' + filename_
        if os.path.isfile(path_filename):
            os.remove(path_filename)
        file = open(path_filename, "w")
        file.write(cf.BOREHOLE_NAME_BOREHOLE_INFO_F(self.name))

        file.write(cf.START_SECTIONS_TAG_BOREHOLE_INFO)
        for section in self.section_list:
            file.write(cf.START_SECTION_TAG_BOREHOLE_INFO)
            file.write(cf.SECTION_NAME_BOREHOLE_INFO_F(section.name))
            file.write(cf.SECTION_DEPTH_BOREHOLE_INFO_F(section.depth))
            file.write(cf.SECTION_LENGTH_BOREHOLE_INFO_F(section.length))
            file.write(cf.END_SECTION_TAG_BOREHOLE_INFO)
        file.write(cf.END_SECTIONS_TAG_BOREHOLE_INFO)
        file.close()

    def load_info_from_file(self, filename_: str = cf.BOREHOLE_INFO_SAVE_FILENAME) -> None:
        path = self.path() + '/' + filename_
        if not os.path.isfile(path):
            return
        file = open(path, "r")

        is_start = True
        is_in_section = False
        tmp_name, tmp_depth, tmp_length = '', -1, -1.
        for line in file:
            if is_start:
                if line[:len(cf.BOREHOLE_NAME_BOREHOLE_INFO)] != cf.BOREHOLE_NAME_BOREHOLE_INFO:
                    file.close()
                    return
                self.name = line[len(cf.BOREHOLE_NAME_BOREHOLE_INFO) + 1:-1]
                is_start = False
            else:
                if is_in_section:
                    if line[:len(cf.SECTION_NAME_BOREHOLE_INFO)] == cf.SECTION_NAME_BOREHOLE_INFO:
                        tmp_name = line[len(cf.SECTION_NAME_BOREHOLE_INFO) + 1:-1]
                    elif line[:len(cf.SECTION_DEPTH_BOREHOLE_INFO)] == cf.SECTION_DEPTH_BOREHOLE_INFO:
                        tmp_depth = int(float(line[len(cf.SECTION_DEPTH_BOREHOLE_INFO) + 1:]))
                    elif line[:len(cf.SECTION_LENGTH_BOREHOLE_INFO)] == cf.SECTION_LENGTH_BOREHOLE_INFO:
                        tmp_length = float(line[len(cf.SECTION_LENGTH_BOREHOLE_INFO) + 1:])
                    elif line == cf.END_SECTION_TAG_BOREHOLE_INFO:
                        self.add_section(tmp_name, tmp_depth, tmp_length)
                        is_in_section = False
                elif line == cf.START_SECTION_TAG_BOREHOLE_INFO:
                    is_in_section = True
                    tmp_name, tmp_depth, tmp_length = '', -1, -1.
        file.close()
