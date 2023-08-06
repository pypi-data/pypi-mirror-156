import datetime
import re
from typing import List, Tuple, Collection


class HeaderSyntaxError(ValueError):
    """Invalid syntax found in a WFDB header file."""


# Record line
# Format: RECORD_NAME/NUM_SEG NUM_SIG SAMP_FREQ/COUNT_FREQ(BASE_COUNT_VAL) SAMPS_PER_SIG BASE_TIME BASE_DATE
_rx_record = re.compile(
    r"""
    [ \t]* (?P<record_name>[-\w]+)
           /?(?P<n_seg>\d*)
    [ \t]+ (?P<n_sig>\d+)
    [ \t]* (?P<fs>\d*\.?\d*)
           /*(?P<counter_freq>-?\d*\.?\d*)
           \(?(?P<base_counter>-?\d*\.?\d*)\)?
    [ \t]* (?P<sig_len>\d*)
    [ \t]* (?P<base_time>\d{,2}:?\d{,2}:?\d{,2}\.?\d{,6})
    [ \t]* (?P<base_date>\d{,2}/?\d{,2}/?\d{,4})
    """,
    re.VERBOSE,
)

# Signal line
# Format: FILE_NAME FORMATxSAMP_PER_FRAME:SKEW+BYTE_OFFSET ADC_GAIN(BASELINE)/UNITS ADC_RES ADC_ZERO CHECKSUM BLOCK_SIZE DESCRIPTION
_rx_signal = re.compile(
    r"""
    [ \t]* (?P<file_name>~?[-\w]*\.?[\w]*)
    [ \t]+ (?P<fmt>\d+)
           x?(?P<samps_per_frame>\d*)
           :?(?P<skew>\d*)
           \+?(?P<byte_offset>\d*)
    [ \t]* (?P<adc_gain>-?\d*\.?\d*e?[\+-]?\d*)
           \(?(?P<baseline>-?\d*)\)?
           /?(?P<units>[\w\^\-\?%\/]*)
    [ \t]* (?P<adc_res>\d*)
    [ \t]* (?P<adc_zero>-?\d*)
    [ \t]* (?P<init_value>-?\d*)
    [ \t]* (?P<checksum>-?\d*)
    [ \t]* (?P<block_size>\d*)
    [ \t]* (?P<sig_name>[\S]?[^\t\n\r\f\v]*)
    """,
    re.VERBOSE,
)

# Segment line
_rx_segment = re.compile(
    r"""
    [ \t]* (?P<seg_name>[-\w]*~?)
    [ \t]+ (?P<seg_len>\d+)
    """,
    re.VERBOSE,
)


def wfdb_strptime(time_string: str) -> datetime.time:
    """
    Given a time string in an acceptable WFDB format, return
    a datetime.time object.

    Valid formats: SS, MM:SS, HH:MM:SS, all with and without microsec.

    Parameters
    ----------
    time_string : str
        The time to be converted to a datetime.time object.

    Returns
    -------
    datetime.time object
        The time converted from str format.

    """
    n_colons = time_string.count(":")

    if n_colons == 0:
        time_fmt = "%S"
    elif n_colons == 1:
        time_fmt = "%M:%S"
    elif n_colons == 2:
        time_fmt = "%H:%M:%S"

    if "." in time_string:
        time_fmt += ".%f"

    return datetime.datetime.strptime(time_string, time_fmt).time()


def parse_header_content(
    header_content: str,
) -> Tuple[List[str], List[str]]:
    """
    Parse the text of a header file.

    Parameters
    ----------
    header_content: str
        The string content of the full header file

    Returns
    -------
    header_lines : List[str]
        A list of all the non-comment lines
    comment_lines : List[str]
        A list of all the comment lines
    """
    header_lines, comment_lines = [], []
    for line in header_content.splitlines():
        line = line.strip()
        # Comment line
        if line.startswith("#"):
            comment_lines.append(line)
        # Non-empty non-comment line = header line.
        elif line:
            header_lines.append(line)

    return header_lines, comment_lines


