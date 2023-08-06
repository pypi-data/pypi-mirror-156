"""
A module with better designs for encapsulating header information. To replace _header in a future major release.
"""
from dataclasses import dataclass, field
import datetime
from typing import List, Optional, Tuple

# from tokenize import group


@dataclass
class A:
    a: int = None


@dataclass
class B:
    b: int = None


@dataclass
class C(A, B):
    c: int = None


@dataclass
class RecordFields:
    # Record specification fields
    name: Optional[str] = None
    # n_seg == 1 does NOT mean the same as it being missing.
    n_seg: Optional[int] = None
    n_sig: Optional[int] = None
    fs: Optional[float] = None
    counter_freq: Optional[float] = None
    base_counter: Optional[float] = None
    sig_len: Optional[int] = None
    base_time: Optional[datetime.time] = None
    base_date: Optional[datetime.date] = None


@dataclass
class SignalFields:
    """
    HMMMMM... read vs write defaults?


    """

    # Signal specification fields. One value per channel.
    file_name: List[str] = field(default_factory=list)
    fmt: List[str] = field(default_factory=list)
    samps_per_frame: List[int] = field(default_factory=list)
    skew: List[int] = field(default_factory=list)
    byte_offset: List[int] = field(default_factory=list)
    adc_gain: List[float] = field(default_factory=list)
    baseline: List[int] = field(default_factory=list)
    units: List[str] = field(default_factory=list)
    adc_res: List[int] = field(default_factory=list)
    adc_zero: List[int] = field(default_factory=list)
    init_value: List[int] = field(default_factory=list)
    checksum: List[int] = field(default_factory=list)
    block_size: List[int] = field(default_factory=list)
    sig_name: List[str] = field(default_factory=list)


@dataclass
class SegmentFields:
    # Segment specification fields. One value per segment.
    seg_name: List[str] = None
    seg_len: List[int] = None


@dataclass
class Header(RecordFields, SignalFields, SegmentFields):
    """
    Class capturing all the potential fields in a header file.



    Hmmm, is this necessary?

    Reading:
    - Used to represent raw info read from a header file. Seems wasteful
    if data is just going to be copied over to Single/Multi header classes
    immediately?

    Writing:
    - Write to a file. What if fields conflict? Why offer this API?

    How about having separate Header and MultiHeader classes?

    What about generics? Is there a reason to have both be an instance of Header?

    """

    comments: List[str] = None

    def header_type(self) -> str:
        """
        Single
        Multi-fixed
        Multi-variable
        """
        # if self.


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
            # Look for a comment in the line
            ci = line.find("#")
            if ci > 0:
                header_lines.append(line[:ci])
                # comment on same line as header line
                comment_lines.append(line[ci:])
            else:
                header_lines.append(line)

    return header_lines, comment_lines


x = [1, 2, 3, 4, 5]

y = x[: 2 + 1]
