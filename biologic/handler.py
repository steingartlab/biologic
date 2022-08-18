"""Handler bc it handles the data? Idk, might need to revise."""

import ctypes

from biologic import constants, exceptions

class KBIOData:
    """Class used to represent data obtained with a get_data call
    The data can be obtained as lists of floats through attributes on this
    class. The time is always available through the 'time' attribute. The
    attribute names for the rest of the data, are the same as their names as
    listed in the field_names attribute. E.g:
    * kbio_data.Ewe
    * kbio_data.I
    """

    def __init__(
        self, c_databuffer, c_data_infos, c_current_values, instrument
        ):
        """Initialize the KBIOData object
        Args:
            c_databuffer (Array of :py:class:`ctypes.c_uint32`): ctypes array
                of c_uint32 used as the data buffer
            c_data_infos (:class:`.DataInfos`): Data information structure
            c_current_values (:class:`CurrentValues`): Current values structure
            instrument (:class:`GeneralPotentiostat`): Instrument instance,
                should be an instance of a subclass of
                :class:`GeneralPotentiostat`
        Raises:
            ECLibCustomException: Where the error codes indicate the following:
                * -20000 means that the technique has no entry in
                  :data:`constants.Technique_TO_CLASS`
                * -20001 means that the technique class has no ``data_fields``
                  class variable
                * -20002 means that the ``data_fields`` class variables of the
                  technique does not contain the right information
        """

        technique_id = c_data_infos.TechniqueID
        self.technique = constants.Technique[technique_id]

        # Technique 0 means no data, get_data checks for this, so just return
        if technique_id == 0:
            return

        # Extract the process index, used to seperate data field classes for
        # techniques that support that, self.process = 1 also means no_time
        # variable in the beginning
        self.process = c_data_infos.ProcessIndex
        # Init the data_fields
        self.data_fields = self._init_data_fields(instrument)

        # Extract the number of points and columns
        self.number_of_points = c_data_infos.NbRaws
        self.number_of_columns = c_data_infos.NbCols
        self.starttime = c_data_infos.StartTime

        # Init time property, if the measurement process index indicates that
        # it has a special time variable
        if self.process == 0:
            self.time = []

        # Make lists for the data in properties named after the field_names
        for data_field in self.data_fields:
            setattr(self, data_field.name, [])

        # Parse the data
        self._parse_data(
            c_databuffer, c_current_values.TimeBase, instrument
            )

    def _init_data_fields(self, instrument):
        """Initialize the data fields property"""
        # Get the data_fields class variable from the corresponding technique
        # class
        if self.technique not in constants.Technique:
            message = \
                f'The technique \'{self.technique}\' has no entry in '\
                'constants.Technique_TO_CLASS. The is required to be able '\
                'to interpret the data'

            raise exceptions.ECLibCustomException(message, -20000)

        technique_class = constants.Technique[self.technique]

        if 'data_fields' not in technique_class.__dict__:
            message = 'The technique class {} does not defined a '\
                      '\'data_fields\' class variable, which is required for '\
                      'data interpretation.'.format(technique_class.__name__)
            raise exceptions.ECLibCustomException(message, -20001)

        data_fields_complete = technique_class.data_fields

        # if self.process != 1:
        #     try:
        #         data_fields_out = data_fields_complete['common']
        #     except KeyError:
        #         try:
        #             data_fields_out = data_fields_complete[
        #                 instrument.series]
        #         except KeyError:
        #             message =\
        #                 'Unable to get data_fields from technique class. '\
        #                 'The data_fields class variable in the technique '\
        #                 'class must have either a \'common\' or a \'{}\' '\
        #                 'key'.format(instrument.series)
        #             raise exceptions.ECLibCustomException(
        #                 message, -20002
        #                 )

        if self.process == 1:  # Process 1 means no special time field
            try:
                data_fields_out = data_fields_complete['no_time']
            except KeyError:
                message = 'Unable to get data_fields from technique class. '\
                          'The data_fields class variable in the technique '\
                          'class must have either a \'no_time\' key when '\
                          'returning data with process index 1'
                raise exceptions.ECLibCustomException(message, -20002)
        else:
            try:
                data_fields_out = data_fields_complete['common']
            except KeyError:
                try:
                    data_fields_out = data_fields_complete[
                        instrument.series]
                except KeyError:
                    message =\
                        f'Unable to get data_fields from technique class. '\
                        'The data_fields class variable in the technique '\
                        'class must have either a \'common\' or a \'{instrument.series}\' '\
                        'key'
                    raise exceptions.ECLibCustomException(
                        message, -20002
                        )

        return data_fields_out

    def _parse_data(self, c_databuffer, timebase, instrument):
        """Parse the data
        Args:
            timebase (float): The timebase for the time calculation
        See :meth:`.__init__` for information about remaining args
        """
        # The data is written as one long array of points with a certain
        # amount of colums. Get the index of the first item of each point by
        # getting the range from 0 til n_point * n_columns in jumps of
        # n_columns
        for index in range(
            0, self.number_of_points * self.number_of_columns,
            self.number_of_columns
            ):
            # If there is not a special time variable
            if self.process != 0:
                time_variable_offset = 0
                continue

            # Calculate the time
            t_high = c_databuffer[index]
            t_low = c_databuffer[index + 1]
            # NOTE: The documentation uses a bitshift operation for the:
            # ((t_high * 2 ** 32) + tlow) operation as
            # ((thigh << 32) + tlow), but I could not be bothered to
            # figure out exactly how a bitshift operation is defined for
            # an int class that can change internal representation, so I
            # just do the explicit multiplication
            self.time.append(
                self.starttime +\
                timebase * ((t_high * 2 ** 32) + t_low)
            )
            # Only offset reading the rest of the variables if there is a
            # special conversion time variable
            time_variable_offset = 2

            # Get remaining fields as defined in data fields
            for field_number, data_field in enumerate(
                self.data_fields
                ):
                value = c_databuffer[index + time_variable_offset +
                                     field_number]
                # If the type is supposed to be float, convert the numeric to
                # float using the convinience function
                if data_field.type is ctypes.c_float:
                    value = instrument.convert_numeric_into_single(
                        value
                        )

                # Append the field value to the appropriate list in a property
                getattr(self, data_field.name).append(value)

        # Check that the rest of the buffer is blank
        for index in range(
            self.number_of_points * self.number_of_columns, 1000
            ):
            assert c_databuffer[index] == 0

    @property
    def data_field_names(self):
        """Return a list of extra data fields names (besides time)"""

        return [data_field.name for data_field in self.data_fields]