def _parse_record_line(record_line: str) -> dict:
    """
    Extract fields from a record line string into a dictionary.

    Parameters
    ----------
    record_line : str
        The record line contained in the header file

    Returns
    -------
    record_fields : dict
        The fields for the given record line.

    """
    # Dictionary for record fields
    record_fields = {}

    # Read string fields from record line
    match = _rx_record.match(record_line)
    if match is None:
        raise HeaderSyntaxError("invalid syntax in record line")
    (
        record_fields["record_name"],
        record_fields["n_seg"],
        record_fields["n_sig"],
        record_fields["fs"],
        record_fields["counter_freq"],
        record_fields["base_counter"],
        record_fields["sig_len"],
        record_fields["base_time"],
        record_fields["base_date"],
    ) = match.groups()

    for field in RECORD_SPECS.index:
        # Replace empty strings with their read defaults (which are
        # mostly None)
        if record_fields[field] == "":
            record_fields[field] = RECORD_SPECS.loc[field, "read_default"]
        # Typecast non-empty strings for non-string (numerical/datetime)
        # fields
        else:
            if RECORD_SPECS.loc[field, "allowed_types"] == int_types:
                record_fields[field] = int(record_fields[field])
            elif RECORD_SPECS.loc[field, "allowed_types"] == float_types:
                record_fields[field] = float(record_fields[field])
                # cast fs to an int if it is close
                if field == "fs":
                    fs = float(record_fields["fs"])
                    if round(fs, 8) == float(int(fs)):
                        fs = int(fs)
                    record_fields["fs"] = fs
            elif field == "base_time":
                record_fields["base_time"] = wfdb_strptime(
                    record_fields["base_time"]
                )
            elif field == "base_date":
                record_fields["base_date"] = datetime.datetime.strptime(
                    record_fields["base_date"], "%d/%m/%Y"
                ).date()

    # This is not a standard WFDB field, but is useful to set.
    if record_fields["base_date"] and record_fields["base_time"]:
        record_fields["base_datetime"] = datetime.datetime.combine(
            record_fields["base_date"], record_fields["base_time"]
        )

    return record_fields


def _parse_signal_lines(signal_lines: Collection[str]):
    """
    Extract fields from a list of signal line strings into a dictionary.

    Parameters
    ----------
    signal_lines : list
        The name of the signal line that will be used to extact fields.

    Returns
    -------
    signal_fields : dict
        The fields for the given signal line.

    """
    n_sig = len(signal_lines)
    # Dictionary for signal fields
    signal_fields = {}

    # Each dictionary field is a list
    for field in SIGNAL_SPECS.index:
        signal_fields[field] = n_sig * [None]

    # Read string fields from signal line
    for ch in range(n_sig):
        match = _rx_signal.match(signal_lines[ch])
        if match is None:
            raise HeaderSyntaxError("invalid syntax in signal line")
        (
            signal_fields["file_name"][ch],
            signal_fields["fmt"][ch],
            signal_fields["samps_per_frame"][ch],
            signal_fields["skew"][ch],
            signal_fields["byte_offset"][ch],
            signal_fields["adc_gain"][ch],
            signal_fields["baseline"][ch],
            signal_fields["units"][ch],
            signal_fields["adc_res"][ch],
            signal_fields["adc_zero"][ch],
            signal_fields["init_value"][ch],
            signal_fields["checksum"][ch],
            signal_fields["block_size"][ch],
            signal_fields["sig_name"][ch],
        ) = match.groups()

        for field in SIGNAL_SPECS.index:
            # Replace empty strings with their read defaults (which are mostly None)
            # Note: Never set a field to None. [None]* n_sig is accurate, indicating
            # that different channels can be present or missing.
            if signal_fields[field][ch] == "":
                signal_fields[field][ch] = SIGNAL_SPECS.loc[
                    field, "read_default"
                ]

                # Special case: missing baseline defaults to ADCzero if present
                if field == "baseline" and signal_fields["adc_zero"][ch] != "":
                    signal_fields["baseline"][ch] = int(
                        signal_fields["adc_zero"][ch]
                    )
            # Typecast non-empty strings for numerical fields
            else:
                if SIGNAL_SPECS.loc[field, "allowed_types"] is int_types:
                    signal_fields[field][ch] = int(signal_fields[field][ch])
                elif SIGNAL_SPECS.loc[field, "allowed_types"] is float_types:
                    signal_fields[field][ch] = float(signal_fields[field][ch])
                    # Special case: adc_gain of 0 means 200
                    if (
                        field == "adc_gain"
                        and signal_fields["adc_gain"][ch] == 0
                    ):
                        signal_fields["adc_gain"][ch] = 200.0

    return signal_fields


def _read_segment_lines(segment_lines: Collection[str]):
    """
    Extract fields from segment line strings into a dictionary.

    Parameters
    ----------
    segment_line : list
        The name of the segment line that will be used to extact fields.

    Returns
    -------
    segment_fields : dict
        The fields for the given segment line.

    """
    # Dictionary for segment fields
    segment_fields = {}

    # Each dictionary field is a list
    for field in SEGMENT_SPECS.index:
        segment_fields[field] = [None] * len(segment_lines)

    # Read string fields from signal line
    for i in range(len(segment_lines)):
        match = _rx_segment.match(segment_lines[i])
        if match is None:
            raise HeaderSyntaxError("invalid syntax in segment line")
        (
            segment_fields["seg_name"][i],
            segment_fields["seg_len"][i],
        ) = match.groups()

        # Typecast strings for numerical field
        if field == "seg_len":
            segment_fields["seg_len"][i] = int(segment_fields["seg_len"][i])

    return segment_fields
